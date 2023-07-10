from datetime import datetime, date
from tempfile import NamedTemporaryFile
from pathlib import Path
import pytest
from lxml.etree import Element

from rssadd import add_item, _PUBDATE_FORMAT


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
    assert len(items) == 2
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
