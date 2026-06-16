# danfse

Python library to generate a **DANFSe** (Documento Auxiliar da NFS-e) **single-page A4 PDF**
from a Brazilian NFS-e XML.

## Install

```bash
pip install danfse
```

## Usage (library)

```python
from danfse import generate_danfse_pdf

generate_danfse_pdf("invoice.xml", "danfse.pdf")
```

## Usage (CLI)

```bash
danfse generate invoice.xml danfse.pdf
```

## Status

This is an initial minimal implementation:
- Reads an XML file
- Extracts a few common NFS-e fields (best-effort)
- Generates a simple PDF layout on A4

The codebase is organized in layers so it can evolve to full compliance with the official
DANFSe spec (layout blocks, QR Code, watermark, conditional sections, etc.).

