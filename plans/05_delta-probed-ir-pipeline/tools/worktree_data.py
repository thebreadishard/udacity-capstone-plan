"""Give a git worktree the main checkout's git-ignored data by hard links, show what is shared, and take the links away again.

A worktree holds no git-ignored files, so every test that reads a corpus folder, a module's out/ records, the website export or
probes/results_m1 fails there (TASKS 222). Copying 80k files costs disk and minutes; a hard link costs neither and needs no second copy
kept in step. The price is that a linked file is the main checkout's file under a second name. Any write into an existing linked path —
open for writing or appending, `Path.write_text`, `np.savez`, `torch.save` onto the same name — changes the main checkout's original. Only
a write that builds a temp file and moves it over the name (`os.replace`) breaks the link and leaves the original alone; a new file in a
linked folder is the worktree's own. So a folder that any test writes into is never linked (EXCLUDED_DIRS), and a test that writes into
a default folder is a bug in the test: its output belongs in tmp_path.

    python tools/worktree_data.py link <worktree> [--dirs DIR ...]    # DIR relative to the repository root; default DEFAULT_DIRS
    python tools/worktree_data.py status <worktree>                   # how many worktree files are links to the main checkout's
    python tools/worktree_data.py unlink <worktree>                   # removes exactly those links, never anything else

The main checkout is read from git (the worktree's common git directory), never from a path written here. Both checkouts must be on one
volume: a hard link cannot cross volumes. Every file-system call goes through os_path(), so a worktree with a long name works on Windows
where its deepest files pass MAX_PATH.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

PLAN = "plans/05_delta-probed-ir-pipeline"

DEFAULT_DIRS: tuple[tuple[str, str], ...] = (
    ("website/export/out", "the Atlas export that the website and module tests read"),
    (f"{PLAN}/modules/05_support_predictor", "the corpus molecules and out/ records and models that most regression pins read"),
    (f"{PLAN}/probes/results_m1", "probe results (CC Hessians, composite rows, anharmonic runs) that pins compare against"),
    (f"{PLAN}/modules/standout_pattern_proposer/out", "the standout scorer's checkpoints that deck_pin_runner and test_pp_embed_load read"),
    (f"{PLAN}/modules/06_generative_candidates/notebook/out", "module 06's checkpoints that test_m06_gate's load_run test reads"),
)

EXCLUDED_DIRS: tuple[tuple[str, str], ...] = (
    (f"{PLAN}/modules/08_industry_synthesis", "module 08's tests write into its out/; through a link that would write the main checkout's file"),
)

SKIPPED_PARTS = frozenset({"__pycache__", ".ruff_cache", ".pytest_cache"})   # caches are rebuilt per checkout and rewritten in place
_NAMES_A_REPOSITORY = ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE", "GIT_PREFIX")   # as review_gate.py: ask the checkout itself
GIT_TIMEOUT_S = 300
SHOWN = 20
_EXTENDED_PREFIX = "\\\\?\\"


class WorktreeDataError(RuntimeError):
    """A request the tool refuses, with the reason."""


@dataclass(frozen=True)
class Checkouts:
    """The main checkout and one of its linked worktrees, both resolved and checked by find_checkouts."""

    main: Path
    worktree: Path


@dataclass
class LinkReport:
    """What link() did: counts plus the paths a reader has to look at."""

    linked: int = 0
    already: int = 0
    skipped: int = 0
    refused: list[str] = field(default_factory=list)
    not_ignored: list[str] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return not (self.refused or self.not_ignored)


class LinkStopped(WorktreeDataError):
    """link() stopped partway; `report` holds what was done before the failure, so the caller can say it."""

    def __init__(self, reason: str, report: LinkReport) -> None:
        super().__init__(reason)
        self.report = report


def git_env() -> dict[str, str]:
    """The environment without the variables that point git at another repository (a hook or an outer git sets them)."""
    return {k: v for k, v in os.environ.items() if k not in _NAMES_A_REPOSITORY}


def _git(cwd: Path, *args: str, stdin: str | None = None, ok: tuple[int, ...] = (0,)) -> str:
    """Run git in `cwd` and return its stdout; an exit outside `ok` is raised with git's own message."""
    try:
        done = subprocess.run(["git", "-C", str(cwd), *args], input=stdin, capture_output=True, text=True, encoding="utf-8",
                              timeout=GIT_TIMEOUT_S, check=False, env=git_env())
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise WorktreeDataError(f"git {' '.join(args)} in {cwd} did not run: {exc}") from exc
    if done.returncode not in ok:
        raise WorktreeDataError(f"git {' '.join(args)} in {cwd} failed: {done.stderr.strip()}")
    return done.stdout


