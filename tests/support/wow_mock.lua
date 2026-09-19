frames = {}
namedFrames = {}
bindings = {}
macroExecutions = {}
worldMarkerActions = {}
worldMarkers = {}
allowMarkerClear = true
selectedTarget = nil
targetMarkers = {}
targetMarkRequests = {}
targetPingRequests = {}
targetClearAllRequests = 0
allowTargetMark = true
allowTargetPing = true
mouseFocus = nil
chatMessages = {}
combat = false
cursorMode = nil
useKeyDown = true
modifiers = ""
missingHandlerMethods = false
reportedErrors = {}
cursorX, cursorY = 0, 0
leftMouseDown = false

local Frame = {}
Frame.__index = Frame

function Frame:GetName()
    return self.name
end

function Frame:RegisterEvent(event)
    self.events[event] = true
end

function Frame:UnregisterEvent(event)
    self.events[event] = nil
end

function Frame:SetScript(kind, fn)
    self.scripts[kind] = fn
end

function Frame:HookScript(kind, fn)
    if not self.hooks[kind] then self.hooks[kind] = {} end
    table.insert(self.hooks[kind], fn)
end

function Frame:SetAttribute(key, value)
    self.attrs[key] = value
end

function Frame:GetAttribute(key)
    return self.attrs[key]
end

function Frame:SetFrameRef(key, frame)
    self.refs[key] = frame
end

function Frame:GetFrameRef(key)
    return self.refs[key]
end

function Frame:SetBindingClick(_, key, frameName, button)
    bindings[key] = { owner = self, frame = frameName, button = button }
end

function Frame:ClearBindings()
    for key, binding in pairs(bindings) do
        if binding.owner == self then bindings[key] = nil end
    end
end

-- A deterministic approximation of the native hover group, not its frame
-- timing, geometry, protected execution or registration lifetime.
function Frame:RegisterAutoHide(duration)
    self.autoHide = { duration = duration, elapsed = 0, regions = { [self] = true } }
end

function Frame:AddToAutoHide(frame)
    assert(self.autoHide, "RegisterAutoHide must precede AddToAutoHide")
    self.autoHide.regions[frame] = true
end

function Frame:UnregisterAutoHide() self.autoHide = nil end

function Frame:Show()
    if self.shown then return end
    self.shown = true
    if self.attrs["_onshow"] then
        run_secure(self.attrs["_onshow"], self, nil, nil)
    end
    if self.scripts.OnShow then self.scripts.OnShow(self) end
    local hooks = self.hooks["OnShow"] or {}
    for _, fn in ipairs(hooks) do fn(self) end
end

function Frame:Hide()
    if not self.shown then return end
    self.shown = false
    if self.attrs["_onhide"] then
        run_secure(self.attrs["_onhide"], self, nil, nil)
    end
    if self.scripts.OnHide then self.scripts.OnHide(self) end
    local hooks = self.hooks["OnHide"] or {}
    for _, fn in ipairs(hooks) do fn(self) end
end

function Frame:SetShown(shown)
    if shown then self:Show() else self:Hide() end
end

function Frame:IsShown()
    return self.shown
end

function Frame:IsVisible()
    return self.shown and (not self.parent or self.parent:IsVisible())
end

function Frame:RegisterForClicks(...)
    self.clicks = { ... }
end

function Frame:RegisterForDrag(button) self.dragButton = button end

function Frame:CreateTexture()
    local texture = {}
    function texture:SetAllPoints() end
    function texture:SetSize() end
    function texture:SetPoint() end
    function texture:SetTexture(path) self.path = path end
    function texture:SetColorTexture(...) self.color = { ... } end
    function texture:AddMaskTexture(mask) self.mask = mask end
    table.insert(self.textures, texture)
    return texture
end

function Frame:CreateMaskTexture()
    local mask = {}
    function mask:SetTexture(path) self.path = path end
    function mask:SetAllPoints(texture) self.target = texture end
    return mask
end

function Frame:CreateFontString()
    local label = {}
    function label:SetPoint() end
    function label:SetText(text) self.text = text end
    return label
end

function Frame:SetSize(width, height) self.width, self.height = width, height end
function Frame:SetFrameStrata(value) self.strata = value end
function Frame:SetClampedToScreen() end
function Frame:EnableMouse(value) self.mouseEnabled = value end
function Frame:SetPoint(...)
    assert(not (combat and self.name == "EasyMarksWheel"), "protected move in combat")
    self.point = { ... }
end
function Frame:SetAllPoints() end
function Frame:SetBackdrop() end
function Frame:SetBackdropColor() end
function Frame:SetBackdropBorderColor() end
function Frame:SetHighlightTexture(path)
    self.highlight = self:CreateTexture()
    self.highlight:SetTexture(path)
