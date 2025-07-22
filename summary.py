from table_x import build_table_x
from table_y import build_table_y
from table_z import build_table_z

if __name__ == '__main__':
    tab_x = build_table_x()
    tab_y = build_table_y()
    tab_z = build_table_z()
    print('Table X. Treatment Approach.')
    print(tab_x.to_string())
    print('* NMV-r, nirmatrelvir-ritonavir.')
    print('* \u00b9 Any treatment administered prior to extended nirmatrelvir-ritonavir, ' +
          'including standard 5-day Paxlovid courses with or without other antivirals.')
    print('* \u00b2 Extended nirmatrelvir-ritonavir regimens (with or without concurrent antivirals) ' +
          'when no subsequent antiviral therapy was administered.')
    print('Table Y. Demographics and Clinical Characteristics.')
    print(tab_y.to_string())
    print('* NMV-r, nirmatrelvir-ritonavir.')
    print('* \u00b9 Treatment setting where prolonged NMV-r was administered.')
    print('Table Z')
    print(tab_z.fillna(''))
    print('Anti-CD-20 umfasst Rituximab, Obinutuzumab, Ocrelizumab, Mosunetuzumab.')
