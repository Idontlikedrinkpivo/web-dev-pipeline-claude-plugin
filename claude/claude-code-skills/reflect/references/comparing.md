# Comparing two versions of the plugin

Read before deciding that a change to the plugin made runs cheaper, faster or better. One run of each version
proves little: two runs of the same plan on the same version already differ in spend and in returns, so a single
pair can measure the noise instead of the change. The method below is the one Ponytail's authors used for their benchmark (585 sessions), cut to
what a maintainer can run.

## The method

1. **The same input.** A fixed task the change touches — a plan of a fixture project for `work`, an SRS for
   `plan`, frames for `screen-spec` — copied fresh for every run (`git worktree` or a copy of the fixture), so no
   run starts from another's leftovers.
2. **Several runs per version.** At least 3, better 5, for the base (the plugin before the change) and for the
   variant (after). Fewer than 3 and the interval below is not worth reading.
3. **Measure each run alone.** After each run:
   `python3 "${CLAUDE_SKILL_DIR}/scripts/measure.py" <run folder> --progress <its progress.md> --json <runs>/<variant>-<task>-<n>.json`.
4. **Compare by median and ratio, with an interval.**

   ```bash
   python3 "${CLAUDE_SKILL_DIR}/scripts/compare.py" --metric total --metric session --metric per_accepted_unit \
     --metric first_review_share --task <name> --base <runs>/base-<task>-*.json --variant <runs>/new-<task>-*.json
   ```

   Per task: the median of each version and their ratio; over the tasks: the geometric mean of the ratios with a
   95% interval from a bootstrap over the runs. «Лучше» / «хуже» only when the interval stays on one side of
   1.00; otherwise «разницы не видно» — run more, or accept that the change does not matter.
5. **Quality first.** A cheaper variant counts only when quality held: `first_review_share` (units accepted at the
   first review) and the task's own checks — the tests green, the review's verdict, the eval's assertions — are not
   worse. A saving bought with more returns is not a saving.

## What to report

The table and the summary `compare.py` prints, the number of runs per version and task, and what the input was.
Say what was not measured (the input tokens of a stage that reads no logs, a task with one run).
