"""Tests for the template and version checks.

@doc: docs/design/Checkers.md#5-테스트
"""

from pathlib import Path

from tests.support import RepoTestCase
from projinit.check_template import check_common_files, check_version
from projinit.config import load_project
from projinit.init import init_project, package_version


class CheckTemplateTest(RepoTestCase):
    """@doc: docs/design/Checkers.md#5-테스트"""

    def setUp(self) -> None:
        super().setUp()
        init_project(self.root, "git@github.com:me/demo.git")

    def messages(self) -> list[tuple[str, str]]:
        project = load_project(self.root)
        problems = check_common_files(project) + check_version(project, package_version())
        return [(str(Path(problem.path).relative_to(self.root)), problem.message) for problem in problems]

    def test_freshly_initialized_folder_passes(self) -> None:
        self.assertEqual(self.messages(), [])

    def test_reports_edited_and_missing_common_files(self) -> None:
        self.write("docs/CodeRule.md", "손으로 고침\n")
        (self.root / ".githooks/commit-msg").unlink()
        self.assertEqual(
            self.messages(),
            [
                ("docs/CodeRule.md", "템플릿과 다름 (init --refresh-common으로 다시 만든다)"),
                (".githooks/commit-msg", "공통 파일 없음"),
            ],
        )

    def test_reports_missing_template_values(self) -> None:
        config = self.root / "projinit.toml"
        config.write_text(config.read_text().replace('repository = "git@github.com:me/demo.git"\n', ""))
        self.assertIn(("projinit.toml", "docs/PullRequestRule.md: 값이 없는 빈 자리: repository"), self.messages())

    def test_version_mismatch_unless_a_command_is_set(self) -> None:
        config = self.root / "projinit.toml"
        config.write_text(config.read_text().replace(f'version = "{package_version()}"', 'version = "9.9.9"'))
        project = load_project(self.root)
        self.assertEqual(
            [problem.message for problem in check_version(project, package_version())],
            [f"설정의 버전 9.9.9과 실행 중인 검사기 버전 {package_version()}이 다름"],
        )
        config.write_text(config.read_text().replace("[projinit]\n", '[projinit]\ncommand = "uv run projinit"\n'))
        self.assertEqual(check_version(load_project(self.root), package_version()), [])
