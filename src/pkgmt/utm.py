"""
Tools for adding utm codes to markdown files

Docs on how to use it, explain --word-diff
"""

from pathlib import Path
import re
from collections import namedtuple

# Define a named tuple type with 'text', 'link', and 'name' fields
Link = namedtuple("Link", ["text", "link", "name"])


def parse_links_from_md(file_path):
    with open(file_path, "r") as file:
        data = file.read()

    # Regular expression to match markdown links
    link_pattern = re.compile(r"(\[([^\[]+)\]\(([^)]+)\))")

    # Find all matches in the file
    matches = re.findall(link_pattern, data)

    # Create a Link named tuple for each match and filter out images
    links = [
        Link(text=match[0], link=match[2].split("?")[0], name=match[1])
        for match in matches
        if not match[2].endswith((".png", ".jpg", ".jpeg", ".gif"))
    ]

    return links


def find_markdown_files(path):
    # Convert the directory to a Path object
    path = Path(path)

    if path.is_file() and path.suffix == ".md":
        yield str(path)

    # Use the glob method to match all .md files in the directory and subdirectories
    for markdown_file in path.glob("**/*.md"):
        yield str(markdown_file)


def add_utm_tags(
    directory, utm_source=None, utm_medium=None, utm_campaign=None, base_urls=None
):
    # Iterate over markdown files in the directory
    for file_path in find_markdown_files(directory):
        utm_params = []

        with open(file_path, "r") as file:
            data = file.read()

        # If utm_source is None, use the filename (without extension and directories)
        # as utm_source
        if not utm_source:
            utm_source_ = Path(file_path).stem
        else:
            utm_source_ = utm_source

        utm_params.append(f"utm_source={utm_source_}")

        if utm_medium:
            utm_params.append(f"utm_medium={utm_medium}")

        if utm_campaign:
            utm_params.append(f"utm_campaign={utm_campaign}")

        utm_content = "?" + "&".join(utm_params) if utm_params else ""

        # Parse the links in the file
        links = parse_links_from_md(file_path)

        # Replace each link with the link plus UTM tags
        for link in links:
            if base_urls and not any(
                link.link.startswith(base_url) for base_url in base_urls
            ):
                continue

            utm_link = link.link + utm_content
            data = data.replace(link.text, f"[{link.name}]({utm_link})")

        # Write the modified data back to the file
        with open(file_path, "w") as file:
            file.write(data)
