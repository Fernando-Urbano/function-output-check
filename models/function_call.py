from dataclasses import dataclass, field
from typing import List

from models.parameter_definition import ParameterDefinition

@dataclass
class FunctionCall:
    full_name: str
    name: str
    key_columns: List[str] = field(default_factory=list)
    parameters: List[ParameterDefinition] = field(default_factory=list)