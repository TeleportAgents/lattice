from dataclasses import dataclass


@dataclass
class Entity:
    _id: str
    function_name: str
    namespace: str
    definition: str
