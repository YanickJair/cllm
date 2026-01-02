from clm_core.config.schemas import CLMConfig
from clm_core.types import CLMOutput, SDCompressionConfig
from clm_core.components.sys_prompt import SysPromptConfig
from .encoder import CLMEncoder

from .__version__ import __description__, __title__, __version__

__all__ = [
    "__version__",
    "__title__",
    "__description__",
    "CLMEncoder",
    "CLMConfig",
    "CLMOutput",
    "SysPromptConfig",
    "SDCompressionConfig"
]

__locals = locals()
for __name in __all__:
    if not __name.startswith("__"):
        setattr(__locals[__name], "__module__", "clm_core")
