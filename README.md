# Estimated Roster Resources and College Football Outcomes Beyond the Closing Market

Author: Joshua Batenhorst

This repository contains the analysis code, edited abstract, aggregate results and audit documentation for NIL-2025-QC-v3, dated October 1, 2026.

## Findings

The reconstruction includes 347 games and a frozen resource table covering 68 programs. Higher-resource teams won 201 of 308 resolved unequal-resource comparisons (65.3%). In the specified models, resource gap added no statistically detectable information beyond the closing spread: dyadic p=.721 for scoring margin and p=.655 for win probability. Wide confidence intervals limit interpretation. These results do not establish causation, equivalence or a validated wagering rule.

Read [the abstract](ABSTRACT.md), [primary results](results/primary.csv), and [the audit notes](AUDIT.md).

## Data availability and pending permissions

**This public release does not contain the underlying game records or resource table. It is not yet a complete publicly reproducible dataset.**

The author reports sending requests for historical resource-source confirmation and redistribution permission to the resource publisher and Covers on October 1, 2026. Permission remains pending; this repository does not claim clearance. Source data, archived source tables, row-level market lines and the full private release ZIP are withheld.

The code is available under the MIT license. That license applies only to analysis.py and verify.py. It does not grant rights to third-party data. See [DATA_AVAILABILITY.md](DATA_AVAILABILITY.md).

The repository link can be supplied with this disclosure. Sloan's acceptance of a repository with withheld inputs has not been confirmed. Creating this repository does not resolve the conference's data-availability requirement or establish that an application has been submitted.

## Running the analysis once inputs are available

Use Python 3.11 or later. Executed dependency versions are recorded in results/environment.json.

Install dependencies with:

    python -m pip install -r requirements.txt

Place the authorized private release inputs at their original paths, including data/ and the archived reference tables required by verify.py. See DATA_DICTIONARY.md and the file paths in the code. Then run:

    python analysis.py
    python verify.py

The scripts regenerate results and compare them with archived values. Without the withheld inputs, these commands cannot complete. Do not interpret missing inputs as a successful reproduction.

## Scope

This study covers estimated college football roster resources and game outcomes. It includes no personal wager ledger, astrology results or uniform research. The reconstruction and secondary analyses were not preregistered.

## Assistance and responsibility

ChatGPT assisted with coding, audits and editing. Reported independent checks use separate calculations within the verification script; they are not external peer review. The author remains responsible for the study and its submission.
