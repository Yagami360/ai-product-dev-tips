import argparse
import base64
from contextlib import ExitStack, suppress
from fnmatch import fnmatch
from io import BytesIO
import json
import os
from pathlib import Path
import re
from signal import pause
from socket import AF_UNIX, SHUT_WR, create_connection, socket
import subprocess
import sys
from tempfile import TemporaryDirectory
import time

from anthropic import APIError, Anthropic
from PIL import Image, ImageDraw, ImageGrab

WIDTH, HEIGHT = 1024, 768
PATTERN = "invoice-*.pdf"
SESSION_SOCKET = "/tmp/computer-use-session.sock"
DEFAULT_MESSAGE = (
    "Thunar の画面で Downloads を確認し、ファイル名が invoice- で始まる PDF だけを "
    "Invoices に移動してください。\n"
    "残りのファイルは Downloads に置いたままにしてください。"
)
PDF_NAMES = ("invoice-2026-08.pdf", "invoice-2026-09.pdf", "meeting-notes.pdf")
TEXT_NAMES = ("invoice-draft.txt", "readme.txt")
KEYS = {
    "Control_L+s",
    "Control_L+a",
    "Control_L+l",
    "Control_L+x",
    "Control_L+c",
    "Control_L+v",
    "Alt_L+Up",
    "Return",
    "Escape",
    "Tab",
    "Shift_L+Tab",
    "Up",
    "Down",
    "Left",
    "Right",
    "Home",
    "End",
    "BackSpace",
}


def create_fixture(downloads, invoices):
    downloads.mkdir()
    invoices.mkdir()
    for name in PDF_NAMES:
        image = Image.new("RGB", (420, 160), "white")
        ImageDraw.Draw(image).text((24, 24), name, fill="black")
        image.convert("P").save(downloads / name)
    for name in TEXT_NAMES:
        (downloads / name).write_text(f"Demo file: {name}\n", encoding="utf-8")


def file_contents(directory):
    if directory.is_symlink():
        return None
    try:
        return {
            path.name: (
                path.read_bytes() if path.is_file() and not path.is_symlink() else None
            )
            for path in directory.iterdir()
        }
    except (FileNotFoundError, NotADirectoryError):
        return None


def stop_process(process):
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def wait_for_port(process, port):
    for _ in range(50):
        if process.poll() is not None:
            break
        try:
            with create_connection(("127.0.0.1", port), timeout=0.2):
                return
        except OSError:
            time.sleep(0.1)
    raise RuntimeError(f"Desktop viewer could not listen on port {port}.")


def pause_view(message):
    print(message, flush=True)
    try:
        input()
    except EOFError:
        return False
    return True


class Desktop:
    def __init__(self, downloads, invoices):
        self.downloads = downloads
        self.invoices = invoices
        self.env = os.environ.copy()
        self.env.pop("ANTHROPIC_API_KEY", None)
        self.env.pop("ANTHROPIC_AUTH_TOKEN", None)
        self.env.pop("NOVNC_PASSWORD", None)
        runtime = downloads.parent / ".runtime"
        runtime.mkdir(mode=0o700)
        self.env.update(HOME=str(downloads.parent), XDG_RUNTIME_DIR=str(runtime))

    def command(self, *args):
        return subprocess.run(
            args, env=self.env, check=True, capture_output=True, text=True, timeout=10
        ).stdout

    def launch(self, processes, *command, stderr=None):
        process = subprocess.Popen(
            command, env=self.env, stdout=subprocess.DEVNULL, stderr=stderr
        )
        processes.callback(stop_process, process)
        return process

    def start(self, processes):
        self.launch(processes, "openbox", "--sm-disable")
        self.launch(processes, "dbus-run-session", "--", "thunar", str(self.downloads))
        window = self.command(
            "xdotool", "search", "--sync", "--onlyvisible", "--class", "^Thunar$"
        ).splitlines()[0]
        self.command("xdotool", "windowactivate", "--sync", window)
        self.command(
            "wmctrl", "-ir", hex(int(window)), "-b", "add,maximized_vert,maximized_horz"
        )
        time.sleep(0.3)
        self.command("xdotool", "key", "Control_L+2")
        time.sleep(0.3)

    def start_viewer(self, processes, *, password=None):
        auth_options = ["-viewonly", "-nopw"]
        if password is not None:
            password_file = self.downloads.parent / ".runtime" / "vnc-password"
            fd = os.open(password_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "w", encoding="ascii") as file:
                file.write(password + "\n")
            auth_options = ["-passwdfile", str(password_file)]
        vnc = self.launch(
            processes,
            "x11vnc",
            "-display",
            self.env["DISPLAY"],
            "-localhost",
            "-rfbport",
            "5900",
            "-forever",
            "-shared",
            *auth_options,
            "-nosel",
            "-noxdamage",
            "-quiet",
        )
        wait_for_port(vnc, 5900)
        proxy_log = self.downloads.parent / "websockify.log"
        with proxy_log.open("w", encoding="utf-8") as log:
            proxy = self.launch(
                processes,
                str(Path(sys.executable).with_name("websockify")),
                "--web",
                "/opt/novnc",
                "6080",
                "127.0.0.1:5900",
                stderr=log,
            )
        try:
            wait_for_port(proxy, 6080)
        except RuntimeError:
            print(proxy_log.read_text(encoding="utf-8"), file=sys.stderr)
            raise

    def screenshot(self):
        return ImageGrab.grab(xdisplay=self.env["DISPLAY"])

    def execute(self, action):
        name = action.get("action")
        if name == "screenshot":
            png = BytesIO()
            self.screenshot().save(png, format="PNG")
            return {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": base64.b64encode(png.getvalue()).decode("ascii"),
                },
            }

        if name in ("left_click", "double_click"):
            coordinate = action.get("coordinate")
            if (
                not isinstance(coordinate, list)
                or len(coordinate) != 2
                or any(type(value) is not int for value in coordinate)
                or not (0 <= coordinate[0] < WIDTH and 0 <= coordinate[1] < HEIGHT)
            ):
                raise ValueError(
                    "Click must use integer coordinates inside the screen."
                )
            if action.get("key"):
                raise ValueError("Use Ctrl+S (Control_L+s) for multi-file selection.")
            x, y = map(str, coordinate)
            count = "2" if name == "double_click" else "1"
            self.command("xdotool", "mousemove", x, y, "click", "--repeat", count, "1")
        elif name == "key":
            key = action.get("text")
            if not isinstance(key, str) or key not in KEYS:
                raise ValueError("Use X11 names such as Control_L+s or Return.")
            self.command("xdotool", "key", "--clearmodifiers", key)
        elif name == "type":
            text = action.get("text")
            if text not in (PATTERN, str(self.downloads), str(self.invoices)):
                raise ValueError(
                    "Type only the demo glob or a task folder's exact path."
                )
            self.command("xdotool", "type", "--clearmodifiers", "--", text)
        else:
            raise ValueError(
                "Allowed actions: screenshot, left_click, double_click, key, type."
            )

        time.sleep(0.35)
        return {"type": "text", "text": "OK"}


