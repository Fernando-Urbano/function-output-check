# streamlit_app.py
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Function Output Check", layout="wide")

st.sidebar.title("Tutorial Navigation")
page = st.sidebar.radio("Select a page:", [
    "Welcome",
    "Create Function Call", 
    "Edit Function Calls", 
    "Run Function Call", 
    "Rerun Function", 
    "Compare Calls"
])

if page == "Welcome":
    st.title("📍 PiCheck: Function Output Validator ✅")
    
    st.markdown("""
    ### Welcome to PiCheck!
    
    This app helps you verify that your functions produce consistent outputs before and after code changes.
    You can define function calls, execute them with random parameters, and then compare results
    between different environments or code versions.
    
    ### How to use this app:
    
    1. **Create Function Call** - Define which functions you want to test and how parameters should be generated
    2. **Edit Function Calls** - View and edit your saved function definitions
    3. **Run Function Call** - Execute your functions with randomly generated parameters
    4. **Rerun Function** - Re-execute functions using parameters from previous runs
    5. **Compare Calls** - Compare results between different environments to identify changes
    
    Get started by selecting an option from the sidebar!
    """)

elif page == "Create Function Call":
    st.title("Create Function Call")
    
    st.markdown("""
    ### Define a new function to test
    
    Use this form to define a function you want to test. The app will generate random parameters 
    based on your specifications and save the results for comparison.
    
    #### Required information:
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Function Complete Path", placeholder="module.submodule.function_name")
        st.text_input("Function Name (for storage)", placeholder="my_function")
        st.text_area("Key Columns (comma-separated, optional)", placeholder="id,name,value")
    
    st.markdown("### Function Parameters")
    st.markdown("""
    Define the parameters for your function. For each parameter, you can specify:
    - Parameter name
    - Data type (int, float, str, date, boolean)
    - Value range or specific values
    - List options (if the parameter should be a list)
    """)
    
    with st.expander("Add Parameter", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Parameter Name", key="param1", placeholder="param_name")
            st.selectbox("Parameter Type", ["int", "float", "str", "date", "boolean"], key="type1")
            st.checkbox("Is List?", key="is_list1")
        with col2:
            st.text_input("Min Value", key="min1", placeholder="Minimum value or 'today' for dates")
            st.text_input("Max Value", key="max1", placeholder="Maximum value or 'today' for dates")
            st.text_input("List Size (min,max or exact)", key="list_size1", placeholder="5 or 1,10")
    
    st.button("+ Add Another Parameter")
    col1, col2 = st.columns([1, 5])
    with col1:
        st.button("Save Function Call")

elif page == "Edit Function Calls":
    st.title("Edit Function Calls")
    
    st.markdown("""
    ### View and edit your saved function calls
    
    This table shows all the function calls you've defined. You can edit parameters or delete function calls.
    """)
    
    data = {
        "full_name": ["module.func1", "package.module.func2"],
        "name": ["func1", "func2"],
        "parameters": ["param1, param2", "x, y, z"],
        "actions": ["Edit", "Edit"]
    }
    
    df = pd.DataFrame(data)
    st.dataframe(df)
    
    st.markdown("""
    Click "Edit" to modify parameter settings for a function. You cannot change the function name or path after creation.
    """)

elif page == "Run Function Call":
    st.title("Run Function Call")
    
    st.markdown("""
    ### Execute functions with random parameters
    
    Select a function and specify how many times to run it. The app will generate random parameters
    based on your specifications and save the results.
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.selectbox("Select Function", ["func1", "func2", "func3"])
        st.number_input("Number of Runs", min_value=1, value=10)
        st.text_input("Results Folder", placeholder="prod/v1")
    
    with col2:
        st.markdown("""
        #### Results storage
        
        Results will be saved to:  
        `data/results/{folder}/{function_name}/`
        
        Each run creates a file:  
        `run_{timestamp}.pkl`
        
        Each file contains:
        - Function result
        - Parameters used
        - Timestamp
        - Execution time
        """)
    
    st.button("Run Function")

elif page == "Rerun Function":
    st.title("Rerun Function")
    
    st.markdown("""
    ### Re-execute functions with saved parameters
    
    This feature allows you to run a function using exact parameters from previous runs.
    Perfect for testing if code changes affect function output.
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.selectbox("Select Function", ["func1", "func2", "func3"])
        st.text_input("Source Folder (parameters)", placeholder="prod/v1")
        st.text_input("Destination Folder (results)", placeholder="prod/v2")
        st.date_input("Start Date (optional)", value=None)
        st.time_input("Start Time (optional)", value=None)
    
    with col2:
        st.markdown("""
        #### How rerunning works
        
        1. The app loads parameters from previous runs in your source folder
        2. It executes the function with these exact parameters
        3. Results are saved to the destination folder
        
        If you specify a datetime, only runs after that time will be rerun.
        
        This helps you verify that code changes don't affect function behavior.
        """)
    
    st.button("Rerun Function")

elif page == "Compare Calls":
    st.title("Compare Function Calls")
    
    st.markdown("""
    ### Compare function outputs between different environments
    
    Select two folders containing function results to compare. The app will match files
    by timestamp and check if the outputs are identical.
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.selectbox("Select Function", ["func1", "func2", "func3"])
        st.text_input("Before Folder", placeholder="prod/v1")
        st.text_input("After Folder", placeholder="prod/v2")
    
    with col2:
        st.markdown("""
        #### Comparison checks
        
        For each pair of results, the app checks:
        
        1. ✓ If both results are dataframes OR arent dataframes
        2. ✓ If they have the same number of columns
        3. ✓ If the data matches exactly
        
        Results with differences are highlighted for review.
        """)
    
    st.button("Compare Results")
    
    st.markdown("### Comparison Results")
    st.markdown("Here's what a comparison table will look like:")
    
    data = {
        "param1": [10, 20, 30],
        "param2": ["A", "B", "C"],
        "Dataframe Check": ["✅", "✅", "❌"],
        "Columns Check": ["✅", "❌", "N/A"],
        "Values Check": ["✅", "❌", "N/A"],
        "details": ["View", "View", "View"]
    }
    
    df = pd.DataFrame(data)
    st.dataframe(df)

