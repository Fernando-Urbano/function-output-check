import os
import json
from dataclasses import asdict
from typing import List

from models.function_call import FunctionCall
from models.parameter_definition import ParameterDefinition

# Path to your JSON backing store
FUNCTION_CALLS_PATH = os.path.join("data", "function_calls.json")

def load_function_calls() -> List[FunctionCall]:
    """
    Reads all saved FunctionCall definitions from JSON.
    Returns an empty list if the file doesn't exist or is empty.
    """
    if not os.path.exists(FUNCTION_CALLS_PATH):
        return []

    with open(FUNCTION_CALLS_PATH, "r") as f:
        try:
            raw = json.load(f)
        except json.JSONDecodeError:
            return []

    calls: List[FunctionCall] = []
    for item in raw:
        params = []
        for p in item.get("parameters", []):
            # Normalize range (stored as list) to tuple
            range_val = tuple(p["range"]) if p.get("range") is not None else None
            # Normalize list_length
            ll = p.get("list_length")
            if isinstance(ll, list):
                list_length_val = tuple(ll)
            else:
                list_length_val = ll

            params.append(ParameterDefinition(
                name=p["name"],
                type=p["type"],
                range=range_val,
                specific_values=p.get("specific_values"),
                is_list=p.get("is_list", False),
                list_length=list_length_val
            ))

        calls.append(FunctionCall(
            full_name=item["full_name"],
            name=item["name"],
            key_columns=item.get("key_columns", []),
            parameters=params
        ))

    return calls


def save_function_calls(calls: List[FunctionCall]) -> None:
    """
    Overwrites the JSON file with the current list of FunctionCall objects.
    """
    os.makedirs(os.path.dirname(FUNCTION_CALLS_PATH), exist_ok=True)
    with open(FUNCTION_CALLS_PATH, "w") as f:
        # asdict will convert dataclasses to dicts; default=str makes dates into "YYYY-MM-DD"
        json.dump(
            [asdict(call) for call in calls],
            f,
            indent=4,
            default=str
        )


def add_function_call(call: FunctionCall) -> None:
    """
    Adds a new FunctionCall (and saves).
    Raises ValueError if a call with the same name already exists.
    """
    calls = load_function_calls()
    if any(existing.name == call.name for existing in calls):
        raise ValueError(f"A function call named '{call.name}' already exists.")
    calls.append(call)
    save_function_calls(calls)


def delete_function_call(name: str) -> None:
    """
    Removes the FunctionCall with the given name (and saves).
    """
    calls = load_function_calls()
    filtered = [c for c in calls if c.name != name]
    save_function_calls(filtered)    # <-- actually invoke save


def update_function_call(updated: FunctionCall) -> None:
    """
    Replace an existing FunctionCall (matched by .name) in the store.
    """
    calls = load_function_calls()
    for idx, existing in enumerate(calls):
        if existing.name == updated.name:
            calls[idx] = updated
            save_function_calls(calls)
            return
    raise ValueError(f"No function call named '{updated.name}' found.")