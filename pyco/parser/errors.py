from typing import NoReturn


def error(file: str, line: int, type: str, detail: str) -> NoReturn:
    print(
        f"An error occurred while parsing: {type}",
        f"Location: {file}:{line}",
        detail,
        sep="\n",
    )
    exit(1)
