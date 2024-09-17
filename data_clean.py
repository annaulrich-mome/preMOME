import pandas as pd
import numpy as np
import myclean


FELVI_SHEET = 'Munka1'
PREMOME_FILE = 'C:/Users/ulricha/Downloads/premome/PreMOME_Resztvevok_Adatelemzeshez.xlsx'
NEPTUN_FILE = 'C:/Users/ulricha/Downloads/premome/NEPTUN_lekérdezés_20240911.xlsx'
FELVI_FILE_22 = 'C:/Users/ulricha/Downloads/premome/listazo-jelentkezesek-220509_153938.xlsx'
FELVI_FILE_23 = 'C:/Users/ulricha/Downloads/premome/Jelentkezések_20230307.xlsx'
premome = pd.read_excel(PREMOME_FILE, sheet_name=None)


### preMOME

# sheets correspond to different premome courses
elokeszito_2022 = premome['Előkészítő_2022']
intenziv_2023 = premome['Intenzív 2023']
elokeszito_2021 = premome['Előkészítő_2021']
intenziv_2022 = premome['Intenzív 2022']

elokeszito_2022 = myclean.rename_and_drop(df=elokeszito_2022, str_to_find='résztvevő neve')
intenziv_2023 = myclean.rename_and_drop(df=intenziv_2023, str_to_find='résztvevő neve')

elokeszito_2021 = myclean.rename_and_drop(df=elokeszito_2021, str_to_find='résztvevő neve')
intenziv_2022 = myclean.rename_and_drop(df=intenziv_2022, str_to_find='résztvevő neve')

elokeszitok23 = pd.concat([elokeszito_2022, intenziv_2023])
elokeszitok23 = elokeszitok23.map(lambda x: x.strip() if isinstance(x, str) else x)

elokeszitok22 = pd.concat([elokeszito_2021, intenziv_2022])
elokeszitok22 = elokeszitok22.map(lambda x: x.strip() if isinstance(x, str) else x)

# add column with N for taken courses per résztvevő
elokeszitok23['Kurzus szám'] = elokeszitok23.groupby('résztvevő neve').transform('size')
elokeszitok23['Év'] = "2023/24"
elokeszitok22['Kurzus szám'] = elokeszitok22.groupby('résztvevő neve').transform('size')
elokeszitok22['Év'] = "2022/23"

elokeszitok_22_23 = pd.concat([elokeszitok23, elokeszitok22])


#elokeszitok_22_23['Születési hely'] = elokeszitok_22_23['Születési hely'].astype(str).apply(lambda x: x.split()[0] if 'Budapest' in x else x)
elokeszitok_22_23.rename(columns = {'kurzus neve':'Kurzus neve'}, inplace=True)

elokeszitok_22_23_final = (pd.merge(elokeszitok_22_23.groupby( ['résztvevő neve', 'Év'], as_index=False).agg({'Kurzus neve': '; '.join}),
                              elokeszitok_22_23[['résztvevő neve', 'Kurzus szám', 'Év']],
                              how='right',
                              on=['résztvevő neve', 'Év'])
                       .drop_duplicates())

elokeszitok_22_23_final['résztvevő neve'] = elokeszitok_22_23_final['résztvevő neve'].str.upper()

if elokeszitok_22_23_final[['résztvevő neve', 'Év']].value_counts().sum() != elokeszitok_22_23_final.shape[0]:
    print("Duplikátumok az összesített preMOMEs diákok között!")



### FELVI

felvi_22 = pd.read_excel(FELVI_FILE_22, sheet_name='Jelentkezések')
felvi_22['Év'] = "2022/23"
felvi_23 = pd.read_excel(FELVI_FILE_23, sheet_name='Jelentkezések')
felvi_23['Év'] = "2023/24"
felvi_22_23 = pd.concat([felvi_22, felvi_23])

felvi_22_23['kepzes'] = felvi_22_23['Szak neve'].apply(lambda x: x.replace(" (angol nyelven)", ""))
felvi_22_23 = felvi_22_23.map(lambda x: x.strip() if isinstance(x, str) else x)

felvi_22_23['nev'] = felvi_22_23['Név'].str.upper()
felvi_22_23.rename(columns = {'Felvételi azonosítószám':'alp_vkod',
                              'Finanszírozás': 'finforma',
                              'Lakóhely - ország': 'lakhely_orszag',
                              'Lakóhely - település': 'lakhely_telepules'}, inplace=True)

# remove one if applicant applied to both government-subsidized and self-supported options
felvi_22_23 = (felvi_22_23.groupby(['nev', 'kepzes', 'Év'])
               .apply(lambda df: df[df['finforma'] == 'A'] if len(df) > 1 else df)
               .reset_index(drop=True))

