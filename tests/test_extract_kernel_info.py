import gzip
import struct
import tempfile
import unittest
from pathlib import Path

from tools.extract_kernel_info import extract_kernel_info


VERSION_LINE = (
    b"Linux version 6.6.89-android15-8-gabcdef "
    b"(builder@host) (Android clang version 19.0.0) "
    b"#1 SMP PREEMPT Fri Jul 18 10:11:12 UTC 2026\x00"
)


def boot_image(kernel):
    header = bytearray(4096)
    header[:8] = b"ANDROID!"
    struct.pack_into("<I", header, 8, len(kernel))
    struct.pack_into("<I", header, 20, 1580)
    struct.pack_into("<I", header, 40, 3)
    return bytes(header) + kernel


class ExtractKernelInfoTests(unittest.TestCase):
    def write_image(self, data):
        handle = tempfile.NamedTemporaryFile(suffix=".img", delete=False)
        handle.write(data)
        handle.close()
        self.addCleanup(Path(handle.name).unlink, missing_ok=True)
        return Path(handle.name)

    def test_extracts_version_and_build_time_from_raw_kernel(self):
        result = extract_kernel_info(self.write_image(boot_image(VERSION_LINE)))

        self.assertEqual(result["kernel_version"], "6.6.89-android15-8-gabcdef")
        self.assertEqual(result["kernel_time"], "Fri Jul 18 10:11:12 UTC 2026")

    def test_decompresses_gzip_kernel_before_scanning(self):
        result = extract_kernel_info(self.write_image(boot_image(gzip.compress(VERSION_LINE))))

        self.assertEqual(result["kernel_version"], "6.6.89-android15-8-gabcdef")
        self.assertEqual(result["kernel_time"], "Fri Jul 18 10:11:12 UTC 2026")


if __name__ == "__main__":
    unittest.main()
