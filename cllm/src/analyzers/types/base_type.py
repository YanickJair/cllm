from typing import Any

from pydantic import BaseModel


class Type(BaseModel):
    """Base class to support types definition"""
    def format(self) -> Any:
        raise NotImplementedError
