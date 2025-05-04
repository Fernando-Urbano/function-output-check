import streamlit as st

from components.function_call_form import render_function_call_form
from services.validation_service import validate_function_call
from services.storage_service import add_function_call

def main():
    st.title("🚀 Create New Function Call")

    new_call = render_function_call_form()

    if new_call:
        try:
            validate_function_call(new_call)
            add_function_call(new_call)
            st.success(f"Function call '{new_call.name}' saved successfully.")
        except Exception as err:
            st.error(f"Error: {err}")

if __name__ == "__main__":
    main()
