import importlib.util
import json
import os
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock


SCRIPT = (
    Path(__file__).parents[1]
    / ".cursor"
    / "skills"
    / "seedance2-api"
    / "scripts"
    / "atlas_seedance.py"
)
SPEC = importlib.util.spec_from_file_location("atlas_seedance", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps(self.payload).encode()


class AtlasSeedanceTest(unittest.TestCase):
    @mock.patch.dict(os.environ, {"ATLASCLOUD_API_KEY": "test-key"}, clear=True)
    @mock.patch.object(MODULE.urllib.request, "urlopen")
    def test_text_submission_uses_text_model_once(self, urlopen):
        urlopen.return_value = FakeResponse({"data": {"id": "prediction-1"}})

        result = MODULE.submit(
            "A paper boat on a calm lake",
            duration=4,
            resolution="480p",
            ratio="1:1",
            generate_audio=False,
        )

        self.assertEqual(result["id"], "prediction-1")
        self.assertEqual(urlopen.call_count, 1)
        request = urlopen.call_args.args[0]
        payload = json.loads(request.data)
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(
            request.full_url,
            "https://api.atlascloud.ai/api/v1/model/generateVideo",
        )
        self.assertEqual(payload["model"], MODULE.TEXT_MODEL)
        self.assertEqual(payload["duration"], 4)
        self.assertFalse(payload["generate_audio"])

    @mock.patch.dict(os.environ, {"ATLASCLOUD_API_KEY": "test-key"}, clear=True)
    @mock.patch.object(MODULE.urllib.request, "urlopen")
    def test_local_image_selects_image_model(self, urlopen):
        urlopen.return_value = FakeResponse({"data": {"id": "prediction-2"}})
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "frame.png"
            image.write_bytes(b"png-data")
            MODULE.submit("Animate the frame", image=str(image))

        payload = json.loads(urlopen.call_args.args[0].data)
        self.assertEqual(payload["model"], MODULE.IMAGE_MODEL)
        self.assertEqual(payload["image"], "cG5nLWRhdGE=")

    @mock.patch.dict(os.environ, {"ATLASCLOUD_API_KEY": "test-key"}, clear=True)
    @mock.patch.object(MODULE.time, "sleep")
    @mock.patch.object(MODULE.urllib.request, "urlopen")
    def test_prediction_get_retries_transient_network_error(self, urlopen, sleep):
        urlopen.side_effect = [
            urllib.error.URLError("temporary"),
            FakeResponse({"data": {"id": "prediction-3", "status": "processing"}}),
        ]

        result = MODULE.query("prediction-3")

        self.assertEqual(result["status"], "processing")
        self.assertEqual(urlopen.call_count, 2)
        sleep.assert_called_once_with(1)

    @mock.patch.dict(os.environ, {"ATLASCLOUD_API_KEY": "test-key"}, clear=True)
    @mock.patch.object(MODULE.urllib.request, "urlopen")
    def test_submit_does_not_retry(self, urlopen):
        urlopen.side_effect = urllib.error.URLError("offline")
        with self.assertRaises(urllib.error.URLError):
            MODULE.submit("A paper boat")
        self.assertEqual(urlopen.call_count, 1)


if __name__ == "__main__":
    unittest.main()
