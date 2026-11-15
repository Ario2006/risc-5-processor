# How we work

Same rules as our T081 repo. Read this once before your first pull request.

## The rules

1. **Never push to `main`.** Every change goes through a pull request (PR).
2. **One task, one branch, one PR.** Pick your issue, branch for it, write `Closes #N` in the PR.
3. **Sarvesh and Husain review and merge.** You do not merge your own PR. Their own PRs are reviewed and merged by any other teammate.
4. **`make test` passes before you push.** If you touch `rtl/`, also run `make synth perf figures`
   and commit the new `results/` and `figures/`, because the report quotes them.
5. **Every number in the report comes from `results/`.** Never type a number you did not read there.
6. **Write your report section and viva notes as you go.** Every issue names the section you own.
7. **Deadline: 16 November.** Open a draft PR early; small PRs merge fast.

## First time setup

```sh
git clone https://github.com/Ario2006/risc-5-processor.git
cd risc-5-processor
uv sync
make test          # needs Icarus Verilog, see README, section Setup
```

## For each task

```sh
git switch main && git pull
git switch -c report/3-verification      # <area>/<issue>-<short-name>
# ... work ...
git status
git add report/sections/verification.tex
git commit -m "docs(report): rewrite the verification section"
git push -u origin report/3-verification
```

Open the link Git prints and fill in the PR template.
If Git reports a **conflict**, stop and ask in the group chat. Never force push.

## Names

- **Branch:** `<area>/<issue>-<short-name>`. Areas: `rtl`, `tb`, `tools`, `eval`, `report`, `slides`, `viva`, `repo`.
- **Commit and PR title:** `type(area): what changed`. Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`.

## Code

- Every new file starts with two `ABOUTME:` comment lines saying what it is (`//` in Verilog, `#` in Python and assembly, `%` in LaTeX).
- Verilog: `default_nettype none`, one module per file, combinational logic in `always @(*)`, not functions called from `assign` (report, Section V.D explains why).
- A new test program goes in `programs/tests/`; the suite picks it up and checks it on all three CPUs against the ISS automatically.
