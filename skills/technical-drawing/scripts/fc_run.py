#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# ///
"""Run a Python file inside the running FreeCAD GUI and print what it printed.

Talks to the XML-RPC server of the FreeCADMCP addon (the same server the
freecad-mcp MCP tools call), so the model and drawing code can live in files
the agent edits and re-runs instead of in inline tool arguments.

    fc_run.py model.py [drawing.py ...]   run files in order, stop at first error
    fc_run.py --ping                      check FreeCAD can run code now
    fc_run.py --headless geom.py          run in a separate freecadcmd process

--headless is for geometry that might crash OpenCascade (fillets, chamfers,
many-tool booleans): a segfault there kills only the helper process, and the
GUI with every open document survives. The file must not import FreeCADGui.
"""
import argparse
import os
import shutil
import signal
import subprocess
import sys
import xmlrpc.client

URI = os.environ.get("FREECAD_RPC", "http://localhost:9875")
FREECADCMD = os.environ.get("FREECADCMD") or shutil.which("freecadcmd") or \
    "/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd"


# Each file runs in a fresh namespace under its own filename, so tracebacks
# name the file and line, and names from one run never leak into the next.
# The addon discards captured output when the code raises, so the wrapper
# catches the exception, prints the traceback after a marker, and returns
# normally; main() turns the marker into a failure.
FAILED = "__FC_RUN_FAILED__"
WRAPPER = """
import traceback as _tb
_path = {path!r}
_ns = {{"__name__": "__main__", "__file__": _path}}
try:
    exec(compile(open(_path, encoding="utf-8").read(), _path, "exec"), _ns)
except Exception:
    print({failed!r})
    print(_tb.format_exc())
"""


def proxy(timeout: float) -> xmlrpc.client.ServerProxy:
    class T(xmlrpc.client.Transport):
        def make_connection(self, host):
            c = super().make_connection(host)
            c.timeout = timeout
            return c

    headers = []
    token = os.environ.get("FREECAD_MCP_TOKEN")
    if token:
        headers = [("Authorization", f"Bearer {token}")]
    return xmlrpc.client.ServerProxy(URI, transport=T(headers=headers), allow_none=True)


def run_headless(files, timeout) -> int:
    import tempfile
    for f in files:
        path = os.path.abspath(f)
        fd, log = tempfile.mkstemp(suffix=".log")
        os.close(fd)
        # freecadcmd routes sys.stdout through its own console buffer, which a
        # segfault discards; a line-buffered log file keeps every line printed
        # before the crash.
        code = (f"import sys; sys.stdout = sys.stderr = open({log!r}, 'w', buffering=1)\n"
                + WRAPPER.format(path=path, failed=FAILED))
        print(f"--- {f} (headless)")
        try:
            r = subprocess.run([FREECADCMD, "-c", code], capture_output=True,
                               text=True, timeout=timeout)
            timed_out = False
        except subprocess.TimeoutExpired:
            timed_out = True
        out = open(log, encoding="utf-8", errors="replace").read()
        os.remove(log)
        print(out.strip().replace(FAILED, "FAILED:"), flush=True)
        if timed_out:
            print(f"FAILED: timed out after {timeout}s", file=sys.stderr)
            return 1
        if r.returncode < 0:
            sig = signal.Signals(-r.returncode).name
            print(f"FAILED: freecadcmd killed by {sig} - OpenCascade crashed on this "
                  "geometry; the GUI is unaffected", file=sys.stderr)
            return 1
        if FAILED in out or r.returncode != 0:
            print(r.stderr.strip()[-2000:], file=sys.stderr)
            return 1
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--ping", action="store_true")
    ap.add_argument("--headless", action="store_true")
    ap.add_argument("--timeout", type=float, default=120)
    a = ap.parse_args()
    if a.headless:
        return run_headless(a.files, a.timeout)
    s = proxy(a.timeout + 30)
    if a.ping:
        # The RPC server answers get_rpc_status while a modal dialog (such as
        # Document Recovery after a crash) blocks the GUI thread, so the ping
        # runs real code; a blocked GUI fails it at once with the reason.
        try:
            r = proxy(40).execute_code("print('ok')", 10)
        except ConnectionRefusedError:
            print("FreeCAD not ready: nothing listens on", URI,
                  "- FreeCAD is not running (relaunch: open -a FreeCAD)", file=sys.stderr)
            return 1
        if isinstance(r, dict) and r.get("success"):
            print("FreeCAD ready")
            return 0
        print("FreeCAD not ready:", r.get("error", r) if isinstance(r, dict) else r, file=sys.stderr)
        return 1
    for f in a.files:
        path = os.path.abspath(f)
        r = s.execute_code(WRAPPER.format(path=path, failed=FAILED), a.timeout)
        out = r.get("message", "") if isinstance(r, dict) else str(r)
        out = out.replace("Python code executed successfully.\nOutput: ", "", 1)
        print(f"--- {f}")
        print(out.strip().replace(FAILED, "FAILED:"))
        if FAILED in out:
            return 1
        if not (isinstance(r, dict) and r.get("success")):
            print(r.get("error", "") if isinstance(r, dict) else "", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