end
function Frame:GetHighlightTexture() return self.highlight end
function Frame:ClearAllPoints()
    assert(not (combat and self.name == "EasyMarksWheel"), "protected reanchor in combat")
    self.point = nil
end
function Frame:GetParent() return self.parent end
function Frame:GetWidth() return self.width end
function Frame:GetHeight() return self.height end
function Frame:GetCenter()
    if self.name == "UIParent" then return 960, 540 end
    local point = self.point
    assert(point and point[1] == "CENTER" and point[3] == "CENTER", "mock only models centered wheel")
    local x, y = point[2]:GetCenter()
    return x + point[4], y + point[5]
end
function Frame:SetMultiLine(value) self.multiline = value end
function Frame:SetAutoFocus(value) self.autoFocus = value end
function Frame:SetFontObject() end
function Frame:SetWidth(value) self.width = value end
function Frame:SetHeight(value) self.height = value end
function Frame:SetScrollChild(child) self.scrollChild = child end
function Frame:SetVerticalScroll(value) self.scrollOffset = value end
function Frame:SetText(value)
    self.text = value
    if self.scripts.OnTextChanged then self.scripts.OnTextChanged(self) end
end
function Frame:SetCursorPosition(value) self.cursorPosition = value end
function Frame:SetFocus() self.focused = true end
function Frame:ClearFocus() self.focused = false end
function Frame:HighlightText() self.highlighted = true end

function CreateFrame(_, name, parent, template)
    local frame = setmetatable({
        name = name,
        parent = parent,
        attrs = {},
        refs = {},
        events = {},
        scripts = {},
        hooks = {},
        wraps = {},
        textures = {},
        template = template or "",
        -- WoW frames are visible by default; Initialize explicitly hides
        -- wheel, cursor, and placement where needed.
        shown = true,
    }, Frame)
    table.insert(frames, frame)
    if name then namedFrames[name] = frame end
    if missingHandlerMethods then frame.SetFrameRef = false end
    return frame
end

function SecureHandlerSetFrameRef(frame, key, target)
    frame.refs[key] = target
end

function run_secure(code, self, button, down, message)
    local chunk, err = loadstring(
        "local self, button, down, message = ...\n" .. code,
        "@secure-handler"
    )
    assert(chunk, err)
    return chunk(self, button, down, message)
end

function SecureHandlerWrapScript(frame, script, header, pre, post)
    assert(type(pre) == "string", "pre-handler must be a string")
    frame.wraps[script] = { header = header, pre = pre, post = post }
end

local function modified_attribute(frame, name, number)
    return frame.attrs[modifiers .. name .. number]
        or frame.attrs["*" .. name .. number]
        or frame.attrs[modifiers .. name .. "*"]
        or frame.attrs["*" .. name .. "*"]
        or frame.attrs[name .. number]
        or frame.attrs[name]
end

local function clear_world_marker(marker)
    table.insert(worldMarkerActions, { marker = marker, action = "clear" })
    if not allowMarkerClear then return end
    if marker then
        worldMarkers[marker] = nil
    else
        for id in pairs(worldMarkers) do worldMarkers[id] = nil end
    end
end

-- Only the macro forms used here are modeled from the native handlers.
-- This is not a general parser or proof of secure execution/permissions.
-- Ground placement macros remain recorded verbatim.
local function execute_macro(text)
    table.insert(macroExecutions, text)
    for line in text:gmatch("[^\n]+") do
        local command, arguments = line:match("^(%S+)%s+(.+)$")
        if command == SLASH_CLEAR_WORLD_MARKER1 then
            if arguments:lower() == ALL:lower() then
                clear_world_marker(nil)
            else
                local marker = tonumber(arguments)
                assert(marker and marker >= 1 and marker <= 8, "unmodeled clear marker")
                clear_world_marker(marker)
            end
        elseif command == SLASH_CLICK1 then
            local conditional = arguments:match("^%[@target,exists%] (.+)$")
            if not conditional or selectedTarget then
                local name, button = (conditional or arguments):match("^(%S+) (%S+)$")
                local delegate = namedFrames[name]
                assert(delegate and button == "LeftButton", "unmodeled click delegate")
                assert(modified_attribute(delegate, "type", "1") == "raidtarget",
                    "only native raidtarget delegation is modeled; no macro chaining")
                simulate_secure_click(delegate, button, false)
            end
        elseif command == SLASH_TARGET_MARKER1 then
            local value = arguments:match("^%[@target,exists%] (.+)$")
            assert(value, "unmodeled target marker macro")
            if selectedTarget then
                local keep = value:sub(1, 1) == "!"
                local marker = tonumber(keep and value:sub(2) or value)
                assert(marker and marker >= 0 and marker <= 8)
                if not (keep and targetMarkers[selectedTarget] == marker) then
                    table.insert(targetMarkRequests, { target = selectedTarget, marker = marker })
                    if allowTargetMark then
                        targetMarkers[selectedTarget] = marker ~= 0 and marker or nil
                    end
                end
            end
        elseif command == SLASH_PING1 and not arguments:find("[@cursor]", 1, true) then
            local kind = arguments:match("^%[@target,exists%] (%d+)$")
            assert(kind, "unmodeled target ping macro")
            if selectedTarget then
                table.insert(targetPingRequests, {
                    target = selectedTarget, kind = tonumber(kind), accepted = allowTargetPing,
                })
            end
        else
            assert(command == SLASH_WORLD_MARKER1 or command == SLASH_PING1,
                "unmodeled macro command")
        end
    end
