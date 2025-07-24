import pandas as pd
from data_preprocessing import (
    TOTAL,
    MONO,
    COMBO,
    COL_EXT,
    COL_OTHER,
    COL_THERAPY,

    parse_ext,
    fmt_pct,
    fmt_p,
    fmt_iqr,
    fmt_range,
    cont_test,
    chi_or_fisher,
    rate_calc,
    fill_rate,
)


def build_table_x():
    days_t, courses_t = parse_ext(TOTAL[COL_EXT])
    days_m, courses_m = parse_ext(MONO[COL_EXT])
    days_c, courses_c = parse_ext(COMBO[COL_EXT])
    index = pd.MultiIndex.from_tuples(
        [
            ('N =', ''),
            ('First-line therapy\u00b9, n (%)', ''),
            ('First-line therapy\u00b9, n (%)', 'Remdesivir'),
            ('First-line therapy\u00b9, n (%)', 'Molnupiravir'),
            ('First-line therapy\u00b9, n (%)', 'Standard 5-day Paxlovid'),
            ('First-line therapy\u00b9, n (%)', 'Other antivirals'),
            ('First-line therapy\u00b9, n (%)', 'None'),
            ('Last line therapy\u00b2, n (%)', ''),
            ('Last line therapy\u00b2, n (%)', 'Combination therapy'),
            ('Last line therapy\u00b2, n (%)', 'Monotherapy'),
            ('Treatment courses, n (%)', ''),
            ('Treatment courses, n (%)', 'Single prolonged course'),
            ('Treatment courses, n (%)', 'Multiple courses'),
            ('Duration', ''),
            ('Duration', 'Median duration, days (IQR)'),
            ('Duration', 'Duration range, days'),
        ],
        names=['Category', 'Subcategory'],
    )
    t_x = pd.DataFrame(index=index, columns=[
        'Total',
        'Monotherapy',
        'Combination',
        'p-value',
    ])
    t_x.loc[('N =', '')] = [len(TOTAL), len(MONO), len(COMBO), '']

    def add_rate(row, st, sm, sc):
        fill_rate(t_x, row, st, sm, sc, blank=st.sum() == 0)

    labels = [
        'Standard 5-day Paxlovid',
        'Remdesivir',
        'Molnupiravir',
        'Other antivirals',
    ]
    cols = ['flag_pax5d', 'flag_rdv', 'flag_mpv', 'flag_other']
    for lbl, col in zip(labels, cols):
        add_rate(
            ('First-line therapy\u00b9, n (%)', lbl),
            TOTAL[col],
            MONO[col],
            COMBO[col],
        )
    add_rate(
        ('First-line therapy\u00b9, n (%)', 'None'),
        TOTAL[COL_OTHER].astype(str).str.lower().str.strip().eq('none'),
        MONO[COL_OTHER].astype(str).str.lower().str.strip().eq('none'),
        COMBO[COL_OTHER].astype(str).str.lower().str.strip().eq('none'),
    )
    t_x.loc[('First-line therapy\u00b9, n (%)', '')] = ''
    com_flag_t = TOTAL[COL_THERAPY].str.startswith('c', na=False)
    mono_flag_t = TOTAL[COL_THERAPY].str.startswith('m', na=False)
    idx = ('Last line therapy\u00b2, n (%)', 'Combination therapy')
    t_x.at[idx, 'Total'] = fmt_pct(int(com_flag_t.sum()), len(TOTAL))
    t_x.at[idx, 'Monotherapy'] = fmt_pct(0, len(MONO))
    t_x.at[idx, 'Combination'] = fmt_pct(len(COMBO), len(COMBO))
    p_last = chi_or_fisher(len(COMBO), 0, 0, len(MONO))
    t_x.at[idx, 'p-value'] = ''
    idx = ('Last line therapy\u00b2, n (%)', 'Monotherapy')
    t_x.at[idx, 'Total'] = fmt_pct(int(mono_flag_t.sum()), len(TOTAL))
    t_x.at[idx, 'Monotherapy'] = fmt_pct(len(MONO), len(MONO))
    t_x.at[idx, 'Combination'] = fmt_pct(0, len(COMBO))
    t_x.at[idx, 'p-value'] = ''
    t_x.loc[('Last line therapy\u00b2, n (%)', '')] = ''
    t_x.at[('Last line therapy\u00b2, n (%)', ''), 'p-value'] = fmt_p(p_last)
    single_t = courses_t == 1
    multi_t = courses_t > 1
    single_m = courses_m == 1
    multi_m = courses_m > 1
    single_c = courses_c == 1
    multi_c = courses_c > 1
    row = ('Treatment courses, n (%)', 'Single prolonged course')
    t_x.at[row, 'Total'] = fmt_pct(int(single_t.sum()), len(TOTAL))
    t_x.at[row, 'Monotherapy'] = fmt_pct(int(single_m.sum()), len(MONO))
    t_x.at[row, 'Combination'] = fmt_pct(int(single_c.sum()), len(COMBO))
    row = ('Treatment courses, n (%)', 'Multiple courses')
    t_x.at[row, 'Total'] = fmt_pct(int(multi_t.sum()), len(TOTAL))
    t_x.at[row, 'Monotherapy'] = fmt_pct(int(multi_m.sum()), len(MONO))
    t_x.at[row, 'Combination'] = fmt_pct(int(multi_c.sum()), len(COMBO))
    p_course = chi_or_fisher(int(single_c.sum()), int(multi_c.sum()), int(single_m.sum()), int(multi_m.sum()))
    t_x.at[('Treatment courses, n (%)', 'Single prolonged course'), 'p-value'] = ''
    t_x.at[('Treatment courses, n (%)', 'Multiple courses'), 'p-value'] = ''
    t_x.loc[('Treatment courses, n (%)', '')] = ''
    t_x.at[('Treatment courses, n (%)', ''), 'p-value'] = fmt_p(p_course)
    t_x.at[('Duration', 'Median duration, days (IQR)'), 'Total'] = fmt_iqr(days_t)
    t_x.at[('Duration', 'Median duration, days (IQR)'), 'Monotherapy'] = fmt_iqr(days_m)
    t_x.at[('Duration', 'Median duration, days (IQR)'), 'Combination'] = fmt_iqr(days_c)
    t_x.at[('Duration', 'Duration range, days'), 'Total'] = fmt_range(days_t)
    t_x.at[('Duration', 'Duration range, days'), 'Monotherapy'] = fmt_range(days_m)
    t_x.at[('Duration', 'Duration range, days'), 'Combination'] = fmt_range(days_c)
    t_x.loc[('Duration', '')] = ''
    p_dur = cont_test(days_m.dropna(), days_c.dropna())
    t_x.at[('Duration', 'Median duration, days (IQR)'), 'p-value'] = fmt_p(p_dur)
    t_x.at[('Duration', 'Duration range, days'), 'p-value'] = fmt_p(p_dur)
    foot = (
        '- NMV-r, nirmatrelvir-ritonavir.\n'
        '1: Any treatment administered prior to extended nirmatrelvir-ritonavir, '
        'including standard 5-day Paxlovid courses with or without other antivirals.\n'
        '2: Extended nirmatrelvir-ritonavir regimens (with or without concurrent antivirals) '
        'when no subsequent antiviral therapy was administered.'
    )
    t_x.attrs['footnote'] = foot
    return t_x


