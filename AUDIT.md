# QC v3 audit notes

## Documented corrections

The original reconstruction is preserved privately. QC v3 changes two games:
- Northwestern–Minnesota, November 22, 2025: Northwestern's score corrected from 35 to 38; Minnesota remains at 35. Official sources: https://nusports.com/news/2025/11/22/cats-complete-comeback-secure-bowl-eligibility-in-38-35-win-over-minnesota and https://gophersports.com/game-center/21770 .
- Missouri–Kansas, September 6, 2025: an inconsistent game-row resource join was corrected to match the unchanged frozen resource table.

Across those games, 12 field entries changed, including derived quantities and provenance notes. Frozen tiers, closing lines and other scores remain unchanged. One missing-score game remains null.

An earlier before-correction descriptive calculation counted the erroneous tie as a loss. QC v3 excludes that unresolved tie from binary win-rate denominators. Corrected rates are unaffected by this reporting fix.

## Recorded verification

results/independent_verification.json records checks of normal equations, explicit shared-team pair covariance, row orientation and ordering, archived primary reproduction, resource join consistency and range-midpoint arithmetic. These checks passed on the private complete release. The public subset cannot independently rerun those checks without the inputs.

## Unresolved matters

- The earlier audit reported corroboration of 65 resource ranges; Virginia Tech, Cincinnati and UCF still require historical confirmation. The exact original 2025–26 source-page snapshot has not been recovered. Numerical reproduction does not authenticate source-year provenance.
- Archived seasonal slopes reproduce, but their uncertainty and interaction p-values remain unreconciled. These claims are excluded from the abstract.
- The archived joint phase-by-tier test lacks sufficient executable specification and is not represented as reproduced.
- The original sensitivity seed was not recovered. The new 500-draw series uses seed 20260930 and is not an exact reproduction of that archived simulation.
- Most preserved historical scores and market lines have not been independently recertified in this correction task.
- Cross-season replication and 2024 reconstruction have not been run.
- Redistribution permissions are pending and organizer acceptance of withheld inputs is unconfirmed.
- No application confirmation is available.

## Editorial version

ABSTRACT.md matches the grammar-edited Word abstract from October 1, 2026: 417 whitespace-delimited words including title and headings. Editing changed exposition and future-research questions, not numerical results or the analysis method.