end

-- Models only the input contract, not WoW's secure execution or taint engine.
function simulate_secure_click(frame, button, down)
    if not frame:IsVisible() then return false end
    local edge = down and "Down" or "Up"
    local registered = false
    for _, click in ipairs(frame.clicks or { "LeftButtonUp" }) do
        if click == "Any" .. edge or click == button .. edge then registered = true end
    end
    if not registered then return false end
    local wrapper = frame.wraps["OnClick"]
    local message
    if wrapper then
        local newbutton
        newbutton, message = run_secure(wrapper.pre, frame, button, down)
        if newbutton == false then return false end
        if type(newbutton) == "string" then button = newbutton end
    end
    if frame.scripts["OnClick"] then
        frame.scripts["OnClick"](frame, button, down)
    elseif frame.template:find("SecureActionButtonTemplate", 1, true) then
        local onDown = frame.attrs["useOnKeyDown"]
        if onDown == nil then onDown = useKeyDown end
        local number = button == "LeftButton" and "1" or button == "RightButton" and "2"
        if number and down == onDown then
            local kind = modified_attribute(frame, "type", number)
            if kind == "macro" then
                execute_macro(modified_attribute(frame, "macrotext", number))
            elseif kind == "worldmarker" then
                local marker = modified_attribute(frame, "marker", number)
                local action = modified_attribute(frame, "action", number)
                assert(action == "clear", "unmodeled world action")
                clear_world_marker(marker)
            elseif kind == "raidtarget" then
                local action = modified_attribute(frame, "action", number)
                if action == "clear-all" then
                    targetClearAllRequests = targetClearAllRequests + 1
                    if allowTargetMark then
                        for unit in pairs(targetMarkers) do targetMarkers[unit] = nil end
                    end
                else
                    assert(action == "clear" and modified_attribute(frame, "unit", number) == "target",
                        "unmodeled raidtarget action")
                    if selectedTarget then
                        table.insert(targetMarkRequests, { target = selectedTarget, marker = 0 })
                        if allowTargetMark then targetMarkers[selectedTarget] = nil end
                    end
                end
            end
        end
    elseif frame.template:find("SecureHandlerClickTemplate", 1, true) and frame.attrs["_onclick"] then
        run_secure(frame.attrs["_onclick"], frame, button, down)
    end
    -- Native SecureHandlers runs postBody only when preBody returns a
    -- non-nil second value. Always running it masked the stuck-cursor bug.
    if wrapper and wrapper.post and message ~= nil then
        run_secure(wrapper.post, frame, button, down, message)
    end
    for _, hook in ipairs(frame.hooks["OnClick"] or {}) do hook(frame, button, down) end
    return true
end

local function hover_event(frame, script, motion)
    local wrapper = frame.wraps[script]
    local allow, message
    if wrapper and motion then
        if script == "OnEnter" then
            frame.attrs._wrapentered = true
            allow, message = run_secure(wrapper.pre, frame)
        elseif frame.attrs._wrapentered then
            frame.attrs._wrapentered = nil
            allow, message = run_secure(wrapper.pre, frame)
        end
    end
    if allow == false then return end
    if frame.scripts[script] then frame.scripts[script](frame, motion) end
    if wrapper and wrapper.post and message ~= nil then
        run_secure(wrapper.post, frame, nil, nil, message)
    end
    for _, hook in ipairs(frame.hooks[script] or {}) do hook(frame, motion) end
end

function simulate_hover(frame, motion)
    if motion == nil then motion = true end
    if frame and not frame:IsVisible() then return false end
    local previous = mouseFocus
    mouseFocus = frame
    if previous then hover_event(previous, "OnLeave", motion) end
    if frame then hover_event(frame, "OnEnter", motion) end
    return true
end

