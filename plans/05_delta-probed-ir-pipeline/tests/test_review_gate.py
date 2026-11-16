"""The review gate in git's own hooks (the user, 14 and 16 November 2026): tools/review_gate.py and tools/install_git_hooks.py.

Every test that moves a ref does it in a throw-away repository under pytest's temporary directory. That repository has the
real layout: the two tools and their configuration are tracked in it under `tools/`, the hooks are installed by its own copy
of the installer - which acts on the repository it is checked out in and on no other, so nothing here can install a hook
into the repository these tests live in - and the hook reads the configuration from that repository's trunk. git runs with an
empty global configuration and without the caller's GIT_* variables.

What is pinned: each way of moving the trunk is refused without a review and passes with one; `log_only` refuses none of them;
moves git reports to no hook are judged at the next one; the reviewed set, class by class; the key (reproducible, not
replayable, blind to unreviewed paths); the failure modes and the way out of each; the installer and its shim.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import ClassVar

import pytest

PLAN = Path(__file__).resolve().parents[1]
TOOLS = PLAN / "tools"
sys.path.insert(0, str(TOOLS))
import install_git_hooks as hooks  # noqa: E402  the path line above must run first
import review_gate as R  # noqa: E402  the path line above must run first

SHIPPED = ("review_gate.py", "review_gate.json", "install_git_hooks.py")
UNREVIEWED = "no review on record"
MASTER = "refs/heads/master"
Done = subprocess.CompletedProcess


class Sandbox:
    """A repository of this test's own, laid out as the real one: the gate tracked under tools/, called by its own hooks.

    master holds a.py, TASKS.md and tools/; `side` adds s.py and `docs` changes TASKS.md, each one commit ahead; HEAD is master.
    """

    templates: ClassVar[dict[bool, Path]] = {}        # filled by the session's `templates` fixture: every test copies one

    def __init__(self, root: Path, *, log_only: bool = False, install: bool = True) -> None:
        root.mkdir(exist_ok=True)
        self.root, self.repo = root, root / "repo"
        (root / "gitconfig").write_text("[user]\n\tname = Test\n\temail = test@example.invalid\n[init]\n\tdefaultBranch = master\n"
                                        "[core]\n\tautocrlf = false\n[commit]\n\tgpgsign = false\n", encoding="utf-8")
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        self.env.update(GIT_CONFIG_GLOBAL=str(root / "gitconfig"), GIT_CONFIG_NOSYSTEM="1", GIT_TERMINAL_PROMPT="0",
                        GIT_EDITOR="true")
        if log_only in Sandbox.templates:
            shutil.copytree(Sandbox.templates[log_only], self.repo)
        else:
            self._build(log_only)
        if install:
            self.installer("install", check=True)

    def _build(self, log_only: bool) -> None:
        (self.repo / "tools").mkdir(parents=True)
        for name in SHIPPED:
            shutil.copy(TOOLS / name, self.repo / "tools" / name)
        config = json.loads((TOOLS / "review_gate.json").read_text(encoding="utf-8"))
        config["reviewed"]["tooling config"] += ["tools/review_gate.json"]        # where this repository keeps it
        self.configure(**(config | {"log_only": log_only}))
        self.git("init", "-q")
        self.git("add", "-f", "tools")
        self.commit({"a.py": "one\n", "TASKS.md": "board\n"}, "first")
        for branch, files in (("side", {"s.py": "side\n"}), ("docs", {"TASKS.md": "board, a row more\n"})):
            self.git("switch", "-q", "-c", branch)
            self.commit(files, branch)
            self.git("switch", "-q", "master")

    def configure(self, **changes: object) -> None:
        """Change the configuration in the working tree; the hook reads the trunk's, so a test commits it to make it count."""
        path = self.repo / "tools" / "review_gate.json"
        path.write_text(json.dumps(json.loads(path.read_text(encoding="utf-8")) | changes, indent=2), encoding="utf-8")

    def run(self, argv: list[str], cwd: Path | None = None, check: bool = False) -> Done:
        done = subprocess.run(argv, cwd=cwd or self.repo, env=self.env, capture_output=True, text=True, check=False,
                              timeout=120)
        if check and done.returncode != 0:
            raise RuntimeError(f"{argv} failed (exit {done.returncode}): {done.stdout}{done.stderr}")
        return done

    def git(self, *args: str, cwd: Path | None = None) -> Done:
        """A git call that must succeed; `try_git` for one whose refusal is the test."""
        return self.run(["git", *args], cwd, check=True)

    def try_git(self, *args: str, cwd: Path | None = None) -> Done:
        return self.run(["git", *args], cwd)

    def tool(self, *args: str, cwd: Path | None = None) -> Done:
        return self.run([sys.executable, str(self.repo / "tools" / "review_gate.py"), *args], cwd)

    def installer(self, what: str, check: bool = False) -> Done:
        return self.run([sys.executable, str(self.repo / "tools" / "install_git_hooks.py"), what], check=check)

    def stage(self, files: dict[str, str]) -> None:
        for name, text in files.items():
            (self.repo / name).parent.mkdir(parents=True, exist_ok=True)
            (self.repo / name).write_text(text, encoding="utf-8")
        self.git("add", "-f", "--", *files)

    def commit(self, files: dict[str, str], message: str) -> None:
        self.stage(files)
        self.git("commit", "-q", "-m", message)

    def past_the_hooks(self, *args: str) -> None:
        """A git call with the hooks switched off: what the gate can only notice afterwards."""
        self.git("-c", f"core.hooksPath={self.root}", *args)

    def record(self, *selector: str) -> Done:
        done = self.tool("record", *selector, "--reviewer", "agent-7", "--findings", "2", "--verdict", "both fixed")
        if done.returncode != 0:
            raise RuntimeError(f"record {selector} failed: {done.stderr}")
        return done

    def rev(self, name: str = MASTER) -> str:
        return self.git("rev-parse", name).stdout.strip()

    def hook_file(self, name: str) -> Path:
        return self.repo / ".git" / "hooks" / name

    def state(self, name: str) -> Path:
        return self.repo / ".git" / R.STATE_DIR / name

    def decisions(self) -> list[dict]:
        path = self.state(R.DECISIONS)
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()] if path.exists() else []

    def judged_landing(self, since: int) -> dict:
        """The journal's line for the move that just brought the trunk where it is. Fails when no hook judged it: the tests
        that expect a landing to pass must not pass because the hook is gone."""
        lines = [d for d in self.decisions()[since:] if d.get("trunk") == MASTER and d["trunk_after"] == self.rev()]
        assert lines, "the trunk moved and no hook judged it"
        return lines[-1]

    def with_origin(self) -> Path:
        """A bare remote that holds what the repository holds."""
        origin = self.root / "origin.git"
        self.git("clone", "-q", "--bare", str(self.repo), str(origin), cwd=self.root)
        self.git("remote", "add", "origin", str(origin))
        self.git("fetch", "-q", "origin")
        return origin

    def commit_elsewhere(self, origin: Path, files: dict[str, str]) -> None:
        """A commit made in another clone and pushed: what a cloud session or a merge on GitHub leaves on the remote."""
        clone = self.root / "elsewhere"
        self.git("clone", "-q", str(origin), str(clone), cwd=self.root)
        for name, text in files.items():
            (clone / name).write_text(text, encoding="utf-8")
        self.git("add", "--", *files, cwd=clone)
        self.git("commit", "-q", "-m", "made elsewhere", cwd=clone)
        self.git("push", "-q", "origin", "master", cwd=clone)


@pytest.fixture(scope="session", autouse=True)
def templates(tmp_path_factory: pytest.TempPathFactory) -> None:
    """The two repositories every test starts from, refusing and logging, built once: a dozen processes saved per test."""
    Sandbox.templates.clear()
    for log_only in (False, True):
        built = Sandbox(tmp_path_factory.mktemp("template"), log_only=log_only, install=False).repo
        Sandbox.templates[log_only] = built


@pytest.fixture
def sb(tmp_path: Path) -> Sandbox:
    return Sandbox(tmp_path)


@pytest.fixture
def logging_sb(tmp_path: Path) -> Sandbox:
    return Sandbox(tmp_path, log_only=True)


# ---------------------------------------------------------------- every way of moving the trunk

