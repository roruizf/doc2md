def anchor_id(page_num: int) -> str:
    return f"page-{page_num}"


def render_anchor(page_num: int) -> str:
    return f'<a id="{anchor_id(page_num)}"></a>\n**[Page {page_num}]**\n'

