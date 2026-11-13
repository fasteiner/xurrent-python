"""Unit tests for the release conditions in .github/workflows/release.yml and the CI matrix.

A push releases (tag, CHANGELOG and version update, GitHub release, PyPI on main) only when it changes the
package itself, i.e. something under src/. The check step's shell script is run here against a throwaway
git repository.
"""
import os
import re
import shutil
import subprocess

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CONDITION = "env.package_changed == 'true'"


def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as file:
        return file.read().replace("\r\n", "\n")


def steps_of(workflow, job):
    """(title, text) of each step of a job, in order."""
    body = workflow.split(f"\n  {job}:\n", 1)[1]
    body = re.split(r"\n  [A-Za-z][\w-]*:\n", body, maxsplit=1)[0]
    parts = re.split(r"\n(?=      - (?:name|uses): )", body)
    return [(part.splitlines()[0].strip(), part) for part in parts[1:]]


def check_script(workflow):
    """The run script of the 'Check for package changes' step, dedented."""
    text = dict(steps_of(workflow, "create-release"))["- name: Check for package changes"]
    block = text.split("        run: |\n", 1)[1]
    lines = []
    for line in block.splitlines():
        if line.strip() and not line.startswith("          "):
            break
        lines.append(line[10:])
    return "\n".join(lines)


def test_every_step_after_the_check_needs_package_changes():
    steps = steps_of(read(".github/workflows/release.yml"), "create-release")
    titles = [title for title, _ in steps]
    check = titles.index("- name: Check for package changes")
    for title, text in steps[check + 1:]:
        conditions = re.findall(r"^        if: (.+)$", text, re.MULTILINE)
        assert conditions and CONDITION in conditions[0], title


def test_pypi_publish_needs_package_changes_on_main():
    workflow = read(".github/workflows/release.yml")
    publish = workflow.split("\n  pypi-publish:\n", 1)[1]
    condition = re.search(r"^    if: (.+)$", publish, re.MULTILINE).group(1)
    assert "github.ref == 'refs/heads/main'" in condition
    assert "needs.create-release.outputs.package_changed == 'true'" in condition


def test_no_forced_patch_release_without_package_changes():
    workflow = read(".github/workflows/release.yml")
    assert "python_changed" not in workflow
    assert "PREV_TAG" not in workflow and "NEW_PATCH" not in workflow
    assert "grep -qE '^src/'" in check_script(workflow)


def test_python_39_runs_on_ubuntu_24_04():
    # ubuntu-latest (26.04) has no Python 3.9 in actions/setup-python
    ci = read(".github/workflows/python-package.yml")
    assert "runs-on: ${{ matrix.python-version == '3.9' && 'ubuntu-24.04' || 'ubuntu-latest' }}" in ci
    assert '"3.9"' in ci


@pytest.fixture
def repo(tmp_path):
    if not shutil.which("git") or not shutil.which("bash"):
        pytest.skip("git and bash are needed")
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.invalid")

    def git(*args):
        return subprocess.run(["git", *args], cwd=tmp_path, env=env, check=True,
                              capture_output=True, text=True).stdout.strip()

    def commit(path, content):
        file = tmp_path / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(content)
        git("add", "-A")
        git("commit", "-q", "-m", f"change {path}")
        return git("rev-parse", "HEAD")

    git("init", "-q")
    return tmp_path, commit


def run_check(path, before, sha):
    script = check_script(read(".github/workflows/release.yml"))
    script = script.replace("${{ github.event.before }}", before).replace("${{ github.sha }}", sha)
    env_file, out_file = path / "github_env", path / "github_output"
    for file in (env_file, out_file):          # fresh per run, as in GitHub Actions
        file.write_text("")
    result = subprocess.run(["bash", "-e", "-c", script], cwd=path, capture_output=True, text=True,
                            env=dict(os.environ, GITHUB_ENV=str(env_file), GITHUB_OUTPUT=str(out_file)))
    assert result.returncode == 0, result.stderr
    output = out_file.read_text()
    assert output == env_file.read_text()
    return output.strip()


def test_readme_only_push_releases_nothing(repo):
    path, commit = repo
    base = commit("src/xurrent/core.py", "v1")
    head = commit("README.md", "docs")
    assert run_check(path, base, head) == "package_changed=false"


def test_change_in_src_releases(repo):
    path, commit = repo
    base = commit("README.md", "docs")
    head = commit("src/xurrent/core.py", "v2")
    assert run_check(path, base, head) == "package_changed=true"


def test_tests_and_docs_alone_release_nothing(repo):
    path, commit = repo
    base = commit("src/xurrent/core.py", "v1")
    commit("tests/unit_tests/test_x.py", "t")
    head = commit("docs/generate_api_docs.py", "g")
    assert run_check(path, base, head) == "package_changed=false"


def test_all_commits_of_a_push_count(repo):
    # A push of several commits whose last one only touches the README still releases a src/ change
    path, commit = repo
    base = commit("README.md", "a")
    commit("src/xurrent/core.py", "v2")
    head = commit("README.md", "b")
    assert run_check(path, base, head) == "package_changed=true"


@pytest.mark.parametrize("before", ["0000000000000000000000000000000000000000", "", "1234567890abcdef1234567890abcdef12345678"])
def test_unknown_before_falls_back_to_the_last_commit(repo, before):
    # New branch (zeros), missing value or a force-pushed, unknown commit: compare with HEAD^
    path, commit = repo
    commit("src/xurrent/core.py", "v1")
    head = commit("src/xurrent/core.py", "v2")
    assert run_check(path, before, head) == "package_changed=true"
    head = commit("README.md", "docs")
    assert run_check(path, before, head) == "package_changed=false"