def _commit(sb: Sandbox) -> Done:
    sb.stage({"a.py": "two\n"})
    return sb.try_git("commit", "-q", "-m", "x")


def _commit_with_a_global_option(sb: Sandbox) -> Done:
    sb.stage({"a.py": "two\n"})
    return sb.try_git("-c", "user.name=Someone", "commit", "-q", "-m", "x")


def _commit_through_git_exe(sb: Sandbox) -> Done:
    sb.stage({"a.py": "two\n"})
    return sb.run([shutil.which("git.exe") or "git", "commit", "-q", "-m", "x"])


def _commit_of_a_path_with_an_empty_index(sb: Sandbox) -> Done:
    (sb.repo / "a.py").write_text("two\n", encoding="utf-8")
    return sb.try_git("commit", "-q", "-m", "x", "a.py")


def _amend(sb: Sandbox) -> Done:
    sb.stage({"a.py": "two\n"})
    return sb.try_git("commit", "-q", "--amend", "--no-edit")


def _fast_forward_merge(sb: Sandbox) -> Done:
    return sb.try_git("merge", "-q", "side")


def _merge_with_a_message(sb: Sandbox) -> Done:
    return sb.try_git("merge", "-q", "--no-ff", "-m", "bring side home", "side")


def _true_merge(sb: Sandbox) -> Done:
    sb.git("merge", "-q", "docs")                     # the trunk moves on first, unreviewed paths only
    return sb.try_git("merge", "-q", "-m", "merge", "side")


def _pull(sb: Sandbox) -> Done:
    sb.commit_elsewhere(sb.with_origin(), {"e.py": "elsewhere\n"})
    return sb.try_git("pull", "-q", "origin", "master")


def _reset_hard(sb: Sandbox) -> Done:
    return sb.try_git("reset", "-q", "--hard", "side")


def _branch_force(sb: Sandbox) -> Done:
    sb.git("switch", "-q", "--detach")
    return sb.try_git("branch", "-f", "master", "side")


def _checkout_capital_b(sb: Sandbox) -> Done:
    sb.git("switch", "-q", "side")
    return sb.try_git("checkout", "-q", "-B", "master", "side")


def _update_ref(sb: Sandbox) -> Done:
    return sb.try_git("update-ref", MASTER, sb.rev("side"))


def _update_ref_through_a_symbolic_ref(sb: Sandbox) -> Done:
    sb.git("switch", "-q", "--detach")
    sb.git("symbolic-ref", "refs/heads/alias", MASTER)
    return sb.try_git("update-ref", "refs/heads/alias", sb.rev("side"))


def _push_into_this_repository(sb: Sandbox) -> Done:
    sb.git("switch", "-q", "--detach")
    return sb.try_git("push", "-q", ".", "side:master")


def _fetch_into_the_trunk(sb: Sandbox) -> Done:
    sb.git("switch", "-q", "--detach")
    return sb.try_git("fetch", "-q", ".", "side:master")


def _am(sb: Sandbox) -> Done:
    patch = sb.root / "side.patch"
    patch.write_text(sb.git("format-patch", "-1", "--stdout", "side").stdout, encoding="utf-8")
    return sb.try_git("am", "-q", str(patch))


def _detached_commit_then_pointed_at(sb: Sandbox) -> Done:
    sb.git("switch", "-q", "--detach")
    sb.commit({"a.py": "two\n"}, "on no branch")      # free: it moves HEAD only
    return sb.try_git("branch", "-f", "master", "HEAD")


def _rebase(sb: Sandbox) -> Done:
    sb.git("merge", "-q", "docs")
    return sb.try_git("rebase", "-q", "side")


def _cherry_pick(sb: Sandbox) -> Done:
    return sb.try_git("cherry-pick", "side")


def _from_another_worktree(sb: Sandbox) -> Done:
    other = sb.root / "worktree"
    sb.git("worktree", "add", "-q", str(other), "side")
    return sb.try_git("update-ref", MASTER, "HEAD", cwd=other)


def _absorbed_by_an_ours_merge_then_reset_to(sb: Sandbox) -> Done:
    """`merge -s ours` makes side an ancestor of the trunk without landing a line of it (16 Nov 2026, the second review)."""
    sb.git("merge", "-q", "-s", "ours", "-m", "ours", "side")
    return sb.try_git("reset", "-q", "--hard", "side")


def _grafted_as_an_ancestor_then_pointed_at(sb: Sandbox) -> Done:
    sb.git("switch", "-q", "--detach")
    sb.git("replace", "--graft", sb.rev(), sb.rev("side"))
    return sb.try_git("update-ref", MASTER, sb.rev("side"))


def _commit_on_a_replaced_trunk(sb: Sandbox) -> Done:
    """`git replace` shows git side's tree where the trunk's commit is, so a board-only commit carries s.py along."""
    sb.git("replace", sb.rev(), sb.rev("side"))
    sb.git("read-tree", "-u", "--reset", "HEAD")
    sb.stage({"TASKS.md": "a row\n"})
    return sb.try_git("commit", "-q", "-m", "board only")


WAYS: dict[str, Callable[[Sandbox], Done]] = {
    "git commit": _commit,
    "git -c x=y commit": _commit_with_a_global_option,
    "git.exe commit": _commit_through_git_exe,
    "git commit <path>, empty index": _commit_of_a_path_with_an_empty_index,
    "git commit --amend": _amend,
    "git merge (fast-forward)": _fast_forward_merge,
    "git merge --no-ff -m": _merge_with_a_message,
    "git merge (true merge)": _true_merge,
    "git pull": _pull,
    "git reset --hard <branch>": _reset_hard,
    "git branch -f master": _branch_force,
    "git checkout -B master": _checkout_capital_b,
    "git update-ref": _update_ref,
    "git update-ref through a symbolic ref": _update_ref_through_a_symbolic_ref,
    "git push . side:master": _push_into_this_repository,
    "git fetch . side:master": _fetch_into_the_trunk,
    "git am": _am,
    "detached commit, then pointed at": _detached_commit_then_pointed_at,
    "git rebase": _rebase,
    "git cherry-pick": _cherry_pick,
    "another worktree": _from_another_worktree,
    "merge -s ours, then reset --hard": _absorbed_by_an_ours_merge_then_reset_to,
    "replace --graft, then update-ref": _grafted_as_an_ancestor_then_pointed_at,
    "commit on a replaced trunk": _commit_on_a_replaced_trunk,
}


def reviewed_code_on_the_trunk(sb: Sandbox) -> set[str]:
    """The reviewed files the trunk really holds, replacement refs aside."""
    names = sb.run(["git", "--no-replace-objects", "ls-tree", "-r", "--name-only", MASTER], check=True).stdout.split()
    return {name for name in names if name.endswith(".py") and not name.startswith("tools/")}


@pytest.mark.parametrize("way", WAYS)
def test_every_way_of_moving_the_trunk_is_refused_without_a_review(sb: Sandbox, way: str) -> None:
    done = WAYS[way](sb)
    assert done.returncode != 0, f"{way} moved the trunk unseen: {done.stdout}{done.stderr}"
    assert UNREVIEWED in done.stderr, done.stderr
    assert reviewed_code_on_the_trunk(sb) == {"a.py"}, "the trunk holds code nobody reviewed"
    assert sb.run(["git", "--no-replace-objects", "show", f"{MASTER}:a.py"], check=True).stdout == "one\n"
    assert sb.decisions()[-1]["refused"] is True


@pytest.mark.parametrize("way", WAYS)
def test_log_only_refuses_none_of_them_and_logs_each(logging_sb: Sandbox, way: str) -> None:
    """The same calls with the one switch on: each one succeeds, which also shows the scenario is a real move of the trunk."""
    before = logging_sb.rev()
    done = WAYS[way](logging_sb)
    assert done.returncode == 0, f"{way}: {done.stdout}{done.stderr}"
    assert "log only" in done.stderr and UNREVIEWED in done.stderr
    assert logging_sb.rev() != before
    would = [d for d in logging_sb.decisions() if not d["allowed"]]
    assert would and not any(d["refused"] for d in would)


