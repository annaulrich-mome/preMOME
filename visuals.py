import matplotlib.pyplot as plt
import seaborn as sns

merged_all = pd.concat([merged, felvi_neptun_elokeszitok], ignore_index=True)
sns.set(font_scale=2, palette="pastel", style='whitegrid')
### Count faceted by MOME course applied
# filter for MOME courses with at least one applicant who took a preMOME course

courses = merged_all.loc[merged_all['preMOME'] == "Igen", "MOME képzés"].unique()
g = sns.catplot(data=merged_all[(merged_all['MOME képzés'].isin(courses)) &
                            (merged_all['Felvették'] != "Nem jelentkezett")],
                kind="count", x="preMOME", hue="Felvették",
                order=["Igen", "Nem"], hue_order=["Igen", "Nem"],
                col="MOME képzés", col_wrap=4, sharey=False)
g.set_titles('{col_name}')
g.set_ylabels("Jelentkezők (#)")
# iterate through axes
for ax in g.axes.ravel():

    # add annotations
    for c in ax.containers:
        ax.bar_label(c, label_type='edge')
    ax.margins(y=0.2)
#plt.show()
plt.savefig("Figure1.png")

### Count
# all applicants who got rejected will count as one, even if applied to multiple courses
merged_all_noadmission = merged_all[merged_all['Felvették'] == "Nem"]
merged_all_noadmission = merged_all_noadmission.groupby(['nev', 'Év']).apply(lambda df: df.iloc[0]).reset_index(drop=True)
merged_all_collapsed = pd.concat([merged_all_noadmission, merged_all[merged_all['Felvették'] != "Nem"]], ignore_index=True)

sns.set(font_scale=1, palette="pastel", style='whitegrid')

g = sns.catplot(data=merged_all_collapsed, kind="count", x="preMOME", hue="Felvették",
                order=["Igen", "Nem"], hue_order=["Igen", "Nem", "Nem jelentkezett"], col="Év")
g.set_titles('{col_name}')
g.set_ylabels("Jelentkezők (#)")
# iterate through axes
for ax in g.axes.ravel():

    # add annotations
    for c in ax.containers:
        ax.bar_label(c, label_type='edge')
    ax.margins(y=0.2)
#plt.show()
plt.savefig("Figure2.png")

### Percent
merged_all_collapsed_perc = (pd.crosstab(merged_all_collapsed["preMOME"], merged_all_collapsed["Felvették"])
                .apply(lambda x: x/sum(x)*100, axis=1)
                .melt(ignore_index=False))
g = sns.catplot(data=merged_all_collapsed_perc, kind="bar", x="preMOME", y="value", hue="Felvették")
g.set_ylabels("Százalék (%)")
#plt.show()
plt.savefig("Figure3.png")

### Percent without those who did not apply
merged_all_collapsed2 = merged_all_collapsed.loc[merged_all_collapsed['Felvették'] != "Nem jelentkezett"]
merged_all_collapsed_perc2 = (pd.crosstab(merged_all_collapsed2["preMOME"], merged_all_collapsed2["Felvették"])
                .apply(lambda x: x/sum(x)*100, axis=1)
                .melt(ignore_index=False))
g = sns.catplot(data=merged_all_collapsed_perc2, kind="bar", x="preMOME", y="value", hue="Felvették")
g.set_ylabels("Százalék (%)")
#plt.show()
plt.savefig("Figure4.png")


### Number of PreMOME courses taken
g = sns.catplot(data=merged_all_collapsed, kind="count", x="Kurzus szám", hue="Felvették",
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
#plt.show()
plt.savefig("Figure5.png")

merged_all_collapsed_perc3 = (pd.crosstab(merged_all_collapsed["Kurzus szám"], merged_all_collapsed["Felvették"])
                .apply(lambda x: x/sum(x)*100, axis=1)
                .melt(ignore_index=False))
g = sns.catplot(data=merged_all_collapsed_perc3, kind="bar", x="Kurzus szám", y="value", hue="Felvették")
g.set_xlabels("preMOME kurzus (#)")
g.set_ylabels("Százalék (%)")
#plt.show()
plt.savefig("Figure6.png")


### Number of MOME courses applied
merged_all_collapsed2["MOME képzés szám"] = merged_all_collapsed2["MOME képzés szám"].map(lambda x: '{0:.0f}'.format(x))
g = sns.catplot(data=merged_all_collapsed2[merged_all_collapsed2['Felvették'] != "Nem jelentkezett"],
                kind="count", x="MOME képzés szám", hue="Felvették",
                hue_order=["Igen", "Nem"])
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
#plt.show()
plt.savefig("Figure7.png")

merged_all_collapsed_perc4 = (pd.crosstab(merged_all_collapsed2["MOME képzés szám"], merged_all_collapsed2["Felvették"])
                .apply(lambda x: x/sum(x)*100, axis=1)
                .melt(ignore_index=False))
g = sns.catplot(data=merged_all_collapsed_perc4, kind="bar", x="MOME képzés szám", y="value", hue="Felvették")
g.set_xlabels("MOME képzés (#)")
g.set_ylabels("Százalék (%)")
#plt.show()
plt.savefig("Figure8.png")