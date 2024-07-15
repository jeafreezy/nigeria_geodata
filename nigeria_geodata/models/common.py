from dataclasses import dataclass


@dataclass(frozen=True)
class DataSourceInfo:
    name: str
    url: str
    description: str
