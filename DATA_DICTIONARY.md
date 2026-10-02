# Data dictionary

Blank CSV fields represent missing values, never zero. One row is one game. Stable key is date plus the unordered pair of program names. Preserve original spelling and source notes; don't join by a substring.

| Fields | Meaning |
|---|---|
| Week | Archive week 0–16 or separately labeled supplemental CFP; do not coerce CFP to numeric week |
| Date | ISO game date |
| Team A, Team B | Source orientation, not necessarily home/away |
| Team A/B Resource Mid ($M) | Frozen midpoint in millions USD |
| Higher/Lower-Resource Team | Midpoint ordering; resource ties have no resolved side |
| Resource Gap ($M), Resource Gap % | Absolute midpoint difference; difference/lower midpoint, stored as fraction |
| Frozen Tier | Very Close <.10; Close .10–.20; Clear Gap ≥.20; use archived boundary convention |
| Home/Away/Neutral | Original location field; blank where unavailable |
| Market Favorite | Program receiving positive expected winning margin |
| Closing Spread | Positive magnitude of favorite's expected winning margin |
| Closing Total | Pregame expected combined score, points |
| Team A/B Score | Final score; null in one game |
| Winner | Larger final-score side; original contains erroneous Tie, QC removes it |
| Higher-Resource Won? | Original derived Boolean, blank when side/outcome unresolved |
| Favorite Margin | Favorite's actual points minus opponent's points |
| Spread Error (pts) | Absolute difference between favorite margin and closing spread |
| Combined Score | Sum of final scores |
| O/U Result | Over/Under/Push relative to closing total |
| Total Error Abs/Signed (pts) | Absolute/signed combined score minus closing total |
| Source/Notes | Market/results archive ancestry and versioned correction evidence |

Resources: one row per program; Payroll Low/High and Midpoint are millions USD. Conference is source label. Source dates, estimate type, comparability flags and outcome consultation status remain as recorded. Archived metadata are provenance claims from the prior workflow, not independently verified statements about an upstream source snapshot.

Outputs: n is the actual model row count. coef, se, p and ci fields are numerical model results. Covariance distinguishes HC3, logistic score sandwich and dyadic. Range quantiles describe stress-test draws. Null p for win-rate draws is deliberate. Exploratory tests are not adjusted for multiplicity.
