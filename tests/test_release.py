"""Tests that the README names the version being released.

@doc: docs/design/Templates.md#5-버전-묶기-i10
"""

import re
import tomllib
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_VERSION_RE = re.compile(r"\bv(\d+\.\d+\.\d+)\b")


class ReadmeVersionTest(unittest.TestCase):
    """@doc: docs/design/Templates.md#5-버전-묶기-i10"""

    def test_readme_versions_match_package_version(self) -> None:
        version = tomllib.loads((_ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
        found = _VERSION_RE.findall((_ROOT / "README.md").read_text(encoding="utf-8"))
        self.assertTrue(found)
        self.assertEqual(set(found), {version})


if __name__ == "__main__":
    unittest.main()
