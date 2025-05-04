import random
from datetime import date, timedelta
from models.parameter_definition import ParameterDefinition

def _to_date(val):
    if isinstance(val, date):
        return val
    if isinstance(val, str) and val.lower() == "today":
        return date.today()
    raise ValueError(val)

def generate_value(param: ParameterDefinition):
    # pick a single value
    def pick_one():
        if param.specific_values:
            return random.choice(param.specific_values)
        if param.range:
            low, high = param.range
            if param.type == "int":
                return random.randint(int(low), int(high))
            if param.type == "float":
                return random.uniform(float(low), float(high))
            if param.type == "date":
                d0, d1 = _to_date(low), _to_date(high)
                span = (d1 - d0).days
                return d0 + timedelta(days=random.randint(0, span))
        # fallback
        return None

    if param.is_list:
        ln = param.list_length
        count = ln if isinstance(ln, int) else random.randint(*ln)
        return [pick_one() for _ in range(count)]
    else:
        return pick_one()

def generate_parameters(params: list[ParameterDefinition]) -> dict:
    return {p.name: generate_value(p) for p in params}
