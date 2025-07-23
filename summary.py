from table_x import build_table_x, build_table_x_raw
from table_y import build_table_y
from data_preprocessing import baseline_stats

if __name__ == '__main__':
    tab_x = build_table_x()
    tab_y = build_table_y()
    base = baseline_stats()
    print('Table X. Treatment Approach.')
    print(tab_x.to_string())
    print('* Paxlovid, nirmatrelvir-ritonavir.')
    print('* \u00b9 Any treatment administered prior to extended nirmatrelvir-ritonavir, ' +
          'including standard 5-day Paxlovid courses with or without other antivirals.')
    print('* \u00b2 Extended nirmatrelvir-ritonavir regimens (with or without concurrent antivirals) ' +
          'when no subsequent antiviral therapy was administered.')
    print('Table Y. Demographics and Clinical Characteristics.')
    print(tab_y.to_string())
    print('* Paxlovid, nirmatrelvir-ritonavir.')
    print('* \u00b9 Treatment setting where prolonged Paxlovid was administered.')
    print('Baseline therapy distribution')
    print(base.to_string())
    tab_x.to_excel('table_x_v7.xlsx')
    build_table_x_raw().to_csv('table_x_v7.csv')
