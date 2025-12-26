from cllm.config.schemas import CLMConfig, CLMOutput
from cllm.core.encoder import CLMEncoder

from .__version__ import __description__, __title__, __version__

__all__ = [
    "__version__",
    "__title__",
    "__description__",
    "CLMEncoder",
    "CLMConfig",
    "CLMOutput",
]

__locals = locals()
for __name in __all__:
    if not __name.startswith("__"):
        setattr(__locals[__name], "__module__", "cllm")
