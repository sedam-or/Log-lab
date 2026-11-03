"""Form dan route login Source (FastAPI). Keputusan auth ada di SourceService.

Route sesuai kontrak: GET /login (form), POST /login (form), POST /api/v1/login (JSON),
GET /health. Kedua jalur login memakai SourceService.login sehingga event-nya sama.
"""
import html
import json
from typing import Any, Optional

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse

from loglab.config import Settings
from loglab.source_service import SourceService

MAX_USERNAME = 64
MAX_PASSWORD = 128
MAX_BODY_BYTES = 4 * 1024  # batas body POST /api/v1/login

LOGIN_FORM = (
    '<form method="post" action="/login">'
    '<p><label>Username <input name="username" maxlength="64" '
    'autocomplete="username"></label></p>'
    '<p><label>Password <input name="password" type="password" maxlength="128" '
    'autocomplete="current-password"></label></p>'
    '<p><button type="submit">Login</button></p>'
    "</form>"
)


def _page(title: str, body: str) -> str:
    safe_title = html.escape(title)
    return (
        '<!doctype html><html lang="id"><head><meta charset="utf-8">'
        f"<title>{safe_title}</title></head><body><h1>{safe_title}</h1>"
        f"{body}</body></html>"
    )


def _valid_credentials(username: Any, password: Any) -> bool:
    return (
        isinstance(username, str)
        and isinstance(password, str)
        and 0 < len(username) <= MAX_USERNAME
        and 0 < len(password) <= MAX_PASSWORD
    )


def create_app(
    settings: Settings, service: Optional[SourceService] = None, lifespan=None
) -> FastAPI:
    service = service or SourceService(settings)
    app = FastAPI(
        title="LogLab Source",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        lifespan=lifespan,
    )

    @app.get("/", response_class=HTMLResponse)
    @app.get("/login", response_class=HTMLResponse)
    def index() -> str:
        return _page("Login uji LogLab", LOGIN_FORM)

    @app.get("/health")
    def health() -> dict:
        """Liveness minimal. HTTP 200 bukan bukti outbox terkirim atau Monitor terjangkau."""
        return {
            "service": "loglab-source",
            "state": "ready",
            "contract_version": settings.contract_version,
        }

    @app.post("/api/v1/login")
    async def login_json(request: Request) -> JSONResponse:
        """Jalur JSON untuk alat uji: {"username": ..., "password": ...}."""
        declared = request.headers.get("content-length", "")
        if declared.isdigit() and int(declared) > MAX_BODY_BYTES:
            service.count_request_rejected()
            return JSONResponse({"error": "request_too_large"}, status_code=413)
        body = await request.body()
        if len(body) > MAX_BODY_BYTES:
            service.count_request_rejected()
            return JSONResponse({"error": "request_too_large"}, status_code=413)
        try:
            data = json.loads(body)
        except (ValueError, UnicodeDecodeError):
            data = None
        if not isinstance(data, dict) or not _valid_credentials(
            data.get("username"), data.get("password")
        ):
            service.count_request_rejected()
            return JSONResponse({"error": "invalid_request"}, status_code=400)
        client_id = request.client.host if request.client else "unknown"
        is_success, _event = service.login(data["username"], data["password"], client_id)
        if is_success:
            return JSONResponse({"result": "success"})
        return JSONResponse({"result": "failure"}, status_code=401)

    @app.post("/login", response_class=HTMLResponse)
    def login(
        request: Request,
        username: str = Form(""),
        password: str = Form(""),
    ) -> HTMLResponse:
        if not _valid_credentials(username, password):
            service.count_request_rejected()
            return HTMLResponse(
                _page(
                    "Permintaan tidak valid",
                    "<p>Username dan password wajib diisi.</p>" + LOGIN_FORM,
                ),
                status_code=400,
            )
        client_id = request.client.host if request.client else "unknown"
        is_success, _event = service.login(username, password, client_id)
        if is_success:
            return HTMLResponse(
                _page("Login berhasil", f"<p>Selamat datang, {html.escape(username)}.</p>")
            )
        return HTMLResponse(
            _page("Login gagal", "<p>Username atau password salah.</p>" + LOGIN_FORM),
            status_code=401,
        )

    return app
