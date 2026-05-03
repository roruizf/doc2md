from doc2md.rendering.page_anchors import anchor_id, render_anchor


def test_render_anchor_format() -> None:
    assert render_anchor(1) == '<a id="page-1"></a>\n**[Page 1]**\n'


def test_anchor_id_page_zero() -> None:
    assert anchor_id(0) == "page-0"
    assert render_anchor(0) == '<a id="page-0"></a>\n**[Page 0]**\n'


def test_anchor_id_large_page() -> None:
    assert anchor_id(10000) == "page-10000"
    assert render_anchor(10000) == '<a id="page-10000"></a>\n**[Page 10000]**\n'

