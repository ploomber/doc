def remove_code_block_markers(code_string: str, remove_text: bool = True) -> str:
    """Remove code block markers from a markdown code block.

    Parameters
    ----------
    code_string : str
        The input string containing markdown code block(s)
    remove_text : bool, default=True
        If True, searches for and removes code block markers anywhere in the text.
        If False, only removes markers if they are at the start and end of the text.

    Returns
    -------
    str
        The code string with code block markers removed.
        If no code block markers are found, returns the original string.

    Notes
    -----
    Code block markers are identified by the ``` sequence.
    When remove_text=True, this function will find the first and last occurrences
    of code block markers and extract only the code between them.
    When remove_text=False, it only removes the markers if they are at the start
    and end of the string.
    """
    lines = code_string.strip().split("\n")

    if not remove_text:
        # Simple check for code blocks at start and end
        if lines[0].startswith("```") and lines[-1].startswith("```"):
            return "\n".join(lines[1:-1])
        return code_string

    # Find start and end of code block
    start_idx = 0
    end_idx = len(lines)

    for i, line in enumerate(lines):
        if "```" in line:
            start_idx = i + 1
            break

    for i in range(len(lines) - 1, -1, -1):
        if "```" in lines[i]:
            end_idx = i
            break

    # If we found a code block, extract just the code
    if start_idx < end_idx:
        return "\n".join(lines[start_idx:end_idx])

    return code_string