def _git_path(cwd: Path, flag: str) -> Path:
    return Path(_git(cwd, "rev-parse", "--path-format=absolute", flag).strip()).resolve()


def repository_of(path: Path) -> Path:
    """The common git directory of the repository that `path` lies in: one per repository, shared by all its worktrees."""
    return _git_path(path, "--git-common-dir")


def find_checkouts(worktree: Path, repository: Path) -> Checkouts:
    """Resolve `worktree` and its main checkout from git, refusing anything but a linked worktree's top level in `repository`.

    The main checkout is the parent of the common git directory. Linking into the main checkout itself would make every ignored file a
    link to itself, and a worktree of another repository would receive the wrong data, so both are refused, as is a worktree on another
    volume, where os.link cannot work.
    """
    if not worktree.is_dir():
        raise WorktreeDataError(f"{worktree} is not a directory")
    top = _git_path(worktree, "--show-toplevel")
    if not os.path.samefile(top, worktree):
        raise WorktreeDataError(f"{worktree} is inside a checkout, not its top level ({top}); give the top level")
    common = repository_of(worktree)
    if not os.path.samefile(common, repository):
        raise WorktreeDataError(f"{worktree} belongs to the repository at {common}, not to {repository}")
    if os.path.samefile(_git_path(worktree, "--git-dir"), common):
        raise WorktreeDataError(f"{worktree} is the main checkout itself; give a linked worktree (git worktree list)")
    main = common.parent
    if not (main / ".git").is_dir() or not os.path.samefile(_git_path(main, "--show-toplevel"), main):
        raise WorktreeDataError(f"the repository at {common} has no main checkout at {main} (a bare repository has no data to link)")
    if os.stat(main).st_dev != os.stat(worktree).st_dev:
        raise WorktreeDataError(f"{worktree} and {main} are on different volumes; a hard link cannot cross volumes")
    return Checkouts(main=main, worktree=top)


def validate_dirs(dirs: list[str]) -> tuple[str, ...]:
    """Normalise the requested folders to repository-relative posix paths, refusing ones outside the repository or inside an excluded folder.

    An excluded folder is refused rather than silently dropped: a caller who names it expects its files, and getting none would look like
    a missing-data failure later.
    """
    if not dirs:
        raise WorktreeDataError("no folders given")
    clean = []
    for raw in dirs:
        rel = PurePosixPath(raw.replace("\\", "/"))
        if rel.is_absolute() or ".." in rel.parts or rel.parts[:1] in ((), (".",)) or ":" in rel.parts[0]:
            raise WorktreeDataError(f"{raw!r}: give a folder relative to the repository root, inside it")
        for excluded, reason in EXCLUDED_DIRS:
            if rel.is_relative_to(excluded):
                raise WorktreeDataError(f"{raw!r} lies in {excluded}, which is never linked: {reason}")
        clean.append(rel.as_posix())
    return tuple(clean)


def is_skipped(rel: str) -> bool:
    """A cache file, or a file under an excluded folder (reachable when a requested folder contains it)."""
    path = PurePosixPath(rel)
    return bool(SKIPPED_PARTS.intersection(path.parts)) or any(path.is_relative_to(excluded) for excluded, _ in EXCLUDED_DIRS)


def ignored_files(checkout: Path, dirs: tuple[str, ...]) -> list[str]:
    """The git-ignored files under `dirs` in `checkout`, as repository-relative posix paths."""
    out = _git(checkout, "ls-files", "-z", "--others", "--ignored", "--exclude-standard", "--", *dirs)
    return [rel for rel in out.split("\0") if rel]


def ignored_here(checkout: Path, rels: list[str]) -> set[str]:
    """Which of `rels` the branch checked out in `checkout` ignores; git answers for paths that do not exist yet as well."""
    if not rels:
        return set()
    out = _git(checkout, "check-ignore", "-z", "--stdin", stdin="\0".join(rels) + "\0", ok=(0, 1))   # 1: none of them is ignored
    return {rel for rel in out.split("\0") if rel}


def os_path(path: Path | str) -> str:
    r"""Return the form of `path` that this tool hands to the OS: on Windows the extended-length form, elsewhere the path unchanged.

    Windows refuses a path past MAX_PATH (260 characters) unless it carries the \\?\ prefix or long paths are enabled machine-wide; a
    worktree with a long folder name pushes a deeply nested results file past it (WinError 3 on os.link). The prefix switches off Windows'
    own parsing, so the path behind it must be absolute with backslashes. Messages keep the plain path.
    """
    if sys.platform != "win32":
        return os.fspath(path)
    full = os.path.abspath(path)
    if full.startswith(_EXTENDED_PREFIX):
        return full
    if full.startswith("\\\\"):   # a UNC path \\server\share\... takes the \\?\UNC\ form
        return f"{_EXTENDED_PREFIX}UNC\\{full[2:]}"
    return _EXTENDED_PREFIX + full


