import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
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
felvi = felvi.map(lambda x: x.strip() if isinstance(x, str) else x)
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
felvi['nev'] = felvi['nev'].str.upper()

if elokeszitok_final['résztvevő neve'].nunique() != elokeszitok_final.shape[0]:
    print("Duplikátumok az összesített preMOMEs diákok között!")

#hard-code for now
felvi.loc[felvi['lakhely_telepules'] == 'Komárom', 'lakhely_orszag'] = "Magyarország"

felvi.sort_values(by=['alp_vkod', 'felvettek'], inplace=True)
felvi_collapsed = felvi.groupby('alp_vkod', as_index=False).agg(
    {'felvettek': '; '.join, 'finforma': '; '.join, 'kepzes': '; '.join}
)
felvi_formatted = pd.merge(felvi_collapsed,
                           felvi[['alp_vkod', 'nev', 'lakhely_orszag', 'lakhely_telepules']].drop_duplicates(),
                           how='left',
                           on='alp_vkod'
                          )

if felvi_formatted['alp_vkod'].nunique() != felvi_formatted.shape[0]:
    print("Duplikátumok a felvi-s diákok között!")

merged = pd.merge(elokeszitok_final,
                  felvi_formatted,
                  how='left',
                  left_on='résztvevő neve',
                  right_on='nev')

if any(merged['résztvevő neve'].duplicated()):
    print(sum(merged['résztvevő neve'].duplicated()),
          "duplikált diák az merge-ölt adatban!")

# three duplicates, filter out manually based on place of birth and current location and/or preMOME course and university course
merged = merged[~((merged['résztvevő neve'] == 'GÁL ZSÓFIA') & (merged["kepzes"] == 'formatervezés'))]
merged = merged[~((merged['résztvevő neve'] == 'KOVÁCS HANNA') & (merged["lakhely_telepules"] == 'Magyaratád'))]
merged = merged[~((merged['résztvevő neve'] == 'VARGA BARBARA') & (merged["kepzes"] == 'fotográfia'))]

print("A duplikátumok kezelése után", sum(merged['résztvevő neve'].duplicated()), "duplikátum maradt a merge-ölt adatban.")

merged = merged.rename(
    columns={"alp_vkod": "Felvi id",
             "Kurzus neve": "preMOME kurzus",
             "kepzes": "egyetemi kepzes",
             "Kurzus szám": "preMOME össz kurzus szám"}
)

merged['felvettek I/N'] = np.where(
     merged.felvettek.isnull(),
    "N/A",
    np.where(
        merged.felvettek.str.contains("I"), "I", "N"
    )
)

# save as excel
merged[['résztvevő neve', 'preMOME kurzus','preMOME össz kurzus szám', 'Felvi id','egyetemi kepzes','finforma', 'felvettek', 'felvettek I/N']].to_excel("Felvi_adatok_PreMOME_Elokeszitok2023_Intenziv2024.xlsx")



################# Visualizations

merged2 = pd.merge(elokeszitok_final,
                  felvi_formatted,
                  how='outer',
                  left_on='résztvevő neve',
                  right_on='nev')

merged2['Felvették'] = np.where(
     merged2.felvettek.isnull(),
    "Nem jelentkezett",
    np.where(
        merged2.felvettek.str.contains("I"), "Igen", "Nem"
    )
)

merged2['preMOME'] = np.where(
     merged2['Kurzus neve'].isnull(),
    "Nem",
    "Igen"
)

merged2['Kurzus szám'] = merged2['Kurzus szám'].map(lambda x: '{0:.0f}'.format(x))
merged2['MOME képzés'] = merged2['kepzes'].astype(str).apply(lambda x: x.split("; ")[0])
merged2['MOME képzés'] = merged2['MOME képzés'].apply(lambda x: x.replace(" (angol nyelven)", ""))
merged2['MOME képzés szám'] = (merged2['kepzes'].
                               astype(str).
                               apply(lambda x: len(set(x.replace(" (angol nyelven)", "").split("; "))))) # number of unique courses applied
merged2 = merged2.replace('nan', None)


### Count
sns.set_style("whitegrid")
sns.set_palette("pastel")
g = sns.catplot(data=merged2, kind="count", x="preMOME", hue="Felvették",
                order=["Igen", "Nem"], hue_order=["Igen", "Nem", "Nem jelentkezett"])
g.set_ylabels("Résztvevők (#)")
# iterate through axes
for ax in g.axes.ravel():

    # add annotations
    for c in ax.containers:
        ax.bar_label(c, label_type='edge')
    ax.margins(y=0.2)
plt.show()


### Percent
merged2_perc = (pd.crosstab(merged2["preMOME"], merged2["Felvették"])
                .apply(lambda x: x/sum(x)*100, axis=1)
                .melt(ignore_index=False))
g = sns.catplot(data=merged2_perc, kind="bar", x="preMOME", y="value", hue="Felvették")
g.set_ylabels("Százalék (%)")
plt.show()


### Percent without those who did not apply
merged3 = merged2.loc[merged2['Felvették'] != "Nem jelentkezett"]
merged3_perc = (pd.crosstab(merged3["preMOME"], merged3["Felvették"])
                .apply(lambda x: x/sum(x)*100, axis=1)
                .melt(ignore_index=False))
g = sns.catplot(data=merged3_perc, kind="bar", x="preMOME", y="value", hue="Felvették")
g.set_ylabels("Százalék (%)")
plt.show()


### Count faceted by MOME course applied
# filter for MOME courses with at least one applicant who took a preMOME course
courses = merged2.loc[merged2['preMOME'] == "Igen", "MOME képzés"].unique()

g = sns.catplot(data=merged2[merged2['MOME képzés'].isin(courses)], kind="count", x="preMOME", hue="Felvették",
                order=["Igen", "Nem"], hue_order=["Igen", "Nem", "Nem jelentkezett"],
                col="MOME képzés", col_wrap=4, sharey=False)
g.set_titles('{col_name}')
g.set_ylabels("Résztvevők (#)")
# iterate through axes
for ax in g.axes.ravel():

    # add annotations
    for c in ax.containers:
        ax.bar_label(c, label_type='edge')
    ax.margins(y=0.2)
plt.show()


### Number of PreMOME courses taken
g = sns.catplot(data=merged2, kind="count", x="Kurzus szám", hue="Felvették",
                hue_order=["Igen", "Nem", "Nem jelentkezett"])
# iterate through axes
for ax in g.axes.ravel():

    # add annotations
    for c in ax.containers:
        # add custom labels with the labels=labels parameter if needed
        # labels = [f'{h}' if (h := v.get_height()) > 0 else '' for v in c]
        ax.bar_label(c, label_type='edge')
    ax.margins(y=0.2)
g.set_ylabels("Résztvevők (#)")
g.set_xlabels("preMOME kurzus (#)")
plt.show()


### Number of MOME courses applied
g = sns.catplot(data=merged2[merged2['Felvették'] != "Nem jelentkezett"], kind="count", x="MOME képzés szám", hue="Felvették",
                hue_order=["Igen", "Nem", "Nem jelentkezett"])
# iterate through axes
for ax in g.axes.ravel():

    # add annotations
    for c in ax.containers:
        # add custom labels with the labels=labels parameter if needed
        # labels = [f'{h}' if (h := v.get_height()) > 0 else '' for v in c]
        ax.bar_label(c, label_type='edge')
    ax.margins(y=0.2)
g.set_ylabels("Résztvevők (#)")
g.set_xlabels("MOME képzés (#)")
plt.show()
