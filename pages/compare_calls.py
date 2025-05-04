import os
import json
import pickle
from datetime import datetime
from pathlib import Path
import streamlit as st
import pandas as pd
import glob
from importlib import import_module
from utils.compare_dfs import compare_dfs

def stringify_keys(d):
    if isinstance(d, dict):
        return {str(k): stringify_keys(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [stringify_keys(i) for i in d]
    else:
        return d

st.title("🔍 Compare Function Calls")

# ensure keys exist
if 'records' not in st.session_state:
    st.session_state['records'] = []
    st.session_state['df_records'] = None

json_path = os.path.join(os.getcwd(), "data", "function_calls.json")
try:
    with open(json_path, "r") as f:
        function_calls = json.load(f)
except Exception as e:
    st.error(f"Error loading function calls: {e}")
    st.stop()

options = {f'{fc["full_name"]} ({fc["name"]})': fc for fc in function_calls}
selected_key = st.selectbox("Select a function", list(options.keys()))
selected_function = options[selected_key]
fn_name = selected_function["name"]

base_results_path = os.path.join(os.getcwd(), "data", "results")
folder_candidates = []
base_path = Path(base_results_path)
for candidate in base_path.rglob('*'):
    if candidate.is_dir() and (candidate / fn_name).is_dir():
        folder_candidates.append(str(candidate.relative_to(base_path)))
folder_candidates = list(set(folder_candidates))
if not folder_candidates:
    st.error("No available result folders found for the selected function.")
    st.stop()

path_before = st.selectbox("Select 'Path Before'", folder_candidates, key="before")
path_after = st.selectbox("Select 'Path After'", folder_candidates, key="after")

if st.button("Compare Calls"):
    abs_before = os.path.join(base_results_path, path_before, fn_name)
    abs_after = os.path.join(base_results_path, path_after, fn_name)
    if not (os.path.exists(abs_before) and os.path.exists(abs_after)):
        st.error("One of the selected folders does not exist.")
        st.stop()

    files_before = set([f for f in os.listdir(abs_before) if f.startswith("run_") and f.endswith(".pkl")])
    files_after = set([f for f in os.listdir(abs_after) if f.startswith("run_") and f.endswith(".pkl")])
    common_files = files_before.intersection(files_after)

    if not common_files:
        st.warning("No matching run files found between the two folders.")
    else:
        records = []
        for fname in sorted(common_files):
            fpath_before = os.path.join(abs_before, fname)
            fpath_after = os.path.join(abs_after, fname)
            with open(fpath_before, "rb") as fb, open(fpath_after, "rb") as fa:
                data_before = pickle.load(fb)
                data_after = pickle.load(fa)

            params_before = data_before.get("parameters", {})
            params_after = data_after.get("parameters", {})
            record = {"File": fname}
            all_params = set(list(params_before.keys()) + list(params_after.keys()))
            for key in all_params:
                assert params_before.get(key, "N/A") == params_after.get(key, "N/A"), \
                    f"Parameter '{key}' differs between before and after for file {fname}"
                record[f"{key}"] = params_before.get(key, "N/A")

            result_before = data_before.get("result")
            result_after = data_after.get("result")

            is_df_before = isinstance(result_before, pd.DataFrame)
            is_df_after = isinstance(result_after, pd.DataFrame)
            data_frame_before_check = "✅" if is_df_before else "❌"
            data_frame_after_check = "✅" if is_df_after else "❌"
            record["DataFrame Check"] = data_frame_before_check + " " + data_frame_after_check

            record["Columns Check"] = "-"
            record["Values Check"] = "-"
            detail = {}
            if is_df_before and is_df_after:
                record["Columns Check"] = "✅" if result_before.shape[1] == result_after.shape[1] else "❌"
                cmp_df = compare_dfs(result_before, result_after, selected_function.get("key_columns", []), path_before, path_after)
                
                record["Values Check"] = "✅" if result_before.equals(result_after) else "❌"
                detail = cmp_df
            else:
                detail = pd.DataFrame({"before": [str(result_before)], "after": [str(result_after)]})

            record["_detail"] = detail
            records.append(record)

        df_records = pd.DataFrame(records)
        st.session_state['records'] = records
        st.session_state['df_records'] = df_records

# render results (persists across reruns)
if st.session_state['records']:
    df_records = st.session_state['df_records']
    records    = st.session_state['records']

    st.subheader("Comparison Results")
    st.dataframe(df_records.drop(columns=["_detail"]).style.set_properties(**{'text-align': 'center'}))

    search_term = st.text_input("Search Files", "")
    if search_term:
        filtered_records = [rec for rec in records if search_term.lower() in rec["File"].lower()]
    else:
        filtered_records = records

    for rec in filtered_records:
        with st.expander(f"Detail for {rec['File']}"):
            st.dataframe(rec["_detail"])