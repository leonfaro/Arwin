# Progress Log

- Created `AGENTS.md` with contributor instructions as per project requirements.
- Initialized `progress.md` to track future changes.
- Updated rules: only base R plus packages ggplot2 and ggsankeyfier are permitted.
- Extracted POI, sPOI mono, and sPOI combo worksheets to CSV via `extract_csvs.R`; checked row counts (104/29/56) and trimmed whitespace.
- Removed `extract_csvs.R` to comply with package restrictions.
- Renamed `POI_n104_raw.csv` to `POI_n_104.csv` for downstream analysis.
- Added `plot_sankey.R` implementing the POI Sankey workflow.