def run_demo(desktop, trace):
    actions = [
        {"action": "key", "text": "Control_L+s"},
        {"action": "type", "text": PATTERN},
        {"action": "key", "text": "Return"},
        {"action": "key", "text": "Control_L+x"},
        {"action": "key", "text": "Control_L+l"},
        {"action": "type", "text": str(desktop.invoices)},
        {"action": "key", "text": "Return"},
        {"action": "key", "text": "Control_L+v"},
    ]
    for action in actions:
        desktop.execute(action)
        trace.append({"action": action["action"]})


def send_message():
    message = sys.stdin.read()
    with socket(AF_UNIX) as connection:
        try:
            connection.connect(SESSION_SOCKET)
            connection.sendall(json.dumps(message, ensure_ascii=False).encode("utf-8"))
            connection.shutdown(SHUT_WR)
            with connection.makefile("rb") as response:
                output = response.read()
        except (
            FileNotFoundError,
            ConnectionRefusedError,
            ConnectionResetError,
            BrokenPipeError,
        ):
            raise SystemExit(
                "この画面には指示を送れません。make stop の後、make run で起動してください。"
            ) from None
    if not output:
        raise SystemExit("Claude の実行結果を受け取れませんでした。")
    print(output.decode("utf-8"))
    return json.loads(output)["success"]


