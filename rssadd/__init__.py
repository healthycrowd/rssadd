from datetime import datetime
from lxml.etree import parse, Element, fromstring, tostring

from .parser import FeedParser
from .source_type import SourceType


__version__ = "1.1.0"

_PUBDATE_FORMAT = "%a, %d %b %Y %H:%M:%S %z"
_FEED_EMPTY = b"""<?xml version="1.0" encoding="utf-8"?>
<rss xmlns:atom="http://www.w3.org/2005/Atom" version="2.0">
  <channel>
      <title> </title>
      <link> </link>
      <description> </description>
  </channel>
</rss>"""


def add_element(from_source=None, to_source=None, element=None, max_items=None):
    if from_source is None:
        from_source = _FEED_EMPTY
    from_type = SourceType.from_source(from_source)
    to_type = SourceType.to_source(to_source)

    if from_type == SourceType.ELEMENT:
        root = from_source
    elif from_type == SourceType.STRING:
        root = fromstring(from_source, parser=FeedParser)
    elif from_type == SourceType.FILE:
        tree = parse(from_source, FeedParser)
        root = tree.getroot()
    channel = root.find("channel")

    if element is not None:
        first_item = channel.find("item")
        if first_item is None:
            channel.append(element)
        else:
            first_item.addprevious(element)

    if max_items is not None:
        items = channel.findall("item")
        while len(items) > max_items:
            channel.remove(items.pop(-1))

    kwargs = {
        "pretty_print": True,
        "xml_declaration": True,
        "encoding": "utf-8",
    }
    if to_type == SourceType.ELEMENT:
        return root
    if to_type == SourceType.STRING:
        return tostring(root, **kwargs)
    if to_type == SourceType.FILE:
        return tree.write(to_source, **kwargs)
    raise Exception("Unexpected value for to_source type")


def add_item(from_source=None, to_source=None, tags=None, max_items=None):
    if tags is None:
        tags = []
    else:
        tags = tags.copy()

    new_item = Element("item")
    for tag in tags:
        if isinstance(tag, str):
            tag = fromstring(tag, parser=FeedParser)
        elif not isinstance(tag, type(Element("a"))):
            raise TypeError(f"Unexpected type {tag}")
        new_item.append(tag)
    if new_item.find("pubDate") is None:
        tag = Element("pubDate")
        tag.text = datetime.now().strftime(_PUBDATE_FORMAT)
        new_item.append(tag)

    return add_element(from_source, to_source, new_item, max_items)


__all__ = ("add_element", "add_item")
