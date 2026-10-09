"""
XLC — eXtreme Latency Codec (WWWMMM)

Paketa kryesore eksporton:
  - XLCCodec   : encoder/decoder me matrix projection
  - XLCPacket  : paketa e enkoduar
  - XLCResult  : rezultati i dekodimit
  - WWWMMM     : 6-dimensional resonance profile
  - ALPHABET   : 26-shkronja alfabet i parakompjutuar

Shembull i shpejtë:
    from xlc import XLCCodec

    codec = XLCCodec()
    packet = codec.encode("A")
    result = codec.decode_packet(packet)
    # result.symbol == "A", result.decode_latency_ns < 10_000
"""

from xlc_alphabet import ALPHABET, WWWMMM  # type: ignore
from xlc_codec import XLCCodec, XLCPacket, XLCResult  # type: ignore
from xlc_command_router import RouteResult, XLCCommandRouter  # type: ignore
from xlc_inspector import XLCInspectionReport, XLCInspector  # type: ignore
from xlc_key import XLCKey  # type: ignore
from xlc_layers import LayerBuilder, LayerPrint, LayerStack, Nanoide, StackSimilarity  # type: ignore
from xlc_lock import LockResult, XLCLock  # type: ignore

__all__ = [
    "XLCCodec",
    "XLCPacket",
    "XLCResult",
    "WWWMMM",
    "ALPHABET",
    "XLCKey",
    "XLCLock",
    "LockResult",
    "LayerBuilder",
    "LayerStack",
    "LayerPrint",
    "StackSimilarity",
    "Nanoide",
    "XLCInspectionReport",
    "XLCInspector",
    "XLCCommandRouter",
    "RouteResult",
]