def run_claude(desktop, model, max_turns, trace, message):
    messages = [
        {
            "role": "user",
            "content": (
                f"{message or DEFAULT_MESSAGE}\n\n"
                f"Downloads のパスは {desktop.downloads}、Invoices のパスは {desktop.invoices} です。\n"
                "最初にスクリーンショットを取得し、移動後に Invoices の中身を確認してください。\n"
                "Ctrl+S（パターンで選択）、Ctrl+X、Ctrl+L、Ctrl+V を使用できます。\n"
                "key 操作の text には、Control_L+s や Return などの X11 キー名を指定してください。\n"
                f"type 操作に指定できるのは {PATTERN} または対象フォルダーの正確なパスです。\n"
                "操作は Thunar 内で行い、最後に Invoices を表示してください。"
            ),
        }
    ]
    with Anthropic(timeout=30, max_retries=0) as client:
        for _ in range(max_turns):
            response = client.beta.messages.create(
                model=model,
                max_tokens=1200,
                betas=["computer-use-2025-11-24"],
                tools=[
                    {
                        "name": "computer",
                        "type": "computer_20251124",
                        "display_width_px": WIDTH,
                        "display_height_px": HEIGHT,
                    }
                ],
                messages=messages,
            )
            calls = [block for block in response.content if block.type == "tool_use"]
            trace.append({"stop_reason": response.stop_reason})
            if not calls:
                return

            messages.append(
                {
                    "role": "assistant",
                    "content": [
                        block.model_dump(exclude_none=True)
                        for block in response.content
                    ],
                }
            )
            results = []
            for call in calls:
                result = {"type": "tool_result", "tool_use_id": call.id}
                try:
                    if call.name != "computer":
                        raise ValueError("Unknown tool.")
                    result["content"] = [desktop.execute(call.input)]
                except ValueError as error:
                    result.update(content=str(error), is_error=True)
                results.append(result)
                trace.append(
                    {
                        "action": call.input.get("action"),
                        "is_error": result.get("is_error", False),
                    }
                )
            messages.append({"role": "user", "content": results})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["demo", "claude", "manual"], default="demo")
    parser.add_argument("--model", default="claude-sonnet-4-6")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--out-dir", type=Path, default=Path("/tmp/run-output"))
    parser.add_argument("--view", action="store_true")
    session = parser.add_mutually_exclusive_group()
    session.add_argument("--wait-for-message", action="store_true")
    session.add_argument("--send-message", action="store_true")
    args = parser.parse_args()
    if args.max_turns < 1:
        parser.error("--max-turns must be at least 1")
    if args.wait_for_message and args.mode != "claude":
        parser.error("--wait-for-message requires --mode claude")
    needs_api_key = args.send_message or (
        args.mode == "claude" and not args.wait_for_message
    )
    if needs_api_key and not os.environ.get("ANTHROPIC_API_KEY"):
        parser.error("Set ANTHROPIC_API_KEY to run in claude mode.")
    if args.send_message:
        raise SystemExit(0 if send_message() else 1)
    if args.wait_for_message:
        Path(SESSION_SOCKET).unlink(missing_ok=True)
    manual = args.mode == "manual"
    password = os.environ.get("NOVNC_PASSWORD", "") if manual else None
    if manual and not re.fullmatch(r"[A-Za-z0-9]{8}", password):
        parser.error("Set NOVNC_PASSWORD to eight ASCII letters or digits in .env.")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    trace = []
    api_error = None
    with TemporaryDirectory(
        prefix="computer-use-"
    ) as workspace, ExitStack() as processes:
        downloads = Path(workspace) / "Downloads"
        invoices = Path(workspace) / "Invoices"
        create_fixture(downloads, invoices)
        initial = file_contents(downloads)
        expected_invoices = {
            name: data for name, data in initial.items() if fnmatch(name, PATTERN)
        }
        expected_downloads = {
            name: data
            for name, data in initial.items()
            if name not in expected_invoices
        }

        desktop = Desktop(downloads, invoices)
        desktop.start(processes)
        desktop.screenshot().save(args.out_dir / "before.png")
        if args.view or manual or args.wait_for_message:
            desktop.start_viewer(processes, password=password)
        message = ""
        if args.wait_for_message:
            with socket(AF_UNIX) as server:
                server.bind(SESSION_SOCKET)
                server.listen(1)
                print(
                    "noVNC is ready. Run make send-message to start Claude.", flush=True
                )
                connection, _ = server.accept()
                connection = processes.enter_context(connection)
            with connection.makefile("rb") as request:
                message = json.load(request)
        elif args.view and not manual:
            pause_view(
                "noVNC is ready. Open it in your browser, then press Enter to start."
            )
        start = time.monotonic()
        if manual:
            if not pause_view(
                "noVNC is ready. Sort the files in your browser, then press Enter here to finish."
            ):
                raise SystemExit("Manual mode needs an open terminal input stream.")
        elif args.mode == "claude":
            try:
                run_claude(desktop, args.model, args.max_turns, trace, message)
            except APIError as error:
                api_error = type(error).__name__
        else:
            run_demo(desktop, trace)

        actual_downloads = file_contents(downloads)
        actual_invoices = file_contents(invoices)
        success = (
            api_error is None
            and actual_downloads == expected_downloads
            and actual_invoices == expected_invoices
        )
        result = {
            "mode": args.mode,
            "success": success,
            "downloads": sorted(actual_downloads or {}),
            "invoices": sorted(actual_invoices or {}),
            "expected_downloads": sorted(expected_downloads),
            "expected_invoices": sorted(expected_invoices),
            "seconds": round(time.monotonic() - start, 3),
            "trace": trace,
        }
        unavailable = [
            name
            for name, contents in (
                ("Downloads", actual_downloads),
                ("Invoices", actual_invoices),
            )
            if contents is None
        ]
        if unavailable:
            result["unavailable_folders"] = unavailable
        if api_error:
            result["api_error"] = api_error
        desktop.screenshot().save(args.out_dir / "after.png")
        if args.view and not manual and not args.wait_for_message:
            pause_view(
                "Run finished. Press Enter to close the viewer and export the artifacts."
            )

        output = json.dumps(result, indent=2)
        (args.out_dir / "result.json").write_text(output + "\n", encoding="utf-8")
        if args.wait_for_message:
            with suppress(BrokenPipeError, ConnectionResetError):
                connection.sendall(output.encode("utf-8"))
            connection.close()
            print("Run finished. Run make stop to close the viewer.", flush=True)
            while True:
                pause()

    print(output)
    raise SystemExit(0 if success else 1)
