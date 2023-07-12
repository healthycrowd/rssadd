from datetime import datetime, date
from tempfile import NamedTemporaryFile
from pathlib import Path
import pytest
from lxml.etree import Element, tostring, fromstring

from rssadd import add_item, add_element, _PUBDATE_FORMAT
from rssadd.parser import FeedParser


FEED_EMPTY_ADDED = """<?xml version='1.0' encoding='utf-8'?>
<rss xmlns:atom="http://www.w3.org/2005/Atom" version="2.0">
  <channel>
    <title> </title>
    <link> </link>
    <description> </description>
    <item>
      <title>testtitle</title>
      <description>testdescription</description>
      <pubDate>{pubdate}</pubDate>
    </item>
  </channel>
</rss>
"""
FEED_EXISTING = b"""<?xml version='1.0' encoding='utf-8'?>
<rss xmlns:atom="http://www.w3.org/2005/Atom" version="2.0">
  <channel>
    <title>testtitle</title>
    <link>testlink</link>
    <description>testdescription</description>
  </channel>
</rss>
"""
FEED_EXISTING_ADDED = """<?xml version='1.0' encoding='utf-8'?>
<rss xmlns:atom="http://www.w3.org/2005/Atom" version="2.0">
  <channel>
    <title>testtitle</title>
    <link>testlink</link>
    <description>testdescription</description>
    <item>
      <title>testtitle</title>
      <description>testdescription</description>
      <pubDate>{pubdate}</pubDate>
    </item>
  </channel>
</rss>
"""
FEED_EXISTING_ADDED_FILE = """<?xml version='1.0' encoding='UTF-8'?>
<rss xmlns:atom="http://www.w3.org/2005/Atom" version="2.0">
  <channel>
    <title>testtitle</title>
    <link>testlink</link>
    <description>testdescription</description>
    <item>
      <title>testtitle</title>
      <description>testdescription</description>
      <pubDate>{pubdate}</pubDate>
    </item>
  </channel>
</rss>
"""
TAGS = ["<title>testtitle</title>", "<description>testdescription</description>"]


def pubdate(feed, pubdate=None):
    if not pubdate:
        pubdate = datetime.now().strftime(_PUBDATE_FORMAT)
    return feed.format(pubdate=pubdate).encode()


def assert_items(items, titles):
    for item in items:
        assert item.find("title").text == titles.pop(0)


def test_success_default_to_str():
    actual = add_item(tags=TAGS)
    expected = pubdate(FEED_EMPTY_ADDED)
    assert actual == expected


def test_success_str_to_str():
    actual = add_item(from_source=FEED_EXISTING, tags=TAGS)
    expected = pubdate(FEED_EXISTING_ADDED)
    assert actual == expected


def test_success_file_to_file():
    fromfile = NamedTemporaryFile()
    tofile = NamedTemporaryFile()
    Path(fromfile.name).write_bytes(FEED_EXISTING)

    add_item(from_source=fromfile.name, to_source=tofile.name, tags=TAGS)
    actual = Path(tofile.name).read_bytes()
    expected = pubdate(FEED_EXISTING_ADDED_FILE)
    assert actual == expected


def test_success_element_to_element():
    root = Element("rss")
    channel = Element("channel")
    item = Element("item")
    title = Element("title")
    title.text = "testtitle"
    item.append(title)
    channel.append(item)
    root.append(channel)

    added_title = Element("title")
    added_title.text = title.text

    add_item(from_source=root, to_source=root, tags=[added_title])
    items = channel.findall("item")
    assert len(items) == 2, tostring(root)
    for item in items:
        assert item.find("title").text == title.text


def test_success_custom_pubdate():
    actual = add_item(tags=TAGS + ["<pubDate>testpubdate</pubDate>"])
    expected = pubdate(FEED_EMPTY_ADDED, pubdate="testpubdate")
    assert actual == expected


def test_fail_unknown_from():
    with pytest.raises(TypeError):
        add_item(from_source=1, tags=TAGS)


def test_fail_unknown_to():
    with pytest.raises(TypeError):
        add_item(to_source=1, tags=TAGS)


def test_fail_unknown_tag():
    with pytest.raises(TypeError):
        add_item(tags=[1])


def test_success_has_items_add():
    root = Element("rss")
    channel = Element("channel")
    root.append(channel)
    for text in range(3):
        item = Element("item")
        title = Element("title")
        title.text = f"{text}"
        link = Element("link")
        link.text = "testlink"
        item.append(title)
        item.append(link)
        channel.append(item)

    added_title = Element("title")
    added_title.text = "title"
    added_link = Element("link")
    added_link.text = "testlink"

    add_item(from_source=root, to_source=root, tags=[added_title, added_link])
    items = channel.findall("item")
    assert len(items) == 4, tostring(root)
    assert_items(items, ["title", "0", "1", "2", "3"])


def test_success_has_items_add_max():
    root = Element("rss")
    channel = Element("channel")
    root.append(channel)
    for text in range(3):
        item = Element("item")
        title = Element("title")
        title.text = f"{text}"
        link = Element("link")
        link.text = "testlink"
        item.append(title)
        item.append(link)
        channel.append(item)

    added_title = Element("title")
    added_title.text = "title"
    added_link = Element("link")
    added_link.text = "testlink"

    add_item(
        from_source=root, to_source=root, tags=[added_title, added_link], max_items=2
    )
    items = channel.findall("item")
    assert len(items) == 2, tostring(root)
    assert_items(items, ["title", "0"])


def test_success_add_element():
    root = Element("rss")
    channel = Element("channel")
    root.append(channel)
    for text in range(3):
        item = Element("item")
        title = Element("title")
        title.text = f"{text}"
        link = Element("link")
        link.text = "testlink"
        item.append(title)
        item.append(link)
        channel.append(item)

    added_item = Element("item")
    added_title = Element("title")
    added_title.text = "title"
    added_link = Element("link")
    added_link.text = "testlink"
    added_item.append(added_title)
    added_item.append(added_link)

    add_element(from_source=root, to_source=root, element=added_item, max_items=2)
    items = channel.findall("item")
    assert len(items) == 2, tostring(root)
    assert_items(items, ["title", "0"])


def test_success_add_element_none():
    root = Element("rss")
    channel = Element("channel")
    root.append(channel)
    for text in range(3):
        item = Element("item")
        title = Element("title")
        title.text = f"{text}"
        link = Element("link")
        link.text = "testlink"
        item.append(title)
        item.append(link)
        channel.append(item)

    add_element(from_source=root, to_source=root, max_items=2)
    items = channel.findall("item")
    assert len(items) == 2, tostring(root)
    assert_items(items, ["0", "1"])
