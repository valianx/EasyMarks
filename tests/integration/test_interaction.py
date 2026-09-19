"""Pruebas de interacción de Easy Marks con un mock mínimo de WoW.

Estas pruebas comprueban el cableado Lua y las transiciones que el addon
declara. El mock no reproduce el motor seguro ni el cliente WoW, por lo que no
valida que Blizzard acepte macros, pings o acciones protegidas en juego.
"""

from pathlib import Path
from itertools import product
import unittest

from lupa.lua51 import LuaRuntime


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CORE_PATH = PROJECT_ROOT / "addon" / "EasyMarks" / "Core.lua"


MOCK_WOW = (PROJECT_ROOT / "tests/support/wow_mock.lua").read_text(encoding="utf-8")


class EasyMarksInteractionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not CORE_PATH.is_file():
            raise AssertionError(f"No se encontró Core.lua: {CORE_PATH}")

    def make_runtime(self):
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute(MOCK_WOW)
        toc = (CORE_PATH.parent / "EasyMarks.toc").read_text(encoding="utf-8")
        files = [line for line in toc.splitlines() if line and not line.startswith("#")]
        lua.globals().dependencySources = lua.table_from([
            lua.table_from({"path": path, "source": (CORE_PATH.parent / path).read_text(encoding="utf-8")})
            for path in files if path != "Core.lua"
        ])
        lua.globals().addonVersion = next(line.split(": ", 1)[1] for line in toc.splitlines()
                                        if line.startswith("## Version:"))
        return lua

    def setUp(self):
        self.lua = self.make_runtime()
        self.lua.globals().load_core(CORE_PATH.read_text(encoding="utf-8"))
        self.lua.globals().trigger_addon_loaded("EasyMarks")

    def attr(self, frame_name, key):
        return self.lua.globals().attribute(frame_name, key)

    def is_shown(self, frame_name):
        return bool(self.lua.globals().shown(frame_name))

    def click(self, frame_name, button, down):
        return bool(
            self.lua.globals().simulate_secure_click(
                self.lua.globals().namedFrames[frame_name], button, down
            )
        )

    def open_wheel(self):
        self.lua.globals().SlashCmdList["EASYMARKS"]()
        self.assertTrue(self.is_shown("EasyMarksWheel"))

    def select_color(self, color_id):
        if not self.is_shown("EasyMarksWheel"):
            self.open_wheel()
        self.assertTrue(self.click(f"EasyMarksColor{color_id}", "LeftButton", False))

    def test_eight_colors_have_distinct_world_and_ping_macro_mapping(self):
        expected_ids = set()
        texture_ids = [6, 4, 3, 7, 1, 2, 5, 8]
        for color_id in range(1, 9):
            frame_name = f"EasyMarksColor{color_id}"
            self.assertEqual(self.attr(frame_name, "marker-id"), color_id)
            macro = self.attr(frame_name, "place-macro")
            self.assertEqual(macro, f"/wm [@cursor] {color_id}\n/ping [@cursor] 5")
            expected_ids.add(macro.splitlines()[0].rsplit(" ", 1)[-1])
            self.assertIsNone(self.attr(frame_name, "*type1"))
            icon = self.lua.globals().namedFrames[frame_name].textures[1].path
            self.assertTrue(icon.endswith(f"UI-RaidTargetingIcon_{texture_ids[color_id - 1]}"))
        self.assertEqual(expected_ids, {str(value) for value in range(1, 9)})

    def test_selecting_color_enters_placement_without_executing_macro(self):
        self.select_color(1)

        self.assertEqual(self.lua.globals().macro_count(), 0)
        self.assertTrue(self.is_shown("EasyMarksWheel"))
        self.assertTrue(self.is_shown("EasyMarksPlacement"))
        self.assertEqual(self.attr("EasyMarksPlacement", "marker-id"), 1)
        self.assertEqual(
            self.attr("EasyMarksPlacement", "*macrotext1"),
            "/wm [@cursor] 1\n/ping [@cursor] 5",
        )
        self.assertEqual(self.lua.globals().binding_frame("ESCAPE"), "EasyMarksPlacement")
        self.assertEqual(self.lua.globals().binding_button("ESCAPE"), "RightButton")

    def test_left_up_runs_one_two_command_macro_and_cleans_state(self):
        self.select_color(2)

        self.assertFalse(self.click("EasyMarksPlacement", "LeftButton", True))
        self.assertEqual(self.lua.globals().macro_count(), 0)
        self.assertTrue(self.is_shown("EasyMarksPlacement"))

        self.assertTrue(self.click("EasyMarksPlacement", "LeftButton", False))
        self.assertEqual(self.lua.globals().macro_count(), 1)
        macro = self.lua.globals().macro_text(1)
        self.assertEqual(macro.splitlines(), ["/wm [@cursor] 2", "/ping [@cursor] 5"])
        self.assertFalse(self.is_shown("EasyMarksPlacement"))
        self.assertTrue(self.is_shown("EasyMarksWheel"))
        self.assertIsNone(self.lua.globals().binding_frame("ESCAPE"))
        self.assertIsNone(self.lua.globals().cursor_mode())
        self.assertFalse(self.is_shown("EasyMarksCursor"))
        self.assertIsNone(self.attr("EasyMarksPlacement", "*macrotext1"))
        self.assertIsNone(self.attr("EasyMarksPlacement", "marker-id"))

        # A hidden placement button cannot generate a duplicate action.
        self.assertFalse(self.click("EasyMarksPlacement", "LeftButton", False))
        self.assertEqual(self.lua.globals().macro_count(), 1)

    def test_right_click_and_escape_cancel_without_emitting_macro(self):
        self.select_color(3)
        self.assertFalse(self.click("EasyMarksPlacement", "RightButton", True))
        self.assertTrue(self.is_shown("EasyMarksPlacement"))
        self.assertTrue(self.click("EasyMarksPlacement", "RightButton", False))
        self.assertEqual(self.lua.globals().macro_count(), 0)
        self.assertFalse(self.is_shown("EasyMarksPlacement"))
        self.assertTrue(self.is_shown("EasyMarksWheel"))
        self.assertIsNone(self.lua.globals().binding_frame("ESCAPE"))

        self.select_color(4)
        self.assertTrue(self.lua.globals().simulate_binding("ESCAPE"))
        self.assertEqual(self.lua.globals().macro_count(), 0)
        self.assertFalse(self.is_shown("EasyMarksPlacement"))
        self.assertTrue(self.is_shown("EasyMarksWheel"))
        self.assertIsNone(self.lua.globals().binding_frame("ESCAPE"))
        self.assertIsNone(self.lua.globals().cursor_mode())
        self.assertFalse(self.is_shown("EasyMarksCursor"))
        self.assertFalse(self.lua.globals().simulate_binding("ESCAPE"))
        self.assertTrue(self.is_shown("EasyMarksWheel"))
        self.assertIsNone(self.lua.globals().binding_frame("ESCAPE"))

    def test_reopen_and_combat_guarded_slash(self):
        self.select_color(5)
        self.assertTrue(self.is_shown("EasyMarksPlacement"))

        self.lua.globals().set_combat(True)
        self.lua.globals().SlashCmdList["EASYMARKS"]()
        self.assertTrue(self.is_shown("EasyMarksPlacement"))
        self.assertTrue(self.is_shown("EasyMarksWheel"))
        self.assertIn("In combat", self.lua.globals().last_chat_message())

        self.lua.globals().set_combat(False)
        self.lua.globals().SlashCmdList["EASYMARKS"]()
        self.assertFalse(self.is_shown("EasyMarksPlacement"))
        self.assertFalse(self.is_shown("EasyMarksWheel"))
        self.assertIsNone(self.lua.globals().binding_frame("ESCAPE"))

    def test_all_secure_snippets_compile_and_down_does_not_fire_action(self):
        result = self.lua.globals().compile_all_secure()
        self.assertTrue(result[0], result[1:])
        self.assertGreaterEqual(result[1], 7)
        self.assertFalse(self.attr("EasyMarksPlacement", "useOnKeyDown"))

        self.select_color(6)
        self.assertFalse(self.click("EasyMarksPlacement", "LeftButton", True))
        self.assertEqual(self.lua.globals().macro_count(), 0)
        self.assertTrue(self.is_shown("EasyMarksPlacement"))

    def test_unregistered_or_hidden_color_clicks_do_not_arm(self):
        self.assertFalse(self.click("EasyMarksColor1", "LeftButton", False))
        self.open_wheel()
        self.assertFalse(self.click("EasyMarksColor1", "MiddleButton", False))
        self.assertFalse(self.click("EasyMarksColor1", "LeftButton", True))
        self.assertFalse(self.is_shown("EasyMarksPlacement"))
        self.assertEqual(self.lua.globals().macro_count(), 0)
        self.assertEqual(self.lua.globals().SLASH_EASYMARKS1, "/emarks")
        self.assertEqual(self.lua.globals().SLASH_EASYMARKS2, "/easymarks")

    def test_toggle_and_cancel_preserve_unrelated_binding(self):
        self.lua.execute('UIParent:SetBindingClick(true, "F12", "OtherAddon", "LeftButton")')
        self.lua.globals().set_combat(True)
        self.assertTrue(self.click("EasyMarksToggle", "LeftButton", False))
        self.assertTrue(self.click("EasyMarksColor8", "LeftButton", False))
        self.assertTrue(self.lua.globals().simulate_binding("ESCAPE"))
        self.assertEqual(self.lua.globals().binding_frame("F12"), "OtherAddon")
        self.assertIsNone(self.lua.globals().binding_frame("ESCAPE"))
        self.assertEqual(self.lua.globals().macro_count(), 0)
        self.assertFalse(self.lua.globals().simulate_binding("ESCAPE"))
        self.assertTrue(self.is_shown("EasyMarksWheel"))
        self.assertTrue(self.click("EasyMarksToggle", "LeftButton", False))
        self.assertFalse(self.is_shown("EasyMarksWheel"))
        self.assertEqual(self.lua.globals().binding_frame("F12"), "OtherAddon")

    def test_confirmation_ignores_cvar_and_modifier_combinations(self):
        prefixes = ("", "shift-", "ctrl-", "alt-", "ctrl-shift-", "alt-ctrl-shift-")
        expected = 0
        for cvar in (False, True):
            for prefix in prefixes:
                with self.subTest(cvar=cvar, modifiers=prefix):
                    self.lua.globals().useKeyDown = cvar
                    self.lua.globals().modifiers = prefix
                    self.select_color(7)
                    self.assertFalse(self.click("EasyMarksPlacement", "LeftButton", True))
                    self.assertEqual(self.lua.globals().macro_count(), expected)
                    self.assertTrue(self.click("EasyMarksPlacement", "LeftButton", False))
                    expected += 1
                    self.assertEqual(self.lua.globals().macro_count(), expected)
                    self.assertEqual(self.lua.globals().macro_text(expected), "/wm [@cursor] 7\n/ping [@cursor] 5")
                    self.assertFalse(self.is_shown("EasyMarksPlacement"))

    def test_minimap_icon_opens_without_chat_commands(self):
        button = self.lua.globals().namedFrames["EasyMarksToggle"]
        self.assertEqual(button.parent.GetName(button.parent), "Minimap")
        self.assertGreater(len(button.textures), 0)
        self.assertIsNone(self.lua.globals().namedFrames["EasyMarksClose"])
        self.assertTrue(self.click("EasyMarksToggle", "LeftButton", False))
        self.assertTrue(self.is_shown("EasyMarksWheel"))
        self.assertEqual(self.lua.globals().macro_count(), 0)

    def test_reselection_changes_only_next_mark_and_keeps_wheel_open(self):
        self.select_color(1)
        self.assertTrue(self.click("EasyMarksColor4", "LeftButton", False))
        self.assertTrue(self.is_shown("EasyMarksWheel"))
        self.assertEqual(self.lua.globals().macro_count(), 0)
        self.assertEqual(self.attr("EasyMarksPlacement", "marker-id"), 4)
        self.assertTrue(self.click("EasyMarksPlacement", "LeftButton", False))
        self.assertEqual(self.lua.globals().macro_text(1), "/wm [@cursor] 4\n/ping [@cursor] 5")
        self.assertFalse(self.click("EasyMarksPlacement", "LeftButton", False))
        self.assertEqual(self.lua.globals().macro_count(), 1)
        self.assertTrue(self.is_shown("EasyMarksWheel"))
        self.select_color(2)
        self.assertTrue(self.click("EasyMarksPlacement", "LeftButton", False))
        self.assertEqual(self.lua.globals().macro_count(), 2)
        self.assertFalse(self.is_shown("EasyMarksPlacement"))

    def test_minimap_releases_pending_selection_even_in_combat(self):
        # Strata checks cover our declared layering, not native hit testing.
        strata_order = {"HIGH": 1, "DIALOG": 2, "FULLSCREEN_DIALOG": 3}
        frames = self.lua.globals().namedFrames
        for name in ("EasyMarksWheel", "EasyMarksToggle"):
            self.assertGreater(strata_order[frames[name].strata],
                               strata_order[frames["EasyMarksPlacement"].strata])
        for combat in (False, True):
            with self.subTest(combat=combat):
                self.lua.globals().set_combat(False)
                self.select_color(6)
                self.lua.globals().set_combat(combat)
                self.assertTrue(self.click("EasyMarksToggle", "LeftButton", False))
                self.assertFalse(self.is_shown("EasyMarksWheel"))
                self.assertFalse(self.is_shown("EasyMarksPlacement"))
                self.assertFalse(self.is_shown("EasyMarksCursor"))
                self.assertIsNone(self.lua.globals().cursor_mode())
                self.assertIsNone(self.lua.globals().binding_frame("ESCAPE"))
                self.assertIsNone(self.attr("EasyMarksPlacement", "*macrotext1"))
                self.assertEqual(self.lua.globals().macro_count(), 0)

    def test_other_mouse_buttons_do_not_consume_or_execute_selection(self):
        self.select_color(7)
        self.assertFalse(self.click("EasyMarksPlacement", "MiddleButton", False))
        self.assertTrue(self.is_shown("EasyMarksPlacement"))
        self.assertEqual(self.lua.globals().macro_count(), 0)
        self.assertTrue(self.lua.globals().simulate_binding("ESCAPE"))
        self.assertFalse(self.is_shown("EasyMarksPlacement"))

    def start_drag(self, x=100, y=200):
        self.lua.globals().cursorX, self.lua.globals().cursorY = x, y
        self.lua.globals().leftMouseDown = True
        handle = self.lua.globals().namedFrames["EasyMarksDragHandle"]
        handle.scripts.OnDragStart(handle, "LeftButton")
        return handle

    def test_drag_cancels_selection_and_saves_scaled_position(self):
        self.lua.execute("function UIParent:GetEffectiveScale() return 2 end")
        self.select_color(3)
        self.lua.execute("worldMarkers[3] = true; targetMarkers.enemy = 8")
        handle = self.start_drag()
        self.lua.globals().cursorX, self.lua.globals().cursorY = 300, 260
        handle.scripts.OnUpdate(handle)
        self.assertFalse(self.is_shown("EasyMarksPlacement"))
        self.assertIsNone(self.lua.globals().cursor_mode())
        self.assertEqual(self.lua.globals().macro_count(), 0)
        self.assertTrue(self.lua.globals().worldMarkers[3])
        self.assertEqual(self.lua.globals().targetMarkers["enemy"], 8)
        self.assertEqual(self.lua.globals().targetClearAllRequests, 0)

        position = self.lua.globals().EasyMarksDB.position
        self.assertEqual((position.x, position.y), (100, 30))
        handle.scripts.OnDragStop(handle)
        self.lua.globals().cursorX = 900
        handle.scripts.OnUpdate(handle)
        wheel = self.lua.globals().namedFrames["EasyMarksWheel"]
        self.assertEqual((wheel.point[4], wheel.point[5]), (100, 30))
        self.assertEqual(len(self.lua.globals().reportedErrors), 0)

    def test_drag_stops_on_combat_and_cannot_restart_in_combat(self):
        self.open_wheel()
        handle = self.start_drag()
        self.lua.globals().cursorX = 180
        handle.scripts.OnUpdate(handle)
        self.lua.globals().set_combat(True)
        self.lua.globals().cursorX = 800
        # Check the OnUpdate guard before the combat event is dispatched.
        handle.scripts.OnUpdate(handle)
        handle.scripts.OnEvent(handle, "PLAYER_REGEN_DISABLED")
        self.start_drag()
        handle.scripts.OnUpdate(handle)
        wheel = self.lua.globals().namedFrames["EasyMarksWheel"]
        self.assertEqual(wheel.point[4], 80)
        self.assertEqual(len(self.lua.globals().reportedErrors), 0)
        self.assertTrue(self.click("EasyMarksColor2", "LeftButton", False))
        self.assertTrue(self.lua.globals().simulate_binding("ESCAPE"))
        self.assertFalse(self.is_shown("EasyMarksPlacement"))
        self.assertEqual(self.lua.globals().macro_count(), 0)

    def test_hide_and_mouse_release_stop_drag_without_native_movement(self):
        self.open_wheel()
        handle = self.start_drag()
        self.lua.globals().cursorX = 140
        handle.scripts.OnUpdate(handle)
        self.lua.globals().leftMouseDown = False
        self.lua.globals().cursorX = 700
        handle.scripts.OnUpdate(handle)
        wheel = self.lua.globals().namedFrames["EasyMarksWheel"]
        self.assertEqual(wheel.point[4], 40)
        self.start_drag()
        self.assertTrue(self.click("EasyMarksToggle", "LeftButton", False))
        self.assertTrue(self.click("EasyMarksToggle", "LeftButton", False))
        self.lua.globals().cursorX = 900
        handle.scripts.OnUpdate(handle)
        self.assertEqual(wheel.point[4], 40)
        self.assertEqual(len(self.lua.globals().reportedErrors), 0)

    def test_position_restores_on_load_and_invalid_saved_position_falls_back(self):
        for saved, expected in (("{ x = 120, y = -60 }", (120, -60)),
                                ("{ x = 'bad', y = 12 }", (0, 0)),
                                ("{ x = math.huge, y = 0 }", (0, 0))):
            with self.subTest(saved=saved):
                lua = self.make_runtime()
                lua.execute("EasyMarksDB = { errors = {}, position = " + saved + " }")
                lua.globals().load_core(CORE_PATH.read_text(encoding="utf-8"))
                lua.globals().trigger_addon_loaded("EasyMarks")
                point = lua.globals().namedFrames["EasyMarksWheel"].point
                self.assertEqual((point[4], point[5]), expected)
                self.assertEqual(len(lua.globals().reportedErrors), 0)

    def test_startup_does_not_depend_on_injected_frame_ref_methods(self):
        lua = self.make_runtime()
        lua.globals().missingHandlerMethods = True
        lua.globals().load_core(CORE_PATH.read_text(encoding="utf-8"))
        lua.globals().trigger_addon_loaded("EasyMarks")
        self.assertEqual(len(lua.globals().reportedErrors), 0)
        self.assertTrue(lua.globals().simulate_secure_click(
            lua.globals().namedFrames["EasyMarksToggle"], "LeftButton", False
        ))
        self.assertTrue(lua.globals().shown("EasyMarksWheel"))

    def test_startup_failure_is_reported_and_command_still_responds(self):
        lua = self.make_runtime()
        lua.execute('''
            local createFrame = CreateFrame
            CreateFrame = function(kind, name, ...)
                if name == "EasyMarksWheel" then error("simulated startup failure") end
                return createFrame(kind, name, ...)
            end
        ''')
        lua.globals().load_core(CORE_PATH.read_text(encoding="utf-8"))
        lua.globals().trigger_addon_loaded("EasyMarks")
        self.assertEqual(len(lua.globals().reportedErrors), 1)
        lua.globals().SlashCmdList["EASYMARKS"]()
        self.assertIn("simulated startup failure", lua.globals().last_chat_message())
        entry = lua.globals().EasyMarksDB.errors[1]
        self.assertEqual(entry.context, "startup")
        self.assertIn("simulated startup failure", entry.message)
        self.assertTrue(entry.stack)

    def test_right_click_opens_errors_without_arming_or_marking(self):
        self.assertTrue(self.click("EasyMarksToggle", "RightButton", False))
        self.assertEqual(len(self.lua.globals().reportedErrors), 0)
        self.assertTrue(self.is_shown("EasyMarksErrorViewer"))
        viewer = self.lua.globals().namedFrames["EasyMarksErrorViewer"]
        self.assertIn("no errors recorded", viewer.edit.text)
        self.assertTrue(viewer.edit.focused)
        self.assertFalse(self.is_shown("EasyMarksWheel"))
        self.assertFalse(self.is_shown("EasyMarksPlacement"))
        self.assertEqual(self.lua.globals().macro_count(), 0)

        viewer.edit.scripts.OnEscapePressed(viewer.edit)
        self.assertFalse(self.is_shown("EasyMarksErrorViewer"))
        self.assertFalse(viewer.edit.focused)
        self.lua.execute('addonNamespace.Errors:Record("prueba", "detalle copiable")')
        self.assertTrue(self.click("EasyMarksToggle", "RightButton", False))
        self.assertTrue(self.is_shown("EasyMarksErrorViewer"))
        self.assertIn("detalle copiable", viewer.edit.text)
        self.assertEqual(len(self.lua.globals().reportedErrors), 0)

    def test_protected_action_errors_are_filtered_by_addon(self):
        self.lua.execute('''
            for _, frame in ipairs(frames) do
                if frame.events["ADDON_ACTION_BLOCKED"] then
                    frame.scripts.OnEvent(frame, "ADDON_ACTION_BLOCKED", "AnotherAddon", "HiddenAction")
                    frame.scripts.OnEvent(frame, "ADDON_ACTION_FORBIDDEN", "EasyMarks", "PlaceRaidMarker")
                end
            end
        ''')
        entries = self.lua.globals().EasyMarksDB.errors
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[1].message, "PlaceRaidMarker")


    def test_idle_escape_leaves_wheel_visible_in_and_out_of_combat(self):
        for combat in (False, True):
            with self.subTest(combat=combat):
                self.setUp()
                self.lua.globals().set_combat(combat)
                self.assertTrue(self.click("EasyMarksToggle", "LeftButton", False))
                self.assertIsNone(self.lua.globals().binding_frame("ESCAPE"))
                self.assertFalse(self.lua.globals().simulate_binding("ESCAPE"))
                self.assertTrue(self.is_shown("EasyMarksWheel"))
                self.assertEqual(self.lua.globals().macro_count(), 0)
                self.assertTrue(self.click("EasyMarksToggle", "LeftButton", False))
                self.assertFalse(self.is_shown("EasyMarksWheel"))


    def hover(self, name=None, motion=True):
        frame = self.lua.globals().namedFrames[name] if name else None
        return self.lua.globals().simulate_hover(frame, motion)

    def test_clear_hover_group_preserves_reachability_without_actions(self):
        self.open_wheel()
        for combat in (False, True):
            with self.subTest(combat=combat):
                self.lua.globals().set_combat(combat)
                self.assertFalse(self.is_shown("EasyMarksClear1"))
                self.hover("EasyMarksColor1")
                self.assertTrue(self.is_shown("EasyMarksClear1"))
                self.lua.globals().simulate_auto_hide(1)
                self.assertTrue(self.is_shown("EasyMarksClear1"))
                self.hover("EasyMarksClear1")
                self.lua.globals().simulate_auto_hide(1)
                self.assertTrue(self.is_shown("EasyMarksClear1"))
                self.assertIn("Clear Blue", self.lua.globals().GameTooltip.text)
                self.hover()
                self.lua.globals().simulate_auto_hide(0.05)
                self.assertTrue(self.is_shown("EasyMarksClear1"))
                self.hover("EasyMarksColor1")
                self.lua.globals().simulate_auto_hide(1)
                self.assertTrue(self.is_shown("EasyMarksClear1"))
                self.hover()
                self.lua.globals().simulate_auto_hide(1)
                self.assertFalse(self.is_shown("EasyMarksClear1"))
                self.assertFalse(self.is_shown("EasyMarksPlacement"))
                self.assertEqual(len(self.lua.globals().worldMarkerActions), 0)
                self.assertEqual(self.lua.globals().macro_count(), 0)

    def test_left_clear_removes_ground_color_and_selected_target_together(self):
        self.select_color(3)
        self.lua.execute("worldMarkers[1] = true; worldMarkers[3] = true; targetMarkers.enemy = 8; targetMarkers.other = 6")
        self.lua.globals().selectedTarget = "enemy"
        self.hover("EasyMarksColor1")
        self.click("EasyMarksClear1", "LeftButton", False)
        self.assertIsNone(self.lua.globals().worldMarkers[1])
        self.assertIsNone(self.lua.globals().targetMarkers["enemy"])
        self.assertTrue(self.lua.globals().worldMarkers[3])
        self.assertEqual(self.lua.globals().targetMarkers["other"], 6)
        self.assertEqual(len(self.lua.globals().targetPingRequests), 0)
        self.assertFalse(self.is_shown("EasyMarksPlacement"))
        self.assertIsNone(self.lua.globals().binding_frame("ESCAPE"))
        self.assertTrue(self.is_shown("EasyMarksWheel"))

    def test_clear_targets_only_its_world_id_on_left_release(self):
        self.open_wheel()
        expected = 0
        for cvar in (False, True):
            for prefix in ("", "shift-", "ctrl-", "alt-", "alt-ctrl-shift-"):
                for color in range(1, 9):
                    with self.subTest(cvar=cvar, modifiers=prefix, color=color):
                        self.lua.globals().useKeyDown = cvar
                        self.lua.globals().modifiers = prefix
                        self.lua.execute("for i = 1, 8 do worldMarkers[i] = true end")
                        self.hover(f"EasyMarksColor{color}")
                        name = f"EasyMarksClear{color}"
                        self.assertFalse(self.click(name, "LeftButton", True))
                        self.assertFalse(self.click(name, "MiddleButton", False))
                        self.assertEqual(len(self.lua.globals().worldMarkerActions), expected)
                        self.assertTrue(self.click(name, "LeftButton", False))
                        expected += 1
                        actions = self.lua.globals().worldMarkerActions
                        self.assertEqual(len(actions), expected)
                        self.assertEqual((actions[expected].marker, actions[expected].action),
                                         (color, "clear"))
                        remaining = set(self.lua.globals().worldMarkers.keys())
                        self.assertEqual(remaining, set(range(1, 9)) - {color})
                        self.assertTrue(self.is_shown("EasyMarksWheel"))
                        self.assertEqual(self.lua.globals().macro_count(), expected)

    def test_clear_releases_pending_selection_even_if_native_action_is_denied(self):
        for combat in (False, True):
            for allowed in (False, True):
                with self.subTest(combat=combat, allowed=allowed):
                    self.setUp()
                    self.select_color(3)
                    self.lua.globals().set_combat(combat)
                    self.lua.globals().allowMarkerClear = allowed
                    self.lua.globals().allowTargetMark = not allowed
                    self.lua.globals().selectedTarget = "enemy"
                    self.lua.execute("worldMarkers[2] = true; worldMarkers[3] = true")
                    self.lua.execute("targetMarkers.enemy = 8; targetMarkers.other = 6")
                    self.hover("EasyMarksColor2")
                    self.assertTrue(self.click("EasyMarksClear2", "LeftButton", False))
                    self.assertEqual(bool(self.lua.globals().worldMarkers[2]), not allowed)
                    self.assertTrue(self.lua.globals().worldMarkers[3])
                    self.assertEqual(bool(self.lua.globals().targetMarkers["enemy"]), allowed)
                    self.assertEqual(self.lua.globals().targetMarkers["other"], 6)
                    self.assertFalse(self.is_shown("EasyMarksPlacement"))
                    self.assertFalse(self.is_shown("EasyMarksCursor"))
                    self.assertIsNone(self.lua.globals().cursor_mode())
                    self.assertIsNone(self.lua.globals().binding_frame("ESCAPE"))
                    self.assertIsNone(self.attr("EasyMarksPlacement", "*macrotext1"))
                    self.assertTrue(self.is_shown("EasyMarksWheel"))
                    self.hover()
                    self.lua.globals().simulate_auto_hide(10)
                    self.assertEqual(len(self.lua.globals().worldMarkerActions), 1)
                    self.assertEqual(len(self.lua.globals().targetMarkRequests), 1)
                    self.assertEqual(len(self.lua.globals().targetPingRequests), 0)
                    self.assertEqual(self.lua.globals().macro_count(), 1)
                    self.assertEqual(len(self.lua.globals().reportedErrors), 0)
                    self.click("EasyMarksColor4", "LeftButton", False)
                    self.click("EasyMarksPlacement", "LeftButton", False)
                    self.assertEqual(self.lua.globals().macro_count(), 2)
                    self.assertFalse(self.is_shown("EasyMarksPlacement"))

    def test_closing_wheel_resets_all_clear_controls_and_hover_registrations(self):
        for combat in (False, True):
            with self.subTest(combat=combat):
                self.setUp()
                self.open_wheel()
                self.lua.globals().set_combat(combat)
                for color in range(1, 9):
                    self.hover(f"EasyMarksColor{color}")
                self.assertTrue(self.click("EasyMarksToggle", "LeftButton", False))
                self.assertTrue(self.click("EasyMarksToggle", "LeftButton", False))
                for color in range(1, 9):
                    name = f"EasyMarksClear{color}"
                    self.assertFalse(self.is_shown(name))
                    self.assertIsNone(self.lua.globals().namedFrames[name].autoHide)
                    self.assertFalse(self.click(name, "LeftButton", False))
                self.assertEqual(len(self.lua.globals().worldMarkerActions), 0)

    def test_non_motion_enter_preserves_tooltip_without_revealing_clear(self):
        self.open_wheel()
        self.hover("EasyMarksColor5", motion=False)
        self.assertFalse(self.is_shown("EasyMarksClear5"))
        self.assertIn("Yellow", self.lua.globals().GameTooltip.text)
        self.assertTrue(self.lua.globals().GameTooltip.shown)
        self.hover("EasyMarksColor5")
        self.assertTrue(self.is_shown("EasyMarksClear5"))
        self.assertEqual(len(self.lua.globals().worldMarkerActions), 0)


    def test_right_click_marks_and_pings_current_target_for_each_color(self):
        self.open_wheel()
        for color, icon in enumerate((6, 4, 3, 7, 1, 2, 5, 8), start=1):
            with self.subTest(color=color):
                target = f"unit-{color}"
                self.lua.globals().selectedTarget = target
                self.assertTrue(self.click(f"EasyMarksColor{color}", "RightButton", False))
                self.assertEqual(self.lua.globals().targetMarkers[target], icon)
                mark = self.lua.globals().targetMarkRequests[color]
                ping = self.lua.globals().targetPingRequests[color]
                self.assertEqual((mark.target, mark.marker), (target, icon))
                self.assertEqual((ping.target, ping.kind), (target, 5))
                self.assertEqual(self.lua.globals().macro_text(color),
                                 f"/tm [@target,exists] !{icon}\n/ping [@target,exists] 5")
                self.assertFalse(self.is_shown("EasyMarksPlacement"))
                self.assertFalse(self.is_shown("EasyMarksCursor"))
                self.assertIsNone(self.lua.globals().binding_frame("ESCAPE"))
                self.assertTrue(self.is_shown("EasyMarksWheel"))
        self.assertEqual(len(self.lua.globals().targetMarkRequests), 8)
        self.assertEqual(len(self.lua.globals().targetPingRequests), 8)
        self.assertEqual(len(self.lua.globals().worldMarkerActions), 0)

    def test_right_click_without_target_releases_selection_without_signals(self):
        self.select_color(1)
        self.lua.globals().selectedTarget = None
        self.assertTrue(self.click("EasyMarksColor8", "RightButton", False))
        self.assertEqual(len(self.lua.globals().targetMarkRequests), 0)
        self.assertEqual(len(self.lua.globals().targetPingRequests), 0)
        self.assertEqual(len(self.lua.globals().worldMarkerActions), 0)
        self.assertFalse(self.is_shown("EasyMarksPlacement"))
        self.assertFalse(self.is_shown("EasyMarksCursor"))
        self.assertIsNone(self.lua.globals().cursor_mode())
        self.assertIsNone(self.lua.globals().binding_frame("ESCAPE"))
        self.assertTrue(self.is_shown("EasyMarksWheel"))
        self.assertFalse(self.click("EasyMarksPlacement", "LeftButton", False))

    def test_target_click_uses_release_for_modifiers_cvar_and_combat(self):
        self.open_wheel()
        expected = 0
        for combat in (False, True):
            for cvar in (False, True):
                for prefix in ("", "shift-", "ctrl-", "alt-", "alt-ctrl-shift-"):
                    with self.subTest(combat=combat, cvar=cvar, prefix=prefix):
                        self.lua.globals().set_combat(combat)
                        self.lua.globals().useKeyDown = cvar
                        self.lua.globals().modifiers = prefix
                        self.lua.globals().selectedTarget = f"unit-{expected}"
                        self.assertFalse(self.click("EasyMarksColor2", "RightButton", True))
                        self.assertEqual(len(self.lua.globals().targetPingRequests), expected)
                        self.assertTrue(self.click("EasyMarksColor2", "RightButton", False))
                        expected += 1
                        self.assertEqual(len(self.lua.globals().targetMarkRequests), expected)
                        self.assertEqual(len(self.lua.globals().targetPingRequests), expected)
                        self.assertFalse(self.is_shown("EasyMarksPlacement"))

    def test_repeated_target_click_keeps_icon_and_ping_requires_another_click(self):
        self.open_wheel()
        self.lua.globals().selectedTarget = "enemy"
        self.click("EasyMarksColor8", "RightButton", False)
        self.lua.globals().simulate_auto_hide(10)
        self.assertEqual(len(self.lua.globals().targetPingRequests), 1)
        self.click("EasyMarksColor8", "RightButton", False)
        self.assertEqual(self.lua.globals().targetMarkers["enemy"], 8)
        self.assertEqual(len(self.lua.globals().targetMarkRequests), 1)
        self.assertEqual(len(self.lua.globals().targetPingRequests), 2)

    def test_target_rejection_does_not_retry_or_block_later_ground_marking(self):
        for allow_mark in (False, True):
            for allow_ping in (False, True):
                with self.subTest(mark=allow_mark, ping=allow_ping):
                    self.setUp()
                    self.select_color(1)
                    self.lua.globals().selectedTarget = "enemy"
                    self.lua.globals().allowTargetMark = allow_mark
                    self.lua.globals().allowTargetPing = allow_ping
                    self.lua.globals().set_combat(True)
                    self.click("EasyMarksColor7", "RightButton", False)
                    self.assertFalse(self.is_shown("EasyMarksPlacement"))
                    self.assertIsNone(self.lua.globals().binding_frame("ESCAPE"))
                    self.assertEqual(bool(self.lua.globals().targetMarkers["enemy"]), allow_mark)
                    self.assertEqual(self.lua.globals().targetPingRequests[1].accepted, allow_ping)
                    self.lua.globals().simulate_auto_hide(10)
                    self.assertEqual(len(self.lua.globals().targetMarkRequests), 1)
                    self.assertEqual(len(self.lua.globals().targetPingRequests), 1)
                    self.click("EasyMarksColor1", "LeftButton", False)
                    self.click("EasyMarksPlacement", "LeftButton", False)
                    self.assertEqual(self.lua.globals().macro_text(2), "/wm [@cursor] 1\n/ping [@cursor] 5")
                    self.assertTrue(self.is_shown("EasyMarksWheel"))

    def test_right_clear_removes_ground_and_selected_unit_icon_without_ping(self):
        for combat in (False, True):
            for cvar in (False, True):
                for prefix in ("", "shift-", "ctrl-", "alt-ctrl-shift-"):
                    with self.subTest(combat=combat, cvar=cvar, prefix=prefix):
                        self.setUp()
                        self.select_color(1)
                        self.lua.execute("targetMarkers.enemy = 8; targetMarkers.other = 6; worldMarkers[1] = true")
                        self.lua.globals().selectedTarget = "enemy"
                        self.lua.globals().set_combat(combat)
                        self.lua.globals().useKeyDown = cvar
                        self.lua.globals().modifiers = prefix
                        self.hover("EasyMarksColor1")
                        self.assertFalse(self.click("EasyMarksClear1", "RightButton", True))
                        self.assertTrue(self.click("EasyMarksClear1", "RightButton", False))
                        self.assertEqual(self.lua.globals().macro_text(1),
                                         "/cwm 1\n/click [@target,exists] EasyMarksClearTarget LeftButton")
                        self.assertIsNone(self.lua.globals().targetMarkers["enemy"])
                        self.assertEqual(self.lua.globals().targetMarkers["other"], 6)
                        self.assertIsNone(self.lua.globals().worldMarkers[1])
                        self.assertEqual(len(self.lua.globals().targetMarkRequests), 1)
                        self.assertEqual(len(self.lua.globals().targetPingRequests), 0)
                        self.assertFalse(self.is_shown("EasyMarksPlacement"))
                        self.assertIsNone(self.lua.globals().binding_frame("ESCAPE"))
                        self.assertTrue(self.is_shown("EasyMarksWheel"))

    def test_clear_without_target_still_removes_ground_color(self):
        self.select_color(3)
        self.hover("EasyMarksColor3")
        self.lua.execute("targetMarkers.other = 8; worldMarkers[3] = true")
        self.click("EasyMarksClear3", "RightButton", False)
        self.assertEqual(len(self.lua.globals().targetMarkRequests), 0)
        self.assertEqual(len(self.lua.globals().targetPingRequests), 0)
        self.assertIsNone(self.lua.globals().worldMarkers[3])
        self.assertEqual(self.lua.globals().targetMarkers["other"], 8)
        self.assertFalse(self.is_shown("EasyMarksPlacement"))

    def test_clear_all_removes_all_group_markers_once_on_release_and_frees_cursor(self):
        cases = product((False, True), (False, True), ("LeftButton", "RightButton"),
                        ("", "shift-", "ctrl-", "alt-ctrl-shift-"), (None, "enemy"))
        for combat, cvar, button, prefix, target in cases:
            with self.subTest(combat=combat, cvar=cvar, button=button, prefix=prefix, target=target):
                self.setUp()
                self.select_color(4)
                self.lua.execute("for i = 1, 8 do worldMarkers[i] = true end")
                self.lua.execute("targetMarkers.party1 = 1; targetMarkers.party2 = 6; targetMarkers.enemy = 8")
                self.lua.globals().selectedTarget = target
                self.lua.globals().set_combat(combat)
                self.lua.globals().useKeyDown = cvar
                self.lua.globals().modifiers = prefix
                self.assertFalse(self.click("EasyMarksClearAll", button, True))
                self.assertFalse(self.click("EasyMarksClearAll", "MiddleButton", False))
                self.assertEqual(len(self.lua.globals().worldMarkerActions), 0)
                self.assertEqual(self.lua.globals().targetClearAllRequests, 0)
                self.assertTrue(self.click("EasyMarksClearAll", button, False))
                self.assertEqual(set(self.lua.globals().worldMarkers.keys()), set())
                self.assertEqual(set(self.lua.globals().targetMarkers.keys()), set())
                self.assertFalse(self.is_shown("EasyMarksPlacement"))
                self.assertFalse(self.is_shown("EasyMarksCursor"))
                self.assertIsNone(self.lua.globals().cursor_mode())
                self.assertIsNone(self.lua.globals().binding_frame("ESCAPE"))
                self.assertIsNone(self.attr("EasyMarksPlacement", "*macrotext1"))
                self.assertTrue(self.is_shown("EasyMarksWheel"))
                self.lua.globals().simulate_auto_hide(10)
                self.assertEqual(len(self.lua.globals().worldMarkerActions), 1)
                self.assertIsNone(self.lua.globals().worldMarkerActions[1].marker)
                self.assertEqual(self.lua.globals().targetClearAllRequests, 1)
                self.assertEqual(len(self.lua.globals().targetMarkRequests), 0)
                self.assertEqual(len(self.lua.globals().targetPingRequests), 0)
                self.assertEqual(self.lua.globals().macro_count(), 1)
                self.assertEqual(len(self.lua.globals().reportedErrors), 0)

    def test_clear_all_respects_independent_denials_without_retry_or_success_message(self):
        for ground_allowed, units_allowed in product((False, True), repeat=2):
            with self.subTest(ground=ground_allowed, units=units_allowed):
                self.setUp()
                self.select_color(1)
                self.lua.execute("worldMarkers[1] = true; targetMarkers.party1 = 8; targetMarkers.enemy = 6")
                self.lua.globals().set_combat(True)
                self.lua.globals().allowMarkerClear = ground_allowed
                self.lua.globals().allowTargetMark = units_allowed
                messages = len(self.lua.globals().chatMessages)
                self.click("EasyMarksClearAll", "LeftButton", False)
                self.assertEqual(bool(self.lua.globals().worldMarkers[1]), not ground_allowed)
                self.assertEqual(bool(self.lua.globals().targetMarkers["party1"]), not units_allowed)
                self.assertEqual(bool(self.lua.globals().targetMarkers["enemy"]), not units_allowed)
                self.assertFalse(self.is_shown("EasyMarksPlacement"))
                self.assertIsNone(self.lua.globals().binding_frame("ESCAPE"))
                self.assertTrue(self.is_shown("EasyMarksWheel"))
                self.lua.globals().simulate_auto_hide(10)
                self.assertEqual(len(self.lua.globals().worldMarkerActions), 1)
                self.assertEqual(self.lua.globals().targetClearAllRequests, 1)
                self.assertEqual(len(self.lua.globals().targetPingRequests), 0)
                self.assertEqual(len(self.lua.globals().chatMessages), messages)

    def test_cleanup_uses_localized_commands_and_all_label(self):
        self.lua = self.make_runtime()
        self.lua.globals().SLASH_CLEAR_WORLD_MARKER1 = "/clear_test"
        self.lua.globals().SLASH_CLICK1 = "/click_test"
        self.lua.globals().ALL = "Todo"
        self.lua.globals().load_core(CORE_PATH.read_text(encoding="utf-8"))
        self.lua.globals().trigger_addon_loaded("EasyMarks")
        self.open_wheel()
        self.lua.execute("worldMarkers[1] = true; worldMarkers[8] = true; targetMarkers.party1 = 8")
        self.hover("EasyMarksColor8")
        self.click("EasyMarksClear8", "RightButton", False)
        self.assertIsNone(self.lua.globals().worldMarkers[8])
        self.assertTrue(self.lua.globals().worldMarkers[1])
        self.assertEqual(self.lua.globals().targetMarkers["party1"], 8)
        self.click("EasyMarksClearAll", "LeftButton", False)
        self.assertEqual(self.lua.globals().macro_text(2),
                         "/clear_test Todo\n/click_test EasyMarksClearAllUnits LeftButton")
        self.assertEqual(set(self.lua.globals().worldMarkers.keys()), set())
        self.assertEqual(set(self.lua.globals().targetMarkers.keys()), set())

    def test_clear_all_is_unavailable_when_wheel_is_closed_and_delegates_have_no_mouse_input(self):
        self.assertFalse(self.click("EasyMarksClearAll", "LeftButton", False))
        for name in ("EasyMarksClearTarget", "EasyMarksClearAllUnits"):
            self.assertFalse(self.lua.globals().namedFrames[name].mouseEnabled)
            self.assertEqual(self.attr(name, "*type1"), "raidtarget")
        self.open_wheel()
        self.click("EasyMarksToggle", "LeftButton", False)
        self.assertFalse(self.click("EasyMarksClearAll", "RightButton", False))
        self.assertEqual(self.lua.globals().targetClearAllRequests, 0)
        self.assertEqual(len(self.lua.globals().worldMarkerActions), 0)


if __name__ == "__main__":
    unittest.main()
