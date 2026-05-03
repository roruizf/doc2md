
import yaml

from doc2md.core.document import Frontmatter


def render_frontmatter(fm: Frontmatter) -> str:
    data = fm.model_dump()
    yaml_text = yaml.safe_dump(
        data,
        sort_keys=False,
        allow_unicode=True,
    )
    return f"---\n{yaml_text}---\n"

