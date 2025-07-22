import pandas as pd
from data_preprocessing import (
    TOTAL,
    MONO,
    COMBO,
    COL_EXT,
    COL_NMV_STD,
    COL_OTHER,
    COL_THERAPY,

    parse_ext,
    fmt_pct,
    chi_or_fisher,
    fmt_p,
    fmt_iqr,

    fmt_range,
    cont_test,
)


def build_table_x():
    days_t, courses_t = parse_ext(TOTAL[COL_EXT])
    days_m, courses_m = parse_ext(MONO[COL_EXT])
    days_c, courses_c = parse_ext(COMBO[COL_EXT])
    index = pd.MultiIndex.from_tuples(
        [
            ('N=', ''),
            ('First-line therapy\u00b9, n (%)', ''),
            ('First-line therapy\u00b9, n (%)', 'Remdesivir'),
            ('First-line therapy\u00b9, n (%)', 'Molnupiravir'),
            ('First-line therapy\u00b9, n (%)', 'Standard 5-day Paxlovid'),
            ('First-line therapy\u00b9, n (%)', 'Other antivirals'),
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
        'Primary Cohort (n=104)',
        'Subgroup monotherapy (n=33)',
        'Subgroup combination (n=57)',
        'p-value',
    ])
    t_x.at[('N=', ''), 'Primary Cohort (n=104)'] = len(TOTAL)
    t_x.at[('N=', ''), 'Subgroup monotherapy (n=33)'] = len(MONO)
    t_x.at[('N=', ''), 'Subgroup combination (n=57)'] = len(COMBO)
    t_x.at[('N=', ''), 'p-value'] = ''

    def add_rate(row, ser_total, ser_mono, ser_combo):
        t_x.at[row, 'Primary Cohort (n=104)'] = fmt_pct(int(ser_total.sum()), len(TOTAL))
        t_x.at[row, 'Subgroup monotherapy (n=33)'] = fmt_pct(int(ser_mono.sum()), len(MONO))
        t_x.at[row, 'Subgroup combination (n=57)'] = fmt_pct(int(ser_combo.sum()), len(COMBO))
        if ser_total.sum():
            a11 = int(ser_combo.sum())
            a12 = len(ser_combo) - a11
            a21 = int(ser_mono.sum())
            a22 = len(ser_mono) - a21
            p = chi_or_fisher(a11, a12, a21, a22)
            t_x.at[row, 'p-value'] = fmt_p(p)
        else:
            t_x.at[row, 'p-value'] = ''

    drug_map = {
        'rdv': 'Remdesivir',
        'remdesivir': 'Remdesivir',
        'mpv': 'Molnupiravir',
        'molnupiravir': 'Molnupiravir',
    }

    def classify(row):
        if pd.to_numeric(row[COL_NMV_STD], errors='coerce') >= 1:
            return 'Standard 5-day Paxlovid'
        txt = str(row[COL_OTHER]).lower()
        for k, d in drug_map.items():
            if k in txt:
                return d
        return 'Other antivirals'

    cat_t = TOTAL.apply(classify, axis=1)
    cat_m = MONO.apply(classify, axis=1)
    cat_c = COMBO.apply(classify, axis=1)
    for c in ['Remdesivir', 'Molnupiravir', 'Standard 5-day Paxlovid', 'Other antivirals']:
        add_rate(('First-line therapy\u00b9, n (%)', c), cat_t == c, cat_m == c, cat_c == c)
    t_x.loc[('First-line therapy\u00b9, n (%)', '')] = ''
    com_flag_t = TOTAL[COL_THERAPY].str.startswith('c', na=False)
    mono_flag_t = TOTAL[COL_THERAPY].str.startswith('m', na=False)
    idx = ('Last line therapy\u00b2, n (%)', 'Combination therapy')
    t_x.at[idx, 'Primary Cohort (n=104)'] = fmt_pct(int(com_flag_t.sum()), len(TOTAL))
    t_x.at[idx, 'Subgroup monotherapy (n=33)'] = fmt_pct(0, len(MONO))
    t_x.at[idx, 'Subgroup combination (n=57)'] = fmt_pct(len(COMBO), len(COMBO))
    p_last = chi_or_fisher(len(COMBO), 0, 0, len(MONO))
    t_x.at[idx, 'p-value'] = fmt_p(p_last)
    idx = ('Last line therapy\u00b2, n (%)', 'Monotherapy')
    t_x.at[idx, 'Primary Cohort (n=104)'] = fmt_pct(int(mono_flag_t.sum()), len(TOTAL))
    t_x.at[idx, 'Subgroup monotherapy (n=33)'] = fmt_pct(len(MONO), len(MONO))
    t_x.at[idx, 'Subgroup combination (n=57)'] = fmt_pct(0, len(COMBO))
    t_x.at[idx, 'p-value'] = ''
    t_x.loc[('Last line therapy\u00b2, n (%)', '')] = ''
    single_t = courses_t == 1
    multi_t = courses_t > 1
    single_m = courses_m == 1
    multi_m = courses_m > 1
    single_c = courses_c == 1
    multi_c = courses_c > 1
    row = ('Treatment courses, n (%)', 'Single prolonged course')
    t_x.at[row, 'Primary Cohort (n=104)'] = fmt_pct(int(single_t.sum()), len(TOTAL))
    t_x.at[row, 'Subgroup monotherapy (n=33)'] = fmt_pct(int(single_m.sum()), len(MONO))
    t_x.at[row, 'Subgroup combination (n=57)'] = fmt_pct(int(single_c.sum()), len(COMBO))
    row = ('Treatment courses, n (%)', 'Multiple courses')
    t_x.at[row, 'Primary Cohort (n=104)'] = fmt_pct(int(multi_t.sum()), len(TOTAL))
    t_x.at[row, 'Subgroup monotherapy (n=33)'] = fmt_pct(int(multi_m.sum()), len(MONO))
    t_x.at[row, 'Subgroup combination (n=57)'] = fmt_pct(int(multi_c.sum()), len(COMBO))
    p_course = chi_or_fisher(int(single_c.sum()), int(multi_c.sum()), int(single_m.sum()), int(multi_m.sum()))
    t_x.at[('Treatment courses, n (%)', 'Single prolonged course'), 'p-value'] = fmt_p(p_course)
    t_x.at[('Treatment courses, n (%)', 'Multiple courses'), 'p-value'] = ''
    t_x.loc[('Treatment courses, n (%)', '')] = ''
    t_x.at[('Duration', 'Median duration, days (IQR)'), 'Primary Cohort (n=104)'] = fmt_iqr(days_t)
    t_x.at[('Duration', 'Median duration, days (IQR)'), 'Subgroup monotherapy (n=33)'] = fmt_iqr(days_m)
    t_x.at[('Duration', 'Median duration, days (IQR)'), 'Subgroup combination (n=57)'] = fmt_iqr(days_c)
    t_x.at[('Duration', 'Duration range, days'), 'Primary Cohort (n=104)'] = fmt_range(days_t)
    t_x.at[('Duration', 'Duration range, days'), 'Subgroup monotherapy (n=33)'] = fmt_range(days_m)
    t_x.at[('Duration', 'Duration range, days'), 'Subgroup combination (n=57)'] = fmt_range(days_c)
    t_x.loc[('Duration', '')] = ''
    p_dur = cont_test(days_m.dropna(), days_c.dropna())
    t_x.at[('Duration', 'Median duration, days (IQR)'), 'p-value'] = fmt_p(p_dur)
    t_x.at[('Duration', 'Duration range, days'), 'p-value'] = fmt_p(p_dur)
    return t_x


if __name__ == '__main__':
    print('Table X. Treatment Approach.')
    print(build_table_x().to_string())
