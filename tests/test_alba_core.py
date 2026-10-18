import json

import pytest

from alba_core import AlbaCore, SignalFrame


def test_signal_frame_validates_and_calculates_mean_squared_power():
    channels = {"F3": -2, "F4": 4}
    metadata = {"source": "device-1"}

    frame = SignalFrame(timestamp=0, channels=channels, metadata=metadata)
    channels["F3"] = 100

    assert frame.timestamp == 0
    assert frame.channels == {"F3": -2.0, "F4": 4.0}
    assert frame.metadata == {"source": "device-1"}
    assert frame.band_power() == 10.0


@pytest.mark.parametrize(
    "metadata",
    [
        ["scanner", {"tide": [1, 2]}, "printer"],
        "unstructured stigma film frame",
        b"\x00\x01",
        None,
    ],
)
def test_signal_frame_preserves_unrestricted_metadata(metadata):
    frame = SignalFrame(timestamp=1.0, channels={"F3": 1.0}, metadata=metadata)

    assert frame.metadata == metadata


@pytest.mark.parametrize(
    ("channels", "error"),
    [
        ({}, ValueError),
        ({"F3": float("nan")}, ValueError),
        ({"F3": True}, TypeError),
        ({"": 1.0}, ValueError),
    ],
)
def test_signal_frame_rejects_invalid_measurements(channels, error):
    with pytest.raises(error):
        SignalFrame(timestamp=1.0, channels=channels)


def test_ingest_requires_explicit_start_when_auto_start_is_disabled():
    alba = AlbaCore(auto_start=False)

    with pytest.raises(RuntimeError, match="must be started"):
        alba.ingest({"F3": 1.0})

    alba.start()
    assert alba.ingest({"F3": 1.0}).channels == {"F3": 1.0}


def test_batch_ingestion_is_atomic_when_a_frame_is_invalid():
    alba = AlbaCore()

    with pytest.raises(ValueError):
        alba.ingest_batch(
            [
                {"timestamp": 1.0, "channels": {"F3": 1.0}},
                {"timestamp": 2.0, "channels": {}},
            ]
        )

    assert alba.history() == []
    assert alba.health()["status"] == "idle"


def test_load_history_is_atomic_when_payload_is_invalid(tmp_path):
    alba = AlbaCore(max_history=2)
    alba.ingest({"F3": 1.0}, timestamp=1.0)
    source = tmp_path / "history.json"
    source.write_text(
        json.dumps(
            [
                {"timestamp": 2.0, "channels": {"F3": 2.0}},
                {"timestamp": 3.0, "channels": {}},
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        alba.load_history(source)

    assert [frame.timestamp for frame in alba.history()] == [1.0]


def test_history_round_trip_preserves_real_frames(tmp_path):
    source = AlbaCore()
    source.ingest(
        {"F3": 1.5, "F4": -0.5},
        metadata={"device": "eeg-1"},
        timestamp=10.0,
    )
    path = source.export_history(tmp_path / "history.json")

    restored = AlbaCore(auto_start=False)
    assert restored.load_history(path) == 1
    assert restored.health()["status"] == "idle"
    assert restored.last_frame() == source.last_frame()