def test_the_trunk_as_a_symbolic_ref_is_refused(sb: Sandbox) -> None:
    done = sb.try_git("symbolic-ref", MASTER, "refs/heads/side")
    assert done.returncode != 0 and "symbolic ref" in done.stderr
    assert sb.try_git("symbolic-ref", "-q", MASTER).returncode != 0


def test_log_only_lets_even_that_pass_and_the_journal_still_names_a_commit(logging_sb: Sandbox) -> None:
    done = logging_sb.try_git("symbolic-ref", MASTER, "refs/heads/side")
    assert done.returncode == 0 and "symbolic ref" in done.stderr and "log only" in done.stderr
    assert logging_sb.decisions()[-1]["trunk_after"] == logging_sb.rev("side")
    assert "nothing moved it unseen" in logging_sb.tool("status", "--unseen").stdout


# ---------------------------------------------------------------- moves git reports to no hook

def _copied_over(sb: Sandbox) -> None:
    sb.git("branch", "-C", "side", "master")


def _renamed_over(sb: Sandbox) -> None:
    sb.git("branch", "-M", "side", "master")


def _deleted_then_renamed(sb: Sandbox) -> None:
    sb.git("branch", "-D", "master")
    sb.git("branch", "-m", "side", "master")


def _committed_with_hooks_off(sb: Sandbox) -> None:
    sb.git("switch", "-q", "master")
    sb.stage({"s.py": "side\n"})
    sb.past_the_hooks("commit", "-q", "-m", "past every hook")


PAST_THE_HOOK = {"git branch -C": _copied_over, "git branch -M": _renamed_over, "git branch -D, then -m": _deleted_then_renamed,
                 "git -c core.hooksPath= commit": _committed_with_hooks_off}


@pytest.mark.parametrize("how", PAST_THE_HOOK)
def test_a_move_no_hook_saw_is_judged_at_the_next_move_and_before_a_push(sb: Sandbox, how: str) -> None:
    """git writes a copied or renamed branch without a ref transaction, and a call can switch hooks off: the trunk then holds
    s.py unreviewed. The next move the hook sees is refused, whatever it brings, until the unseen one has its record."""
    origin = sb.with_origin()
    sb.git("switch", "-q", "--detach")
    journal = len(sb.decisions())
    PAST_THE_HOOK[how](sb)
    assert "s.py" in reviewed_code_on_the_trunk(sb), "the scenario did not move the trunk"
    assert not [d for d in sb.decisions()[journal:] if not d["allowed"]], "git reports this move now: the gate saw it"
    sb.git("switch", "-q", "master")
    for blocked in (("merge", "-q", "docs"), ("push", "-q", "origin", "master")):
        done = sb.try_git(*blocked)
        assert done.returncode != 0 and "without this hook" in done.stderr and UNREVIEWED in done.stderr
    assert sb.tool("check").returncode == 1
    sb.try_git("merge", "--abort")                    # the refused merge is still open; putting things back must not be refused
    sb.git("reset", "-q", "--hard", "HEAD")
    status = sb.tool("status", "--unseen").stdout
    assert "[code] s.py" in status and "REFUSED" in status
    sb.record("--unseen")
    sb.git("merge", "-q", "docs")
    sb.git("push", "-q", "origin", "master")
    assert sb.git("rev-parse", MASTER, cwd=origin).stdout.strip() == sb.rev()
    assert "nothing moved it unseen" in sb.tool("status", "--unseen").stdout


def test_an_unseen_move_can_be_undone_to_where_the_gate_left_the_trunk(sb: Sandbox) -> None:
    """Refusing every move after an unseen one would also refuse its undo (16 Nov 2026, the second review)."""
    left_at = sb.rev()
    sb.git("switch", "-q", "--detach")
    sb.git("branch", "-C", "side", "master")
    since = len(sb.decisions())
    sb.git("update-ref", MASTER, left_at)
    assert "the journal lists" in sb.judged_landing(since)["reason"]
    assert "nothing moved it unseen" in sb.tool("status", "--unseen").stdout


def test_a_move_back_does_not_launder_an_unseen_move(sb: Sandbox) -> None:
    """Back to the known commit and forward again: the journal must not come to list the unseen commit as one the trunk
    held (16 Nov 2026, the third review: the back-move's line had it as trunk_before, and that counted)."""
    known, unseen = sb.rev(), sb.rev("side")
    sb.git("switch", "-q", "--detach")
    for _ in range(2):                                # back and forth, twice
        sb.past_the_hooks("update-ref", MASTER, unseen)
        since = len(sb.decisions())
        sb.git("update-ref", MASTER, known)
        line = sb.judged_landing(since)
        assert (line["trunk_before"], line["held"]) == (known, True)
        done = sb.try_git("update-ref", MASTER, unseen)
        assert done.returncode != 0 and UNREVIEWED in done.stderr
    assert unseen not in json.dumps([(d.get("trunk_before"), d.get("trunk_after")) for d in sb.decisions()])
    sb.git("switch", "-q", "master")
    sb.commit({"TASKS.md": "a row\n"}, "the trunk is where the gate left it, and free for the board")


def test_what_log_only_let_land_is_not_a_commit_the_trunk_held(logging_sb: Sandbox) -> None:
    """Under log_only a would-be-refused move lands, and a board-only commit on top of an unseen move passes: neither makes
    a commit the trunk may freely return to once the gate refuses."""
    sb, known = logging_sb, logging_sb.rev()
    sb.git("merge", "-q", "side")
    landed = sb.decisions()[-1]
    assert (landed["trunk_after"], landed["allowed"], landed["held"]) == (sb.rev(), False, False)
    sb.git("reset", "-q", "--hard", known)
    sb.git("switch", "-q", "--detach")
    sb.git("branch", "-C", "side", "master")
    sb.git("switch", "-q", "master")
    sb.commit({"TASKS.md": "a row\n"}, "board, on top of the unseen move")
    on_top = sb.decisions()[-1]
    assert (on_top["trunk_before"], on_top["trunk_after"], on_top["allowed"], on_top["held"]) == (known, sb.rev(), True, False)


@pytest.mark.parametrize("swap", [{"never_reviewed": ["**"]}, {"log_only": True}])
def test_an_unseen_move_is_not_judged_by_the_configuration_it_brought(sb: Sandbox, swap: dict) -> None:
    """A commit that reviews nothing, or only logs, put on the trunk with the hooks off, used to make the next commits pass."""
    sb.git("switch", "-q", "-c", "evil")
    sb.configure(**swap)
    sb.stage({"e.py": "evil\n", "tools/review_gate.json": (sb.repo / "tools" / "review_gate.json").read_text(encoding="utf-8")})
    sb.git("commit", "-q", "-m", "code, and a configuration that waves it through")
    sb.git("switch", "-q", "--detach")
    sb.past_the_hooks("update-ref", MASTER, "evil")
    sb.git("switch", "-q", "master")
    for files in ({"TASKS.md": "a row\n"}, {"a.py": "three\n"}):
        sb.stage(files)
        done = sb.try_git("commit", "-q", "-m", "after the swap")
        assert done.returncode != 0 and "without this hook" in done.stderr and "log only" not in done.stderr
    status = sb.tool("status", "--unseen").stdout
    assert "[code] e.py" in status and "[tooling config] tools/review_gate.json" in status and "the hook refuses" in status


def test_an_unseen_move_of_unreviewed_paths_is_logged_and_passes(sb: Sandbox) -> None:
    sb.git("switch", "-q", "--detach")
    sb.git("branch", "-C", "docs", "master")
    sb.git("switch", "-q", "master")
    sb.commit({"TASKS.md": "one more row\n"}, "docs")
    assert "without this hook" in sb.decisions()[-2]["reason"] and sb.decisions()[-2]["allowed"]


def test_log_only_logs_an_unseen_move_and_goes_on(logging_sb: Sandbox) -> None:
    sb = logging_sb
    sb.git("switch", "-q", "--detach")
    sb.git("branch", "-C", "side", "master")
    sb.git("switch", "-q", "master")
    done = sb.try_git("merge", "-q", "docs")
    assert done.returncode == 0 and "without this hook" in done.stderr and "log only" in done.stderr
    assert sb.decisions()[-1]["trunk_after"] == sb.rev()
    assert "nothing moved it unseen" in sb.tool("status", "--unseen").stdout