# felvi_22_23.sort_values(by=['alp_vkod'], inplace=True)
# felvi_22_23_collapsed = felvi_22_23.groupby('alp_vkod', as_index=False).agg({'finforma': '; '.join, 'kepzes': '; '.join})
# felvi_22_23_formatted = pd.merge(felvi_22_23_collapsed,
#                            felvi_22_23[['alp_vkod', 'nev', 'lakhely_orszag', 'lakhely_telepules', 'Év']].drop_duplicates(),
#                            how='left',
#                            on='alp_vkod'
#                           )

# exclude those few applicants who cannot be mapped to the preMOME students
felvi_22_23 = felvi_22_23.groupby(['nev', 'Év']).filter(lambda df: df['alp_vkod'].nunique() == 1)

if felvi_22_23[['nev', 'kepzes', 'Év']].value_counts().sum() != felvi_22_23.shape[0]:
    print("Duplikált hallgató-képzés-felvételi év rekord(ok) a felvi-s diákok között!")

### NEPTUN

header = ['Neptun kód', 'Nyomtatási név', 'Felvételi azonosító', 'Születési dátum',
          'Születési hely', 'Hallgató képzése', 'Képzés jogviszony kezdete']

neptun = pd.read_excel(NEPTUN_FILE, names=header)

if len(set(felvi_22_23['kepzes']).difference(set(neptun['Hallgató képzése']))) > 0:
    print('Néhány felvi-s képzés nem található meg a Neptun-ban!')

neptun['Nyomtatási név'] = neptun['Nyomtatási név'].str.upper()

if neptun[['Nyomtatási név', 'Hallgató képzése']].value_counts().sum() != neptun.shape[0]:
    print('Duplikált hallgató-képzés rekord(ok) a Neptun-ban!')

neptun['Év'] = np.where(
    neptun['Képzés jogviszony kezdete'].str.contains("^2022"),
    "2022/23",
    np.where(
        neptun['Képzés jogviszony kezdete'].str.contains("^2023"),
        "2023/24",
        None
    )
)

# merge Felvi and Neptun
felvi_neptun = (pd.merge(felvi_22_23[['nev', 'kepzes', 'Év', 'alp_vkod', 'Születési dátum']].drop_duplicates(),
                         neptun,
                         how='left',
                         left_on=['nev', 'kepzes', 'Év'],
                         right_on=['Nyomtatási név', 'Hallgató képzése', 'Év']))

# where multiple courses were applied to by student and admission was gained, remove courses where no admission was gained
felvi_neptun = (felvi_neptun.groupby(['alp_vkod'])
                 .apply(lambda df: df[df['Képzés jogviszony kezdete'].notnull()] if df['Képzés jogviszony kezdete'].notnull().any() else df)
                 .reset_index(drop=True))

if felvi_neptun[['nev', 'kepzes', 'Év']].value_counts().sum() != felvi_neptun.shape[0]:
    print('Duplikált hallgató-képzés-felvételi év rekord(ok) a merged Felvi és Neptun-ban!')



felvi_neptun_elokeszitok = (pd.merge(felvi_neptun[['nev', 'kepzes', 'Év', 'Képzés jogviszony kezdete', 'alp_vkod']],
                                     elokeszitok_22_23_final,
                                     how='outer',
                                     left_on=['nev', 'Év'],
                                     right_on=['résztvevő neve', 'Év']))

felvi_neptun_elokeszitok['Felvették'] = np.where(
     felvi_neptun_elokeszitok.alp_vkod.isnull(),
    "Nem jelentkezett",
    np.where(
        felvi_neptun_elokeszitok['Képzés jogviszony kezdete'].isnull(), "Nem", "Igen"
    )
)

felvi_neptun_elokeszitok['preMOME'] = np.where(
     felvi_neptun_elokeszitok['Kurzus szám'].isnull(),
    "Nem",
    "Igen"
)

# number of unique MOME courses applied
# alp_vkod is unique to the individual and the year applied
felvi_neptun_elokeszitok['MOME képzés szám'] = felvi_neptun_elokeszitok.groupby(['alp_vkod']).transform('size')
felvi_neptun_elokeszitok['nev'] = felvi_neptun_elokeszitok['nev'].combine_first(felvi_neptun_elokeszitok['résztvevő neve'])

felvi_neptun_elokeszitok['Kurzus szám'] = felvi_neptun_elokeszitok['Kurzus szám'].map(lambda x: '{0:.0f}'.format(x))
felvi_neptun_elokeszitok['MOME képzés'] = felvi_neptun_elokeszitok['kepzes']
felvi_neptun_elokeszitok = felvi_neptun_elokeszitok.replace('nan', None)

if felvi_neptun_elokeszitok[['nev', 'kepzes', 'Év']].value_counts().sum() != felvi_neptun_elokeszitok.shape[0]:
    print('Duplikált hallgató-képzés-felvételi év rekord(ok) a merged Felvi, Neptun ás preMOME-ban!')



#cols_for_plotting = ["Felvették", "MOME képzés szám", "Kurzus szám", "MOME képzés", "preMOME"]