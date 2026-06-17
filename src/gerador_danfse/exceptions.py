from __future__ import annotations


class DanfseError(Exception):
    """Base library error."""


class XmlParseError(DanfseError):
    """Raised when input XML cannot be parsed or mapped."""


class PdfRenderError(DanfseError):
    """Raised when PDF generation fails."""