def test_install_starts_the_journal_once_from_the_trunk_as_it_is(sb: Sandbox) -> None:
    first = sb.decisions()
    assert len(first) == 1 and first[0]["hook"] == "install" and first[0]["trunk_after"] == sb.rev()
    assert first[0]["trunk"] == MASTER
    sb.installer("install")
    assert sb.decisions() == first


# ---------------------------------------------------------------- a remote's trunk

def test_a_push_to_a_remotes_trunk_is_refused_before_it_leaves(sb: Sandbox) -> None:
    origin = sb.with_origin()
    done = sb.try_git("push", "-q", "origin", "side:master")
    assert done.returncode != 0 and UNREVIEWED in done.stderr
    assert sb.git("rev-parse", MASTER, cwd=origin).stdout.strip() == sb.rev()


def test_an_ours_merge_does_not_open_the_remote_trunk_to_the_absorbed_branch(sb: Sandbox) -> None:
    origin = sb.with_origin()
    before = sb.rev()
    sb.git("merge", "-q", "-s", "ours", "-m", "ours", "side")
    done = sb.try_git("push", "-q", "origin", "side:master")
    assert done.returncode != 0 and UNREVIEWED in done.stderr
    assert sb.git("rev-parse", MASTER, cwd=origin).stdout.strip() == before


def test_a_push_of_the_local_trunk_needs_no_second_review(sb: Sandbox) -> None:
    """What is on the local trunk passed the gate there; pushing several landings at once has no key of its own."""
    origin = sb.with_origin()
    for text in ("two\n", "three\n"):
        sb.stage({"a.py": text})
        sb.record("--staged")
        sb.git("commit", "-q", "-m", text.strip())
    since = len(sb.decisions())
    sb.git("push", "-q", "origin", "master")
    assert sb.git("rev-parse", MASTER, cwd=origin).stdout.strip() == sb.rev()
    assert [d["hook"] for d in sb.decisions()[since:]] == ["pre-push"], "the push was not judged"


def test_a_push_onto_a_remote_trunk_we_do_not_have_is_refused(sb: Sandbox) -> None:
    origin = sb.with_origin()
    sb.commit_elsewhere(origin, {"e.py": "elsewhere\n"})
    done = sb.try_git("push", "-q", "--force", "origin", "side:master")
    assert done.returncode != 0 and "Fetch first" in done.stderr


def test_the_stated_limit_push_no_verify_runs_no_hook(sb: Sandbox) -> None:
    """Not a promise but the module's stated limit: git skips pre-push on this flag, and the guard refuses the flag instead
    (tests/test_hooks_guard.py). When this test fails, git has started to run the hook and the limit can go."""
    sb.with_origin()
    assert sb.try_git("push", "-q", "--no-verify", "origin", "side:master").returncode == 0


# ---------------------------------------------------------------- what is never refused

def test_work_off_the_trunk_is_free(sb: Sandbox) -> None:
    sb.git("switch", "-q", "side")
    sb.commit({"s.py": "more\n"}, "on the branch")
    sb.git("merge", "-q", "master")                   # keeping a branch current is not a landing
    sb.git("branch", "another")
    sb.git("tag", "v1")
    sb.git("branch", "-D", "another")
    assert sb.installer("check").returncode == 0, "the hooks were not there to let this pass"
    assert [d["hook"] for d in sb.decisions()] == ["install"], "a ref that is not the trunk reached the gate"


def test_a_landing_of_unreviewed_paths_needs_no_record(sb: Sandbox) -> None:
    sb.commit({"TASKS.md": "a row\n", "GoalGathering/notes/ledger.md": "entry\n", "modules/05/out/result.json": "{}\n",
               "plans/05_delta-probed-ir-pipeline/probes/results_m1/run/copy.py": "x\n",
               "plans/05_delta-probed-ir-pipeline/probes/runspecs/a_run.json": "{}\n"},
              "the board, the ledger, an output, a fetched script, a run spec")
    assert "no reviewed path changes" in sb.judged_landing(1)["reason"]
    sb.git("merge", "-q", "--no-ff", "-m", "docs", "-X", "ours", "docs")
    assert "no reviewed path changes" in sb.judged_landing(2)["reason"]
    assert not sb.state(R.RECORDS).exists()


def test_the_trunk_moves_back_to_a_commit_the_journal_lists(sb: Sandbox) -> None:
    sb.git("merge", "-q", "docs")
    sb.git("reset", "-q", "--hard", "HEAD~1")
    assert "the journal lists" in sb.judged_landing(2)["reason"]


def test_a_move_back_to_an_ancestor_the_journal_does_not_list_is_a_landing(tmp_path: Path) -> None:
    """The gate starts at install; an older commit is not one it saw the trunk at, and what going there changes is judged."""
    sb = Sandbox(tmp_path, install=False)
    sb.commit({"a.py": "two\n"}, "before the gate was installed")
    sb.installer("install", check=True)
    done = sb.try_git("reset", "-q", "--hard", "HEAD~1")
    assert done.returncode != 0 and UNREVIEWED in done.stderr


def test_a_rebase_can_always_be_abandoned(sb: Sandbox) -> None:
    sb.commit({"TASKS.md": "the trunk's own row\n"}, "conflicts with docs")
    before = sb.rev()
    assert sb.try_git("rebase", "-q", "docs").returncode != 0, "the rebase was meant to stop on a conflict"
    sb.git("rebase", "--abort")
    assert sb.rev() == before and sb.git("symbolic-ref", "HEAD").stdout.strip() == MASTER


def test_a_refused_rebase_leaves_the_trunk_and_a_way_back(sb: Sandbox) -> None:
    sb.git("merge", "-q", "docs")
    before = sb.rev()
    assert sb.try_git("rebase", "-q", "side").returncode != 0
    assert sb.rev() == before
    sb.try_git("rebase", "--abort")                   # there may be no rebase left to abort; either way the next line must hold
    sb.git("switch", "-q", "master")
    assert sb.rev("HEAD") == before


def test_a_refused_fast_forward_is_put_back_without_losing_uncommitted_work(sb: Sandbox) -> None:
    """git builds the fast-forward before the ref moves. `git reset --hard HEAD` would put the tree back and take the user's
    uncommitted edits with it (16 Nov 2026: the real checkout had five such files); the message names the command that
    keeps them."""
    (sb.repo / "a.py").write_text("one\nand an edit nobody committed\n", encoding="utf-8")
    done = sb.try_git("merge", "-q", "side")
    advised = f"git read-tree -m -u {sb.rev('side')} HEAD"
    assert done.returncode != 0 and advised in done.stderr
    assert (sb.repo / "s.py").exists(), "git no longer builds the fast-forward before the ref moves: the advice can go"
    sb.git(*advised.split()[1:])
    assert not (sb.repo / "s.py").exists()
    assert sb.git("status", "--porcelain").stdout.split() == ["M", "a.py"]
    assert (sb.repo / "a.py").read_text(encoding="utf-8") == "one\nand an edit nobody committed\n"
    sb.record("--merge", "side")
    sb.git("merge", "-q", "side")


def test_a_refused_commit_is_not_told_to_put_anything_back_blindly(sb: Sandbox) -> None:
    done = _commit(sb)
    assert "Not after a refused commit" in done.stderr
    assert sb.git("diff", "--cached", "--name-only").stdout.split() == ["a.py"], "the staged work is gone"


def test_another_repository_is_not_judged_on_this_ones_records(tmp_path: Path) -> None:
    """Two repositories with the same code: a review recorded in one is no review in the other, and a repository without the
    hooks is not judged at all."""
    one, two, bare = Sandbox(tmp_path / "one"), Sandbox(tmp_path / "two"), Sandbox(tmp_path / "three", install=False)
    one.stage({"a.py": "two\n"})
    one.record("--staged")
    one.git("commit", "-q", "-m", "reviewed here")
    assert UNREVIEWED in _commit(two).stderr
    assert _commit(bare).returncode == 0 and not bare.decisions()


def test_these_tests_would_fail_without_the_hook(sb: Sandbox) -> None:
    """The tests of landings that pass ask the journal for the judged move; here the hooks are gone and that check fails."""
    sb.installer("uninstall", check=True)
    sb.record("--merge", "side")
    sb.git("merge", "-q", "side")
    with pytest.raises(AssertionError, match="no hook judged it"):
        sb.judged_landing(1)


