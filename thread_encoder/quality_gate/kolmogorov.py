import zlib
from typing import Any, Annotated

from annotated_doc import Doc

from . import KolmogorovModel


class KolmogorovAnalyzer:
    """
    Approximates Kolmogorov complexity using zlib compression.

    Core insight: K(x) ≈ len(zlib.compress(x))
    If K(compressed) ≤ K(original), the CLLM output is structurally
    at least as information-dense as the original.

    We also measure information efficiency: how many bits of compressed
    zlib output exist per raw character. Higher = more information dense.
    """

    COMPLEXITY_THRESHOLD = 0.85

    def analyze(
        self,
        original: Annotated[
            Any, Doc("The original input string (before CLM compression).")
        ],
        compressed: Annotated[
            str,
            Doc("The CLM compressed output string to compare against the original."),
        ],
    ) -> KolmogorovModel:
        orig_bytes = original.encode("utf-8")
        clm_bytes = compressed.encode("utf-8")

        orig_zlib = zlib.compress(orig_bytes, level=9)
        clm_zlib = zlib.compress(clm_bytes, level=9)

        orig_k = len(orig_zlib)
        clm_k = len(clm_zlib)

        complexity_ratio = clm_k / orig_k

        orig_density = orig_k / len(orig_bytes)
        clm_density = clm_k / len(clm_bytes)
        information_efficiency = clm_density / orig_density

        passed = complexity_ratio <= self.COMPLEXITY_THRESHOLD

        return KolmogorovModel(
            original_bytes=len(orig_bytes),
            compressed_bytes=clm_k,
            clm_bytes=clm_k,
            original_zlib_bytes=orig_k,
            clm_zlib_bytes=clm_k,
            complexity_ratio=round(complexity_ratio, 4),
            information_efficiency=round(information_efficiency, 4),
            passed=passed,
        )
