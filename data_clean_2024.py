import pandas as pd
import numpy as np
import myclean

FELVI_FILE = 'C:/Users/ulricha/Downloads/premome/FI73435_DontesekEgysorosListaja_0806.xlsx'
FELVI_SHEET = 'Munka1'
PREMOME_FILE = 'C:/Users/ulricha/Downloads/premome/PreMOME_Resztvevok_Adatelemzeshez.xlsx'

felvi = pd.read_excel(FELVI_FILE, sheet_name=FELVI_SHEET)
premome = pd.read_excel(PREMOME_FILE, sheet_name=None)

# premome sheets correspond to different premome courses
elokeszito_2023 = premome['Előkészítők_2023']
intenziv_2024 = premome['INTENZÍV_2024']

elokeszito_2023 = myclean.rename_and_drop(df=elokeszito_2023, str_to_find='résztvevő neve')
intenziv_2024 = myclean.rename_and_drop(df=intenziv_2024, str_to_find='résztvevő neve')

elokeszitok = pd.concat([elokeszito_2023, intenziv_2024])
#TODO: put whitespace-cleaning code into its own function, substitute multiple whitespaces with single whitespace
elokeszitok = elokeszitok.map(lambda x: x.strip() if isinstance(x, str) else x)

# add column with N for taken courses per résztvevő
elokeszitok['Kurzus szám'] = elokeszitok.groupby('résztvevő neve').transform('size')

#TODO: run a check if 'résztvevő neve' is unique to 'Születési idő' and 'Édesanyja leánykori neve'

#hardcode these three cases FOR NOW, have to handle varying 'Születési hely' by 'résztvevő neve'
elokeszitok.loc[elokeszitok['résztvevő neve'] == 'Ludescher-Tyukodi Réka', 'Születési hely'] = 'Románia'
elokeszitok.loc[elokeszitok['résztvevő neve'] == 'Damokos Zsófia', 'Születési hely'] = 'Románia'
elokeszitok.loc[elokeszitok['résztvevő neve'] == 'Szántó Kriszta', 'Születési hely'] = 'Románia'

elokeszitok_final = (pd.merge(elokeszitok.groupby(['résztvevő neve'], as_index=False).agg({'Kurzus neve': '; '.join}),
                              elokeszitok[['résztvevő neve', 'Születési hely', 'Kurzus szám']],
                              how='right',
                              on='résztvevő neve')
                       .drop_duplicates()
                     )

elokeszitok_final['résztvevő neve'] = elokeszitok_final['résztvevő neve'].str.upper()
elokeszitok_final['Év'] = "2024/25"

if elokeszitok_final['résztvevő neve'].nunique() != elokeszitok_final.shape[0]:
    print("Duplikátumok az összesített preMOMEs diákok között!")


felvi = felvi[['nev', 'alp_vkod', 'kepzes', 'finforma', 'felvettek']].drop_duplicates()
felvi['nev'] = felvi['nev'].str.upper()
felvi = felvi.map(lambda x: x.strip() if isinstance(x, str) else x)
felvi['kepzes'] = felvi['kepzes'].apply(lambda x: x.replace(" (angol nyelven)", ""))

# remove one if applicant applied to both government-subsidized and self-supported options
felvi['Év'] = "2024/25"
felvi = (felvi.groupby(['nev', 'kepzes', 'Év'])
               .apply(lambda df: df[df['finforma'] == 'A'] if len(df) > 1 else df)
               .reset_index(drop=True))

if felvi[['nev', 'kepzes', 'Év']].value_counts().sum() != felvi.shape[0]:
    print("Duplikált hallgató-képzés-felvételi év rekord(ok) a felvi-s diákok között!")

# number of unique MOME courses applied
# alp_vkod is unique to the individual and the year applied
felvi['MOME képzés szám'] = felvi.groupby(['alp_vkod']).transform('size')

# where multiple courses were applied to by student and admission was gained, remove courses where no admission was gained
felvi = (felvi.groupby(['alp_vkod'])
         .apply(lambda df: df[df['felvettek'] == 'I'] if df['felvettek'].isin(['I']).any() else df)
         .reset_index(drop=True))

# exclude those few applicants who cannot be mapped to the preMOME students
felvi = felvi.groupby('nev').filter(lambda df: df['alp_vkod'].nunique() == 1)
# hard-code
felvi.loc[felvi['nev'] == 'GÁL ZSÓFIA CSENGE', ['nev']] = "GÁL ZSÓFIA"

merged = pd.merge(elokeszitok_final,
                  felvi,
                  how='outer',
                  left_on=['résztvevő neve', 'Év'],
                  right_on=['nev', 'Év'])

merged['nev'] = merged['nev'].combine_first(merged['résztvevő neve'])

if merged[['nev', 'kepzes', 'Év']].value_counts().sum() != merged[merged['alp_vkod'].notnull()].shape[0]:
    print("Duplikált hallgató-képzés-felvételi év rekord(ok) a felvi + preMOME-s diákok között!")


merged['Felvették'] = np.where(
     merged.alp_vkod.isnull(),
    "Nem jelentkezett",
    np.where(
        merged['felvettek'] == "I", "Igen", "Nem"
    )
)

merged['preMOME'] = np.where(
     merged['Kurzus szám'].isnull(),
    "Nem",
    "Igen"
)

merged['Kurzus szám'] = merged['Kurzus szám'].map(lambda x: '{0:.0f}'.format(x))
merged['MOME képzés'] = merged['kepzes']
merged = merged.replace('nan', None)

