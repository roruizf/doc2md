def image_filename(figure_number: int, page_number: int, ext: str) -> str:
    normalized_ext = ext.lstrip(".").lower()
    return f"fig{figure_number}_page{page_number}.{normalized_ext}"

