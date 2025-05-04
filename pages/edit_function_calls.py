import json
import streamlit as st
from pathlib import Path
import sys, os
import shutil

from components.function_call_form import render_function_call_form
from services.validation_service import validate_function_call
from services.storage_service import update_function_call, delete_function_call

st.set_page_config(page_title="Edit Function Calls", page_icon="📝")

def clean_function_output(function_name):
    try:
        root = Path.cwd()
        results_dir = root / "data" / "results"
        
        if not results_dir.exists():
            st.warning(f"Results directory not found at {results_dir}")
            return False
        
        cleaned_dirs = []
        
        for path in results_dir.glob(f"**/{function_name}"):
            if path.is_dir():
                cleaned_dirs.append(str(path.relative_to(root)))
                shutil.rmtree(path)
        
        if cleaned_dirs:
            st.success(f"Cleaned output directories:\n\n" + "\n\n".join(cleaned_dirs))
            return True
        else:
            st.warning(f"No output directories found for function '{function_name}'")
            return False
            
    except Exception as e:
        st.error(f"Error cleaning output for '{function_name}': {str(e)}")
        return False

def main():
    st.title("📝 Edit Function Calls")

    root = Path.cwd()
    CALLS_JSON = root / "data/function_calls.json"

    st.write("Looking for function_calls.json in:", CALLS_JSON)
    if not CALLS_JSON.exists():
        found = list(root.glob("*.json"))
        st.warning(f"No function_calls.json found. JSONs in cwd: {found}")
        return

    data = json.loads(CALLS_JSON.read_text())
    if "edit_name" not in st.session_state:
        st.session_state.edit_name = None
    if "deleted_names" not in st.session_state:
        st.session_state.deleted_names = []
    if "clean_confirm" not in st.session_state:
        st.session_state.clean_confirm = None
    if "delete_confirm" not in st.session_state:
        st.session_state.delete_confirm = None

    if st.session_state.delete_confirm:
        function_name = st.session_state.delete_confirm
        st.warning(f"Are you sure you want to delete the function '{function_name}'?")
        col1, col2 = st.columns(2)
        if col1.button("Yes, delete function", key="confirm_delete"):
            delete_function_call(function_name)
            st.session_state.deleted_names.append(function_name)
            st.session_state.delete_confirm = None
            st.session_state.edit_name = None
            st.success(f"Deleted '{function_name}'")
            st.rerun()
        if col2.button("No, cancel", key="cancel_delete"):
            st.session_state.delete_confirm = None
            st.info("Deletion cancelled.")

    if st.session_state.clean_confirm:
        function_name = st.session_state.clean_confirm
        st.warning(f"Are you sure you want to clean all output directories for function '{function_name}'?")
        col1, col2 = st.columns(2)
        if col1.button("Yes, clean outputs", key="confirm_clean"):
            clean_function_output(function_name)
            st.session_state.clean_confirm = None
        if col2.button("No, cancel", key="cancel_clean"):
            st.session_state.clean_confirm = None
            st.info("Cleanup cancelled.")

    for entry in data:
        if entry["name"] in st.session_state.deleted_names:
            continue
        names = [p["name"] for p in entry.get("parameters", [])]
        keys = entry.get("key_columns", [])
        c1, c2, c3, c4, c5, c6, c7 = st.columns([3, 2, 3, 3, 1, 1, 1])
        c1.write(entry["full_name"])
        c2.write(entry["name"])
        c3.write(", ".join(names))
        c4.write(", ".join(keys))
        if c5.button("✎", key=f"edit_{entry['name']}"):
            st.session_state.edit_name = entry["name"]
        if c6.button("✘", key=f"delete_{entry['name']}"):
            st.session_state.delete_confirm = entry["name"]
            st.rerun() 
        if c7.button("🧹", key=f"clean_{entry['name']}"):
            st.session_state.clean_confirm = entry["name"]
            st.rerun()

    if st.session_state.edit_name and any(e["name"] == st.session_state.edit_name for e in data):
        entry = next(e for e in data if e["name"] == st.session_state.edit_name)
        st.subheader(f"Edit Parameters for '{entry['name']}'")

        updated_fc = render_function_call_form(existing=entry, disable_basic=True)
        if updated_fc:
            try:
                validate_function_call(updated_fc, original_name=entry["name"])
                update_function_call(updated_fc)
                st.success(f"Updated '{updated_fc.name}'")
                st.session_state.edit_name = None
            except Exception as err:
                st.error(err)
    else:
        st.session_state.edit_name = None

if __name__ == "__main__":
    main()