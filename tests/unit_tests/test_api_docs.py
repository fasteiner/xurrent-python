"""Unit tests for docs/generate_api_docs.py and the committed API reference in docs/api/."""
import ast
import importlib.util
import os
import re

import pytest

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
_spec = importlib.util.spec_from_file_location("generate_api_docs", os.path.join(ROOT, "docs", "generate_api_docs.py"))
gen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gen)

LINK = re.compile(r"\]\(([^)\s]+)\)")


@pytest.fixture(scope="module")
def package():
    return gen.read_package()


def anchors(markdown):
    return {re.sub(r"[^a-z0-9_-]", "", h.strip().lower().replace(" ", "-"))
            for h in re.findall(r"^#{1,6} (.+)$", markdown, re.MULTILINE)}


def test_committed_docs_and_readme_table_are_up_to_date(capsys):
    # Fails after a change to a class, method, docstring or enum: run python docs/generate_api_docs.py
    assert gen.main(["--check"]) == 0, capsys.readouterr().out


def test_every_class_method_and_enum_is_documented(package):
    classes, enums = package
    pages = gen.build()
    domain_classes = set()
    for filename in os.listdir(os.path.join(ROOT, "src", "xurrent")):
        if filename.endswith(".py"):
            with open(os.path.join(ROOT, "src", "xurrent", filename), encoding="utf-8") as file:
                tree = ast.parse(file.read())
            domain_classes |= {n.name for n in tree.body if isinstance(n, ast.ClassDef)
                               and any(ast.unparse(b) == "JsonSerializableDict" for b in n.bases)}
    assert {c.name for c in classes} == domain_classes | {"XurrentApiHelper"}
    for info in classes:
        page = pages[f"{info.name}.md"]
        headings = set(re.findall(r"^### (\w+)$", page, re.MULTILINE))
        assert {m.name for m in info.methods} <= headings, info.name
        assert set(info.enums) <= headings, info.name
    documented = {name for name, enum in enums.items() if enum.owner}
    assert documented == set(enums)


@pytest.mark.parametrize("wiki", [False, True])
def test_no_dangling_links(wiki):
    pages = gen.build(wiki=wiki)
    page_anchors = {name[:-3]: anchors(content) for name, content in pages.items()}
    wiki_url = f"{gen.REPO_URL}/wiki"
    for name, content in pages.items():
        for target in LINK.findall(content):
            if wiki and target.startswith(wiki_url):
                target = target[len(wiki_url):].lstrip("/") or "Home"
            elif target.startswith("http"):
                continue
            page, _, anchor = target.partition("#")
            page = page[:-3] if page.endswith(".md") else page
            page = page or name[:-3]
            assert page in page_anchors, f"{name}: {target}"
            if anchor:
                assert anchor in page_anchors[page], f"{name}: {target}"


def test_readme_links_point_to_generated_pages():
    with open(os.path.join(ROOT, "README.md"), encoding="utf-8") as file:
        readme = file.read()
    pages = set(gen.build())
    linked = re.findall(r"/blob/main/docs/api/(\w+\.md)\)", readme)
    assert linked and set(linked) <= pages


def test_endpoints_come_from_the_code(package):
    classes, _ = package
    endpoints = {(c.name, m.name): m.endpoint for c in classes for m in c.methods}
    assert endpoints[("Request", "get_by_id")] == "GET /requests/{id}"
    assert endpoints[("Request", "get_notes")] == "GET /requests/{id}/notes"
    assert endpoints[("Request", "create")] == "POST /requests"
    assert endpoints[("Request", "update")] == "PATCH /requests/{id}"
    assert endpoints[("Request", "remove_ci")] == "DELETE /requests/{id}/cis/{ci_id}"
    assert endpoints[("Calendar", "get_hours")] == "GET /calendars/{id}/calendar_hours"
    assert endpoints[("ConfigurationItem", "get_configuration_items")] == "GET /cis"
    assert endpoints[("XurrentApiHelper", "search")] == "GET /search"
    assert endpoints[("Request", "close")] is None          # delegates to update(); no endpoint of its own


def test_cross_references_both_directions():
    pages = gen.build()
    request, person = pages["Request.md"], pages["Person.md"]
    assert "- [Person](Person.md): `created_by`, `member`, `requested_by`, `requested_for`" in request
    used_by = person[person.index("Used by:"):]
    assert "- [Request](Request.md): `created_by`, `member`, `requested_by`, `requested_for`" in used_by
    assert "| `category` | `Optional[str]` | `None` | [RequestCategory](#requestcategory) (unknown values stay text) |" in request


def test_wiki_pages_use_wiki_links():
    pages = gen.build(wiki=True)
    assert "Home.md" in pages and "_Sidebar.md" in pages and "README.md" not in pages
    # Absolute links: the wiki home page is served at .../wiki (no trailing slash), relative links would break
    wiki = f"{gen.REPO_URL}/wiki"
    assert f"]({wiki}/Person)" in pages["Request.md"] and ".md)" not in pages["Request.md"]
    assert f"- [Request]({wiki}/Request)" in pages["_Sidebar.md"]
    assert f"]({wiki}/Request)" in pages["Home.md"]
    assert not re.search(r"\]\((?!https?://|#)", "".join(pages.values()))


def test_render_doc_lists_parameters_and_fences_examples():
    doc = ("Do something.\n\n:param name: The name\n    continued here\n:return: The result\n\n"
           ">>> 1 + 1\n2")
    lines = gen.render_doc(doc)
    assert lines[0] == "Do something."
    assert "- `name`: The name continued here" in lines
    assert "- Returns: The result" in lines
    text = "\n".join(lines)
    assert "```python\n>>> 1 + 1\n2\n```" in text


def test_updated_readme_needs_markers():
    with pytest.raises(ValueError):
        gen.updated_readme("# no markers here\n")
