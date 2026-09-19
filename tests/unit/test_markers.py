"""Pure Lua domain tests: no WoW globals, frames or client mock."""
from pathlib import Path
import unittest

from lupa.lua51 import LuaError, LuaRuntime

SOURCE = Path(__file__).resolve().parents[2] / "addon/EasyMarks/Domain/Markers.lua"


class MarkerTests(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        namespace = self.lua.table()
        self.lua.execute(SOURCE.read_text(encoding="utf-8"), "EasyMarks", namespace)
        self.markers = namespace.Markers

    def test_eight_unique_native_colors_and_texture_anchors(self):
        entries = self.markers.list
        self.assertEqual(len(entries), 8)
        self.assertEqual({entries[i].texture for i in range(1, 9)}, set(range(1, 9)))
        self.assertEqual(entries[1].texture, 6)  # Blue world marker uses square texture.
        self.assertEqual(entries[5].texture, 1)  # Yellow world marker uses star texture.
        self.assertTrue(self.markers.IconPath(entries[1]).endswith("UI-RaidTargetingIcon_6"))

    def test_macro_has_one_world_marker_and_one_ground_ping(self):
        for marker in range(1, 9):
            with self.subTest(marker=marker):
                macro = self.markers.BuildMacro(marker, "/wm", "/ping")
                self.assertEqual(macro.splitlines(),
                                 [f"/wm [@cursor] {marker}", "/ping [@cursor] 5"])

    def test_commands_are_supplied_by_adapter_not_hardcoded(self):
        self.assertEqual(self.markers.BuildMacro(2, "/marker_test", "/ping_test"),
                         "/marker_test [@cursor] 2\n/ping_test [@cursor] 5")

    def test_invalid_marker_is_rejected_before_action_is_built(self):
        for marker in (None, 0, 9, -1, 1.5, "1", True):
            with self.subTest(marker=marker), self.assertRaises(LuaError):
                self.markers.BuildMacro(marker, "/wm", "/ping")

    def test_target_macro_maps_world_colors_to_unit_icons_and_requires_target(self):
        for color, icon in enumerate((6, 4, 3, 7, 1, 2, 5, 8), start=1):
            with self.subTest(color=color):
                macro = self.markers.BuildTargetMacro(color, "/tm", "/ping")
                self.assertEqual(macro.splitlines(),
                                 [f"/tm [@target,exists] !{icon}", "/ping [@target,exists] 5"])
                self.assertNotIn("cursor", macro)
                self.assertNotIn("mouseover", macro)

    def test_target_macro_uses_localized_commands_supplied_by_adapter(self):
        self.assertEqual(self.markers.BuildTargetMacro(1, "/target_test", "/ping_test"),
                         "/target_test [@target,exists] !6\n/ping_test [@target,exists] 5")

    def test_target_macro_rejects_invalid_marker(self):
        for color in (None, 0, 9, -1, 1.5, "1", True):
            with self.subTest(color=color), self.assertRaises(LuaError):
                self.markers.BuildTargetMacro(color, "/tm", "/ping")

    def test_clear_macro_preserves_world_id_and_requires_selected_target_only_for_unit(self):
        for color in range(1, 9):
            with self.subTest(color=color):
                macro = self.markers.BuildClearMacro(color, "/cwm", "/click", "ClearTarget")
                self.assertEqual(macro.splitlines(),
                                 [f"/cwm {color}", "/click [@target,exists] ClearTarget LeftButton"])

    def test_clear_macro_rejects_invalid_ids_including_zero(self):
        for color in (None, 0, 9, -1, 1.5, "1", True):
            with self.subTest(color=color), self.assertRaises(LuaError):
                self.markers.BuildClearMacro(color, "/cwm", "/click", "ClearTarget")

    def test_clear_commands_and_all_keyword_use_client_localization(self):
        self.assertEqual(self.markers.BuildClearMacro(8, "/clear_test", "/click_test", "ClearTarget"),
                         "/clear_test 8\n/click_test [@target,exists] ClearTarget LeftButton")
        self.assertEqual(self.markers.BuildClearAllMacro("/clear_test", "Todo", "/click_test", "ClearUnits"),
                         "/clear_test Todo\n/click_test ClearUnits LeftButton")

    def test_clear_all_has_no_selected_target_requirement_or_ping(self):
        macro = self.markers.BuildClearAllMacro("/cwm", "All", "/click", "ClearUnits")
        self.assertEqual(macro.splitlines(), ["/cwm All", "/click ClearUnits LeftButton"])


if __name__ == "__main__":
    unittest.main()
