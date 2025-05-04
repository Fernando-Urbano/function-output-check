import re
from datetime import date, datetime
from typing import Any, Tuple

from models.parameter_definition import ParameterDefinition
from models.function_call import FunctionCall
from services.storage_service import load_function_calls

ALLOWED_TYPES = {"int", "float", "str", "date", "boolean"}

def _to_date(val: Any) -> date:
    if isinstance(val, (date, datetime)):
        return val if isinstance(val, date) else val.date()
    if isinstance(val, str) and val.lower() == "today":
        return date.today()
    raise ValueError(f"Invalid date value: {val!r}")

def validate_parameter_definition(param: ParameterDefinition) -> None:
    errors = []

    # name must be a valid Python identifier
    if not re.match(r'^[A-Za-z_]\w*$', param.name):
        errors.append(f"name '{param.name}' is not a valid identifier")

    # type must be supported
    if param.type not in ALLOWED_TYPES:
        errors.append(f"type '{param.type}' not in {ALLOWED_TYPES}")

    # either range or specific_values — not both
    if param.range is not None and param.specific_values:
        errors.append("provide either 'range' or 'specific_values', not both")

    # range validity
    if param.range is not None:
        low, high = param.range
        if param.type in ("int", "float"):
            try:
                low, high = float(low), float(high)
                if low > high:
                    errors.append("range lower bound > upper bound")
            except (ValueError, TypeError):
                errors.append("range bounds must be convertible to numbers")
        elif param.type == "date":
            try:
                low_d, high_d = _to_date(low), _to_date(high)
                if low_d > high_d:
                    errors.append("date range lower bound > upper bound")
            except ValueError as e:
                errors.append(str(e))
        else:
            errors.append(f"range not supported for type '{param.type}'")

    # specific_values validity
    if param.specific_values:
        for v in param.specific_values:
            if param.type == "int" and not isinstance(v, int):
                errors.append(f"value {v!r} must be int")
            if param.type == "float" and not isinstance(v, (int, float)):
                errors.append(f"value {v!r} must be float")
            if param.type == "str" and not isinstance(v, str):
                errors.append(f"value {v!r} must be str")
            if param.type == "boolean" and not isinstance(v, bool):
                errors.append(f"value {v!r} must be boolean")
            if param.type == "date":
                try:
                    _to_date(v)
                except ValueError:
                    errors.append(f"value {v!r} must be date or 'today'")

    # list settings
    if param.is_list:
        if param.list_length is None:
            errors.append("list_length required when is_list=True")
        else:
            if isinstance(param.list_length, int):
                if param.list_length < 1:
                    errors.append("list_length must be ≥ 1")
            elif (
                isinstance(param.list_length, (tuple, list))
                and len(param.list_length) == 2
            ):
                mn, mx = param.list_length
                if not all(isinstance(x, int) for x in (mn, mx)):
                    errors.append("list_length bounds must be ints")
                elif mn > mx or mn < 0:
                    errors.append("invalid list_length range")
            else:
                errors.append("list_length must be int or tuple(int, int)")
    else:
        if param.list_length is not None:
            errors.append("list_length should be None when is_list=False")

    if errors:
        raise ValueError(f"Parameter '{param.name}': " + "; ".join(errors))


def validate_function_call(call: FunctionCall, original_name: str = None) -> None:
    errors = []

    # full_name syntax
    if not re.match(r'^[A-Za-z_]\w*(\.[A-Za-z_]\w*)*$', call.full_name):
        errors.append(f"full_name '{call.full_name}' is not a valid module path")

    # name syntax
    if not re.match(r'^[A-Za-z_]\w*$', call.name):
        errors.append(f"name '{call.name}' is not a valid identifier")

    # uniqueness
    existing = load_function_calls()
    for fc in existing:
        # skip comparing to itself when editing
        if fc.name == call.name and fc.name != original_name:
            errors.append(f"a function call named '{call.name}' already exists")

    # validate key_columns
    if not isinstance(call.key_columns, list) or any(not isinstance(k, str) for k in call.key_columns):
        errors.append("key_columns must be a list of strings")

    # parameter names unique
    names = [p.name for p in call.parameters]
    if len(names) != len(set(names)):
        errors.append("parameter names must be unique")

    # validate each parameter
    for p in call.parameters:
        try:
            validate_parameter_definition(p)
        except ValueError as e:
            errors.append(str(e))

    if errors:
        raise ValueError("Invalid FunctionCall: " + "; ".join(errors))