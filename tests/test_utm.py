from pathlib import Path

import pytest

from pkgmt.utm import parse_links_from_md, find_markdown_files, Link, add_utm_tags


@pytest.mark.parametrize(
    "file_content, expected_output",
    [
        (
            "[link1](http://example.com)",
            [
                Link(
                    text="[link1](http://example.com)",
                    link="http://example.com",
                    name="link1",
                )
            ],
        ),
        (
            "[link2](http://example.com) and [link3](http://example2.com)",
            [
                Link(
                    text="[link2](http://example.com)",
                    link="http://example.com",
                    name="link2",
                ),
                Link(
                    text="[link3](http://example2.com)",
                    link="http://example2.com",
                    name="link3",
                ),
            ],
        ),
        ("[link4](http://example.com/image.png)", []),
        (
            "[link5](http://example.com) and ![image](http://example.com/image.png)",
            [
                Link(
                    text="[link5](http://example.com)",
                    link="http://example.com",
                    name="link5",
                )
            ],
        ),
    ],
)
def test_parse_links_from_md(file_content, expected_output, tmp_empty):
    # Create a temporary markdown file
    d = Path(tmp_empty) / "sub"
    d.mkdir()
    p = d / "test.md"
    p.write_text(file_content)

    # Call the function with the temporary file
    result = parse_links_from_md(str(p))

    # Check that the function returns the expected output
    assert result == expected_output


def test_find_markdown_files_no_md_files(tmp_empty):
    # Create a temporary directory with no .md files
    d = Path(tmp_empty) / "sub"
    d.mkdir()

    # Call the function with the temporary directory
    result = list(find_markdown_files(str(d)))

    # Check that the function returns an empty list
    assert result == []


def test_find_markdown_files_same_directory(tmp_empty):
    # Create a temporary directory with one .md file
    d = Path(tmp_empty) / "sub"
    d.mkdir()
    p = d / "test.md"
    p.write_text("")

    # Call the function with the temporary directory
    result = list(find_markdown_files(str(d)))

    # Check that the function returns a list with the path to the .md file
    assert result == [str(p)]


def test_find_markdown_files_nested_directories(tmp_empty):
    # Create a temporary directory with nested subdirectories, each with one .md file
    d = Path(tmp_empty) / "sub"
    d.mkdir()
    p1 = d / "test1.md"
    p1.write_text("")
    d2 = d / "sub2"
    d2.mkdir()
    p2 = d2 / "test2.md"
    p2.write_text("")

    # Call the function with the temporary directory
    result = list(find_markdown_files(str(d)))

    # Check that the function returns a list with the paths to the .md files
    assert set(result) == set([str(p1), str(p2)])


@pytest.mark.parametrize(
    "file_content, utm_source, utm_medium, utm_campaign, expected_output",
    [
        (
            "[link1](http://example.com)",
            "source",
            "medium",
            "campaign",
            (
                "[link1](http://example.com?"
                "utm_source=source&utm_medium=medium&utm_campaign=campaign)"
            ),
        ),
        (
            "[link2](http://example2.com)",
            "source2",
            "medium2",
            None,
            "[link2](http://example2.com?utm_source=source2&utm_medium=medium2)",
        ),
    ],
)
def test_add_utm_tags(
    file_content, utm_source, utm_medium, utm_campaign, expected_output, tmp_path
):
    # Create a temporary markdown file
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "test.md"
    p.write_text(file_content)

    # Call the function with the temporary file and some UTM tags
    add_utm_tags(
        str(d), utm_source=utm_source, utm_medium=utm_medium, utm_campaign=utm_campaign
    )

    # Check that the link in the file has been correctly modified
    with open(p, "r") as file:
        data = file.read()
    assert data == expected_output


@pytest.mark.parametrize(
    "file_content, base_urls, utm_source, utm_medium, utm_campaign, expected_output",
    [
        (
            "[link1](http://example.com) [link2](http://notexample.com)",
            ["http://example.com"],
            "source",
            "medium",
            "campaign",
            (
                "[link1](http://example.com?"
                "utm_source=source&utm_medium=medium&utm_campaign=campaign)"
                " [link2](http://notexample.com)"
            ),
        ),
        (
            "[link1](http://example.com) [link2](http://notexample.com)",
            ["http://example.com", "http://notexample.com"],
            "source",
            "medium",
            "campaign",
            (
                "[link1](http://example.com"
                "?utm_source=source&utm_medium=medium&utm_campaign=campaign)"
                " [link2](http://notexample.com?"
                "utm_source=source&utm_medium=medium&utm_campaign=campaign)"
            ),
        ),
        (
            "[link1](http://example.com) [link2](http://notexample.com)",
            None,
            "source",
            "medium",
            "campaign",
            (
                "[link1](http://example.com?"
                "utm_source=source&utm_medium=medium&utm_campaign=campaign)"
                " [link2](http://notexample.com?"
                "utm_source=source&utm_medium=medium&utm_campaign=campaign)"
            ),
        ),
    ],
)
def test_add_utm_tags_with_base_url(
    file_content,
    base_urls,
    utm_source,
    utm_medium,
    utm_campaign,
    expected_output,
    tmp_path,
):
    # Create a temporary markdown file
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "test.md"
    p.write_text(file_content)

    # Call the function with the temporary file and some UTM tags
    add_utm_tags(
        str(d),
        base_urls=base_urls,
        utm_source=utm_source,
        utm_medium=utm_medium,
        utm_campaign=utm_campaign,
    )

    # Check that the link in the file has been correctly modified
    with open(p, "r") as file:
        data = file.read()
    assert data == expected_output


def test_add_utm_tags_utm_source_none(tmp_path):
    # Create a temporary markdown file
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "test.md"
    p.write_text("[link](http://example.com)")

    # Call the function with the temporary file and utm_source set to None
    add_utm_tags(str(d), utm_source=None, utm_medium="medium", utm_campaign="campaign")

    # Check that the link in the file has been correctly modified
    with open(p, "r") as file:
        data = file.read()
    assert data == (
        "[link](http://example.com?"
        "utm_source=test&utm_medium=medium&utm_campaign=campaign)"
    )


def test_add_utm_tags_existing_utm_tags(tmp_path):
    # Create a temporary markdown file with a link that already contains UTM tags
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "test.md"
    p.write_text(
        (
            "[link](http://example.com?"
            "utm_source=old_source&utm_medium=old_medium&utm_campaign=old_campaign)"
        )
    )

    # Call the function with the temporary file and new UTM tags
    add_utm_tags(
        str(d),
        utm_source="new_source",
        utm_medium="new_medium",
        utm_campaign="new_campaign",
    )

    # Check that the UTM tags in the link have been correctly replaced
    with open(p, "r") as file:
        data = file.read()
    assert data == (
        "[link](http://example.com?"
        "utm_source=new_source&utm_medium=new_medium&utm_campaign=new_campaign)"
    )


def test_add_utm_tags_pure_link(tmp_path):
    # Create a temporary markdown file with a pure link
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "test.md"
    p.write_text("http://example.com")

    # Call the function with the temporary file and some UTM tags
    add_utm_tags(
        str(d), utm_source="source", utm_medium="medium", utm_campaign="campaign"
    )

    # Check that the link in the file has not been modified
    with open(p, "r") as file:
        data = file.read()
    assert data == "http://example.com"