def is_inside(top: Path | str, path: Path | str) -> bool:
    """Whether `path`, with every junction and symlink on the way resolved, lies under `top` (resolved the same way).

    A folder in the worktree that is a junction or symlink into the main checkout would make a create or remove act on the main checkout.
    Both sides go through os_path(): realpath keeps the prefix of a prefixed path, so the two compare in the same form.
    """
    real_top, real = (os.path.normcase(os.path.realpath(os_path(p))) for p in (top, path))
    try:
        return os.path.commonpath([real_top, real]) == real_top
    except ValueError:   # another drive on Windows: certainly not inside
        return False


def _same_file(a: Path | str, b: Path | str) -> bool:
    sa, sb = os.lstat(os_path(a)), os.lstat(os_path(b))
    return (sa.st_ino, sa.st_dev) == (sb.st_ino, sb.st_dev)


def _link_one(checkouts: Checkouts, rel: str) -> str:
    """Link one file and say what happened: 'linked', 'already' (an identical link), 'skipped' (no regular file) or 'refused'.

    An existing different file at the target is the worktree's own and is never overwritten. A target whose real path leaves the worktree
    is refused before anything is created.
    """
    src, dst = checkouts.main / rel, checkouts.worktree / rel
    src_os, dst_os = os_path(src), os_path(dst)
    if os.path.islink(src_os) or not os.path.isfile(src_os):
        return "skipped"
    if not is_inside(checkouts.worktree, dst):
        raise WorktreeDataError(f"{dst} resolves outside the worktree (a junction or symlink on its path); nothing created there")
    if os.path.lexists(dst_os):
        return "already" if _same_file(src_os, dst_os) else "refused"
    try:
        os.makedirs(os.path.dirname(dst_os), exist_ok=True)
        os.link(src_os, dst_os)
    except OSError as exc:
        raise WorktreeDataError(f"could not link {src} to {dst}: {exc}") from exc
    return "linked"


def _count(report: LinkReport, rel: str, outcome: str) -> None:
    if outcome == "linked":
        report.linked += 1
    elif outcome == "already":
        report.already += 1
    elif outcome == "skipped":
        report.skipped += 1
    elif outcome == "refused":
        report.refused.append(rel)
    else:
        raise WorktreeDataError(f"unknown outcome {outcome!r} for {rel}")


def link(checkouts: Checkouts, dirs: tuple[str, ...]) -> LinkReport:
    """Hard-link every ignored file under `dirs` in the main checkout into the worktree at the same relative path.

    A file the worktree's branch does not ignore is not linked: git there would offer it for a commit. A failure partway raises LinkStopped
    with the counts so far.
    """
    report = LinkReport()
    candidates = []
    for rel in ignored_files(checkouts.main, dirs):
        if is_skipped(rel):
            report.skipped += 1
        else:
            candidates.append(rel)
    # Before git sees the paths: on Linux `git check-ignore` stops at a path beyond a symlink with its own error, which would hide ours.
    for rel in candidates:
        if not is_inside(checkouts.worktree, checkouts.worktree / rel):
            raise LinkStopped(f"{checkouts.worktree / rel} resolves outside the worktree (a junction or symlink on its path); "
                              "nothing created", report)
    ignored = ignored_here(checkouts.worktree, candidates)
    for rel in candidates:
        if rel not in ignored:
            report.not_ignored.append(rel)
            continue
        try:
            _count(report, rel, _link_one(checkouts, rel))
        except WorktreeDataError as exc:
            raise LinkStopped(str(exc), report) from exc
    return report


def _is_link_to_main(checkouts: Checkouts, rel: str) -> bool:
    mine, theirs = os_path(checkouts.worktree / rel), os_path(checkouts.main / rel)
    return os.path.isfile(mine) and os.path.lexists(theirs) and _same_file(mine, theirs)


def _is_reparse(path: str) -> bool:
    return os.path.islink(path) or os.path.isjunction(path)


def shared_files(checkouts: Checkouts) -> Iterator[str]:
    """Every file in the worktree that is the main checkout's file at the same relative path (same inode on the same volume).

    Only a file that is the same file at the *same* path counts, so unlink() can never remove a file that merely shares data with some
    other file of the main checkout. Junctions and symlinked folders are not entered (Python 3.14's os.walk enters junctions), and a file
    whose real path leaves the worktree is never counted.
    """
    top = os_path(checkouts.worktree)
    for root, dirnames, filenames in os.walk(top):
        dirnames[:] = [d for d in dirnames if d != ".git" and not _is_reparse(os.path.join(root, d))]
        for name in filenames:
            path = os.path.join(root, name)
            rel = Path(os.path.relpath(path, top)).as_posix()
            if (name != ".git" and not os.path.islink(path) and is_inside(top, path) and _is_link_to_main(checkouts, rel)
                    and os.stat(path).st_nlink > 1):
                yield rel


