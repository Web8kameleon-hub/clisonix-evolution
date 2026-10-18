import base64
import importlib.util
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

from fastapi import HTTPException


MODULE_PATH = Path(__file__).parents[2] / "ocean-core" / "ocean_multimodal.py"
SPEC = importlib.util.spec_from_file_location("ocean_multimodal_under_test", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class RecordingWhisperModel:
    def __init__(self):
        self.received_existing_file = False

    def transcribe(self, path, **kwargs):
        self.received_existing_file = Path(path).is_file()
        word = SimpleNamespace(word=" hello", start=0.0, end=0.4, probability=0.98)
        segment = SimpleNamespace(text="hello", words=[word])
        info = SimpleNamespace(duration=0.4, language="en", language_probability=0.99)
        return iter([segment]), info


class AudioPipelineTests(unittest.IsolatedAsyncioTestCase):
    async def test_transcription_uses_real_model_output(self):
        pipeline = MODULE.AudioPipeline(model_name="local-whisper")
        model = RecordingWhisperModel()
        pipeline._model = model

        result = await pipeline.transcribe_audio(
            base64.b64encode(b"real audio bytes").decode("ascii"),
            include_timestamps=True,
        )

        self.assertTrue(model.received_existing_file)
        self.assertEqual(result["transcript"], "hello")
        self.assertEqual(result["model"], "local-whisper")
        self.assertEqual(result["timestamps"][0]["probability"], 0.98)
        self.assertNotIn("simulated", result["transcript"].lower())

    async def test_invalid_audio_is_rejected(self):
        pipeline = MODULE.AudioPipeline()
        with self.assertRaises(HTTPException) as raised:
            await pipeline.transcribe_audio("not-valid-base64")
        self.assertEqual(raised.exception.status_code, 422)


class MultimodalFusionTests(unittest.IsolatedAsyncioTestCase):
    async def test_fusion_is_grounded_in_observed_outputs(self):
        engine = MODULE.OceanMultimodal()
        engine.vision.analyze_image = AsyncMock(
            return_value={"status": "success", "analysis": "observed image"}
        )
        engine.audio.transcribe_audio = AsyncMock(
            return_value={"status": "success", "transcript": "observed speech"}
        )
        engine._reason = AsyncMock(
            return_value={
                "status": "success",
                "reasoning": "grounded answer",
                "model": "real-model",
            }
        )
        request = MODULE.MultimodalRequest(
            mode=MODULE.SensorMode.MULTIMODAL,
            vision_input=MODULE.VisionRequest(image_base64="image"),
            audio_input=MODULE.AudioRequest(audio_base64="audio"),
            reasoning_prompt="Answer from the media",
        )

        result = await engine._multimodal_fusion(request)

        self.assertEqual(result["integrated_understanding"], "grounded answer")
        context = engine._reason.await_args.args[1]
        self.assertEqual(context["vision"], "observed image")
        self.assertEqual(context["audio_transcript"], "observed speech")

    async def test_multimodal_request_without_media_is_rejected(self):
        engine = MODULE.OceanMultimodal()
        request = MODULE.MultimodalRequest(mode=MODULE.SensorMode.MULTIMODAL)
        with self.assertRaises(HTTPException) as raised:
            await engine._collect_modalities(request)
        self.assertEqual(raised.exception.status_code, 422)


if __name__ == "__main__":
    unittest.main()