function simulate_auto_hide(elapsed)
    for _, frame in ipairs(frames) do
        local registration = frame.autoHide
        if registration then
            local inside = registration.regions[mouseFocus]
            if inside then
                registration.elapsed = 0
            else
                registration.elapsed = registration.elapsed + elapsed
                if registration.elapsed >= registration.duration then frame:Hide() end
            end
        end
    end
end

function simulate_binding(key)
    local binding = bindings[key]
    if not binding then return false end
    local frame = namedFrames[binding.frame]
    return simulate_secure_click(frame, binding.button, false)
end

function trigger_addon_loaded(name)
    for _, frame in ipairs(frames) do
        if frame.events["ADDON_LOADED"] and frame.scripts["OnEvent"] then
            frame.scripts["OnEvent"](frame, "ADDON_LOADED", name)
        end
    end
end

function load_core(source)
    addonNamespace = {}
    for _, module in ipairs(dependencySources) do
        local chunk, err = loadstring(module.source, "@EasyMarks/" .. module.path)
        assert(chunk, err)
        chunk("EasyMarks", addonNamespace)
    end
    local chunk, err = loadstring(source, "@EasyMarks/Core.lua")
    assert(chunk, err)
    chunk("EasyMarks", addonNamespace)
end

function compile_all_secure()
    local count = 0
    local keys = { "_onclick", "_onshow", "_onhide" }
    for _, frame in ipairs(frames) do
        for _, key in ipairs(keys) do
            local code = frame.attrs[key]
            if code then
                local chunk, err = loadstring("local self, button, down = ...\n" .. code, "@secure")
                if not chunk then return false, frame.name, key, err end
                count = count + 1
            end
        end
        for script, wrapper in pairs(frame.wraps) do
            for _, code in ipairs({ wrapper.pre, wrapper.post }) do
                local chunk, err = loadstring("local self, button, down = ...\n" .. code, "@secure-wrap")
                if not chunk then return false, frame.name, script, err end
                count = count + 1
            end
        end
    end
    return true, count
end

function attribute(frameName, key)
    return namedFrames[frameName]:GetAttribute(key)
end

function shown(frameName)
    return namedFrames[frameName]:IsShown()
end

function binding_frame(key)
    return bindings[key] and bindings[key].frame or nil
end

function binding_button(key)
    return bindings[key] and bindings[key].button or nil
end

function macro_count()
    return #macroExecutions
end

function macro_text(index)
    return macroExecutions[index]
end

function last_chat_message()
    return chatMessages[#chatMessages]
end

UIParent = CreateFrame("Frame", "UIParent")
UIParent:SetSize(1920, 1080)
function UIParent:GetEffectiveScale() return 1 end
Minimap = CreateFrame("Frame", "Minimap", UIParent)
UISpecialFrames = {}
ChatFontNormal = {}
-- Scroll helpers are supplied by the client. This mock only checks wiring;
-- it does not validate text layout, native scrolling or clipboard behavior.
function ScrollingEdit_OnLoad() end
function ScrollingEdit_OnTextChanged() end
function ScrollingEdit_OnCursorChanged() end
function ScrollingEdit_OnUpdate() end

GameTooltip = {}
function GameTooltip:SetOwner(owner) self.owner = owner end
function GameTooltip:SetText(text) self.text = text end
function GameTooltip:AddLine() end
function GameTooltip:Show() self.shown = true end
function GameTooltip:Hide() self.shown = false end

DEFAULT_CHAT_FRAME = {}
function DEFAULT_CHAT_FRAME:AddMessage(message)
    table.insert(chatMessages, message)
end

function GetCursorPosition() return cursorX, cursorY end
function IsMouseButtonDown(button) return button == "LeftButton" and leftMouseDown end
function SetCursor(mode) cursorMode = mode end
function ResetCursor() cursorMode = nil end
function InCombatLockdown() return combat end
function set_combat(value) combat = value end
function cursor_mode() return cursorMode end
function date() return "2026-09-17 12:00:00" end
function debugstack() return "EasyMarks/Core.lua:1: test callback" end
function GetBuildInfo() return "12.1.0", "69814" end
C_AddOns = { GetAddOnMetadata = function() return addonVersion end }
function geterrorhandler()
    return function(message) table.insert(reportedErrors, message) end
end

SLASH_WORLD_MARKER1 = "/wm"
SLASH_TARGET_MARKER1 = "/tm"
SLASH_PING1 = "/ping"
SLASH_CLEAR_WORLD_MARKER1 = "/cwm"
SLASH_CLICK1 = "/click"
ALL = "All"
SLASH_EASYMARKS1 = nil
SLASH_EASYMARKS2 = nil
SlashCmdList = {}
