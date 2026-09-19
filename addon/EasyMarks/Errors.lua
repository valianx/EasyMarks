local ADDON_NAME, addon = ...
local Errors = {}
addon.Errors = Errors

local MAX_ERRORS = 30

function Errors:Initialize()
    if type(EasyMarksDB) ~= "table" then EasyMarksDB = {} end
    if type(EasyMarksDB.errors) ~= "table" then EasyMarksDB.errors = {} end
    while #EasyMarksDB.errors > MAX_ERRORS do table.remove(EasyMarksDB.errors, 1) end
    return EasyMarksDB.errors
end

function Errors:Record(context, message)
    local entries = self:Initialize()
    local detail = tostring(message):sub(1, 1500)
    local timestamp = date("%Y-%m-%d %H:%M:%S")
    local last = entries[#entries]
    if last and last.context == context and last.message == detail then
        last.count = (tonumber(last.count) or 1) + 1
        last.lastTime = timestamp
        return
    end
    if #entries >= MAX_ERRORS then table.remove(entries, 1) end
    local version, build = GetBuildInfo()
    entries[#entries + 1] = {
        time = timestamp,
        lastTime = timestamp,
        context = tostring(context):sub(1, 100),
        message = detail,
        stack = debugstack(3, 12, 0):sub(1, 3000),
        version = C_AddOns.GetAddOnMetadata(ADDON_NAME, "Version") or "unknown",
        client = tostring(version) .. "." .. tostring(build),
        count = 1,
    }
end

-- Catch only our callbacks. Do not replace WoW's or another addon's error handler.
function Errors:Run(context, callback, ...)
    local args, count = { ... }, select("#", ...)
    local ok, result = xpcall(function()
        return callback(unpack(args, 1, count))
    end, function(err)
        self:Record(context, err)
        return err
    end)
    if not ok then
        DEFAULT_CHAT_FRAME:AddMessage("|cffff7070Easy Marks:|r Error in " .. context .. ": " .. tostring(result))
        geterrorhandler()(result)
    end
    return ok, result
end

function Errors:Wrap(context, callback)
    return function(...) self:Run(context, callback, ...) end
end

function Errors:Format()
    local entries = self:Initialize()
    if #entries == 0 then return "Easy Marks: no errors recorded." end
    local lines = { "Easy Marks · error log (newest first)", "" }
    for index = #entries, 1, -1 do
        local entry = entries[index]
        lines[#lines + 1] = entry.time .. " | " .. entry.context .. " | occurrences: " .. entry.count
        lines[#lines + 1] = "Addon " .. entry.version .. " | WoW " .. entry.client
        lines[#lines + 1] = entry.message
        lines[#lines + 1] = entry.stack
        lines[#lines + 1] = ""
    end
    return table.concat(lines, "\n")
end

function Errors:Show()
    if not self.viewer then
        local frame = CreateFrame("Frame", "EasyMarksErrorViewer", UIParent, "BackdropTemplate")
        frame:SetSize(650, 430)
        frame:SetPoint("CENTER")
        frame:SetFrameStrata("DIALOG")
        frame:SetClampedToScreen(true)
        frame:EnableMouse(true)
        frame:SetBackdrop({
            bgFile = "Interface\\Buttons\\WHITE8X8",
            edgeFile = "Interface\\Tooltips\\UI-Tooltip-Border", edgeSize = 12,
            insets = { left = 3, right = 3, top = 3, bottom = 3 },
        })
        frame:SetBackdropColor(0.035, 0.045, 0.07, 0.98)
        local title = frame:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
        title:SetPoint("TOPLEFT", 18, -16)
        title:SetText("Easy Marks · Errors")
        local instructions = frame:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
        instructions:SetPoint("TOPLEFT", 18, -43)
        instructions:SetText("Press Ctrl+A, then Ctrl+C to copy the log.")
        local close = CreateFrame("Button", nil, frame, "UIPanelCloseButton")
        close:SetPoint("TOPRIGHT", -3, -3)
        local scroll = CreateFrame("ScrollFrame", nil, frame, "UIPanelScrollFrameTemplate")
        scroll:SetPoint("TOPLEFT", 18, -70)
        scroll:SetPoint("BOTTOMRIGHT", -36, 20)
        local edit = CreateFrame("EditBox", nil, scroll)
        edit:SetMultiLine(true)
        edit:SetAutoFocus(false)
        edit:SetFontObject(ChatFontNormal)
        edit:SetWidth(590)
        edit:SetHeight(340)
        edit:EnableMouse(true)
        ScrollingEdit_OnLoad(edit)
        edit:SetScript("OnTextChanged", function(self)
            ScrollingEdit_OnTextChanged(self, scroll)
        end)
        edit:SetScript("OnCursorChanged", ScrollingEdit_OnCursorChanged)
        edit:SetScript("OnUpdate", function(self, elapsed)
            ScrollingEdit_OnUpdate(self, elapsed, scroll)
        end)
        edit:SetScript("OnEscapePressed", function() frame:Hide() end)
        scroll:SetScrollChild(edit)
        frame:SetScript("OnHide", function() edit:ClearFocus() end)
        frame.edit = edit
        frame.scroll = scroll
        self.viewer = frame
        table.insert(UISpecialFrames, "EasyMarksErrorViewer")
    end
    self.viewer.edit:SetText(self:Format())
    self.viewer:Show()
    self.viewer.edit:SetCursorPosition(0)
    self.viewer.scroll:SetVerticalScroll(0)
    self.viewer.edit:SetFocus()
    self.viewer.edit:HighlightText()
end
