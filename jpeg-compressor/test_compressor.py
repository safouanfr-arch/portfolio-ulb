"""ImageMagick integration test on Linux or WSL."""

import hashlib
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().with_name("compress_jpg.sh")


class CompressorTests(unittest.TestCase):
    def setUp(self):
        if shutil.which("magick"):
            self.convert = ["magick"]
            self.identify = ["magick", "identify"]
        elif shutil.which("convert") and shutil.which("identify"):
            self.convert = ["convert"]
            self.identify = ["identify"]
        else:
            self.skipTest("ImageMagick is required")

    def test_directory_processing_keeps_sources_and_existing_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            nested = root / "subdir"
            nested.mkdir()
            large = root / "a large image.JPG"
            small = nested / "small.jpg"
            for image, size in [(large, "100x50"), (small, "16x8")]:
                subprocess.run(
                    [*self.convert, "-size", size, "xc:red", "-set", "comment", "sample", image],
                    check=True,
                )
            source_hash = hashlib.sha256(large.read_bytes()).digest()

            subprocess.run(["bash", SCRIPT, "40", root], check=True, capture_output=True)
            first_output = root / "a large image.compressed.jpg"
            self.assertTrue(first_output.is_file())
            self.assertFalse((nested / "small.compressed.jpg").exists())

            subprocess.run(
                ["bash", SCRIPT, "-r", "-c", "-e", "JPEG", "40", root],
                check=True,
                capture_output=True,
            )
            output = root / "a large image.compressed.JPEG"
            self.assertEqual(self.metadata(output), "40x20|")
            self.assertEqual(self.metadata(nested / "small.compressed.JPEG"), "16x8|")
            self.assertEqual(hashlib.sha256(large.read_bytes()).digest(), source_hash)
            first_bytes = first_output.read_bytes()
            subprocess.run(["bash", SCRIPT, "12", large], check=True, capture_output=True)
            self.assertEqual(first_output.read_bytes(), first_bytes)

    def metadata(self, image):
        return subprocess.check_output(
            [*self.identify, "-format", "%wx%h|%c", image], text=True
        )


if __name__ == "__main__":
    unittest.main()
