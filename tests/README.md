# Skill Test Workspaces

Each subdirectory here is a skill-creator workspace produced during the
optimization of one skill in the plugin:

| Workspace                                       | Skill it tests                          |
|-------------------------------------------------|-----------------------------------------|
| `prd-securability-enhancement-workspace/`       | `skills/prd-securability-enhancement/`  |
| `securability-engineering-workspace/`           | `skills/securability-engineering/`      |
| `securability-engineering-review-workspace/`    | `skills/securability-engineering-review/` |

Inside each workspace:

```
evals/
  evals.json           # eval set: prompts, input files, LLM-as-judge assertions
  inputs/              # any input files referenced by an eval
skill-snapshot/        # frozen pre-optimization SKILL.md (baseline)
iteration-N/           # outputs from a single test run (executors + graders)
  eval-<id>-<slug>/
    eval_metadata.json
    with_skill/        # output produced when running against the live SKILL.md
      outputs/<artifact>.md
      timing.json
      grading.json
    old_skill/         # same, but using skill-snapshot/SKILL.md
      ...
  benchmark.json
  benchmark.md
  review.html          # static skill-creator viewer
scripts/
  aggregate.py         # workspace-local aggregator (only present in some)
```

## Running the tests

`run_tests.py` invokes the Claude Code CLI (`claude`) once per (eval, config)
pair, hands it the eval prompt plus a pointer to the appropriate SKILL.md,
and saves whatever artifact the skill is supposed to produce.

```bash
# Default: run both with_skill and old_skill across every eval, next iteration
python tests/run_tests.py tests/prd-securability-enhancement-workspace

# Live skill only, single eval, also run the LLM-as-judge grader
python tests/run_tests.py tests/securability-engineering-workspace \
    --config with_skill --eval-id 1 --grade

# Force a specific iteration directory (overwrites existing files in it)
python tests/run_tests.py tests/securability-engineering-review-workspace \
    --iteration 2 --grade
```

After a run you can summarize and view results with the same scripts the
optimization process used:

```bash
# Aggregate this iteration into benchmark.json + benchmark.md
python tests/prd-securability-enhancement-workspace/scripts/aggregate.py \
    tests/securability-engineering-workspace/iteration-2 \
    securability-engineering

# Generate the static review HTML (requires skill-creator plugin installed)
python ~/.claude/plugins/marketplaces/claude-plugins-official/plugins/skill-creator/skills/skill-creator/eval-viewer/generate_review.py \
    tests/securability-engineering-workspace/iteration-2 \
    --skill-name securability-engineering \
    --benchmark tests/securability-engineering-workspace/iteration-2/benchmark.json \
    --static tests/securability-engineering-workspace/iteration-2/review.html
```

## Requirements

- **Claude Code CLI** on PATH (`claude --version` must work).
- **Python 3.9+** with no third-party dependencies.

## Notes on the runner

- Outputs go to `iteration-<N>/`. The default `<N>` is the next unused
  number; pass `--iteration` to overwrite.
- Each workspace knows its expected output filename
  (`enhanced-prd.md` / `generated.md` / `report.md`) via `OUTPUT_FILENAMES`
  in `run_tests.py`. Add an entry there if you create a new workspace.
- The runner uses `--output-format json` and `--permission-mode acceptEdits`
  so Claude can write the artifact file without prompting.
- `--grade` runs an LLM-as-judge pass that reads each eval's `assertions`
  and writes a `grading.json` with `expectations[]` (text/passed/evidence)
  and a `summary` block compatible with the workspace aggregator.

## Interpreting `old_skill` results for `securability-engineering-review`

The eval assertions in `securability-engineering-review-workspace/` target the
**current** scoring model: FIASSE v1.1, ten attributes at equal weight
(1/10 each), a weakest-link floor on the overall score, and a 50-item
checklist. The frozen `skill-snapshot/SKILL.md` in that workspace is the
pre-optimization baseline, which used the older nine-sub-attribute / 45-item
model with 33/34/33 pillar weights.

The `old_skill` config therefore scores **badly by design** on that workspace,
and `benchmark.md` will show a large `with_skill` − `old_skill` delta. That
delta is the intended measurement: the baseline cannot satisfy assertions about
a model it predates. It is **not** a regression, and the snapshot must not be
"fixed" to make it pass — doing so destroys the baseline the comparison exists
to provide.

One assertion is a deliberate negative check: it requires the current principle
name (Isolated Integrity) and names the retired one (Derived Integrity) as a
term that must not appear. Expect the baseline to fail that one in particular.
