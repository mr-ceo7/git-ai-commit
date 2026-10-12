"""
Unit tests for git-ai-commit.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from git_ai_commit.generator import clean_commit_message
from git_ai_commit.cli import build_parser
from git_ai_commit.config import save_config, load_config
from git_ai_commit.git_utils import is_git_repository, get_unstaged_files


class TestGenerator(unittest.TestCase):
    def test_clean_commit_message_plain(self):
        msg = "feat: add user authentication"
        self.assertEqual(clean_commit_message(msg), msg)

    def test_clean_commit_message_fences(self):
        raw = "```\nfix: handle null pointer\n```"
        self.assertEqual(clean_commit_message(raw), "fix: handle null pointer")

    def test_clean_commit_message_fences_with_language(self):
        raw = "```markdown\nrefactor: optimize database queries\n```"
        self.assertEqual(clean_commit_message(raw), "refactor: optimize database queries")

    def test_clean_commit_message_quotes(self):
        raw = '"docs: update README installation guide"'
        self.assertEqual(clean_commit_message(raw), "docs: update README installation guide")


class TestParser(unittest.TestCase):
    def setUp(self):
        self.parser = build_parser()

    def test_default_flags(self):
        args = self.parser.parse_args([])
        self.assertFalse(args.interactive)
        self.assertFalse(args.no_push)
        self.assertFalse(args.dry_run)
        self.assertFalse(args.no_stage)
        self.assertIsNone(args.hint)

    def test_custom_flags(self):
        args = self.parser.parse_args(["-m", "hotfix for bug", "-n", "--dry-run", "-i"])
        self.assertEqual(args.hint, "hotfix for bug")
        self.assertTrue(args.no_push)
        self.assertTrue(args.dry_run)
        self.assertTrue(args.interactive)

    def test_config_subcommand(self):
        args = self.parser.parse_args(["config", "--set-key", "test-key-123"])
        self.assertEqual(args.subcommand, "config")
        self.assertEqual(args.set_key, "test-key-123")


class TestGitUtils(unittest.TestCase):
    def test_is_git_repository(self):
        # We know /home/qassim/agy-pool is a git repository
        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.returncode = 0
            mock_proc.stdout = "true\n"
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc
            self.assertTrue(is_git_repository())


if __name__ == "__main__":
    unittest.main()
