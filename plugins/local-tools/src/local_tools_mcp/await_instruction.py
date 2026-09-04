from __future__ import annotations

import datetime as dt
import errno
import hmac
import html
import http.client
import ipaddress
import json
import os
import re
import secrets
import sqlite3
import sys
import threading
import time
import uuid
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlencode, urlsplit

from .json_types import JsonObject, JsonValue

SERVICE_NAME = "local-tools-mcp-await-instruction"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
DEFAULT_JOB_ROOT = Path.home() / ".codex" / "local-tools" / "jobs"
MAX_INSTRUCTION_BYTES = 64 * 1024
WAIT_ID_PATTERN = re.compile(r"wait_[a-f0-9]{32}")

_DASHBOARD_LOCK = threading.Lock()
_DASHBOARD_SERVER: DashboardHTTPServer | None = None
_DASHBOARD_THREAD: threading.Thread | None = None
_DASHBOARD_URL: str | None = None
_DASHBOARD_ROOT: Path | None = None
_DASHBOARD_WATCHDOG_ROOTS: set[Path] = set()


class DashboardHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, address: tuple[str, int], root: Path) -> None:
        self.control_root = root
        super().__init__(address, DashboardRequestHandler)


class AwaitInstructionCancelled(Exception):
    pass


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def format_waiting_since(value: JsonValue) -> str:
    if not isinstance(value, str):
        return "Unknown"
    try:
        timestamp = dt.datetime.fromisoformat(value)
    except ValueError:
        return "Unknown"
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=dt.timezone.utc)
    return timestamp.astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def control_root() -> Path:
    configured = (os.environ.get("LOCAL_TOOLS_MCP_AWAIT_ROOT") or "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    job_root = Path(os.environ.get("LOCAL_TOOLS_MCP_JOB_ROOT", str(DEFAULT_JOB_ROOT))).expanduser()
    return (job_root.parent / "await_instruction").resolve()


def configured_host() -> str:
    raw = (os.environ.get("LOCAL_TOOLS_MCP_AWAIT_HOST") or DEFAULT_HOST).strip()
    try:
        return str(ipaddress.ip_address(raw))
    except ValueError as exc:
        raise ValueError("LOCAL_TOOLS_MCP_AWAIT_HOST must be an IP address") from exc


def configured_port() -> int:
    raw = (os.environ.get("LOCAL_TOOLS_MCP_AWAIT_PORT") or "").strip()
    if not raw:
        return DEFAULT_PORT
    try:
        port = int(raw)
    except ValueError as exc:
        raise ValueError("LOCAL_TOOLS_MCP_AWAIT_PORT must be an integer") from exc
    if port < 0 or port > 65535:
        raise ValueError("LOCAL_TOOLS_MCP_AWAIT_PORT must be between 0 and 65535")
    return port


def dashboard_url(host: str, port: int) -> str:
    url_host = f"[{host}]" if ":" in host else host
    return f"http://{url_host}:{port}/"


def should_open_browser() -> bool:
    raw = (os.environ.get("LOCAL_TOOLS_MCP_AWAIT_OPEN_BROWSER") or "").strip().lower()
    return raw not in {"0", "false", "no", "off"}


def codex_state_paths() -> list[Path]:
    candidates: list[Path] = []
    configured_home = (os.environ.get("CODEX_HOME") or "").strip()
    if configured_home:
        candidates.append(Path(configured_home).expanduser() / "state_5.sqlite")
    home = Path.home()
    candidates.extend(sorted(home.glob(".codex*/state_5.sqlite")))

    unique: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(resolved)
    return unique


def lookup_codex_thread_title(thread_id: str) -> str | None:
    for state_path in codex_state_paths():
        if not state_path.is_file():
            continue
        try:
            connection = sqlite3.connect(
                f"{state_path.as_uri()}?mode=ro",
                uri=True,
                timeout=0.5,
            )
            try:
                row = connection.execute(
                    "SELECT title FROM threads WHERE id = ?",
                    (thread_id,),
                ).fetchone()
            finally:
                connection.close()
        except (OSError, sqlite3.Error):
            continue
        if row is None or not isinstance(row[0], str):
            continue
        title = row[0].strip()
        if title:
            return title if len(title) <= 300 else f"{title[:299]}…"
    return None


def request_path(root: Path, wait_id: str) -> Path:
    return root / f"{wait_id}.request.json"


def response_path(root: Path, wait_id: str) -> Path:
    return root / f"{wait_id}.response.json"


def ensure_control_root(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    try:
        root.chmod(0o700)
    except OSError:
        pass


def write_json(path: Path, payload: JsonObject, *, exclusive: bool = False) -> bool:
    encoded = (json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    temp_path = path.with_name(f".{path.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp")
    descriptor = os.open(temp_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
        if not exclusive:
            temp_path.replace(path)
            return True
        try:
            os.link(temp_path, path)
        except FileExistsError:
            return False
        return True
    finally:
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass


def read_json(path: Path) -> JsonObject | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def safe_unlink(path: Path) -> None:
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass


def process_exists(pid: JsonValue) -> bool:
    if isinstance(pid, bool) or not isinstance(pid, int) or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def valid_wait_record(payload: JsonObject) -> bool:
    return (
        isinstance(payload.get("wait_id"), str)
        and WAIT_ID_PATTERN.fullmatch(payload["wait_id"]) is not None
        and isinstance(payload.get("thread_id"), str)
        and bool(payload["thread_id"].strip())
        and isinstance(payload.get("thread_label"), str)
        and bool(payload["thread_label"].strip())
        and (payload.get("comment") is None or isinstance(payload.get("comment"), str))
        and isinstance(payload.get("token"), str)
        and bool(payload["token"])
    )


def load_wait(root: Path, wait_id: str) -> JsonObject | None:
    if WAIT_ID_PATTERN.fullmatch(wait_id) is None:
        return None
    record = read_json(request_path(root, wait_id))
    if record is None or not valid_wait_record(record) or record["wait_id"] != wait_id:
        return None
    return record


def list_pending_waits(root: Path) -> list[JsonObject]:
    ensure_control_root(root)
    records: list[JsonObject] = []
    for path in root.glob("wait_*.request.json"):
        record = read_json(path)
        if record is None or not valid_wait_record(record):
            continue
        wait_id = record["wait_id"]
        if response_path(root, wait_id).exists():
            continue
        if not process_exists(record.get("pid")):
            safe_unlink(path)
            safe_unlink(response_path(root, wait_id))
            continue
        records.append(record)
    records.sort(key=lambda record: str(record.get("created_at") or ""))
    return records


def register_wait(root: Path, thread_id: str, comment: str | None = None) -> JsonObject:
    ensure_control_root(root)
    thread_id = thread_id.strip()
    if not thread_id:
        raise ValueError("Codex thread ID is unavailable")
    if len(thread_id) > 200:
        raise ValueError("Codex thread ID is invalid")
    thread_title = lookup_codex_thread_title(thread_id)
    thread_label = thread_title or f"Codex thread {thread_id}"
    wait_id = f"wait_{uuid.uuid4().hex}"
    record = {
        "wait_id": wait_id,
        "thread_id": thread_id,
        "thread_title": thread_title,
        "thread_label": thread_label,
        "comment": comment,
        "created_at": utc_now(),
        "pid": os.getpid(),
        "token": secrets.token_urlsafe(32),
    }
    write_json(request_path(root, wait_id), record)
    return record


def browser_wait_record(record: JsonObject) -> JsonObject:
    return {
        "wait_id": record["wait_id"],
        "thread_id": record["thread_id"],
        "thread_title": record.get("thread_title"),
        "thread_label": record["thread_label"],
        "comment": record.get("comment"),
        "created_at": record.get("created_at"),
        "waiting_since": format_waiting_since(record.get("created_at")),
        "token": record["token"],
    }


DASHBOARD_SCRIPT = r"""
const container = document.querySelector('.threads');
const liveStatus = document.querySelector('#live-status');
const selectedWaitId = new URLSearchParams(window.location.search).get('wait_id');
let renderedSignature = '';

function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}

function renderWaits(waits) {
  const ordered = [...waits].sort((left, right) => {
    if (left.wait_id === selectedWaitId) return -1;
    if (right.wait_id === selectedWaitId) return 1;
    return String(left.created_at || '').localeCompare(String(right.created_at || ''));
  });
  const signature = JSON.stringify(
    ordered.map((wait) => [wait.wait_id, wait.thread_label, wait.comment, wait.waiting_since]),
  );
  if (signature === renderedSignature) return;

  const drafts = new Map(
    [...container.querySelectorAll('article[data-wait-id]')].map((card) => [
      card.dataset.waitId,
      card.querySelector('textarea')?.value || '',
    ]),
  );
  container.replaceChildren();
  if (ordered.length === 0) {
    const empty = element('section', undefined, 'empty-state');
    empty.append(element('h2', 'No threads are waiting'));
    empty.append(element('p', 'This page updates automatically when an AI calls await_instruction.'));
    container.append(empty);
    document.title = 'Thread Awaiting Instruction';
  } else {
    for (const wait of ordered) {
      const selected = wait.wait_id === selectedWaitId;
      const card = element('article', undefined, `thread-card${selected ? ' selected' : ''}`);
      card.dataset.waitId = wait.wait_id;
      card.append(element('div', 'Thread Awaiting Instruction', 'eyebrow'));
      card.append(element('h2', wait.thread_label));
      const metadata = element(
        'div',
        `Codex thread ${wait.thread_id}\nWaiting since ${wait.waiting_since} · ${wait.wait_id.slice(-8)}`,
        'metadata',
      );
      card.append(metadata);
      if (wait.comment) {
        const comment = element('div', undefined, 'agent-comment');
        comment.append(element('div', 'Agent message', 'agent-comment-label'));
        comment.append(element('p', wait.comment));
        card.append(comment);
      }

      const form = document.createElement('form');
      form.method = 'post';
      form.action = `/instruction/${encodeURIComponent(wait.wait_id)}`;
      const token = document.createElement('input');
      token.type = 'hidden';
      token.name = 'token';
      token.value = wait.token;
      const textarea = document.createElement('textarea');
      textarea.name = 'instruction';
      textarea.required = true;
      textarea.placeholder = 'Tell this thread what to do next...';
      textarea.value = drafts.get(wait.wait_id) || '';
      const button = element('button', 'Send to this thread');
      button.type = 'submit';
      form.append(token, textarea, button);
      card.append(form);
      container.append(card);
    }
    const selected = ordered.find((wait) => wait.wait_id === selectedWaitId);
    document.title = selected
      ? `Thread Awaiting Instruction - ${selected.thread_label}`
      : 'Thread Awaiting Instruction';
  }
  renderedSignature = signature;
}

async function refreshWaits() {
  try {
    const response = await fetch('/api/waits', {cache: 'no-store'});
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const payload = await response.json();
    renderWaits(payload.waits || []);
    liveStatus.textContent = 'Live';
    liveStatus.className = 'live connected';
  } catch (error) {
    liveStatus.textContent = 'Reconnecting…';
    liveStatus.className = 'live disconnected';
  }
}

container.addEventListener('submit', async (event) => {
  const form = event.target.closest('form');
  if (!form) return;
  event.preventDefault();
  const button = form.querySelector('button');
  button.disabled = true;
  try {
    const response = await fetch(form.action, {
      method: 'POST',
      body: new URLSearchParams(new FormData(form)),
    });
    if (!response.ok) throw new Error(await response.text());
    renderedSignature = '';
    await refreshWaits();
  } catch (error) {
    button.disabled = false;
    liveStatus.textContent = 'Send failed';
    liveStatus.className = 'live disconnected';
  }
});

refreshWaits();
setInterval(refreshWaits, 1000);
"""


def dashboard_page(root: Path, *, selected_wait_id: str | None) -> str:
    waits = list_pending_waits(root)
    if selected_wait_id:
        waits.sort(key=lambda record: record["wait_id"] != selected_wait_id)
    selected = next((record for record in waits if record["wait_id"] == selected_wait_id), None)
    page_title = "Thread Awaiting Instruction"
    if selected is not None:
        page_title = f"{page_title} - {selected['thread_label']}"

    cards: list[str] = []
    for record in waits:
        wait_id = record["wait_id"]
        thread_label = html.escape(record["thread_label"])
        thread_id = html.escape(record["thread_id"])
        token = html.escape(record["token"], quote=True)
        waiting_since = html.escape(format_waiting_since(record.get("created_at")))
        comment = record.get("comment")
        comment_html = ""
        if isinstance(comment, str) and comment:
            comment_html = (
                '<div class="agent-comment"><div class="agent-comment-label">Agent message</div>'
                f"<p>{html.escape(comment)}</p></div>"
            )
        selected_class = " selected" if wait_id == selected_wait_id else ""
        cards.append(
            f"""
    <article class="thread-card{selected_class}" data-wait-id="{html.escape(wait_id)}">
      <div class="eyebrow">Thread Awaiting Instruction</div>
      <h2>{thread_label}</h2>
      <div class="metadata">Codex thread {thread_id}<br>Waiting since {waiting_since} · {html.escape(wait_id[-8:])}</div>
      {comment_html}
      <form method="post" action="/instruction/{quote(wait_id, safe="")}">
        <input type="hidden" name="token" value="{token}">
        <textarea name="instruction" required placeholder="Tell this thread what to do next..."></textarea>
        <button type="submit">Send to this thread</button>
      </form>
    </article>"""
        )

    if not cards:
        cards.append(
            """
    <section class="empty-state">
      <h2>No threads are waiting</h2>
      <p>This page will populate when an AI calls <code>await_instruction</code>.</p>
    </section>"""
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(page_title)}</title>
  <style>
    :root {{ color-scheme: dark; font-family: Inter, ui-sans-serif, system-ui, sans-serif; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; min-height: 100vh; background: #0d1119; color: #f6f8fc; }}
    main {{ width: min(68rem, calc(100% - 2rem)); margin: 0 auto; padding: 2rem 0 4rem; }}
    header {{ display: flex; align-items: end; justify-content: space-between; gap: 1rem; margin-bottom: 1.25rem; }}
    h1 {{ margin: 0; font-size: clamp(1.7rem, 4vw, 2.5rem); }}
    h2 {{ margin: .35rem 0 .3rem; font-size: 1.25rem; }}
    p {{ color: #aeb8cb; }}
    .refresh {{ color: #a9bcff; text-decoration: none; }}
    .header-actions {{ display: flex; align-items: center; gap: 1rem; }}
    .live {{ font-size: .8rem; font-weight: 700; }}
    .connected {{ color: #7ee2a8; }}
    .disconnected {{ color: #ff9b9b; }}
    .threads {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 28rem), 1fr)); gap: 1rem; }}
    .thread-card, .empty-state {{ padding: 1.25rem; border: 1px solid #2d374a; border-radius: .9rem; background: #171d28; }}
    .thread-card.selected {{ border-color: #7897ff; box-shadow: 0 0 0 1px #7897ff; }}
    .eyebrow {{ color: #8fa9ff; font-size: .75rem; font-weight: 800; letter-spacing: .09em; text-transform: uppercase; }}
    .metadata {{ margin-bottom: 1rem; color: #8995aa; font-size: .8rem; white-space: pre-line; }}
    .agent-comment {{ margin-bottom: 1rem; padding: .8rem; border-left: 3px solid #7897ff; border-radius: .35rem; background: #101725; }}
    .agent-comment-label {{ color: #8fa9ff; font-size: .7rem; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; }}
    .agent-comment p {{ margin: .35rem 0 0; color: #dce3f2; white-space: pre-wrap; }}
    textarea {{ width: 100%; min-height: 9rem; resize: vertical; border: 1px solid #3a465d; border-radius: .65rem; padding: .75rem; background: #0c1119; color: inherit; font: inherit; }}
    button {{ margin-top: .7rem; border: 0; border-radius: .65rem; padding: .7rem 1rem; background: #7897ff; color: #091020; font: inherit; font-weight: 800; cursor: pointer; }}
  </style>
</head>
<body>
  <main>
    <header>
      <div><div class="eyebrow">Local Tools MCP</div><h1>Threads Awaiting Instruction</h1></div>
      <div class="header-actions"><span id="live-status" class="live">Connecting…</span><a class="refresh" href="/">Refresh</a></div>
    </header>
    <section class="threads">{"".join(cards)}
    </section>
  </main>
  <script src="/dashboard.js" defer></script>
</body>
</html>
"""


class DashboardRequestHandler(BaseHTTPRequestHandler):
    server: DashboardHTTPServer

    def send_bytes(self, status: HTTPStatus, body: bytes, content_type: str) -> None:
        self.send_response(status.value)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'none'; style-src 'unsafe-inline'; script-src 'self'; connect-src 'self'; form-action 'self'",
        )
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, status: HTTPStatus, body: str) -> None:
        self.send_bytes(status, body.encode("utf-8"), "text/html; charset=utf-8")

    def do_GET(self) -> None:
        parsed = urlsplit(self.path)
        if parsed.path == "/health":
            body = json.dumps(
                {"service": SERVICE_NAME, "control_root": str(self.server.control_root)},
                separators=(",", ":"),
            ).encode("utf-8")
            self.send_bytes(HTTPStatus.OK, body, "application/json")
            return
        if parsed.path == "/api/waits":
            body = json.dumps(
                {
                    "waits": [
                        browser_wait_record(record) for record in list_pending_waits(self.server.control_root)
                    ]
                },
                ensure_ascii=False,
                separators=(",", ":"),
            ).encode("utf-8")
            self.send_bytes(HTTPStatus.OK, body, "application/json")
            return
        if parsed.path == "/dashboard.js":
            self.send_bytes(
                HTTPStatus.OK,
                DASHBOARD_SCRIPT.encode("utf-8"),
                "text/javascript; charset=utf-8",
            )
            return
        if parsed.path != "/":
            self.send_html(HTTPStatus.NOT_FOUND, "<h1>Not found</h1>")
            return
        query = parse_qs(parsed.query)
        selected_wait_id = query.get("wait_id", [None])[0]
        self.send_html(
            HTTPStatus.OK,
            dashboard_page(self.server.control_root, selected_wait_id=selected_wait_id),
        )

    def do_POST(self) -> None:
        path = urlsplit(self.path).path
        prefix = "/instruction/"
        if not path.startswith(prefix):
            self.send_html(HTTPStatus.NOT_FOUND, "<h1>Not found</h1>")
            return
        wait_id = path[len(prefix) :]
        record = load_wait(self.server.control_root, wait_id)
        if record is None or not process_exists(record.get("pid")):
            self.send_html(HTTPStatus.NOT_FOUND, "<h1>This thread is no longer waiting</h1>")
            return

        content_type = self.headers.get("Content-Type", "")
        if not content_type.lower().startswith("application/x-www-form-urlencoded"):
            self.send_html(
                HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
                "<h1>Unsupported form encoding</h1>",
            )
            return
        try:
            content_length = int(self.headers.get("Content-Length", ""))
        except ValueError:
            self.send_html(HTTPStatus.BAD_REQUEST, "<h1>Invalid request length</h1>")
            return
        if content_length < 0 or content_length > (MAX_INSTRUCTION_BYTES * 3) + 4096:
            self.send_html(
                HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                "<h1>Instruction is too large</h1>",
            )
            return
        try:
            form = parse_qs(
                self.rfile.read(content_length).decode("utf-8"),
                keep_blank_values=True,
                max_num_fields=2,
            )
        except (UnicodeDecodeError, ValueError):
            self.send_html(HTTPStatus.BAD_REQUEST, "<h1>Invalid form submission</h1>")
            return

        submitted_token = form.get("token", [""])[0]
        if not hmac.compare_digest(submitted_token, record["token"]):
            self.send_html(HTTPStatus.FORBIDDEN, "<h1>Invalid form token</h1>")
            return
        instruction = form.get("instruction", [""])[0]
        if not instruction.strip():
            self.send_html(HTTPStatus.BAD_REQUEST, "<h1>Instruction is required</h1>")
            return
        if len(instruction.encode("utf-8")) > MAX_INSTRUCTION_BYTES:
            self.send_html(
                HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                "<h1>Instruction is too large</h1>",
            )
            return

        accepted = write_json(
            response_path(self.server.control_root, wait_id),
            {"instruction": instruction, "submitted_at": utc_now()},
            exclusive=True,
        )
        if not accepted:
            self.send_html(HTTPStatus.CONFLICT, "<h1>An instruction was already submitted</h1>")
            return
        self.send_html(
            HTTPStatus.OK,
            "<h1>Instruction sent</h1><p>That thread is resuming. You can close this page.</p>",
        )

    def log_message(self, *_args: object) -> None:
        return


def publish_dashboard_url(root: Path, dashboard_url: str) -> None:
    configured = (os.environ.get("LOCAL_TOOLS_MCP_AWAIT_URL_FILE") or "").strip()
    path = Path(configured).expanduser() if configured else root.parent / "await_instruction.url"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        write_json(path, {"dashboard_url": dashboard_url, "updated_at": utc_now()})
    except OSError:
        pass


def dashboard_is_healthy(url: str, root: Path) -> bool:
    parsed = urlsplit(url)
    if parsed.scheme != "http" or parsed.hostname is None or parsed.port is None:
        return False
    connection = http.client.HTTPConnection(parsed.hostname, parsed.port, timeout=0.5)
    try:
        connection.request("GET", "/health")
        response = connection.getresponse()
        body = response.read()
        if response.status != HTTPStatus.OK.value:
            return False
        return json.loads(body) == {"service": SERVICE_NAME, "control_root": str(root)}
    except (OSError, http.client.HTTPException, json.JSONDecodeError):
        return False
    finally:
        connection.close()


def start_dashboard(root: Path) -> tuple[DashboardHTTPServer, threading.Thread, str]:
    host = configured_host()
    port = configured_port()
    try:
        dashboard_server = DashboardHTTPServer((host, port), root)
    except OSError as exc:
        if port == 0 or exc.errno != errno.EADDRINUSE:
            raise
        dashboard_server = DashboardHTTPServer((host, 0), root)

    actual_port = int(dashboard_server.server_address[1])
    url = dashboard_url(host, actual_port)
    dashboard_thread = threading.Thread(
        target=dashboard_server.serve_forever,
        name=f"await-instruction-dashboard-{actual_port}",
        daemon=True,
    )
    dashboard_thread.start()
    publish_dashboard_url(root, url)
    return dashboard_server, dashboard_thread, url


def ensure_dashboard(root: Path) -> str:
    global _DASHBOARD_ROOT, _DASHBOARD_SERVER, _DASHBOARD_THREAD, _DASHBOARD_URL

    with _DASHBOARD_LOCK:
        if (
            _DASHBOARD_ROOT == root
            and _DASHBOARD_THREAD is not None
            and _DASHBOARD_THREAD.is_alive()
            and _DASHBOARD_URL is not None
        ):
            return _DASHBOARD_URL

        if (
            _DASHBOARD_ROOT == root
            and _DASHBOARD_URL is not None
            and dashboard_is_healthy(_DASHBOARD_URL, root)
        ):
            return _DASHBOARD_URL

        preferred_url = dashboard_url(configured_host(), configured_port())
        if configured_port() != 0 and dashboard_is_healthy(preferred_url, root):
            _DASHBOARD_ROOT = root
            _DASHBOARD_SERVER = None
            _DASHBOARD_THREAD = None
            _DASHBOARD_URL = preferred_url
            publish_dashboard_url(root, preferred_url)
            return preferred_url

        dashboard_server, dashboard_thread, url = start_dashboard(root)
        _DASHBOARD_ROOT = root
        _DASHBOARD_SERVER = dashboard_server
        _DASHBOARD_THREAD = dashboard_thread
        _DASHBOARD_URL = url
        return url


def dashboard_watchdog(root: Path) -> None:
    while True:
        try:
            ensure_dashboard(root)
        except (OSError, ValueError) as exc:
            print(
                f"await_instruction dashboard unavailable: {exc}",
                file=sys.stderr,
                flush=True,
            )
        time.sleep(2.0)


def ensure_dashboard_watchdog(root: Path) -> None:
    with _DASHBOARD_LOCK:
        if root in _DASHBOARD_WATCHDOG_ROOTS:
            return
        _DASHBOARD_WATCHDOG_ROOTS.add(root)
    threading.Thread(
        target=dashboard_watchdog,
        args=(root,),
        name="await-instruction-dashboard-watchdog",
        daemon=True,
    ).start()


def start_instruction_dashboard() -> str:
    root = control_root()
    url = ensure_dashboard(root)
    ensure_dashboard_watchdog(root)
    return url


def dashboard_main() -> int:
    url = start_instruction_dashboard()
    print(f"await_instruction dashboard listening at {url}", file=sys.stderr, flush=True)
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        pass
    return 0


def open_dashboard(url: str) -> None:
    try:
        webbrowser.open(url, new=2)
    except Exception as exc:
        print(
            f"Could not open await_instruction dashboard automatically: {exc}",
            file=sys.stderr,
            flush=True,
        )


def wait_for_instruction(
    thread_id: str,
    comment: str | None = None,
    cancellation_event: threading.Event | None = None,
) -> JsonObject:
    if cancellation_event is not None and cancellation_event.is_set():
        raise AwaitInstructionCancelled

    root = control_root()
    record = register_wait(root, thread_id, comment)
    wait_id = record["wait_id"]
    request_file = request_path(root, wait_id)
    response_file = response_path(root, wait_id)
    dashboard_url = start_instruction_dashboard()
    page_url = f"{dashboard_url}?{urlencode({'wait_id': wait_id})}"
    print(
        f"await_instruction is waiting for {record['thread_label']!r} at {page_url}",
        file=sys.stderr,
        flush=True,
    )
    if should_open_browser():
        threading.Thread(
            target=open_dashboard,
            args=(page_url,),
            name=f"await-instruction-browser-{wait_id[-8:]}",
            daemon=True,
        ).start()

    try:
        while True:
            if cancellation_event is not None and cancellation_event.is_set():
                raise AwaitInstructionCancelled
            response = read_json(response_file)
            if response is not None:
                instruction = response.get("instruction")
                if isinstance(instruction, str) and instruction.strip():
                    return {
                        "instruction": instruction,
                        "submitted_at": response.get("submitted_at"),
                        "thread_id": record["thread_id"],
                        "thread_title": record["thread_title"],
                        "comment": record["comment"],
                        "wait_id": wait_id,
                    }
            if cancellation_event is None:
                time.sleep(0.2)
            elif cancellation_event.wait(0.2):
                raise AwaitInstructionCancelled
    finally:
        safe_unlink(request_file)
        safe_unlink(response_file)


__all__ = [
    "AwaitInstructionCancelled",
    "dashboard_main",
    "start_instruction_dashboard",
    "wait_for_instruction",
]
