"""Unit tests for .github/scripts/release_changelog.py (the CHANGELOG step of release.yml on main)."""
import doctest
import importlib.util
import os

import pytest

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
_spec = importlib.util.spec_from_file_location(
    "release_changelog", os.path.join(ROOT, ".github", "scripts", "release_changelog.py"))
rc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rc)

REPO = "https://github.com/fasteiner/xurrent-python"
SAMPLE = (
    "# Changelog\n\n"
    "## [Unreleased]\n\n### Added\n\n- Core: new_thing with under_scores.\n\n"
    "## [0.11.0] - 2026-04-13\n\n### Added\n\n- Core: older.\n\n"
    "## [0.10.0] - 2025-08-16\n\n- Core: oldest.\n\n"
    f"[0.11.0]: {REPO}/compare/v0.10.0...v0.11.0\n\n"
    f"[0.10.0]: {REPO}/compare/v0.9.1...v0.10.0\n"
)


def test_doctests():
    assert doctest.testmod(rc).failed == 0


def test_unreleased_becomes_the_given_version_and_nothing_else_changes():
    new, notice = rc.release(SAMPLE, "0.14.0", REPO, "2026-11-05")
    assert notice is None
    expected = (SAMPLE
                .replace("## [Unreleased]", "## [0.14.0] - 2026-11-05")
                .replace(f"[0.11.0]: {REPO}/compare/v0.10.0...v0.11.0\n",
                         f"[0.14.0]: {REPO}/compare/v0.11.0...v0.14.0\n"
                         f"[0.11.0]: {REPO}/compare/v0.10.0...v0.11.0\n"))
    assert new == expected
    assert "under_scores" in new          # no markdown rewriting (the action escaped underscores)


def test_the_real_changelog_changes_in_two_lines_only():
    with open(os.path.join(ROOT, "CHANGELOG.md"), encoding="utf-8", newline="") as file:
        text = file.read()
    if "## [Unreleased]" not in text:
        pytest.skip("CHANGELOG.md has no [Unreleased] section right now")
    new, notice = rc.release(text, "9.9.9", REPO, "2030-01-01")
    assert notice is None
    old_lines, new_lines = text.splitlines(), new.splitlines()
    assert len(new_lines) == len(old_lines) + 1
    assert "## [9.9.9] - 2030-01-01" in new_lines and "## [Unreleased]" not in new_lines
    added = [line for line in new_lines if line not in old_lines]
    assert added[0] == "## [9.9.9] - 2030-01-01"
    assert added[1].startswith(f"[9.9.9]: {REPO}/compare/v") and added[1].endswith("...v9.9.9")


def test_without_unreleased_section_nothing_changes():
    text = SAMPLE.replace("## [Unreleased]\n\n### Added\n\n- Core: new_thing with under_scores.\n\n", "")
    new, notice = rc.release(text, "0.14.0", REPO, "2026-11-05")
    assert new == text and "no [Unreleased]" in notice


def test_an_existing_version_section_is_left_alone():
    new, notice = rc.release(SAMPLE, "0.11.0", REPO, "2026-11-05")
    assert new == SAMPLE and "already has a section" in notice


@pytest.mark.parametrize("version", ["", "v0.14.0", "0.14", "minor", "0.14.0; rm -rf /"])
def test_invalid_versions_are_refused(version):
    with pytest.raises(ValueError):
        rc.release(SAMPLE, version, REPO, "2026-11-05")


def test_prerelease_versions_are_accepted():
    new, _ = rc.release(SAMPLE, "1.0.0-rc.1", REPO, "2026-11-05")
    assert "## [1.0.0-rc.1] - 2026-11-05" in new


def test_crlf_files_keep_their_line_endings():
    crlf = SAMPLE.replace("\n", "\r\n")
    new, _ = rc.release(crlf, "0.14.0", REPO, "2026-11-05")
    assert new.count("\n") == new.count("\r\n")
    assert f"[0.14.0]: {REPO}/compare/v0.11.0...v0.14.0\r\n" in new


def test_unreleased_link_reference_is_removed():
    text = SAMPLE + f"[unreleased]: {REPO}/compare/v0.11.0...HEAD\n"
    new, _ = rc.release(text, "0.14.0", REPO, "2026-11-05")
    assert "[unreleased]:" not in new


def test_first_release_links_to_its_tag():
    new, _ = rc.release("# Changelog\n\n## [Unreleased]\n\n- Core: first.\n", "0.1.0", REPO + "/", "2026-11-05")
    assert new.endswith(f"\n\n[0.1.0]: {REPO}/releases/tag/v0.1.0\n")


def test_main_writes_the_file(tmp_path, capsys):
    path = tmp_path / "CHANGELOG.md"
    path.write_bytes(SAMPLE.encode())
    assert rc.main([str(path), "0.14.0", REPO, "2026-11-05"]) == 0
    assert path.read_bytes().decode().startswith("# Changelog\n\n## [0.14.0] - 2026-11-05\n")
    assert rc.main([str(path), "0.14.0", REPO, "2026-11-05"]) == 0      # second run: notice, no change
    assert "::notice::" in capsys.readouterr().out
    assert rc.main([str(path)]) == 2


def test_release_workflow_uses_the_calculated_version():
    with open(os.path.join(ROOT, ".github", "workflows", "release.yml"), encoding="utf-8") as file:
        workflow = file.read()
    assert ("python3 .github/scripts/release_changelog.py CHANGELOG.md "
            '"${{ steps.effective-version.outputs.effective_version }}"') in workflow
    assert "command: bump" not in workflow and "bump_type" not in workflow
    # The release notes are still read from [Unreleased] before it is renamed
    assert workflow.index("command: query") < workflow.index("release_changelog.py")
