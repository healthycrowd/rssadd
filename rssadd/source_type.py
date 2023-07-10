from enum import Enum, auto
from urllib.parse import urlparse
from pathlib import Path
from lxml.etree import Element, fromstring, XMLSyntaxError

from .parser import FeedParser


class SourceType(Enum):
    ELEMENT = auto()
    FILE = auto()
    STRING = auto()

    @classmethod
    def from_source(cls, source):
        if isinstance(source, type(Element("a"))):
            return cls.ELEMENT
        if isinstance(source, bytes):
            return cls.STRING
        if not isinstance(source, str):
            raise TypeError(f"Unexpected type {source}")

        if urlparse(source).scheme:
            return cls.FILE
        if Path(source).exists():
            return cls.FILE
        if any(c not in source for c in ("<", ">")):
            return cls.FILE

        try:
            fromstring(source, parser=FeedParser)
            return cls.STRING
        except XMLSyntaxError:
            pass

        # Not guaranteed
        if source.lstrip()[0] == "<" or any(c in source for c in ("\n", "\r")):
            return cls.STRING
        return cls.FILE

    @classmethod
    def to_source(cls, source):
        if isinstance(source, type(Element("a"))):
            return cls.ELEMENT
        if isinstance(source, str):
            return cls.FILE
        if source is None:
            return cls.STRING
        raise TypeError(f"Unexpected type {source}")
