# rename columns and drop first few unnecessary rows, up to and including the row containing the actual column header
def rename_and_drop(df=None, str_to_find=None):
    df.columns = df.loc[df.iloc[:, 0] == str_to_find].drop_duplicates().values.flatten()
    row_index = df.index[df[str_to_find] == str_to_find].tolist()[0] +1
    df = df.tail(-row_index)
    if 'kurzus neve' in df.columns:
        return df[(df['kurzus neve'].notnull()) & (df['kurzus neve'] != 'kurzus neve')]
    else:
        return df

