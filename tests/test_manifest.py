"""Validate the two distinct WoW loaders, not just generic XML syntax."""
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ADDON = Path(__file__).resolve().parents[1] / "addon/EasyMarks"


class ManifestTests(unittest.TestCase):
    def test_bindings_use_the_implicit_loader_not_the_toc_xml_loader(self):
        toc = (ADDON / "EasyMarks.toc").read_text(encoding="utf-8")
        files = [line.strip() for line in toc.splitlines() if line.strip() and not line.startswith("#")]
        self.assertNotIn("Bindings.xml", files)
        self.assertIn("Core.lua", files)
        self.assertLess(files.index("Errors.lua"), files.index("Core.lua"))
        self.assertLess(files.index("Domain/Markers.lua"), files.index("UI/Wheel.lua"))
        self.assertLess(files.index("UI/Wheel.lua"), files.index("Core.lua"))
        for path in files:
            self.assertTrue((ADDON / path).is_file(), path)
        metadata = dict(line[3:].split(":", 1) for line in toc.splitlines() if line.startswith("## "))
        self.assertEqual(metadata["SavedVariables"].strip(), "EasyMarksDB")
        root = ET.parse(ADDON / "Bindings.xml").getroot()
        self.assertEqual(root.tag, "Bindings")
        self.assertEqual(root.find("Binding").get("name"), "CLICK EasyMarksToggle:LeftButton")


if __name__ == "__main__":
    unittest.main()
