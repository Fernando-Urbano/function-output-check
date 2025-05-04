import pandas as pd
import numpy as np

def compare_dfs(df_before, df_after, key_columns, path_before=None, path_after=None):
    df_before, df_after = join_by_key_column(df_before, df_after, key_columns)
    df_mask = df_before.compare(df_after, keep_shape=True).notnull().astype('int')
    if "index_key" in df_mask.columns:
        df_mask = df_mask.drop(columns=["index_key"])
    df_compare = df_before.compare(df_after, keep_shape=True, keep_equal=True)
    
    def highlight_changes(_):
        styles = np.where(df_mask,
                          'background-color: red',
                          '')
        return pd.DataFrame(styles, index=df_compare.index, columns=df_compare.columns)
    
    if "index_key" in df_compare.columns:
        df_compare = df_compare.drop(columns=["index_key"])
    df_compare.rename(
        columns={'self': path_before, 'other': path_after},
        level=1,
        inplace=True
    )
    return df_compare.style.apply(highlight_changes, axis=None)


def join_by_key_column(
        df_before: pd.DataFrame, df_after: pd.DataFrame, key_columns: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    if not key_columns:
        df_before = df_before.reset_index().rename(columns={'index': 'index_key'})
        df_after  = df_after.reset_index().rename(columns={'index': 'index_key'})
        key_columns = ['index_key']
    key_column_values = set([tuple(v) for v in list(df_before[key_columns].values)])
    key_column_values.update(set([tuple(v) for v in list(df_after[key_columns].values)]))
    key_column_df = pd.DataFrame(list(key_column_values), columns=key_columns)
    df_before = key_column_df.merge(df_before, on=key_columns, how='left', suffixes=('', '_before'))
    df_after = key_column_df.merge(df_after, on=key_columns, how='left', suffixes=('', '_after'))
    return df_before, df_after
    


if __name__ == "__main__":
    df1 = pd.DataFrame({
        'id': [1, 2, 3],
        'id2': [10, 30, 30],
        'value': ['A', 'B', 'C']
    })
    
    df2 = pd.DataFrame({
        'id': [2, 3, 4],
        'id2': [10, 20, 30],
        'value': ['B', 'C', 'D']
    })
    
    key_cols = ['id', 'id2']
    compare_dfs(df1, df2, key_cols)
