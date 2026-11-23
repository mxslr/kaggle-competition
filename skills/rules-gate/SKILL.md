---
name: rules-gate
description: "Rules and FAQ compliance gate for Kaggle and other ML competitions. Builds and maintains the comp_notes/RULES.md ledger from the rules page and every host FAQ answer, decides for each technique whether it is allowed, forbidden or unclear, drafts questions for the organizers, and audits notebooks before runs and hand-in so the team is never disqualified at verification. Use it whenever the user pastes competition rules or a new FAQ batch, asks whether a model, dataset, label trick or test-time step is allowed, or before a long run or final submission, even if they only say 'ini boleh ga' or 'FAQ baru'."
---

# Rules gate

A competition result counts only if it survives the organizers' verification. This skill turns the rules and every host answer into a ledger, and it checks every idea and every notebook against that ledger before GPU time is spent.

Reply in the user's language.

## 1. Build or update the ledger

1. Read the official rules page, the competition description and every FAQ or host answer the user provides.
2. For each rule or answer, add a row to `comp_notes/RULES.md` (template: `../workflow/assets/RULES.md`, relative to this skill's folder) with source, date, the rule in one line, and the **implication for our pipeline** in one line. The implication column is the useful part. For example: "FAQ: every frame of a test sequence must be processed directly, also in feature extraction, so per-frame features must run on every frame, not on a subsample plus interpolation."
3. Update the technique decision table: allowed, forbidden or unclear, with the basis.
4. Re-read the whole ledger when a new FAQ batch arrives. Later answers can narrow earlier ones, and the current pipeline may already violate a new answer.

## 2. Decide on a technique

For any proposed idea:
1. Find the closest rows in the ledger. If a row clearly allows it, proceed.
2. If a row forbids it, drop it and say which rule.
3. If no row covers it, or the wording is ambiguous, treat it as **forbidden for now**. Then:
   - draft one short, specific question for the organizers (see `../workflow/references/technique-catalog.md`, section 7);
   - ask the user to send it;
   - if possible, propose a compliant alternative that captures most of the gain.
4. Read host answers literally and conservatively. "Test data may only be used for inference" excludes test statistics, test-fitted preprocessing, pseudo-labels, adversarial validation and LB-derived constants, even when no example names them.

`../workflow/references/technique-catalog.md` lists techniques that are banned in some competitions and allowed in others. Use it to know what to ask, never to assume permission.

## 3. Silent violations to look for

These slip in without anyone deciding to break a rule:
- **Test statistics in outputs**: printed predicted-label counts, test score histograms, test resolution or colour checks, test detection rates.
- **LB-derived constants**: thresholds, dilation or time values, label conventions or blend weights chosen because they scored better on the public LB or matched an LB probe.
- **Cross-row information at test**: sorting, grouping or batching statistics across test rows that change a row's prediction (batch norm in train mode, test-set normalisation).
- **Incomplete input use**: frame or row sampling at test when every input must be used, including inside feature extractors.
- **Hidden dependencies**: cached artifacts that a from-scratch re-run cannot rebuild, internet downloads in offline competitions, unpinned library versions that change results.
- **Text that does not match the code**: notebook markdown that describes labels, data or models differently from what the code does, or hides how labels were produced. When the FAQ asks for transparency, state the process plainly.
- **Licences**: weights or data whose licence conflicts with the prize terms.

## 4. Pre-run and pre-hand-in audit

Before a long run, and again on the exact final notebook:
1. Read the notebook source end to end against the ledger. For a second, independent pass, use the `rules-auditor` agent when the user allows subagents.
2. Report findings as `severity | file:line | what the code does | rule | smallest fix`.
3. Fix only with the user's approval, rebuild the notebook, and hand the user the new `.ipynb` with an instruction to run its debug version on Kaggle first.
4. Confirm that the from-scratch runtime fits the limit with margin, and that every input is an allowed source.

## 5. Transparency section in the notebook

When the rules or FAQ require it (and as good practice otherwise), the notebook states briefly:
- the data sources, pretrained weights and their licences;
- how training labels were produced (manual, AI-assisted, automatic) and how they were validated;
- the evaluation-label convention and the training-data basis for every chosen value;
- how thresholds and blend weights were selected (out-of-fold, never test);
- that test data is used for inference only, when that is the rule.

## 6. Keep the user safe

- Never send messages to organizers, post in forums or submit on the user's behalf without their explicit go-ahead. Draft the text and let them send it.
- If the user asks for a technique the ledger forbids, explain the rule and the risk (disqualification at verification), and offer the closest compliant option.
