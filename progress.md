# Progress Log

- Created `AGENTS.md` with contributor instructions as per project requirements.
- Initialized `progress.md` to track future changes.
- Updated rules: only base R plus packages ggplot2 and ggsankeyfier are permitted.
- Extracted POI, sPOI mono, and sPOI combo worksheets to CSV via `extract_csvs.R`; checked row counts (104/29/56) and trimmed whitespace.
- Removed `extract_csvs.R` to comply with package restrictions.

- Added `sankey_POI.R` for generating the test Sankey plot; includes commented-out export lines.

- Updated sankey_POI.R to read POI_n104_raw.csv and plot with ggsankeyfier. Added labels via geom_text and kept ggsave lines commented.
- Refined sankey_POI.R data filtering and validation to ensure 104 rows after removing blanks.
- Corrected axis assignment for edge table and added console success message.
