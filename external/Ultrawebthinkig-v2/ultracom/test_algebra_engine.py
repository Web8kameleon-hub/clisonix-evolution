from app.algebra import get_binary_algebra


def main() -> None:
    engine = get_binary_algebra()

    single = engine.operate(255, "xor", 170, 8)
    assert single.value == 85, "XOR mismatch"

    sequential_ops = [
        {"operation": "xor", "operand_a": 255, "operand_b": 15, "bits": 8},
        {"operation": "and", "operand_a": 240, "operand_b": 170, "bits": 8},
    ]
    seq_results, seq_errors, seq_final = engine.batch(sequential_ops, mode="sequential")
    assert len(seq_errors) == 0, "Sequential should not error"
    assert len(seq_results) == 2, "Sequential should produce 2 results"
    assert seq_final == seq_results[-1]["result"], "Sequential final mismatch"

    chain_ops = [
        {"operation": "xor", "operand_a": 255, "operand_b": 15, "bits": 8},
        {"operation": "shl", "operand_a": 0, "operand_b": 1, "bits": 8},
    ]
    chain_results, chain_errors, chain_final = engine.batch(
        chain_ops,
        mode="chain",
        chain_intermediate=True,
    )
    assert len(chain_errors) == 0, "Chain should not error"
    assert chain_results[0]["result"] == 240, "Chain first op mismatch"
    assert chain_results[1]["operand_a"] == 240, "Chain should reuse previous result"
    assert chain_final == 224, "Chain final mismatch"

    print("OK: algebra engine smoke test passed")


if __name__ == "__main__":
    main()
