"""Titik masuk Source untuk systemd/uvicorn: `loglab.source_main:app`.

Aplikasi dibuat saat pertama kali dipanggil (bukan saat import), dari variabel LOGLAB_* yang
sudah divalidasi kontrak. `main()` tetap tersedia untuk menjalankan Source langsung dengan HTTPS.
Settings.from_env("source") menolak LOGLAB_ROLE selain `source`.
"""
import uvicorn

from loglab.config import Settings
from loglab.sender import Sender, sender_lifespan
from loglab.source_app import create_app


def build_app(settings: Settings | None = None):
    """Aplikasi Source beserta sender di dalam proses yang sama (satu service, kontrak)."""
    settings = settings or Settings.from_env("source")
    return create_app(settings, lifespan=sender_lifespan(Sender(settings)))


class _LazyApp:
    """ASGI app yang membangun aplikasi sebenarnya pada panggilan pertama (startup uvicorn)."""

    def __init__(self) -> None:
        self._app = None

    async def __call__(self, scope, receive, send) -> None:
        if self._app is None:
            self._app = build_app()
        await self._app(scope, receive, send)


app = _LazyApp()


def main() -> None:
    settings = Settings.from_env("source")
    uvicorn.run(
        build_app(settings),
        host=settings.bind_host,
        port=settings.port,
        ssl_certfile=str(settings.certfile),
        ssl_keyfile=str(settings.keyfile),
    )


if __name__ == "__main__":
    main()
