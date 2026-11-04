#!/usr/bin/env python3
"""
Turn the [Unreleased] section of CHANGELOG.md into the section of the version being released.

Used by .github/workflows/release.yml on main instead of keep-a-changelog-action's ``bump``: that
action can only count up from the last version in the changelog (e.g. 0.11.0 + minor = 0.12.0), while
the package, tag and GitHub release use the version GitVersion calculates (e.g. 0.14.0, after the
previews on Dev). This script writes exactly the version it is given, adds the compare link of the new
version, and leaves the rest of the file untouched.

Usage::

    python3 .github/scripts/release_changelog.py CHANGELOG.md 0.14.0 https://github.com/owner/repo [YYYY-MM-DD]

Exit code 0 also when there is nothing to do (no [Unreleased] section, or the version already has a
section), so a release is never blocked by the changelog; a notice says why.
"""
import re
import sys
from datetime import datetime, timezone
from typing import Optional, Tuple

UNRELEASED = re.compile(r'^## \[Unreleased\][^\r\n]*', re.MULTILINE | re.IGNORECASE)
RELEASE_HEADING = re.compile(r'^## \[(\d+\.\d+\.\d+[^\]]*)\]', re.MULTILINE)
LINK_REFERENCE = re.compile(r'^\[[^\]]+\]: \S+', re.MULTILINE)
VERSION = re.compile(r'^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$')


def release(text: str, version: str, repo_url: str, date: str) -> Tuple[str, Optional[str]]:
    """
    Return the changelog with [Unreleased] renamed to the version, and a notice if nothing changed.

    >>> text = "# Changelog\\n\\n## [Unreleased]\\n\\n- Core: x\\n\\n## [0.11.0] - 2026-04-13\\n\\n- y\\n\\n" \\
    ...        "[0.11.0]: https://github.com/o/r/compare/v0.10.0...v0.11.0\\n"
    >>> new, notice = release(text, '0.14.0', 'https://github.com/o/r', '2026-11-05')
    >>> print(new)
    # Changelog
    <BLANKLINE>
    ## [0.14.0] - 2026-11-05
    <BLANKLINE>
    - Core: x
    <BLANKLINE>
    ## [0.11.0] - 2026-04-13
    <BLANKLINE>
    - y
    <BLANKLINE>
    [0.14.0]: https://github.com/o/r/compare/v0.11.0...v0.14.0
    [0.11.0]: https://github.com/o/r/compare/v0.10.0...v0.11.0
    <BLANKLINE>
    >>> notice is None
    True
    """
    if not VERSION.match(version):
        raise ValueError(f'not a version: {version!r}')
    if re.search(rf'^## \[{re.escape(version)}\]', text, re.MULTILINE):
        return text, f'CHANGELOG.md already has a section for {version}; left unchanged.'
    unreleased = UNRELEASED.search(text)
    if not unreleased:
        return text, 'CHANGELOG.md has no [Unreleased] section; left unchanged.'

    newline = '\r\n' if '\r\n' in text else '\n'
    text = text[:unreleased.start()] + f'## [{version}] - {date}' + text[unreleased.end():]

    previous = RELEASE_HEADING.search(text, unreleased.start() + 1)
    repo_url = repo_url.rstrip('/')
    if previous:
        link = f'[{version}]: {repo_url}/compare/v{previous.group(1)}...v{version}'
    else:
        link = f'[{version}]: {repo_url}/releases/tag/v{version}'
    # Remove a link reference for [Unreleased], it no longer has a section
    text = re.sub(r'^\[Unreleased\]: \S+(?:\r?\n)?', '', text, flags=re.MULTILINE | re.IGNORECASE)
    headings = list(RELEASE_HEADING.finditer(text))
    first_link = LINK_REFERENCE.search(text, headings[-1].end() if headings else 0)
    if first_link:
        text = text[:first_link.start()] + link + newline + text[first_link.start():]
    else:
        text = text.rstrip('\r\n') + newline + newline + link + newline
    return text, None


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) not in (3, 4):
        sys.stderr.write(__doc__)
        return 2
    path, version, repo_url = args[:3]
    date = args[3] if len(args) == 4 else datetime.now(timezone.utc).strftime('%Y-%m-%d')
    with open(path, encoding='utf-8', newline='') as file:   # keep the line endings as they are
        text = file.read()
    new_text, notice = release(text, version, repo_url, date)
    if notice:
        print(f'::notice::{notice}')
        return 0
    with open(path, 'w', encoding='utf-8', newline='') as file:
        file.write(new_text)
    print(f'CHANGELOG.md: [Unreleased] is now [{version}] - {date}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
