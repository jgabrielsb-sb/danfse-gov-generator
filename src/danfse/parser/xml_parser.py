from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from lxml import etree


class DanfseParserError(Exception):
    """Erro base do parser do DANFSe."""


class InvalidXmlError(DanfseParserError):
    """XML inválido ou malformado."""


@dataclass(frozen=True)
class XmlDocument:
    """XML carregado e pronto para navegação pelo mapper."""

    root: etree._Element


class XmlNavigator:
    """
    Navegação genérica no XML ignorando namespace.

    Não conhece tags de domínio NFS-e/DANFSe; o mapper informa os caminhos.
    """

    __slots__ = ("_node",)

    def __init__(self, node: etree._Element | None) -> None:
        self._node = node

    @property
    def node(self) -> etree._Element | None:
        return self._node

    @property
    def local_name(self) -> str | None:
        if self._node is None:
            return None
        return etree.QName(self._node).localname

    def at(self, *tags: str) -> XmlNavigator:
        """Segue filhos diretos pelas tags informadas."""
        return XmlNavigator(_child_path(self._node, tags))

    def find(self, *tags: str) -> XmlNavigator:
        """Busca caminho em profundidade pelas tags informadas."""
        return XmlNavigator(_descendant_path(self._node, tags))

    def value(self) -> str | None:
        """Texto do nó atual."""
        if self._node is None or self._node.text is None:
            return None
        text = self._node.text.strip()
        return text or None

    def text(self, *tags: str) -> str | None:
        """Texto de um filho direto (ou caminho de filhos diretos)."""
        if not tags:
            return self.value()
        return self.at(*tags).value()

    def text_find(self, *tags: str) -> str | None:
        """Texto de um descendente."""
        return self.find(*tags).value()

    def attr(self, name: str) -> str | None:
        if self._node is None:
            return None
        # Atributos XML podem variar em capitalização (ex.: Id vs id).
        candidates = {name, name.lower(), name.upper()}
        if len(name) > 0:
            candidates.add(name[0].upper() + name[1:])
        for candidate in candidates:
            value = self._node.attrib.get(candidate)
            if value is not None:
                value = value.strip()
                if value:
                    return value
        return None


def parse_xml(source: bytes | str | Path) -> XmlDocument:
    """Carrega o XML e retorna um documento navegável."""
    root = _load_xml(source)
    return XmlDocument(root=root)


def _load_xml(source: bytes | str | Path) -> etree._Element:
    if isinstance(source, bytes):
        xml_bytes = source
    elif isinstance(source, Path):
        xml_bytes = source.read_bytes()
    else:
        value = source.strip()
        if value.startswith("<"):
            xml_bytes = value.encode("utf-8")
        else:
            xml_bytes = Path(source).read_bytes()

    parser = etree.XMLParser(
        resolve_entities=False,
        no_network=True,
        remove_blank_text=True,
        recover=False,
    )

    try:
        return etree.fromstring(xml_bytes, parser=parser)
    except etree.XMLSyntaxError as exc:
        raise InvalidXmlError(str(exc)) from exc


def _child_path(node: etree._Element | None, tags: tuple[str, ...]) -> etree._Element | None:
    current = node

    for tag in tags:
        if current is None:
            return None

        found = None
        for child in current:
            if not isinstance(child.tag, str):
                continue
            if etree.QName(child).localname == tag:
                found = child
                break
        current = found

    return current


def _descendant_path(node: etree._Element | None, tags: tuple[str, ...]) -> etree._Element | None:
    if node is None:
        return None

    expression = ".//" + "/".join(f"*[local-name()='{tag}']" for tag in tags)
    result = node.xpath(expression)

    if not result:
        return None

    return result[0]