def build_table_x_raw():
    days_t, courses_t = parse_ext(TOTAL[COL_EXT])
    days_m, courses_m = parse_ext(MONO[COL_EXT])
    days_c, courses_c = parse_ext(COMBO[COL_EXT])
    index = pd.MultiIndex.from_tuples(
        [
            ('First-line therapy\u00b9, n', 'Remdesivir'),
            ('First-line therapy\u00b9, n', 'Molnupiravir'),
            ('First-line therapy\u00b9, n', 'Standard 5-day Paxlovid'),
            ('First-line therapy\u00b9, n', 'Other antivirals'),
            ('First-line therapy\u00b9, n', 'None'),
            ('Last line therapy\u00b2, n', 'Combination therapy'),
            ('Last line therapy\u00b2, n', 'Monotherapy'),
            ('Treatment courses, n', 'Single prolonged course'),
            ('Treatment courses, n', 'Multiple courses'),
            ('Duration, days', 'Median'),
            ('Duration, days', 'Min'),
            ('Duration, days', 'Max'),
        ],
        names=['Category', 'Subcategory'],
    )
    raw = pd.DataFrame(index=index, columns=[
        'Total',
        'Monotherapy',
        'Combination',
        'p-value',
    ])

    def add(row, st, sm, sc):
        nt, nm, nc, p = rate_calc(st, sm, sc)
        raw.at[row, 'Total'] = nt
        raw.at[row, 'Monotherapy'] = nm
        raw.at[row, 'Combination'] = nc
        if nt:
            raw.at[row, 'p-value'] = p

    labels = [
        'Standard 5-day Paxlovid',
        'Remdesivir',
        'Molnupiravir',
        'Other antivirals',
    ]
    cols = ['flag_pax5d', 'flag_rdv', 'flag_mpv', 'flag_other']
    for lbl, col in zip(labels, cols):
        add(('First-line therapy\u00b9, n', lbl), TOTAL[col], MONO[col], COMBO[col])
    add(
        ('First-line therapy\u00b9, n', 'None'),
        TOTAL[COL_OTHER].astype(str).str.lower().str.strip().eq('none'),
        MONO[COL_OTHER].astype(str).str.lower().str.strip().eq('none'),
        COMBO[COL_OTHER].astype(str).str.lower().str.strip().eq('none'),
    )
    com_flag_t = TOTAL[COL_THERAPY].str.startswith('c', na=False)
    mono_flag_t = TOTAL[COL_THERAPY].str.startswith('m', na=False)
    add(
        ('Last line therapy\u00b2, n', 'Combination therapy'),
        com_flag_t,
        MONO[COL_THERAPY].str.startswith('c', na=False),
        COMBO[COL_THERAPY].str.startswith('c', na=False),
    )
    raw.at[('Last line therapy\u00b2, n', 'Combination therapy'), 'p-value'] = chi_or_fisher(
        len(COMBO),
        0,
        0,
        len(MONO),
    )
    raw.at[('Last line therapy\u00b2, n', 'Monotherapy'), 'Total'] = int(mono_flag_t.sum())
    raw.at[('Last line therapy\u00b2, n', 'Monotherapy'), 'Monotherapy'] = len(MONO)
    raw.at[('Last line therapy\u00b2, n', 'Monotherapy'), 'Combination'] = 0
    raw.at[('Last line therapy\u00b2, n', 'Monotherapy'), 'p-value'] = None
    single_t = courses_t == 1
    multi_t = courses_t > 1
    single_m = courses_m == 1
    multi_m = courses_m > 1
    single_c = courses_c == 1
    multi_c = courses_c > 1
    add(('Treatment courses, n', 'Single prolonged course'), single_t, single_m, single_c)
    raw.at[('Treatment courses, n', 'Multiple courses'), 'Total'] = int(multi_t.sum())
    raw.at[('Treatment courses, n', 'Multiple courses'), 'Monotherapy'] = int(multi_m.sum())
    raw.at[('Treatment courses, n', 'Multiple courses'), 'Combination'] = int(multi_c.sum())
    p_course = chi_or_fisher(int(single_c.sum()), int(multi_c.sum()), int(single_m.sum()), int(multi_m.sum()))
    raw.at[('Treatment courses, n', 'Single prolonged course'), 'p-value'] = p_course
    raw.at[('Treatment courses, n', 'Multiple courses'), 'p-value'] = None
    raw.at[('Duration, days', 'Median'), 'Total'] = days_t.median()
    raw.at[('Duration, days', 'Median'), 'Monotherapy'] = days_m.median()
    raw.at[('Duration, days', 'Median'), 'Combination'] = days_c.median()
    raw.at[('Duration, days', 'Min'), 'Total'] = days_t.min()
    raw.at[('Duration, days', 'Min'), 'Monotherapy'] = days_m.min()
    raw.at[('Duration, days', 'Min'), 'Combination'] = days_c.min()
    raw.at[('Duration, days', 'Max'), 'Total'] = days_t.max()
    raw.at[('Duration, days', 'Max'), 'Monotherapy'] = days_m.max()
    raw.at[('Duration, days', 'Max'), 'Combination'] = days_c.max()
    raw.at[('Duration, days', 'Median'), 'p-value'] = cont_test(days_m.dropna(), days_c.dropna())
    raw.at[('Duration, days', 'Min'), 'p-value'] = raw.at[('Duration, days', 'Median'), 'p-value']
    raw.at[('Duration, days', 'Max'), 'p-value'] = raw.at[('Duration, days', 'Median'), 'p-value']
    foot = (
        '- NMV-r, nirmatrelvir-ritonavir.\n'
        '1: Any treatment administered prior to extended nirmatrelvir-ritonavir, '
        'including standard 5-day Paxlovid courses with or without other antivirals.\n'
        '2: Extended nirmatrelvir-ritonavir regimens (with or without concurrent antivirals) '
        'when no subsequent antiviral therapy was administered.'
    )
    raw.attrs['footnote'] = foot
    return raw


if __name__ == '__main__':
    print('Table X. Treatment Approach.')
    print(build_table_x().to_string())
    print('- NMV-r, nirmatrelvir-ritonavir.')
    print(
        '1: Any treatment administered prior to extended nirmatrelvir-ritonavir, '
        'including standard 5-day Paxlovid courses with or without other antivirals.'
    )
    print(
        '2: Extended nirmatrelvir-ritonavir regimens (with or without concurrent antivirals) '
        'when no subsequent antiviral therapy was administered.'
    )