# ---------------------------------------------------------------- the reviewer's flow, end to end

def test_status_record_land_for_a_commit(sb: Sandbox) -> None:
    sb.stage({"a.py": "two\n", "TASKS.md": "a row\n"})
    status = sb.tool("status").stdout
    assert "[code] a.py" in status and "TASKS.md" not in status and "REFUSED" in status
    key = next(line.split()[1] for line in status.splitlines() if line.strip().startswith("key"))
    assert sb.tool("check").returncode == 1
    sb.tool("record", "--key", key, "--reviewer", "agent-7", "--findings", "3", "--verdict", "two fixed, one noted",
            "--note", "a note")
    assert sb.tool("check").returncode == 0 and "agent-7" in sb.tool("status").stdout
    sb.git("commit", "-q", "-m", "reviewed")
    entry = json.loads(sb.state(R.RECORDS).read_text(encoding="utf-8").splitlines()[-1])
    assert (entry["key"], entry["findings"], entry["note"], entry["paths"]) == (key, 3, "a note", ["a.py"])
    judged = sb.judged_landing(1)
    assert judged["key"] == key and "agent-7" in judged["reason"]


@pytest.mark.parametrize("selector, land", [
    (("--merge", "side"), ("merge", "-q", "side")),
    (("--merge", "side"), ("merge", "-q", "--no-ff", "-m", "home", "side")),
    (("--tip", "side"), ("reset", "-q", "--hard", "side")),
    (("--tip", "side"), ("update-ref", MASTER, "side")),
])
def test_a_recorded_branch_lands_by_merge_or_by_pointing(sb: Sandbox, selector: tuple[str, ...], land: tuple[str, ...]) -> None:
    sb.record(*selector)
    sb.git(*land)
    assert reviewed_code_on_the_trunk(sb) == {"a.py", "s.py"}
    assert "reviewed by agent-7" in sb.judged_landing(1)["reason"]


def test_a_true_merge_is_keyed_by_the_tree_it_will_make(sb: Sandbox) -> None:
    sb.git("merge", "-q", "docs")
    assert "a merge of side" in sb.tool("status", "--merge", "side").stdout
    sb.record("--merge", "side")
    sb.git("merge", "-q", "-m", "merge", "side")
    assert "reviewed by agent-7" in sb.judged_landing(2)["reason"]


def test_a_pull_of_work_made_elsewhere_lands_after_its_review(sb: Sandbox) -> None:
    sb.commit_elsewhere(sb.with_origin(), {"e.py": "elsewhere\n"})
    refused = sb.try_git("pull", "-q", "origin", "master")
    assert refused.returncode != 0
    sb.git("read-tree", "-m", "-u", sb.rev("origin/master"), "HEAD")
    sb.record("--merge", "origin/master")
    sb.git("pull", "-q", "origin", "master")
    assert (sb.repo / "e.py").exists() and "reviewed by agent-7" in sb.judged_landing(2)["reason"]


def test_the_command_line_works_from_a_linked_worktrees_own_copy(sb: Sandbox) -> None:
    """CLAUDE.md tells a session to run `python tools/review_gate.py status ...`, and sessions work in worktrees."""
    linked = sb.root / "linked"
    sb.git("worktree", "add", "-q", str(linked), "side")
    done = sb.run([sys.executable, str(linked / "tools" / "review_gate.py"), "status", "--merge", "side"], cwd=linked)
    assert done.returncode == 0 and "[code] s.py" in done.stdout, done.stderr
    assert done.stdout == sb.tool("status", "--merge", "side").stdout
    assert sb.run([sys.executable, str(linked / "tools" / "review_gate.py"), "record", "--merge", "side", "--reviewer", "w",
                   "--findings", "0", "--verdict", "clean"], cwd=linked).returncode == 0
    sb.git("merge", "-q", "side")                     # the record made in the worktree is the main checkout's too
    assert "reviewed by w" in sb.judged_landing(1)["reason"]


def test_a_merge_that_conflicts_has_no_key_until_it_is_resolved(sb: Sandbox) -> None:
    sb.commit({"TASKS.md": "the trunk's own row\n"}, "conflicts with docs")
    done = sb.tool("status", "--merge", "docs")
    assert done.returncode == 1 and "without conflicts" in done.stderr


def test_a_commit_off_the_trunk_is_said_to_land_nothing(sb: Sandbox) -> None:
    sb.git("switch", "-q", "side")
    sb.stage({"s.py": "more\n"})
    done = sb.tool("check")
    assert done.returncode == 0 and "lands nothing" in done.stdout


def test_the_tool_reads_the_whole_tree_from_a_subdirectory(sb: Sandbox) -> None:
    sb.stage({"a.py": "two\n", "deep/b.py": "b\n"})
    here, below = sb.tool("status").stdout, sb.tool("status", cwd=sb.repo / "deep").stdout
    assert here == below and "[code] a.py" in below and "[code] deep/b.py" in below


def test_record_refuses_what_is_not_a_review(sb: Sandbox) -> None:
    sb.stage({"a.py": "two\n"})
    base = ("record", "--reviewer", "agent-7", "--verdict", "clean")
    assert "never negative" in sb.tool(*base, "--findings", "-1").stderr
    assert "names its reviewer" in sb.tool("record", "--reviewer", " ", "--verdict", "clean", "--findings", "0").stderr
    assert "is not the key" in sb.tool(*base, "--findings", "0", "--key", "0" * 20 + ".." + "1" * 20).stderr
    sb.git("reset", "-q")
    sb.stage({"TASKS.md": "a row\n"})
    assert "nothing to record" in sb.tool(*base, "--findings", "0").stderr
    assert not sb.state(R.RECORDS).exists()


def test_export_adds_each_record_to_the_tracked_log_once(sb: Sandbox) -> None:
    log = sb.root / "reviews.jsonl"
    sb.record("--merge", "side")
    assert "1 record(s) added" in sb.tool("export", "--to", str(log)).stdout
    assert "0 record(s) added" in sb.tool("export", "--to", str(log)).stdout
    assert log.read_text(encoding="utf-8") == sb.state(R.RECORDS).read_text(encoding="utf-8")


def test_parallel_records_all_arrive(sb: Sandbox) -> None:
    """Eight `record` calls at once left six lines and a PermissionError when the file was rewritten (16 Nov 2026)."""
    argv = [sys.executable, str(sb.repo / "tools" / "review_gate.py"), "record", "--merge", "side", "--findings", "0",
            "--verdict", "clean", "--reviewer"]
    running = [subprocess.Popen([*argv, f"agent-{n}"], cwd=sb.repo, env=sb.env, stdout=subprocess.DEVNULL,
                                stderr=subprocess.PIPE, text=True) for n in range(8)]
    errors = [p.communicate(timeout=120)[1] for p in running]
    assert [p.returncode for p in running] == [0] * 8, errors
    lines = [json.loads(line) for line in sb.state(R.RECORDS).read_text(encoding="utf-8").splitlines()]
    assert sorted(entry["reviewer"] for entry in lines) == [f"agent-{n}" for n in range(8)]
    assert not sb.state(R.RECORDS + ".lock").exists()


def test_a_lock_left_by_a_dead_process_is_broken_and_logged(sb: Sandbox) -> None:
    """A leftover lock cost eleven seconds and then refused every move of the trunk (16 Nov 2026, the third review)."""
    lock = sb.state(R.DECISIONS + ".lock")
    lock.write_text("pid 1 since long ago\n", encoding="utf-8")
    long_ago = time.time() - R.LOCK_STALE_S - 5
    os.utime(lock, (long_ago, long_ago))
    started = time.monotonic()
    done = sb.try_git("merge", "-q", "docs")
    assert done.returncode == 0 and "broke decisions.log.lock" in done.stderr and time.monotonic() - started < R.LOCK_WAIT_S
    assert sb.judged_landing(1)["allowed"] and "pid 1 since long ago" in sb.state("locks.log").read_text(encoding="utf-8")


