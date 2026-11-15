"""Exercise the generated Notion CLI and MCP against one local HTTP recorder."""

import http.server
import json
import os
import pathlib
import queue
import subprocess
import sys
import tempfile
import threading


class Mcp:
    def __init__(self, binary, entrypoint, environment):
        self.process = subprocess.Popen(
            [binary, "serve", "mcp", str(entrypoint)], env=environment,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        self.messages = queue.Queue()
        self.errors = []
        self.reader = threading.Thread(target=self.read_stdout)
        self.error_reader = threading.Thread(target=lambda: self.errors.append(self.process.stderr.read()))
        self.reader.start()
        self.error_reader.start()
        self.next_id = 0

    def read_stdout(self):
        try:
            for line in self.process.stdout:
                self.messages.put(json.loads(line))
        except Exception as error:
            self.messages.put(error)
        finally:
            self.messages.put(None)

    def send(self, method, params, request_id=None):
        message = {"jsonrpc": "2.0", "method": method, "params": params}
        if request_id is not None:
            message["id"] = request_id
        self.process.stdin.write(json.dumps(message) + "\n")
        self.process.stdin.flush()

    def call(self, method, params):
        self.next_id += 1
        self.send(method, params, self.next_id)
        while True:
            message = self.messages.get(timeout=30)
            assert message is not None and not isinstance(message, Exception), (method, message, self.errors)
            if "id" in message:
                assert message["id"] == self.next_id, message
                return message

    def close(self):
        try:
            self.process.stdin.close()
            self.process.wait(timeout=30)
            assert self.process.returncode == 0, self.errors
        finally:
            if self.process.poll() is None:
                self.process.kill()
                self.process.wait(timeout=10)
            self.reader.join(timeout=10)
            self.error_reader.join(timeout=10)
            assert not self.reader.is_alive() and not self.error_reader.is_alive()


def probe(binary, root):
    legacy_page = json.loads((root / "tests/fixtures/recorded/page_retrieve_ok.json").read_text())
    page_id = legacy_page["id"]
    page = {"object": "page", "id": page_id}
    response_body = [page]
    records = []

    class Recorder(http.server.BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def do_GET(self):
            records.append({"path": self.path, "headers": {k.lower(): v for k, v in self.headers.items()}})
            payload = json.dumps(response_body[0]).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Recorder)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()
    environment = {
        **os.environ,
        "NOTION_BASE_URL": f"http://127.0.0.1:{server.server_port}",
        "NOTION_BEARERAUTH_TOKEN": "fixture-bearer-token",
        "NOTION_BASICAUTH_USERNAME": "fixture-client",
        "NOTION_BASICAUTH_PASSWORD": "fixture-password",
    }
    entrypoint = root / "src/main.harn"

    def command(*args, env=environment):
        result = subprocess.run([binary, *map(str, args)], env=env, capture_output=True, text=True, timeout=30)
        assert result.returncode == 0, (args, result.stdout, result.stderr)
        return result.stdout

    mcp = None
    try:
        catalog = json.loads(command("tool", "schema", entrypoint, "--pretty"))
        tools = catalog["tools"]
        fixture = json.loads((root / "tests/fixtures/notion.openapi.json").read_text())
        expected = {
            (operation["operationId"], method.upper(), path)
            for path, item in fixture["paths"].items()
            for method, operation in item.items()
            if method in {"get", "put", "post", "delete", "options", "head", "patch", "trace"}
        }
        observed = {(tool["source"]["id"], tool["source"]["binding"]["method"], tool["source"]["binding"]["path"]) for tool in tools}
        assert len(tools) == len(expected) == 46 and observed == expected
        parents = {tuple(tool["cli"]["command"][:-1]) for tool in tools}
        for parent in parents:
            help_text = command("tool", "run", entrypoint, *parent, "--help")
            for tool in tools:
                path = tool["cli"]["command"]
                if tuple(path[:-1]) == parent:
                    assert path[-1] in help_text, (path, help_text)
        assert not records, "publication and help must not make HTTP requests"

        mcp = Mcp(binary, entrypoint, environment)
        initialized = mcp.call("initialize", {"protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "notion-probe", "version": "1"}})
        assert "result" in initialized, initialized
        mcp.send("notifications/initialized", {})
        listed = mcp.call("tools/list", {})
        assert "result" in listed, listed
        names = [tool["name"] for tool in listed["result"]["tools"]]
        assert len(names) == len(set(names)) == 46
        assert set(names) == {tool["name"] for tool in tools}

        with tempfile.TemporaryDirectory(prefix="notion-adapter-input-") as temporary:
            input_path = pathlib.Path(temporary) / "input.json"
            input_path.write_text(json.dumps({"page_id": page_id}))
            cli_page = json.loads(command("tool", "run", entrypoint, "pages", "retrieve_a_page", "--harn-input", "@" + str(input_path), "--json"))
            assert cli_page == page
            assert len(records) == 1, records
            called = mcp.call("tools/call", {"name": "retrieve_a_page", "arguments": {"page_id": page_id}})
            assert "error" not in called and not called["result"].get("isError"), called
            assert called["result"]["structuredContent"] == page
            assert len(records) == 2, records
            for record in records:
                assert record["path"] == f"/v1/pages/{page_id}"
                assert record["headers"]["authorization"] == "Bearer fixture-bearer-token"
                assert record["headers"]["notion-version"] == "2022-06-28"

            input_path.write_text("{}")
            refused = subprocess.run([binary, "tool", "run", str(entrypoint), "pages", "retrieve_a_page", "--harn-input", "@" + str(input_path), "--json"], env=environment, capture_output=True, text=True, timeout=30)
            assert refused.returncode != 0
            rejected = mcp.call("tools/call", {"name": "retrieve_a_page", "arguments": {}})
            assert "error" in rejected or rejected["result"].get("isError"), rejected
            assert len(records) == 2, "invalid inputs must refuse before HTTP"

            # The historical full-page recording predates the pinned schema.
            # Keep its extra/missing fields as a real response-validation negative.
            response_body[0] = legacy_page
            input_path.write_text(json.dumps({"page_id": page_id}))
            refused = subprocess.run([binary, "tool", "run", str(entrypoint), "pages", "retrieve_a_page", "--harn-input", "@" + str(input_path), "--json"], env=environment, capture_output=True, text=True, timeout=30)
            assert refused.returncode != 0 and "output violates its declared schema" in refused.stderr
            rejected = mcp.call("tools/call", {"name": "retrieve_a_page", "arguments": {"page_id": page_id}})
            assert "error" in rejected or rejected["result"].get("isError"), rejected
            assert len(records) == 4, "both invalid responses must reach HTTP and refuse"

        missing = {**environment, "NOTION_BASICAUTH_PASSWORD": ""}
        refused = subprocess.run([binary, "tool", "schema", str(entrypoint)], env=missing, capture_output=True, text=True, timeout=30)
        assert refused.returncode != 0
        assert "fixture-bearer-token" not in refused.stdout + refused.stderr
        assert "fixture-password" not in refused.stdout + refused.stderr
        assert not refused.stdout.strip(), "incomplete credentials must not publish a partial catalog"
    finally:
        try:
            if mcp:
                mcp.close()
        finally:
            server.shutdown()
            server.server_close()
            server_thread.join(timeout=10)
            assert not server_thread.is_alive()
    print(json.dumps({"operations": 46, "cli_help_groups": len(parents), "reached": {"cli": 1, "mcp": 1}, "pre_request_refusals": {"cli": 1, "mcp": 1}, "response_refusals": {"cli": 1, "mcp": 1}, "credential_refusals": 1, "http_requests": len(records), "pending": 0}))


if __name__ == "__main__":
    probe(sys.argv[1], pathlib.Path(sys.argv[2]).resolve())
