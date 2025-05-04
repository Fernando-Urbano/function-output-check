import streamlit as st
import os
import json
import time
import pickle
import random
import importlib
import inspect
from datetime import datetime

st.set_page_config(page_title="Run Function", page_icon="▶️")

def generate_random_value(param):
    def sample_value(p_type, rng):
        if p_type == "int":
            return random.randint(int(rng[0]), int(rng[1]))
        elif p_type == "float":
            return random.uniform(float(rng[0]), float(rng[1]))
        elif p_type == "str":
            return "sample"
        elif p_type == "date":
            return datetime.today().strftime("%Y-%m-%d")
        elif p_type == "boolean":
            return random.choice([True, False])
        else:
            return None

    if param.get("specific_values"):
        value = random.choice(param["specific_values"])
    else:
        value = sample_value(param["type"], param.get("range", [0, 1]))
        
    if param.get("is_list", False):
        list_len = param.get("list_length")
        if isinstance(list_len, list):
            count = random.randint(int(list_len[0]), int(list_len[1]))
        else:
            count = int(list_len)
        value = [value for _ in range(count)]
    return value

def load_function_calls():
    json_path = os.path.join(os.getcwd(), "data/function_calls.json")
    if not os.path.exists(json_path):
        st.error("No function_calls.json file found!")
        return []
    with open(json_path, "r") as f:
        return json.load(f)

st.title("▶️ Run Function")

function_calls = load_function_calls()
if not function_calls:
    st.stop()

options = {f'{fc["full_name"]} ({fc["name"]})': fc for fc in function_calls}
selected_key = st.selectbox("Select a function to run", list(options.keys()))
selected_function = options[selected_key]

st.write("Selected Function Call:")
st.write(f"Full name: {selected_function['full_name']}")
st.write(f"Identifier: {selected_function['name']}")
st.write(f"Parameters: {', '.join([p['name'] for p in selected_function.get('parameters', [])])}")

num_runs = st.number_input("Number of runs", min_value=1, step=1, value=1)
results_folder_input = st.text_input("Results folder (e.g., 'prd/pre')", value="prd/pre")

if st.button("Run Function"):
    results_saved = []
    for i in range(num_runs):
        params = {}
        for param in selected_function.get("parameters", []):
            params[param["name"]] = generate_random_value(param)

        full_name = selected_function["full_name"]
        if '.' not in full_name:
            st.error("Invalid full_name format. Expected a full name with module path (e.g., 'module.submodule.function').")
            st.stop()
        module_path, func_name = full_name.rsplit(".", 1)
        mod = importlib.import_module(module_path)
        func = getattr(mod, func_name)

        start_time = time.time()
        try:
            result = func(**params)
        except TypeError as te:
            msg = str(te)
            if "takes no keyword arguments" in msg or "positional-only" in msg:
                sig = inspect.signature(func)
                pos_args = []
                kw_args = {}
                for name, param in sig.parameters.items():
                    if param.kind == inspect.Parameter.POSITIONAL_ONLY:
                        pos_args.append(params[name])
                    else:
                        kw_args[name] = params[name]
                result = func(*pos_args, **kw_args)
            else:
                raise
        except Exception as e:
            result = f"Function call error: {e}"
        elapsed = time.time() - start_time
        run_timestamp = datetime.now()
        timestamp_str = run_timestamp.strftime("%Y%m%d%H%M%S%f")
        
        result_dict = {
            "result": result,
            "parameters": params,
            "timestamp": run_timestamp.isoformat(),
            "time": elapsed
        }
        
        base_path = os.path.join(os.getcwd(), "data", "results", results_folder_input, selected_function["name"])
        os.makedirs(base_path, exist_ok=True)
        file_name = f"run_{timestamp_str}.pkl"
        file_path = os.path.join(base_path, file_name)
        
        with open(file_path, "wb") as f:
            pickle.dump(result_dict, f)
        results_saved.append(file_path)
    
    st.success("Function runs completed!")
    st.write("Saved files:")
    for path in results_saved:
        st.write(path)
