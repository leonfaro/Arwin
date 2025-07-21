# Data interpretation and preprocessing

## Baseline therapy classification

- Parse `baseline therapy` field.
- Group as `immuno_detail` using keywords:
  - `Anti-CD-20` if any of ritux, rtx, obinutuzumab, obinu, obi, ocrelizumab, ocre, ocr, mosunetuzumab, mosu, mos.
  - `CAR-T` if text mentions `CAR-T`.
  - `HSCT` if text mentions `HSCT` or `ASCT`.
  - `None` if text contains `none` or `no IS` or is empty.
  - `Other` otherwise.
- Derive `immuno3` with levels `Anti-CD-20`, `Other`, `None`.
- CAR-T and HSCT remain separate only if at least five cases per group; otherwise consolidate into `Other`.

## Statistical table generation

- Calculate counts and percentages for each row split by `therapy` (Combination vs Monotherapy).
- Use χ² tests for multi-level categories or Fisher's exact test for sparse 2×2 tables.
- Adjust p-values with FDR.
- Print counts per immunosuppressive category as a quick check.

Footnote appended to the table:

*Anti-CD-20 umfasst Rituximab, Obinutuzumab, Ocrelizumab, Mosunetuzumab.*
