# Conda env
```
conda create -n fchk python=3.12
```
```
conda activate fchk
```
```  
pip install -r requirements.txt
```

# Function Output Check

I want to create a streamlit app that checks that the output of the function match before and after a release.

It should be user friendly and allow users to add new functions to be tested.

The app should have the following features:

- Create new function call
- Run function call
- Compare by running the same function call

## Create new function call
It should be a page where the user writes:
- function complete name (with the module path)
- function name (that will match the folder in which the results for that function will be stored)
- key columns: which should be saved as a list (it can be empty)
- add function parameters:
    - for each parameter the user should be able to add:
        - parameter name
        - parameter type (int, float, str, date, boolean)
        - range from where the parameter will be sampled (min and max values - in case of date - the user can select "today" as min/max values)
        - specific values to be used instead of the range ()
        - if parameter value will be inside a list or not
        - if the parameter value is inside a list, how many elements the list should have (the user can define it as [min, max] or a specific number)


The idea is that this function will be called multiple time and the parameters will be generated randomly based on those inputs.

Once the user saves the function call, it should be stored in a JSON file that will be used to generate the parameters for the function calls.

The user also has the option to edit this function call and delete it.

## Check Function Calls
Once you’ve created and saved function calls, go to the Streamlit sidebar and select “Check Function Calls” to view all saved calls in a table showing:
- **full_name**: module path + function
- **name**: your identifier
- **parameters**: comma-separated list of parameter names

In it, you can "edit" the function:
- if you choose to edit, you have the option to alter the parameters, add and remove parameters, and save the changes.
- you cannot change the function name or the full name of the function.

## Run Function Call
The user should have the option to run functions. The user can select a function call from the table and run it. They can define how many times they want to run that function and where the results will be stored.

For each time they run the function, the app should generate random parameters based on the saved function call.

Furthermore, the user can define where the results will be placed. When defining to run they should say how many times it will run and where it will be stored, which should be a string with a folder or a folder path. If the folder does not exist yet, the app should create it. It should all be inside the subfolder of the project folder called `data/results`. Furthermore, the functon name should be used to define an extra subfolder. For instance, if the user defines that they want the result to be in "prd/pre" and the function name is "my_function", the results will be stored in `data/results/prd/pre/my_function/`.

The result should be saved as a pickle file that should be a dictionary. It should have:
- the actual result in the key `result`
- the parameters used in the key `parameters`
- the timestamp of the run in the key `timestamp`
- the time it took to run the function in the key `time`

the name of the pickle file should be "run_{yyyymmddhhmmss}.pkl" where the timestamp is the time when the function was run.

## Rerun Function
This part here should allow the user to specify the function they want to rerun, from which folder they are getting the parameters and to which folder they will save the rerun.

Furthermore, you can specify a datetime from which you want to start the rerun. Every function call is saved with a timestamp, so you can filter the function calls by the timestamp. If you specify a datetime, the app will only rerun the functions that were run after that datetime.

Thus, we are talking about the following inputs:
- function
- from folder (where the parameters are stored)
- to folder (where the results will be stored)
- datetime (optional, if not specified, all function calls will be rerun)

In order to be able to rerun, you have to read the pickle file and extract the parameters.

## Compare Calls
This part should allow the user to compare the results of two function calls. The user can select two folders from where the results will be taken to compare.

First, we should take only the files that match name in both folders: `run_{yyyymmddhhmmss}.pkl`.

Once both files are selected, the app should read the pickle file from both and get the results.

There are three levels of checks:
- check if the results are both dataframes 
- check the number of columns
- compare the results checking row by row

The app should return all the comparison results in a table with the following columns:
- one column for each parameter in the function (for instance, if the parameter is `param1`, the columns will be `param1_before` and `param1_after`):
- column that says if both results are dataframes or not (if both results are dataframes or both results are NOT dataframes, return a "Check" otherwise return "X")
- column that says if the number of columns is the same or not (if both results have the same number of columns, return a "Check" otherwise return "X"). It should only do this check if the results are dataframes.
- column that says if the results are the same or not (if both results are the same, return a "Check" otherwise return "X"). It should only do this check if the results are dataframes.
- finally, there should be a column with the button detail, in which you can view the results of the function before and after.