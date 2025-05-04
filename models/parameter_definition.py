from dataclasses import dataclass
from typing import Any, List, Optional, Tuple, Union

@dataclass
class ParameterDefinition:
    name: str
    type: str
    range: Optional[Tuple[Any, Any]] = None
    specific_values: Optional[List[Any]] = None
    is_list: bool = False
    list_length: Union[int, Tuple[int, int], None] = None