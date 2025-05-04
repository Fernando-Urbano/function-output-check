import streamlit as st
from typing import Optional, Tuple, List, Union, Any
from datetime import date
from dataclasses import asdict

from models.parameter_definition import ParameterDefinition
from models.function_call import FunctionCall

def render_function_call_form(
    existing: Optional[Union[dict, FunctionCall]] = None,
    disable_basic: bool = False,
    key_prefix: str = "",
) -> Optional[FunctionCall]:

    def _get(obj: Any, key: str, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    full_name_def = _get(existing, "full_name", "") if existing else ""
    name_def      = _get(existing, "name",      "") if existing else ""
    raw_params    = _get(existing, "parameters", []) if existing else []
    default_keys  = _get(existing, "key_columns", []) if existing else []

    params_def: List[dict] = []
    for p in raw_params:
        if isinstance(p, dict):
            params_def.append(p)
        else:
            params_def.append(asdict(p))

    full_name = st.text_input(
        "Function full name (module.path.func)",
        value=full_name_def,
        disabled=disable_basic,
        key=f"{key_prefix}_full_name"
    )
    name = st.text_input(
        "Function identifier (used as storage folder name)",
        value=name_def,
        disabled=disable_basic,
        key=f"{key_prefix}_name"
    )

    raw_keys = st.text_input(
        "Key Columns (comma-separated)",
        value=",".join(default_keys),
        disabled=False,
        key=f"{key_prefix}_key_columns"
    )
    key_columns = [k.strip() for k in raw_keys.split(",") if k.strip()]

    count_key = f"{key_prefix}_param_count"
    if count_key not in st.session_state:
        st.session_state[count_key] = len(params_def)

    if st.button("Add parameter", key=f"{key_prefix}_add_param"):
        st.session_state[count_key] += 1

    params: List[ParameterDefinition] = []
    for i in range(st.session_state[count_key]):
        st.subheader(f"Parameter {i + 1}")
        param_def = params_def[i] if i < len(params_def) else {}
        p_name = st.text_input(
            "Name",
            value=param_def.get("name", ""),
            key=f"{key_prefix}_param_{i}_name"
        )
        p_type = st.selectbox(
            "Type",
            ["int", "float", "str", "date", "boolean"],
            index=["int", "float", "str", "date", "boolean"].index(param_def.get("type", "str")),
            key=f"{key_prefix}_param_{i}_type"
        )

        range_val: Optional[Tuple[Union[int, float, date], Union[int, float, date]]] = None
        if p_type in ("int", "float"):
            raw_r = param_def.get("range")
            if isinstance(raw_r, (list, tuple)) and len(raw_r) == 2:
                rd = list(raw_r)
            else:
                rd = [None, None]

            low = st.text_input(
                "Range min",
                value=str(rd[0] or ""),
                key=f"{key_prefix}_param_{i}_range_min"
            )
            high = st.text_input(
                "Range max",
                value=str(rd[1] or ""),
                key=f"{key_prefix}_param_{i}_range_max"
            )
            if low or high:
                range_val = (low, high)

        elif p_type == "date":
            range_key = f"{key_prefix}_param_{i}_range"
            if range_key in st.session_state:
                val = st.session_state[range_key]
                if not (
                    isinstance(val, (tuple, list))
                    and len(val) == 2
                    and all(isinstance(d, date) for d in val)
                ):
                    del st.session_state[range_key]

            default = param_def.get("range", (date.today(), date.today()))
            selected = st.date_input(
                "Date range",
                key=range_key,
                value=default
            )
            if isinstance(selected, tuple):
                range_val = tuple(selected)

        spec_vals = param_def.get("specific_values") or []
        spec_raw = st.text_input(
            "Specific values (comma-separated)",
            value=",".join(map(str, spec_vals)),
            key=f"{key_prefix}_param_{i}_specific"
        )
        specific_values = None
        if spec_raw:
            raw_vals = [v.strip() for v in spec_raw.split(",")]
            if p_type == "int":
                specific_values = []
                for v in raw_vals:
                    try:
                        specific_values.append(int(v))
                    except ValueError:
                        specific_values.append(v)
            elif p_type == "float":
                specific_values = []
                for v in raw_vals:
                    try:
                        specific_values.append(float(v))
                    except ValueError:
                        specific_values.append(v)
            elif p_type == "boolean":
                specific_values = []
                for v in raw_vals:
                    lv = v.lower()
                    if lv in ("true", "false"):
                        specific_values.append(lv == "true")
                    else:
                        specific_values.append(v)
            else:
                specific_values = raw_vals

        is_list = st.checkbox(
            "Parameter is a list?",
            value=param_def.get("is_list", False),
            key=f"{key_prefix}_param_{i}_is_list"
        )
        list_length: Union[int, Tuple[int, int], None] = None
        if is_list:
            length_raw = st.text_input(
                "List length (int or min,max)",
                value=str(param_def.get("list_length", "")),
                key=f"{key_prefix}_param_{i}_list_length"
            )
            if length_raw:
                if "," in length_raw:
                    parts = length_raw.split(",")
                    try:
                        list_length = (int(parts[0]), int(parts[1]))
                    except ValueError:
                        list_length = None
                else:
                    try:
                        list_length = int(length_raw)
                    except ValueError:
                        list_length = None

        params.append(
            ParameterDefinition(
                name=p_name,
                type=p_type,
                range=range_val,
                specific_values=specific_values,
                is_list=is_list,
                list_length=list_length
            )
        )

    if st.button("Save Function Call", key=f"{key_prefix}_save"):
        return FunctionCall(
            full_name=full_name,
            name=name,
            key_columns=key_columns,
            parameters=params
        )

    return None
