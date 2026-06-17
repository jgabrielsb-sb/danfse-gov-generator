from __future__ import annotations

import argparse
import sys

from danfse.api import generate_danfse_pdf


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="danfse", description="Generate DANFSe PDF from NFS-e XML.")
    sub = p.add_subparsers(dest="cmd", required=True)

    gen = sub.add_parser("generate", help="Generate a DANFSe PDF from an XML file.")
    gen.add_argument("xml", help="Input NFS-e XML path")
    gen.add_argument("pdf", help="Output PDF path")
    gen.add_argument("--watermark", default=None, help="Optional watermark text")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.cmd == "generate":
        generate_danfse_pdf(args.xml, args.pdf, watermark=args.watermark)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

