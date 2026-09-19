"""Logger unit tests with only clock, metadata and output stubs; no UI mock."""
from pathlib import Path
import unittest

from lupa.lua51 import LuaRuntime

SOURCE = Path(__file__).resolve().parents[2] / "addon/EasyMarks/Errors.lua"

STUBS = '''
now = "2026-09-17 16:00:00"
stack = "test stack"
reported = {}
chat = {}
function date() return now end
function debugstack() return stack end
function GetBuildInfo() return "test-client", "123" end
C_AddOns = { GetAddOnMetadata = function() return "test-version" end }
existingHandler = function(err) table.insert(reported, err) end
function geterrorhandler() return existingHandler end
DEFAULT_CHAT_FRAME = { AddMessage = function(_, message) table.insert(chat, message) end }
'''


class ErrorTests(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute(STUBS)
        self.reload_module()

    def reload_module(self):
        namespace = self.lua.table()
        self.lua.execute(SOURCE.read_text(encoding="utf-8"), "EasyMarks", namespace)
        self.lua.globals().errors = namespace.Errors

    def test_initialize_preserves_saved_data_and_trims_only_old_entries(self):
        self.lua.execute('''
            EasyMarksDB = { futureSetting = "keep me", errors = {} }
            for i = 1, 35 do EasyMarksDB.errors[i] = { message = "saved " .. i } end
            errors:Initialize()
        ''')
        self.reload_module()
        self.lua.execute("errors:Initialize()")
        db = self.lua.globals().EasyMarksDB
        self.assertEqual(db.futureSetting, "keep me")
        self.assertEqual(len(db.errors), 30)
        self.assertEqual(db.errors[1].message, "saved 6")
        self.assertEqual(db.errors[30].message, "saved 35")

    def test_repeated_errors_update_count_and_last_time_without_growing(self):
        self.lua.execute('''
            errors:Record("selection", "failure")
            now = "2026-09-17 16:01:00"
            errors:Record("selection", "failure")
        ''')
        entries = self.lua.globals().EasyMarksDB.errors
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[1].count, 2)
        self.assertEqual(entries[1].time, "2026-09-17 16:00:00")
        self.assertEqual(entries[1].lastTime, "2026-09-17 16:01:00")
        self.lua.execute('errors:Record("other", "failure"); errors:Record("selection", "failure")')
        self.assertEqual(len(entries), 3)

    def test_capacity_discards_oldest_and_format_lists_newest_first(self):
        self.lua.execute('for i = 1, 35 do errors:Record("test", "failure " .. i) end')
        entries = self.lua.globals().EasyMarksDB.errors
        self.assertEqual(len(entries), 30)
        self.assertEqual(entries[1].message, "failure 6")
        self.assertEqual(entries[30].message, "failure 35")
        text = self.lua.eval("errors:Format()")
        self.assertLess(text.index("failure 35"), text.index("failure 6"))
        self.assertIn("test-version", text)
        self.assertIn("test-client.123", text)

    def test_large_errors_are_bounded(self):
        self.lua.execute('''
            stack = string.rep("s", 5000)
            errors:Record(string.rep("c", 200), string.rep("m", 4000))
        ''')
        entry = self.lua.globals().EasyMarksDB.errors[1]
        self.assertEqual(len(entry.context), 100)
        self.assertEqual(len(entry.message), 1500)
        self.assertEqual(len(entry.stack), 3000)

    def test_success_preserves_nil_arguments_and_does_not_log(self):
        ok, result = self.lua.execute('''
            errors:Initialize()
            return errors:Run("test", function(...)
                assert(select(1, ...) == "first")
                assert(select(2, ...) == nil)
                assert(select(3, ...) == "last")
                return select("#", ...)
            end, "first", nil, "last")
        ''')
        self.assertTrue(ok)
        self.assertEqual(result, 3)
        self.assertEqual(len(self.lua.globals().EasyMarksDB.errors), 0)
        self.assertEqual(len(self.lua.globals().reported), 0)

    def test_failure_is_captured_and_forwarded_without_replacing_handler(self):
        ok, message = self.lua.execute('''
            return errors:Run("initialization", function() error("intentional failure") end)
        ''')
        self.assertFalse(ok)
        self.assertIn("intentional failure", message)
        entry = self.lua.globals().EasyMarksDB.errors[1]
        self.assertEqual(entry.context, "initialization")
        self.assertIn("intentional failure", entry.message)
        self.assertEqual(len(self.lua.globals().reported), 1)
        self.assertEqual(len(self.lua.globals().chat), 1)
        self.assertTrue(self.lua.eval("geterrorhandler() == existingHandler"))


if __name__ == "__main__":
    unittest.main()
