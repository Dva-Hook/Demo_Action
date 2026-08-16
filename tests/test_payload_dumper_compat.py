import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "tools" / "payload_dumper_compat.py"


class PayloadDumperCompatTests(unittest.TestCase):
    def test_forwards_arguments_to_installed_module(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            package = temp / "payload_dumper"
            package.mkdir()
            (package / "__init__.py").write_text("", encoding="utf-8")
            (package / "__main__.py").write_text(
                "import json, os, sys\n"
                "open(os.environ['CAPTURE_ARGS'], 'w', encoding='utf-8').write(json.dumps(sys.argv[1:]))\n",
                encoding="utf-8",
            )
            capture = temp / "args.json"
            env = os.environ.copy()
            env["CAPTURE_ARGS"] = str(capture)
            env["PYTHONPATH"] = str(temp)

            completed = subprocess.run(
                [
                    sys.executable,
                    str(WRAPPER),
                    "--partitions",
                    "boot",
                    "--workers",
                    "4",
                    "--out",
                    "output",
                    "https://cdn.example/ota.zip",
                ],
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(
                json.loads(capture.read_text(encoding="utf-8")),
                [
                    "--partitions",
                    "boot",
                    "--workers",
                    "4",
                    "--out",
                    "output",
                    "https://cdn.example/ota.zip",
                ],
            )


if __name__ == "__main__":
    unittest.main()