def _group_of(rel: str) -> str:
    for folder, _ in DEFAULT_DIRS:
        if PurePosixPath(rel).is_relative_to(folder):
            return folder
    return "(other folders)"


def status(checkouts: Checkouts) -> dict[str, int]:
    """Count the shared files per default folder, so a reader sees what a write in the worktree could reach."""
    counts: dict[str, int] = {}
    for rel in shared_files(checkouts):
        group = _group_of(rel)
        counts[group] = counts.get(group, 0) + 1
    return counts


def unlink(checkouts: Checkouts) -> int:
    """Remove the worktree's names of the main checkout's files, then the folders that held only them; return how many were removed.

    Removing a hard link removes one name; the main checkout's name and the data stay.
    """
    removed = sorted(shared_files(checkouts))
    for rel in removed:
        path = checkouts.worktree / rel
        if not is_inside(checkouts.worktree, path):
            raise WorktreeDataError(f"{path} resolves outside the worktree; not removed")
        os.remove(os_path(path))
    _prune_empty_parents(checkouts.worktree, removed)
    return len(removed)


def _prune_empty_parents(top: Path, removed: list[str]) -> None:
    """Remove the folders left empty by unlink(), deepest first; git keeps no empty folders, so none of them was the branch's."""
    parents = {parent for rel in removed for parent in (top / rel).parents if parent != top and top in parent.parents}
    for folder in sorted(parents, key=lambda p: len(p.parts), reverse=True):
        folder_os = os_path(folder)
        if os.path.isdir(folder_os) and not _is_reparse(folder_os) and is_inside(top, folder_os) and _is_empty(folder_os):
            os.rmdir(folder_os)


def _is_empty(folder: str) -> bool:
    with os.scandir(folder) as entries:
        return next(entries, None) is None


def _print_link_report(report: LinkReport, checkouts: Checkouts) -> None:
    print(f"linked {report.linked}, already linked {report.already}, skipped {report.skipped} (caches, excluded folders, non-files), "
          f"refused {len(report.refused)}, not ignored on this branch {len(report.not_ignored)}")
    for label, rels in (("refused (a different file is already there, left as it is)", report.refused),
                        ("not linked: not ignored on this branch, so git would offer to commit it", report.not_ignored)):
        for rel in rels[:SHOWN]:
            print(f"  {label}: {rel}")
        if len(rels) > SHOWN:
            print(f"  ... and {len(rels) - SHOWN} more")
    if report.linked or report.already:
        print(f"note: these files ARE the main checkout's ({checkouts.main}). Any write into one (open, write_text, np.savez onto the name) "
              f"writes the original there; only a temp file moved over it (os.replace) breaks the link.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="default folders:\n" + "\n".join(f"  {d}  — {r}" for d, r in DEFAULT_DIRS)
                                     + "\nnever linked:\n" + "\n".join(f"  {d}  — {r}" for d, r in EXCLUDED_DIRS))
    sub = parser.add_subparsers(dest="command", required=True)
    p_link = sub.add_parser("link", help="hard-link the main checkout's ignored files under the folders into the worktree")
    p_link.add_argument("worktree", type=Path)
    p_link.add_argument("--dirs", nargs="+", default=[d for d, _ in DEFAULT_DIRS], help="repository-relative folders")
    for name, text in (("status", "count the worktree's files that are the main checkout's"), ("unlink", "remove exactly those links")):
        sub.add_parser(name, help=text).add_argument("worktree", type=Path)
    return parser


def _run(args: argparse.Namespace) -> int:
    dirs = validate_dirs(args.dirs) if args.command == "link" else ()
    checkouts = find_checkouts(args.worktree.resolve(), repository_of(Path(__file__).resolve().parent))
    if args.command == "link":
        try:
            report = link(checkouts, dirs)
        except LinkStopped as exc:
            _print_link_report(exc.report, checkouts)
            raise
        _print_link_report(report, checkouts)
        return 0 if report.clean else 1
    if args.command == "status":
        counts = status(checkouts)
        print(f"{sum(counts.values())} files in {checkouts.worktree} are hard links to {checkouts.main}'s files at the same path")
        for group, n in sorted(counts.items()):
            print(f"  {n:7d}  {group}")
        return 0
    print(f"removed {unlink(checkouts)} links from {checkouts.worktree}; the main checkout's files are untouched")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return _run(args)
    except WorktreeDataError as exc:
        print(f"worktree_data: refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
