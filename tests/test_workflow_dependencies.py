import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "Batch_Kernel_Info_Extractor.yml"


class WorkflowDependencyTests(unittest.TestCase):
    def test_all_referenced_tools_are_present(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        referenced = sorted(set(re.findall(r"tools/[A-Za-z0-9_.-]+\.py", workflow)))

        self.assertEqual(
            referenced,
            [
                "tools/extract_kernel_info.py",
                "tools/payload_dumper_compat.py",
                "tools/resolve_ota.py",
            ],
        )
        for relative_path in referenced:
            with self.subTest(path=relative_path):
                self.assertTrue((ROOT / relative_path).is_file(), relative_path)


if __name__ == "__main__":
    unittest.main()
