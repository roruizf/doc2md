REPLACEMENTS = {
    "—": "--",
    "–": "-",
    "“": '"',
    "”": '"',
    "‘": "'",
    "’": "'",
}


def sanitize(text: str) -> tuple[str, dict[str, int]]:
    counts = {character: 0 for character in REPLACEMENTS}
    output: list[str] = []
    position = 0

    while position < len(text):
        fence = _matching_code_delimiter(text, position)
        if fence is not None:
            end = text.find(fence, position + len(fence))
            if end == -1:
                output.append(text[position:])
                break
            end += len(fence)
            output.append(text[position:end])
            position = end
            continue

        character = text[position]
        replacement = REPLACEMENTS.get(character)
        if replacement is None:
            output.append(character)
        else:
            output.append(replacement)
            counts[character] += 1
        position += 1

    return "".join(output), {key: value for key, value in counts.items() if value}


def _matching_code_delimiter(text: str, position: int) -> str | None:
    if text.startswith("```", position):
        return "```"
    if text.startswith("`", position):
        return "`"
    return None