def test_a_lock_nobody_releases_is_named_instead_of_waited_for(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(R, "LOCK_WAIT_S", 0.1)
    (tmp_path / "records.jsonl.lock").write_text("", encoding="utf-8")
    with pytest.raises(R.GateError, match=r"records\.jsonl\.lock has been held"):
        R._append_line(tmp_path / "records.jsonl", "{}")


# ---------------------------------------------------------------- the key

def test_the_key_is_reproducible_and_blind_to_unreviewed_paths(sb: Sandbox) -> None:
    def key() -> str:
        return next(line.split()[1] for line in sb.tool("status").stdout.splitlines() if line.strip().startswith("key"))

    sb.stage({"a.py": "two\n"})
    first = key()
    assert key() == first
    sb.stage({"TASKS.md": "a row beside the code\n"})
    assert key() == first, "a task-board row staged beside reviewed code made its review stale"
    sb.stage({"a.py": "three\n"})
    assert key() != first


def test_a_review_survives_an_unreviewed_landing_in_between(sb: Sandbox) -> None:
    sb.record("--merge", "side")
    sb.git("merge", "-q", "docs")                     # the trunk's sha changes, its code does not
    sb.git("merge", "-q", "-m", "home", "side")
    assert "reviewed by agent-7" in sb.judged_landing(2)["reason"]


def test_a_record_cannot_be_replayed_onto_other_code(sb: Sandbox) -> None:
    """The key names the code before as well as after: the same change on a trunk whose code has moved on is another landing."""
    sb.record("--merge", "side")
    sb.stage({"a.py": "two\n"})
    sb.record("--staged")
    sb.git("commit", "-q", "-m", "the trunk's code moves on")
    done = sb.try_git("merge", "-q", "-m", "home", "side")
    assert done.returncode != 0 and UNREVIEWED in done.stderr


def test_changed_code_needs_its_own_review(sb: Sandbox) -> None:
    sb.stage({"a.py": "two\n"})
    sb.record("--staged")
    sb.stage({"a.py": "two, and a line nobody read\n"})
    assert UNREVIEWED in sb.try_git("commit", "-q", "-m", "x").stderr


def test_the_code_id_is_of_paths_modes_and_blobs() -> None:
    one = R.code_id({"a.py": "100644 blob 1111", "b.py": "100644 blob 2222"})
    assert one == R.code_id({"b.py": "100644 blob 2222", "a.py": "100644 blob 1111"}) and len(one) == R.ID_LENGTH
    assert one != R.code_id({"a.py": "100755 blob 1111", "b.py": "100644 blob 2222"})
    assert one != R.code_id({"a.py": "100644 blob 1111", "c.py": "100644 blob 2222"})


# ---------------------------------------------------------------- the configuration the hook reads is the trunk's

def test_an_uncommitted_edit_of_the_configuration_changes_nothing(sb: Sandbox) -> None:
    """The hook used to read the working tree's file, and `never_reviewed: ["**"]` there let code pass (16 Nov 2026)."""
    sb.configure(never_reviewed=["**"], log_only=True)
    done = _commit(sb)
    assert done.returncode != 0 and UNREVIEWED in done.stderr


def test_a_change_of_the_configuration_is_itself_a_reviewed_landing(sb: Sandbox) -> None:
    sb.configure(log_only=True)
    sb.git("add", "-f", "tools/review_gate.json")
    assert "[tooling config] tools/review_gate.json" in sb.tool("status").stdout
    assert UNREVIEWED in sb.try_git("commit", "-q", "-m", "switch the gate to logging").stderr
    sb.record("--staged")
    sb.git("commit", "-q", "-m", "switch the gate to logging")      # judged by the configuration before it: refusing
    done = _commit(sb)                                              # and from here on by the one that landed
    assert done.returncode == 0 and "log only" in done.stderr


def test_a_trunk_without_a_configuration_is_judged_by_the_file_and_not_installed_on(tmp_path: Path) -> None:
    sb = Sandbox(tmp_path, install=False)
    sb.git("rm", "-q", "--cached", "tools/review_gate.json")
    sb.git("commit", "-q", "-m", "the trunk before the gate landed on it")
    done = sb.installer("install")
    assert done.returncode == 1 and "land the gate on the trunk first" in done.stderr
    assert not sb.hook_file("reference-transaction").exists()
    assert "[code] s.py" in sb.tool("status", "--tip", "side").stdout


def test_another_trunk_is_a_matter_of_the_configuration(tmp_path: Path) -> None:
    sb = Sandbox(tmp_path, install=False)
    sb.git("branch", "-m", "master", "main")
    sb.configure(trunk="refs/heads/main")
    sb.git("commit", "-q", "-m", "the trunk is main", "tools/review_gate.json")
    sb.installer("install", check=True)
    sb.stage({"a.py": "two\n"})
    assert UNREVIEWED in sb.try_git("commit", "-q", "-m", "x").stderr
    sb.git("switch", "-q", "-c", "master")            # a branch that merely carries the old name is no trunk
    sb.git("commit", "-q", "-m", "free")


# ---------------------------------------------------------------- failing closed, and the way out

def test_a_malformed_record_refuses_reviewed_landings_until_repaired(sb: Sandbox) -> None:
    sb.record("--merge", "side")
    records = sb.state(R.RECORDS)
    records.write_text("<<<<<<< HEAD\n" + records.read_text(encoding="utf-8") + '["a list"]\n{"key": "no reviewer"}\n',
                       encoding="utf-8")
    done = sb.try_git("merge", "-q", "side")
    assert done.returncode != 0 and "records.jsonl: line 1 is not what this file holds" in done.stderr
    assert "review_gate.py repair" in done.stderr
    sb.git("read-tree", "-m", "-u", sb.rev("side"), "HEAD")
    sb.git("merge", "-q", "docs")                     # a landing of unreviewed paths never opens the records
    assert "line 1 is not what this file holds" in sb.tool("record", "--merge", "side", "--reviewer", "x", "--findings",
                                                           "0", "--verdict", "y").stderr
    assert "records.jsonl: 1 line(s) kept, 3 malformed" in sb.tool("repair").stdout
    assert len(sb.state(R.REJECTED[R.RECORDS]).read_text(encoding="utf-8").splitlines()) == 3
    sb.git("merge", "-q", "-m", "home", "side")
    assert "records.jsonl: 1 line(s) kept, 0 malformed" in sb.tool("repair").stdout


@pytest.mark.parametrize("bad_line", ['{"time": "cut off in the midd', '{"trunk": "refs/heads/master", "hook": "x"}',
                                      '{"trunk": "refs/heads/master", "trunk_before": 1, "trunk_after": null}'])
def test_a_malformed_journal_line_refuses_trunk_moves_until_repaired(sb: Sandbox, bad_line: str) -> None:
    with sb.state(R.DECISIONS).open("a", encoding="utf-8") as fh:
        fh.write(bad_line + "\n")
    done = sb.try_git("merge", "-q", "docs")
    assert done.returncode != 0 and "decisions.log: line 2 is not what this file holds" in done.stderr
    assert "review_gate.py repair" in done.stderr
    sb.git("read-tree", "-m", "-u", sb.rev("docs"), "HEAD")           # works with the journal still broken: no ref moves
    assert "decisions.log: 1 line(s) kept, 1 malformed" in sb.tool("repair").stdout
    assert sb.state(R.REJECTED[R.DECISIONS]).read_text(encoding="utf-8") == bad_line + "\n"
    sb.git("merge", "-q", "docs")
    assert sb.judged_landing(1)["allowed"]


def _gate_file_missing(sb: Sandbox) -> None:
    (sb.repo / "tools" / "review_gate.py").unlink()


def _gate_file_does_not_compile(sb: Sandbox) -> None:
    (sb.repo / "tools" / "review_gate.py").write_text("def broken(:\n", encoding="utf-8")


def _python_not_there(sb: Sandbox) -> None:
    """What git run from WSL finds under a `C:/` path: no such interpreter."""
    hook = sb.hook_file("reference-transaction")
    text = hook.read_text(encoding="utf-8").replace(Path(sys.executable).as_posix(), "/nowhere/python")
    hook.write_text(text, encoding="utf-8", newline="\n")


def _configuration_on_the_trunk_unreadable(sb: Sandbox) -> None:
    """Landed with a record, the one way it can arrive: past the hooks it would be an unseen move, judged by the
    configuration before it."""
    sb.git("switch", "-q", "-c", "broken")
    sb.commit({"tools/review_gate.json": "{not json"}, "a broken configuration")
    sb.git("switch", "-q", "master")
    sb.record("--merge", "broken")
    sb.git("merge", "-q", "broken")


BROKEN = {"review_gate.py missing": _gate_file_missing, "review_gate.py does not compile": _gate_file_does_not_compile,
          "the shim's python missing": _python_not_there}


@pytest.mark.parametrize("how", [*BROKEN, "the trunk's configuration unreadable"])
def test_a_broken_installation_refuses_trunk_moves_only_with_the_repair_in_one_line(sb: Sandbox, how: str) -> None:
    {**BROKEN, "the trunk's configuration unreadable": _configuration_on_the_trunk_unreadable}[how](sb)
    done = sb.try_git("merge", "-q", "docs")
    assert done.returncode != 0
    ours = [line for line in done.stderr.splitlines() if line.startswith("review gate: this move of")]
    assert len(ours) == 1
    if how.startswith("the trunk"):                   # the gate ran and said why; `install` would mend nothing there
        assert "reason it gave above" in ours[0] and "install" not in ours[0]
        assert "cannot be read" in done.stderr and "install_git_hooks.py uninstall" in done.stderr
    else:
        assert "install_git_hooks.py install" in ours[0] and "uninstall" in ours[0]
    if how.startswith("the trunk"):
        sb.git("merge", "--abort")                    # that case left a true merge open; undoing it moves no ref and passes
    sb.git("switch", "-q", "side")                    # everything that is not the trunk still works
    sb.git("commit", "-q", "--allow-empty", "-m", "on the branch")
    sb.git("tag", "v1")
    sb.git("update-ref", "refs/heads/another", "HEAD")


@pytest.mark.parametrize("how", BROKEN)
def test_log_only_refuses_nothing_even_with_a_broken_installation(logging_sb: Sandbox, how: str) -> None:
    """The shim reads the one switch from the trunk's configuration itself when the gate cannot run."""
    BROKEN[how](logging_sb)
    done = logging_sb.try_git("merge", "-q", "side")
    assert done.returncode == 0 and "log only" in done.stderr and "could not run" in done.stderr
    assert logging_sb.rev() == logging_sb.rev("side")


def test_uninstall_is_the_way_out_whatever_is_broken(sb: Sandbox) -> None:
    """An unreadable configuration on the trunk refuses every move of it, the one that would mend it included."""
    _configuration_on_the_trunk_unreadable(sb)
    assert sb.try_git("merge", "-q", "docs").returncode != 0
    assert sb.installer("uninstall").stdout.count(": removed") == len(hooks.HOOKS)
    sb.git("merge", "--abort")
    sb.git("merge", "-q", "docs")


class _Crashing(R.Gate):
    def on_reference_transaction(self, state: str, updates: str) -> list[R.Verdict]:
        raise RuntimeError("boom")


@pytest.mark.parametrize("log_only, code", [(False, R.REFUSED), (True, 0)])
def test_a_crash_refuses_the_move_unless_log_only(capsys: pytest.CaptureFixture[str], log_only: bool, code: int) -> None:
    config = R.GateConfig(MASTER, log_only, {"code": ("**/*.py",)}, ())
    assert R.run_hook(_Crashing(config), "reference-transaction", "prepared", "") == code
    assert "RuntimeError: boom" in capsys.readouterr().err


def test_the_hook_without_its_state_refuses() -> None:
    config = R.GateConfig(MASTER, False, {"code": ("**/*.py",)}, ())
    assert R.run_hook(R.Gate(config), "reference-transaction", None, "") == R.REFUSED


def test_a_shim_installed_for_another_trunk_than_the_configuration_names_is_a_broken_installation(sb: Sandbox) -> None:
    done = sb.tool("hook", "reference-transaction", "--trunk", "refs/heads/side", "prepared")
    assert done.returncode == R.BROKEN and "names refs/heads/master as the trunk" in done.stderr


# ---------------------------------------------------------------- the reviewed set (decision b), on the delivered configuration

DELIVERED = R.load_config()
P5 = "plans/05_delta-probed-ir-pipeline/"
REVIEWED_PATHS = {
    "code": ["a.py", P5 + "m05/rungC_train.py", P5 + "tests/test_review_gate.py", P5 + "probes/watch.sh",
             P5 + "probes/battery_state.ps1", P5 + "tools/backup_task.cmd", P5 + "probes/t_density_kernel/ccsd_t_rdm_kernel.c",
             "plans/06_equivalent-faster-mathematics/lean/Plan06/Basic.lean", "website/site/src/lib/bands.ts",
             "website/site/astro.config.mjs", "website/site/src/pages/index.astro", "website/site/scripts/build.js",
             P5 + "tools/hooks/guard.py"],
    "notebooks": [P5 + "modules/05_support_predictor/notebook/deep_learning.ipynb"],
    "patches": [P5 + "probes/patches/pyvpt2_quartic_route_consistency_2026-09-21.patch"],
    "test data": [P5 + "tests/data/anchor_deck_rehearsal_golden.json", P5 + "tests/data/deep/er/pinned.npz"],
    "tooling config": [P5 + "pyproject.toml", "requirements.txt", P5 + "modules/02_opponent_atlas/requirements.txt",
                       P5 + "environments/wsl-qc215.txt", "plans/06_equivalent-faster-mathematics/lean/lakefile.toml",
                       ".gitattributes", ".pre-commit-config.yaml", ".github/workflows/plan05-ci.yml",
                       ".github/workflows/reusable/lint.yml", ".claude/settings.json", ".claude/settings.local.json",
                       P5 + "tools/hooks/guard_config.json", P5 + "tools/review_gate.json"],
    "agent rules": ["CLAUDE.md"],
}
NOT_REVIEWED = [
    P5 + "TASKS.md", P5 + "TASKS_closed.md", P5 + "tools/reviews.jsonl", P5 + "README.md", P5 + "docs/a_note.md",
    P5 + "GoalGathering/notes/Mandate_2026-09-13_Affordable_Plan_Obstacle_Ledger.md",
    P5 + "GoalGathering/architecture/51_deltaH_model_pytorch.py", P5 + "GoalGathering/notes/pr_patches/pyscf_scanner_check.patch",
    P5 + "probes/results_m1/apt_refine_install_2026-10-12/repro_2702.py", P5 + "probes/results_m1/chain42.log",
    P5 + "modules/05_support_predictor/out/E7_rungC_chain41_control1_eval_analytic_seed0.json",
    P5 + "modules/08_industry_synthesis/out/certificates/certificate_benzene_A_8448043181.md", P5 + "modules/05/out/made_by_a_run.py",
    P5 + "probes/runspecs/v14_stage1.json", P5 + "probes/runs/chain42.json",        # launch records: the user, 16 Nov 2026
    P5 + "tools/hosts.tsv", P5 + "environments/README.md",
    P5 + "probes/watch_state/watch_heartbeat", P5 + "data/corpus_release/set.npz", P5 + "probes/results_vpt2/benzene.json",
    P5 + "modules/05_support_predictor/CLAUDE.md", "MEMORY.md", ".gitignore", "website/site/public/LICENSE",
]


@pytest.mark.parametrize("label, path", [(label, path) for label, paths in REVIEWED_PATHS.items() for path in paths])
def test_a_reviewed_path_is_reviewed_under_its_class(label: str, path: str) -> None:
    assert DELIVERED.reviewed_class(path) == label


@pytest.mark.parametrize("path", NOT_REVIEWED)
def test_what_the_user_excluded_and_what_is_not_code_lands_freely(path: str) -> None:
    assert DELIVERED.reviewed_class(path) is None


def test_every_class_of_the_delivered_set_has_a_test_and_the_gate_is_delivered_logging() -> None:
    assert set(DELIVERED.reviewed) == set(REVIEWED_PATHS)
    assert DELIVERED.trunk == MASTER
    assert DELIVERED.log_only is True, "the user lifts log_only after the independent review, in review_gate.json"


def test_the_shim_finds_the_switch_in_the_delivered_file_as_it_is_written() -> None:
    """The shim reads `log_only` with grep when the gate cannot run; the delivered file must be written so that it can."""
    text = (TOOLS / "review_gate.json").read_text(encoding="utf-8")
    assert re.search(r'"log_only"\s*:\s*true', text) and '"log_only"[[:space:]]*:[[:space:]]*true' in hooks.shim(
        "pre-push", MASTER, "tools/review_gate.json")


# ---------------------------------------------------------------- the configuration is checked before anything is judged

GOOD = {"trunk": MASTER, "log_only": False, "reviewed": {"code": ["**/*.py"]}, "never_reviewed": []}


@pytest.mark.parametrize("change, reason", [
    ({"trunk": "master"}, "full branch ref"),
    ({"trunk": "refs/heads/$(reboot)"}, "full branch ref"),
    ({"trunk": None}, "full branch ref"),
    ({"log_only": "no"}, "true or false"),
    ({"reviewed": {}}, "at least one class"),
    ({"reviewed": {"code": []}}, "at least one class"),
    ({"reviewed": ["**/*.py"]}, "class name -> list"),
    ({"reviewed": {"code": "**/*.py"}}, "list of path patterns"),
    ({"never_reviewed": ["out\\\\x"]}, "forward slashes"),
    ({"never_reviewed": ["/abs/**"]}, "no empty part"),
    ({"never_reviewed": ["out/"]}, "no empty part"),
    ({"reviewed": {"code": ["src/**.py"]}}, "only as a whole part"),
    ({"surprise": 1}, "exactly the fields"),
])
def test_a_configuration_that_is_not_one_is_refused_with_the_reason(tmp_path: Path, change: dict, reason: str) -> None:
    path = tmp_path / "gate.json"
    path.write_text(json.dumps(GOOD | change), encoding="utf-8")
    with pytest.raises(R.GateError, match=reason):
        R.load_config(path)


@pytest.mark.parametrize("pattern, path, matches", [
    ("**/*.py", "a.py", True), ("**/*.py", "deep/er/a.py", True), ("**/*.py", "a.pyc", False), ("**/*.py", "a.py/b", False),
    ("*.py", "deep/a.py", False), ("**/out/**", "out/x.json", True), ("**/out/**", "m/out/deep/x.py", True),
    ("**/out/**", "m/output/x.py", False), ("**/out/**", "m/out", False), ("a/*/c.json", "a/b/c.json", True),
    ("a/*/c.json", "a/b/b/c.json", False), ("a/?.py", "a/b.py", True), ("a/?.py", "a/bb.py", False),
    ("a/[b].py", "a/b.py", False), ("a/b.py", "a/bxpy", False),
])
def test_a_pattern_matches_whole_paths_and_stars_stay_within_a_name(pattern: str, path: str, matches: bool) -> None:
    config = R.GateConfig(MASTER, False, {"code": (pattern,)}, ())
    assert (config.reviewed_class(path) == "code") is matches


def test_an_exclusion_wins_over_every_class() -> None:
    config = R.GateConfig(MASTER, False, {"code": ("**/*.py",)}, ("**/out/**",))
    assert config.reviewed_class("m/out/a.py") is None and config.reviewed_class("m/a.py") == "code"


def test_a_configuration_with_a_key_twice_is_refused() -> None:
    """json keeps the last value and the shim's grep finds the first: `log_only` twice would be two different switches."""
    text = '{"log_only": true, ' + json.dumps(GOOD)[1:]
    with pytest.raises(R.GateError, match="log_only is there more than once"):
        R.parse_config(text, "a file")


def test_a_missing_configuration_is_refused(tmp_path: Path) -> None:
    with pytest.raises(R.GateError, match="cannot be read"):
        R.load_config(tmp_path / "none.json")


# ---------------------------------------------------------------- the installer

def hook_files(sb: Sandbox) -> dict[str, str]:
    return {name: sb.hook_file(name).read_text(encoding="utf-8") for name in hooks.HOOKS}


def test_install_is_idempotent_and_check_says_current(sb: Sandbox) -> None:
    first = hook_files(sb)
    again = sb.installer("install")
    assert again.returncode == 0 and again.stdout.count("already current") == len(hooks.HOOKS)
    assert hook_files(sb) == first and all(hooks.MARKER in text for text in first.values())
    assert sb.installer("check").returncode == 0


def test_check_tells_missing_and_stale_from_current(sb: Sandbox) -> None:
    sb.hook_file("pre-push").unlink()
    with sb.hook_file("reference-transaction").open("a", encoding="utf-8", newline="\n") as fh:
        fh.write("# an edit by hand\n")
    done = sb.installer("check")
    assert done.returncode == 1 and "pre-push: missing" in done.stdout and "reference-transaction: stale" in done.stdout
    assert sb.installer("install").stdout.count(": installed") == len(hooks.HOOKS)
    assert sb.installer("check").returncode == 0


def test_a_foreign_hook_is_never_overwritten_and_nothing_is_half_installed(tmp_path: Path) -> None:
    sb = Sandbox(tmp_path, install=False)
    foreign = sb.hook_file("pre-push")
    foreign.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    done = sb.installer("install")
    assert done.returncode == 1 and "did not write" in done.stderr
    assert foreign.read_text(encoding="utf-8") == "#!/bin/sh\nexit 0\n"
    assert not sb.hook_file("reference-transaction").exists()
    assert "pre-push: foreign" in sb.installer("check").stdout
    assert "foreign, left alone" in sb.installer("uninstall").stdout and foreign.exists()


def test_the_pre_commit_frameworks_hook_stays_and_still_runs(tmp_path: Path) -> None:
    sb = Sandbox(tmp_path, install=False)
    theirs = sb.hook_file("pre-commit")
    text = "#!/bin/sh\n# File generated by pre-commit: https://pre-commit.com\necho ran >> .git/pre-commit-ran\n"
    theirs.write_text(text, encoding="utf-8", newline="\n")
    theirs.chmod(0o755)
    sb.installer("install", check=True)
    assert theirs.read_text(encoding="utf-8") == text
    sb.commit({"TASKS.md": "a row\n"}, "docs")
    assert (sb.repo / ".git" / "pre-commit-ran").exists() and sb.judged_landing(1)["allowed"]
    sb.installer("uninstall")
    assert theirs.read_text(encoding="utf-8") == text


def test_uninstall_removes_the_shims_and_the_trunk_is_free_again(sb: Sandbox) -> None:
    assert sb.installer("uninstall").stdout.count(": removed") == len(hooks.HOOKS)
    assert _commit(sb).returncode == 0
    assert sb.installer("check").returncode == 1


def test_install_refuses_a_trunk_the_repository_does_not_have(tmp_path: Path) -> None:
    sb = Sandbox(tmp_path, install=False)
    sb.configure(trunk="refs/heads/main")
    done = sb.installer("install")
    assert done.returncode == 1 and "does not exist" in done.stderr


def test_install_refuses_to_point_the_shared_hooks_at_a_linked_worktree(tmp_path: Path) -> None:
    sb = Sandbox(tmp_path, install=False)
    linked = sb.root / "linked"
    sb.git("worktree", "add", "-q", str(linked), "side")
    done = sb.run([sys.executable, str(linked / "tools" / "install_git_hooks.py"), "install"])
    assert done.returncode == 1 and "linked worktree" in done.stderr
    assert not sb.hook_file("reference-transaction").exists()


@pytest.mark.parametrize("hook", hooks.HOOKS)
def test_the_shim_starts_no_process_before_it_knows_the_trunk_moves(hook: str) -> None:
    """git runs the hook for every ref update of the repository: up to its early exit the shim is shell builtins only."""
    text = hooks.shim(hook, MASTER, "tools/review_gate.json")
    early, late = text.split('[ -n "$hit" ] || exit 0')
    assert """[ "$hit" = "$(git rev-parse --quiet --verify 'refs/heads/master')" ] && exit 0""" in late
    assert text.startswith("#!/bin/sh\n") and "'refs/heads/master'" in early
    assert not any(word in early for word in ("$(", "`", "cat", "grep", "sed", "git ", "python"))
    assert ('[ "$1" = prepared ] || exit 0' in early) is (hook == "reference-transaction")
    assert '[ -x "$python" ] && [ -f "$gate" ]' in late and Path(sys.executable).as_posix() in late
    assert "--trunk 'refs/heads/master' --config-path 'tools/review_gate.json'" in late
    assert hooks.GATE.as_posix() in late and f'[ "$status" = {R.REFUSED} ] && exit 1' in late
