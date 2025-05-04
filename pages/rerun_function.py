import os
import json
import pickle
import streamlit as st
from datetime import datetime
import time as timer
from importlib import import_module
import glob
from pathlib import Path

st.title("🔄 Rerun Function")

functions_json_path = os.path.join(os.getcwd(), "data", "function_calls.json")
try:
    with open(functions_json_path, "r") as f:
        available_functions = json.load(f)
except Exception as e:
    st.error(f"Error loading functions: {e}")
    available_functions = []

options = { f'{func["full_name"]} ({func["name"]})': func for func in available_functions }
selected_key = st.selectbox("Select Function", list(options.keys()))
selected_function = options[selected_key]
func_name = selected_function["name"]

base_results_path = os.path.join(os.getcwd(), "data", "results")
from_folder_candidates = []

base_path = Path(base_results_path)
for candidate in base_path.rglob('*'):
    if candidate.is_dir() and (candidate / func_name).is_dir():
        rel_path = str(candidate.relative_to(base_path))
        from_folder_candidates.append(rel_path)
from_folder_candidates = list(set(from_folder_candidates))

if not from_folder_candidates:
    st.error("Run this function before selecting Rerun or choose another function")
    st.stop()
selected_from_folder = st.selectbox("From folder", options=from_folder_candidates)

to_folder = st.text_input("To folder (relative to data/results)", "")
dt_filter_input = st.text_input("Datetime filter (YYYY-MM-DD HH:MM:SS) - optional", "")

if st.button("Run Rerun"):
    if not (selected_key and selected_from_folder and to_folder):
        st.error("Please provide all required inputs.")
    else:
        dt_filter = None
        if dt_filter_input:
            try:
                dt_filter = datetime.strptime(dt_filter_input, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                st.error("Datetime format should be YYYY-MM-DD HH:MM:SS")
                st.stop()

        abs_from = os.path.join(base_results_path, selected_from_folder, func_name)
        abs_to = os.path.join(base_results_path, to_folder, func_name)
        os.makedirs(abs_to, exist_ok=True)

        files_ran = 0
        if os.path.exists(abs_from):
            for filename in os.listdir(abs_from):
                if filename.startswith("run_") and filename.endswith(".pkl"):
                    try:
                        ts_str = filename[4:-4]
                        try:
                            file_dt = datetime.strptime(ts_str, "%Y%m%d%H%M%S%f")
                        except ValueError:
                            file_dt = datetime.strptime(ts_str, "%Y%m%d%H%M%S")
                    except Exception:
                        continue
                    if dt_filter and file_dt < dt_filter:
                        continue
                    file_path = os.path.join(abs_from, filename)
                    with open(file_path, "rb") as f:
                        data = pickle.load(f)
                    parameters = data.get("parameters", {})
                    
                    try:
                        module_path, func_attr = selected_function["full_name"].rsplit(".", 1)
                        mod = import_module(module_path)
                        func = getattr(mod, func_attr)
                    except Exception as e:
                        st.error(f"Failed to import function: {e}")
                        st.stop()
                    
                    start_time = timer.time()
                    try:
                        result = func(**parameters)
                    except TypeError as te:
                        msg = str(te)
                        if "takes no keyword arguments" in msg or "positional-only" in msg:
                            import inspect
                            sig = inspect.signature(func)
                            pos_args = []
                            kw_args = {}
                            for name, param in sig.parameters.items():
                                if param.kind == inspect.Parameter.POSITIONAL_ONLY:
                                    pos_args.append(parameters[name])
                                else:
                                    kw_args[name] = parameters[name]
                            result = func(*pos_args, **kw_args)
                        else:
                            raise
                    elapsed = timer.time() - start_time

                    new_data = {
                        "result": result,
                        "parameters": parameters,
                        "timestamp": datetime.now().isoformat(),
                        "time": elapsed
                    }
                    new_filename = filename
                    with open(os.path.join(abs_to, new_filename), "wb") as f:
                        pickle.dump(new_data, f)
                    files_ran += 1
            if files_ran:
                st.success(f"Rerun completed for {files_ran} file(s).")
            else:
                st.warning("No matching pickle files found for rerun.")
        else:
            st.error("The specified 'from folder' does not exist.")
