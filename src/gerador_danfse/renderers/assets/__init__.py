from __future__ import annotations

from functools import lru_cache
from importlib import resources
from pathlib import Path

LOGO_FILENAME = "logo-nfs-e-horizontal.png"


@lru_cache(maxsize=1)
def default_logo_path() -> Path | None:
    """Retorna o caminho da logo NFS-e embutida no pacote, se disponível."""
    package_files = resources.files("gerador_danfse.renderers.assets")
    logo = package_files.joinpath(LOGO_FILENAME)
    if logo.is_file():
        with resources.as_file(logo) as path:
            return Path(path)

    local = Path(__file__).resolve().parent / LOGO_FILENAME
    if local.exists():
        return local

    repo_root = Path(__file__).resolve().parents[3] / LOGO_FILENAME
    if repo_root.exists():
        return repo_root

    return None


def resolve_logo_path(logo_path: str | Path | None) -> Path | None:
    if logo_path is not None:
        path = Path(logo_path)
        return path if path.exists() else None
    return default_logo_path()
