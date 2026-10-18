from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union


NumberLike = Union[int, "BinaryNumber"]


@dataclass
class BinaryNumber:
    value: int
    bits: int = 64

    def __post_init__(self) -> None:
        self.bits = max(1, min(64, int(self.bits)))
        self.value = self.value & ((1 << self.bits) - 1)

    @property
    def binary(self) -> str:
        return format(self.value, f"0{self.bits}b")

    @property
    def hex(self) -> str:
        return format(self.value, f"0{max(1, self.bits // 4)}x")

    @property
    def bytes(self) -> bytes:
        size = max(1, (self.bits + 7) // 8)
        return self.value.to_bytes(size, "big", signed=False)

    def to_dict(self) -> Dict[str, Any]:
        ones_count = self.binary.count("1")
        return {
            "value": self.value,
            "binary": self.binary,
            "hex": self.hex,
            "bits": self.bits,
            "ones_count": ones_count,
            "zeros_count": self.bits - ones_count,
        }


class BinaryAlgebraEngine:
    def __init__(self) -> None:
        self.history: List[Dict[str, Any]] = []

    @staticmethod
    def _mask(bits: int) -> int:
        normalized = max(1, min(64, int(bits)))
        return (1 << normalized) - 1

    @staticmethod
    def _to_num(value: NumberLike, bits: int) -> BinaryNumber:
        if isinstance(value, BinaryNumber):
            return BinaryNumber(value.value, bits)
        return BinaryNumber(int(value), bits)

    def operate(self, a: NumberLike, op: str, b: Optional[NumberLike] = None, bits: int = 64) -> BinaryNumber:
        normalized_bits = max(1, min(64, int(bits)))
        left = self._to_num(a, normalized_bits)
        right = self._to_num(0 if b is None else b, normalized_bits)
        op_l = op.lower()
        mask = self._mask(normalized_bits)

        if op_l in ("and", "&"):
            result = left.value & right.value
        elif op_l in ("or", "|"):
            result = left.value | right.value
        elif op_l in ("xor", "^"):
            result = left.value ^ right.value
        elif op_l in ("not", "~"):
            result = ~left.value
        elif op_l == "nand":
            result = ~(left.value & right.value)
        elif op_l == "nor":
            result = ~(left.value | right.value)
        elif op_l == "xnor":
            result = ~(left.value ^ right.value)
        elif op_l in ("shl", "<<"):
            result = left.value << right.value
        elif op_l in ("shr", ">>"):
            result = left.value >> right.value
        elif op_l == "rol":
            shift = right.value % normalized_bits
            result = ((left.value << shift) | (left.value >> (normalized_bits - shift))) & mask
        elif op_l == "ror":
            shift = right.value % normalized_bits
            result = ((left.value >> shift) | (left.value << (normalized_bits - shift))) & mask
        elif op_l in ("add", "+"):
            result = left.value + right.value
        elif op_l in ("sub", "-"):
            result = left.value - right.value
        elif op_l in ("mul", "*"):
            result = left.value * right.value
        elif op_l in ("div", "/"):
            result = 0 if right.value == 0 else left.value // right.value
        elif op_l in ("mod", "%"):
            result = 0 if right.value == 0 else left.value % right.value
        else:
            raise ValueError(f"Unsupported operation: {op}")

        out = BinaryNumber(result, normalized_bits)
        self.history.append(
            {
                "op": op_l,
                "a": left.value,
                "b": right.value if b is not None else None,
                "bits": normalized_bits,
                "result": out.value,
                "timestamp": datetime.now().isoformat(),
            }
        )
        return out

    def operate_raw(self, a: int, op: str, b: int = 0, bits: int = 64) -> bytes:
        return self.operate(a, op, b, bits).bytes

    def batch(
        self,
        operations: List[Dict[str, Any]],
        mode: str = "sequential",
        chain_intermediate: bool = False,
        stop_on_error: bool = True,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Optional[int]]:
        results: List[Dict[str, Any]] = []
        errors: List[Dict[str, Any]] = []
        previous_result = 0

        for idx, item in enumerate(operations):
            try:
                operation = str(item.get("operation", "and"))
                operand_a = int(item.get("operand_a", 0))
                operand_b = int(item.get("operand_b", 0))
                bits = int(item.get("bits", 64))

                if mode == "chain" and chain_intermediate and idx > 0:
                    operand_a = previous_result

                result_num = self.operate(operand_a, operation, operand_b, bits)
                previous_result = result_num.value

                results.append(
                    {
                        "index": idx,
                        "operation": operation.upper(),
                        "operand_a": operand_a,
                        "operand_b": operand_b,
                        "result": result_num.value,
                        "result_binary": result_num.binary,
                        "bits": bits,
                        "success": True,
                    }
                )
            except Exception as exc:
                errors.append({"index": idx, "error": str(exc), "error_code": 1})
                if stop_on_error:
                    break

        final_result = results[-1]["result"] if results else None
        return results, errors, final_result

    def get_stats(self) -> Dict[str, Any]:
        return {
            "operations_history": len(self.history),
            "last_operations": self.history[-5:] if self.history else [],
        }


_algebra: Optional[BinaryAlgebraEngine] = None


def get_binary_algebra() -> BinaryAlgebraEngine:
    global _algebra
    if _algebra is None:
        _algebra = BinaryAlgebraEngine()
    return _algebra
