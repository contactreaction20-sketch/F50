"""Small dependency-free web server for the FUTURE-50 chat workspace."""

from __future__ import annotations

import json
import mimetypes
import os
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from ..core.chat import Future50Chat
from ..core.model_router import ModelRouter
from ..agents.team import MultiAgentTeam
from ..cognition.context import ContextManager
from ..inference.providers import model_provider
from ..research.local_rag import LocalKnowledgeRAG


STATIC_ROOT = Path(__file__).with_name("static")
MAX_BODY_BYTES = 64 * 1024


def _provider_error(reply: str) -> bool:
    lowered = reply.lower()
    return "provider is unavailable" in lowered or "provider inference failed" in lowered or "provider unavailable" in lowered


class ChatWebHandler(BaseHTTPRequestHandler):
    chat = Future50Chat()
    router = ModelRouter()
    team = MultiAgentTeam(router)
    context_manager = ContextManager()
    rag = LocalKnowledgeRAG()

    @classmethod
    def _knowledge_context(cls, message: str, intent: tuple[str, ...]) -> str:
        if "RESEARCH" not in intent:
            return ""
        results = cls.rag.search(message, top_k=3)
        if not results:
            return ""
        evidence = "\n".join(f"- {result.text} (source: {result.source})" for result in results)
        return f"RELEVANT LOCAL EVIDENCE:\n{evidence}"

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/" or path == "/index.html":
            return self._serve_file(STATIC_ROOT / "index.html", "text/html; charset=utf-8")
        if path.startswith("/static/"):
            file_path = (STATIC_ROOT / path.removeprefix("/static/")).resolve()
            if STATIC_ROOT.resolve() in file_path.parents and file_path.is_file():
                content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
                return self._serve_file(file_path, content_type)
        if path == "/api/health":
            provider = model_provider.health_check()
            return self._json({"ok": True, "service": "future50-web", "inference": provider})
        self.send_error(404)

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/chat/stream":
            return self._stream_chat()
        if path != "/api/chat":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_BODY_BYTES:
                return self._json({"error": "Request body must be between 1 and 65536 bytes."}, status=413)
            payload = json.loads(self.rfile.read(length) or b"{}")
            message = str(payload.get("message", "")).strip()
            session_id = str(payload.get("session_id", "default"))[:120]
            if not message:
                return self._json({"error": "Message is required."}, status=400)
            provider_status = model_provider.health_check()
            if provider_status.get("status") == "unavailable":
                return self._json({"error": "Inference provider is unavailable.", "inference": provider_status}, status=503)
            plan = self.team.plan(message)
            model = plan.lead
            snapshot = self.context_manager.snapshot(session_id, message)
            prompt = "\n\n".join(part for part in (snapshot.prompt(), self._knowledge_context(message, snapshot.intent)) if part)
            response = self.chat.generate("user", prompt, model=model)
            if _provider_error(response.text):
                return self._json({"error": response.text}, status=503)
            self.context_manager.remember_many(session_id, [
                ("user", message, 0.8),
                ("assistant", response.text, 0.7),
            ])
            return self._json({
                "reply": response.text,
                "model": model.name,
                "role": model.role.value,
                "lane": plan.lane,
                "specialists": plan.specialists,
                "intent": snapshot.intent,
                "context_confidence": snapshot.confidence,
            })
        except json.JSONDecodeError:
            return self._json({"error": "Request body must be valid JSON."}, status=400)
        except Exception as exc:
            if _provider_error(str(exc)):
                return self._json({"error": str(exc)}, status=503)
            return self._json({"error": f"Local inference failed: {exc}"}, status=500)

    def _stream_chat(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_BODY_BYTES:
                return self._json({"error": "Request body must be between 1 and 65536 bytes."}, status=413)
            payload = json.loads(self.rfile.read(length) or b"{}")
            message = str(payload.get("message", "")).strip()
            session_id = str(payload.get("session_id", "default"))[:120]
            if not message:
                return self._json({"error": "Message is required."}, status=400)
            provider_status = model_provider.health_check()
            if provider_status.get("status") == "unavailable":
                return self._json({"error": "Inference provider is unavailable.", "inference": provider_status}, status=503)
            plan = self.team.plan(message)
            model = plan.lead
            snapshot = self.context_manager.snapshot(session_id, message)
            prompt = "\n\n".join(part for part in (snapshot.prompt(), self._knowledge_context(message, snapshot.intent)) if part)
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "close")
            self.send_header("X-Accel-Buffering", "no")
            self.end_headers()
            self.wfile.write(b'data: {"status": "thinking"}\n\n')
            self.wfile.flush()
            language = model_provider._same_language_instruction(message)
            system = self.team.compose_system(plan, language or "Respond in the same language as the user's message.")
            response_parts = []
            for token in model_provider.stream_generate(prompt, model=model.name, system=system):
                if _provider_error(token):
                    self.wfile.write(f"data: {json.dumps({'error': token})}\n\n".encode("utf-8"))
                    self.wfile.flush()
                    self.close_connection = True
                    return
                response_parts.append(token)
                self.wfile.write(f"data: {json.dumps({'token': token})}\n\n".encode("utf-8"))
                self.wfile.flush()
            self.context_manager.remember_many(session_id, [
                ("user", message, 0.8),
                ("assistant", "".join(response_parts), 0.7),
            ])
            self.wfile.write(b"data: {\"done\": true}\n\n")
            self.wfile.flush()
        except json.JSONDecodeError:
            return self._json({"error": "Request body must be valid JSON."}, status=400)
        except (BrokenPipeError, ConnectionResetError):
            return
        except Exception as exc:
            try:
                self.wfile.write(f"data: {json.dumps({'error': str(exc)})}\n\n".encode("utf-8"))
                self.wfile.flush()
            except OSError:
                pass

    def _serve_file(self, path: Path, content_type: str):
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def run_web_app(host=None, port=None, open_browser=True):
    """Start the local web app and block until the process is stopped."""
    host = host or os.getenv("HOST", "127.0.0.1")
    port = int(port or os.getenv("PORT", "8765"))
    server = ThreadingHTTPServer((host, port), ChatWebHandler)
    url = f"http://{host}:{port}"
    print(f"FUTURE-50 web interface running at {url}")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
