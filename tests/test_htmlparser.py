# MIT licensed
# Copyright (c) 2021 ypsilik <tt2laurent.maud@gmail.com>, et al.

import pytest

lxml_available = True
try:
  import lxml
except ImportError:
  lxml_available = False

pytestmark = [
  pytest.mark.asyncio,
  pytest.mark.needs_net,
  pytest.mark.skipif(not lxml_available, reason="needs lxml"),
]

async def test_xpath_ok(get_version):
    ver = await get_version("aur", {
        "source": "htmlparser",
        "url": "https://aur.archlinux.org/",
        "xpath": '//div[@id="footer"]/p[1]/a/text()',
    })
    assert ver.startswith('v')
    assert '.' in ver

async def test_xpath_element(get_version):
    ver = await get_version("aur", {
        "source": "htmlparser",
        "url": "https://aur.archlinux.org/",
        "xpath": '//div[@id="footer"]/p[1]/a',
    })
    assert ver.startswith('v')
    assert '.' in ver

