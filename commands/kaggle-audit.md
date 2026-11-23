---
description: Audit a Kaggle notebook or pipeline against the competition rules, FAQ and the RULES.md ledger before a run or a final submission.
argument-hint: <notebook or source path, optional FAQ text to add to the ledger>
---

Audit target and notes:

> $ARGUMENTS

Load the `kaggle-competition:rules-gate` skill. Then:

1. Add any new FAQ or host answers to `comp_notes/RULES.md` first, each with its source and date.
2. Read the notebook or source end to end. Use the `rules-auditor` agent for a second, independent pass if the user allows subagents.
3. Report every finding with file and line, the rule it touches, the risk (disqualifying, likely, unclear) and the smallest fix. Include silent risks: values or thresholds chosen from LB or test information, test statistics printed in outputs, external data or weights without a licence or permission, runtime beyond the limit, internet use in a no-internet competition, non-deterministic outputs, and claims in the notebook text that do not match what the code does.
4. Fix only what the user approves, rebuild the notebook, and hand the user the new `.ipynb` with an instruction to run its debug version on Kaggle first.

Reply in the user's language.
