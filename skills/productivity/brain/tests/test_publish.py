import io
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import publish  # noqa: E402

CONCEPT = "---\ntype: Note\ntitle: {title}\n---\n\nBody\n"


def git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True, text=True).stdout.strip()


class PublishTest(unittest.TestCase):
    def setUp(self):
        self._temporary_directory = tempfile.TemporaryDirectory()
        base = Path(self._temporary_directory.name)
        self.remote = base / "remote.git"
        git(base, "init", "-q", "--bare", "-b", "main", str(self.remote))
        self.repo = base / "work"
        git(base, "clone", "-q", str(self.remote), str(self.repo))
        git(self.repo, "config", "user.name", "Test")
        git(self.repo, "config", "user.email", "test@example.com")
        git(self.repo, "switch", "-q", "-c", "main")
        self.root = self.repo / "brain"
        self.write("seed.md", "seed")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "seed")
        git(self.repo, "push", "-q", "-u", "origin", "main")

    def tearDown(self):
        self._temporary_directory.cleanup()

    def write(self, name, title):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(CONCEPT.format(title=title))

    def run_publish(self, *args):
        with redirect_stdout(io.StringIO()) as stream:
            code = publish.main([args[0], str(self.root), *args[1:]])
        return code, stream.getvalue()

    def publish_run(self, *files):
        code, output = self.run_publish("stage", *files)
        if code:
            return code, output
        tree = output.strip().splitlines()[-1].split()[-1]
        return self.run_publish("commit", "--tree", tree, "--message", "Record test")

    def remote_files(self):
        return git(self.remote, "ls-tree", "-r", "--name-only", "main").splitlines()

    def test_pushes_only_the_runs_files(self):
        self.assertEqual(self.run_publish("baseline")[0], 0)
        self.write("new.md", "New")
        code, output = self.publish_run("new.md")
        self.assertEqual(code, 0, output)
        self.assertIn("PUSHED", output)
        self.assertEqual(self.remote_files(), ["brain/new.md", "brain/seed.md"])
        self.assertEqual(git(self.repo, "status", "--porcelain"), "")

    def test_holds_when_validation_fails(self):
        self.run_publish("baseline")
        (self.root / "bad.md").write_text("no frontmatter\n")
        code, output = self.publish_run("bad.md")
        self.assertEqual(code, 3, output)
        self.assertIn("validation", output)

    def test_holds_on_a_new_file_the_run_did_not_claim(self):
        self.run_publish("baseline")
        self.write("new.md", "New")
        self.write("foreign.md", "Foreign")
        code, output = self.publish_run("new.md")
        self.assertEqual(code, 3, output)
        self.assertIn("foreign.md", output)
        self.assertEqual(self.remote_files(), ["brain/seed.md"])

    def test_holds_when_a_run_file_was_dirty_at_baseline(self):
        self.write("seed.md", "Edited by the user")
        self.run_publish("baseline")
        self.write("seed.md", "Edited by Brain")
        code, output = self.publish_run("seed.md")
        self.assertEqual(code, 3, output)
        self.assertIn("uncommitted edits before the run", output)

    def test_holds_when_the_index_was_staged_before_the_run(self):
        (self.repo / "other.txt").write_text("staged elsewhere")
        git(self.repo, "add", "other.txt")
        self.run_publish("baseline")
        self.write("new.md", "New")
        code, output = self.publish_run("new.md")
        self.assertEqual(code, 3, output)
        self.assertIn("staged changes", output)

    def test_holds_when_the_branch_was_ahead_at_baseline(self):
        (self.repo / "local.txt").write_text("unpushed")
        git(self.repo, "add", "local.txt")
        git(self.repo, "commit", "-q", "-m", "local")
        self.run_publish("baseline")
        self.write("new.md", "New")
        code, output = self.publish_run("new.md")
        self.assertEqual(code, 3, output)
        self.assertIn("ahead of or behind", output)

    def test_holds_when_head_moves_after_baseline(self):
        self.run_publish("baseline")
        (self.repo / "local.txt").write_text("concurrent")
        git(self.repo, "add", "local.txt")
        git(self.repo, "commit", "-q", "-m", "concurrent")
        self.write("new.md", "New")
        code, output = self.publish_run("new.md")
        self.assertEqual(code, 3, output)
        self.assertIn("head changed", output)
        self.assertEqual(self.remote_files(), ["brain/seed.md"])

    def test_holds_during_an_unfinished_merge(self):
        git(self.repo, "switch", "-q", "-c", "topic")
        (self.repo / "topic.txt").write_text("topic")
        git(self.repo, "add", "topic.txt")
        git(self.repo, "commit", "-q", "-m", "topic")
        git(self.repo, "switch", "-q", "main")
        git(self.repo, "merge", "-q", "--no-commit", "-s", "ours", "topic")
        code, output = self.run_publish("baseline")
        self.write("new.md", "New")
        code, output = self.publish_run("new.md")
        self.assertEqual(code, 3, output)
        self.assertIn("MERGE_HEAD", output)

    def test_holds_when_the_index_changes_after_review(self):
        self.run_publish("baseline")
        self.write("new.md", "New")
        code, output = self.run_publish("stage", "new.md")
        self.assertEqual(code, 0, output)
        tree = output.strip().splitlines()[-1].split()[-1]
        self.write("new.md", "Changed after review")
        git(self.repo, "add", "brain/new.md")
        code, output = self.run_publish("commit", "--tree", tree, "--message", "Record test")
        self.assertEqual(code, 3, output)
        self.assertIn("after it was reviewed", output)

    def test_skips_a_branch_without_upstream(self):
        git(self.repo, "switch", "-q", "-c", "loose")
        code, output = self.run_publish("baseline")
        self.write("new.md", "New")
        code, output = self.publish_run("new.md")
        self.assertEqual(code, 2, output)
        self.assertIn("no upstream", output)

    def test_pushes_to_a_local_branch_upstream(self):
        git(self.repo, "branch", "-q", "base")
        git(self.repo, "switch", "-q", "-c", "feature", "--track", "base")
        self.run_publish("baseline")
        self.write("new.md", "New")
        code, output = self.publish_run("new.md")
        self.assertEqual(code, 0, output)
        self.assertEqual(git(self.repo, "rev-parse", "base"), git(self.repo, "rev-parse", "feature"))

    def test_pushes_one_refspec_under_push_default_matching(self):
        git(self.repo, "push", "-q", "origin", "main:other")
        git(self.repo, "branch", "-q", "other", "origin/other")
        git(self.repo, "switch", "-q", "other")
        (self.repo / "other.txt").write_text("unpublished")
        git(self.repo, "add", "other.txt")
        git(self.repo, "commit", "-q", "-m", "other")
        git(self.repo, "switch", "-q", "main")
        git(self.repo, "config", "push.default", "matching")
        self.run_publish("baseline")
        self.write("new.md", "New")
        code, output = self.publish_run("new.md")
        self.assertEqual(code, 0, output)
        self.assertNotIn("other.txt", git(self.remote, "ls-tree", "-r", "--name-only", "other"))

    def other_clone(self):
        clone = Path(self._temporary_directory.name) / "elsewhere"
        git(self.repo.parent, "clone", "-q", str(self.remote), str(clone))
        return clone

    def test_holds_when_the_branch_is_behind_its_upstream(self):
        clone = self.other_clone()
        git(clone, "-c", "user.name=T", "-c", "user.email=t@e", "commit", "-q", "--allow-empty", "-m", "ahead")
        git(clone, "push", "-q", "origin", "main")
        git(self.repo, "fetch", "-q")
        self.run_publish("baseline")
        self.write("new.md", "New")
        code, output = self.publish_run("new.md")
        self.assertEqual(code, 3, output)
        self.assertIn("ahead of or behind", output)

    def test_refuses_to_republish_after_upstream_moves_backward(self):
        (self.repo / "removed.txt").write_text("later removed upstream")
        git(self.repo, "add", "removed.txt")
        git(self.repo, "commit", "-q", "-m", "removed later")
        git(self.repo, "push", "-q", "origin", "main")
        self.run_publish("baseline")
        clone = self.other_clone()
        git(clone, "push", "-q", "--force", "origin", "main~1:main")
        self.write("new.md", "New")
        code, output = self.publish_run("new.md")
        self.assertEqual(code, 4, output)
        self.assertNotIn("removed.txt", self.remote_files())

    def test_skips_every_step_outside_git(self):
        outside = Path(self._temporary_directory.name) / "plain"
        (outside / "a.md").parent.mkdir()
        (outside / "a.md").write_text(CONCEPT.format(title="A"))
        self.root = outside
        self.assertEqual(self.run_publish("baseline")[0], 2)
        self.write("b.md", "B")
        code, output = self.run_publish("stage", "b.md")
        self.assertEqual(code, 2, output)
        self.assertIn("not in a Git repository", output)

    def test_pushes_no_tags_under_push_follow_tags(self):
        git(self.repo, "tag", "-a", "-m", "private", "private-tag")
        git(self.repo, "config", "push.followTags", "true")
        self.run_publish("baseline")
        self.write("new.md", "New")
        code, output = self.publish_run("new.md")
        self.assertEqual(code, 0, output)
        self.assertEqual(git(self.remote, "tag", "--list"), "")

    def test_handles_non_ascii_paths(self):
        self.run_publish("baseline")
        self.write("café.md", "Café")
        code, output = self.publish_run("café.md")
        self.assertEqual(code, 0, output)
        self.assertIn("brain/café.md", git(self.remote, "-c", "core.quotePath=false", "ls-tree", "-r", "--name-only", "main"))

    def test_reports_a_rejected_push_and_keeps_the_commit(self):
        self.run_publish("baseline")
        clone = self.other_clone()
        git(clone, "-c", "user.name=T", "-c", "user.email=t@e", "commit", "-q", "--allow-empty", "-m", "race")
        git(clone, "push", "-q", "origin", "main")
        self.write("new.md", "New")
        code, output = self.publish_run("new.md")
        self.assertEqual(code, 4, output)
        self.assertIn("stays local", output)
        self.assertEqual(git(self.repo, "log", "-1", "--format=%s"), "Record test")


if __name__ == "__main__":
    unittest.main()
