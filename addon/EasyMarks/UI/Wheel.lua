local _, addon = ...
local Markers = addon.Markers
local Errors = addon.Errors
local Wheel = {}
addon.Wheel = Wheel

local function Circle(parent, layer, size, r, g, b, alpha)
    local texture = parent:CreateTexture(nil, layer)
    texture:SetSize(size, size)
    texture:SetColorTexture(r, g, b, alpha)
    local mask = parent:CreateMaskTexture()
    mask:SetTexture("Interface\\CharacterFrame\\TempPortraitAlphaMask",
        "CLAMPTOBLACKADDITIVE", "CLAMPTOBLACKADDITIVE")
    mask:SetAllPoints(texture)
    texture:AddMaskTexture(mask)
    return texture, mask
end

local function Text(parent, font, text, point, x, y)
    local label = parent:CreateFontString(nil, "OVERLAY", font)
    label:SetPoint(point, parent, point, x, y)
    label:SetText(text)
    return label
end

local function Tooltip(button, title, description)
    button:SetScript("OnEnter", Errors:Wrap("tooltip", function(self)
        GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
        GameTooltip:SetText(title)
        GameTooltip:AddLine(description, 0.85, 0.88, 0.95, true)
        GameTooltip:Show()
    end))
    button:SetScript("OnLeave", function() GameTooltip:Hide() end)
end

local function RestorePosition(wheel)
    local position = EasyMarksDB.position
    local function Finite(value)
        return type(value) == "number" and value == value and math.abs(value) < math.huge
    end
    if type(position) == "table" and Finite(position.x) and Finite(position.y) then
        local x = math.max(-UIParent:GetWidth(), math.min(UIParent:GetWidth(), position.x))
        local y = math.max(-UIParent:GetHeight(), math.min(UIParent:GetHeight(), position.y))
        wheel:SetPoint("CENTER", UIParent, "CENTER", x, y)
    else
        wheel:SetPoint("CENTER", UIParent, "CENTER", 0, 0)
    end
end

local function ConfigureClear(button, placement, macro)
    button:RegisterForClicks("LeftButtonUp", "RightButtonUp")
    button:SetAttribute("useOnKeyDown", false)
    for index = 1, 2 do
        button:SetAttribute("*type" .. index, "macro")
        button:SetAttribute("*macrotext" .. index, macro)
    end
    SecureHandlerSetFrameRef(button, "placement", placement)
    SecureHandlerWrapScript(button, "OnClick", button, [[
        self:GetFrameRef("placement"):Hide()
    ]])
    button:HookScript("OnHide", function() GameTooltip:Hide() end)
end

local function CreateTargetClear(wheel, name, action)
    -- /click delegates to a native secure action, never another macro.
    -- This button has no physical mouse input and is configured before combat.
    local button = CreateFrame("Button", name, wheel, "SecureActionButtonTemplate")
    button:SetSize(1, 1)
    button:SetPoint("CENTER")
    button:EnableMouse(false)
    button:RegisterForClicks("LeftButtonUp")
    button:SetAttribute("useOnKeyDown", false)
    button:SetAttribute("*type1", "raidtarget")
    button:SetAttribute("*action1", action)
    button:SetAttribute("*unit1", "target")
    return button:GetName()
end

local function AttachClearAll(wheel, placement, macro)
    local button = CreateFrame("Button", "EasyMarksClearAll", wheel, "SecureActionButtonTemplate")
    button:SetSize(58, 24)
    button:SetPoint("CENTER", wheel, "CENTER", 0, 6)
    ConfigureClear(button, placement, macro)
    Text(button, "GameFontNormalSmall", "Clear all", "CENTER", 0, 0)
    button:SetHighlightTexture("Interface\\Buttons\\ButtonHilight-Square", "ADD")
    Tooltip(button, "Clear all", "Clear all ground markers and all unit icons for the group. No ping.")
end

local function AttachClearButton(button, wheel, placement, id, marker, macro)
    local clear = CreateFrame("Button", "EasyMarksClear" .. id, button,
        "SecureActionButtonTemplate")
    clear:SetSize(18, 18)
    clear:SetPoint("TOPRIGHT", button, "TOPRIGHT", 4, 4)
    ConfigureClear(clear, placement, macro)
    clear:Hide()
    local background, mask = Circle(clear, "BACKGROUND", 18, 0.35, 0.055, 0.055, 0.9)
    background:SetPoint("CENTER")
    clear:SetHighlightTexture("Interface\\Buttons\\ButtonHilight-Square", "ADD")
    clear:GetHighlightTexture():AddMaskTexture(mask)
    Text(clear, "GameFontHighlightSmall", "×", "CENTER", 0, 0)
    Tooltip(clear, "Clear " .. marker.name,
        "Clear this ground marker and the selected target's icon. Either mouse button. No ping.")
    SecureHandlerSetFrameRef(button, "clear", clear)
    SecureHandlerSetFrameRef(wheel, "clear" .. id, clear)
    -- Keep the tooltip and secure click handlers intact. Native auto-hide
    -- tracks both controls, so crossing onto the small button never hides it.
    SecureHandlerWrapScript(button, "OnEnter", button, [[
        local clear = self:GetFrameRef("clear")
        clear:Show()
        clear:RegisterAutoHide(0.15)
        clear:AddToAutoHide(self)
    ]])
end

local function AttachDragHandle(wheel, placement)
    local handle = CreateFrame("Button", "EasyMarksDragHandle", wheel, "SecureHandlerClickTemplate")
    handle:SetSize(32, 16)
    handle:SetPoint("CENTER", wheel, "CENTER", 0, -22)
    handle:EnableMouse(true)
    handle:RegisterForDrag("LeftButton")
    handle:RegisterForClicks("RightButtonUp")
    SecureHandlerSetFrameRef(handle, "placement", placement)
    handle:SetAttribute("_onclick", [[ self:GetFrameRef("placement"):Hide() ]])
    for _, offset in ipairs({ -2, 2 }) do
        local grip = handle:CreateTexture(nil, "ARTWORK")
        grip:SetSize(14, 1)
        grip:SetPoint("CENTER", handle, "CENTER", 0, offset)
        grip:SetColorTexture(0.8, 0.8, 0.8, 0.4)
    end
    Tooltip(handle, "Move wheel", "Drag this grip to move the wheel out of combat.")

    local drag
    local function StopDrag() drag = nil end
    handle:SetScript("OnDragStart", Errors:Wrap("drag wheel", function()
        if InCombatLockdown() then return end
        placement:Hide()
        GameTooltip:Hide()
        local x, y = GetCursorPosition()
        local scale = UIParent:GetEffectiveScale()
        local centerX, centerY = wheel:GetCenter()
        local parentX, parentY = UIParent:GetCenter()
        drag = { x = centerX - parentX - x / scale, y = centerY - parentY - y / scale }
    end))
    -- Do not use StartMoving: stopping a protected frame after combat starts
    -- is restricted too. This drag has no native movement to release.
    local UpdateDrag = Errors:Wrap("wheel position", function()
        local x, y = GetCursorPosition()
        local scale = UIParent:GetEffectiveScale()
        wheel:ClearAllPoints()
        wheel:SetPoint("CENTER", UIParent, "CENTER", x / scale + drag.x, y / scale + drag.y)
        local centerX, centerY = wheel:GetCenter()
        local parentX, parentY = UIParent:GetCenter()
        EasyMarksDB.position = { x = centerX - parentX, y = centerY - parentY }
    end)
    handle:SetScript("OnUpdate", function()
        if not drag then return end
        if InCombatLockdown() or not IsMouseButtonDown("LeftButton") then
            StopDrag()
            return
        end
        UpdateDrag()
    end)
    handle:SetScript("OnDragStop", StopDrag)
    handle:SetScript("OnMouseUp", StopDrag)
    wheel:HookScript("OnHide", StopDrag)
    handle:RegisterEvent("PLAYER_REGEN_DISABLED")
    handle:SetScript("OnEvent", StopDrag)
end

function Wheel.Create()
    local wheel = CreateFrame("Frame", "EasyMarksWheel", UIParent,
        "SecureHandlerShowHideTemplate")
    wheel:SetSize(200, 200)
    wheel:SetFrameStrata("DIALOG")
    wheel:SetClampedToScreen(true)
    -- Only the controls receive input; empty background passes clicks through.
    wheel:EnableMouse(false)
    wheel:Hide()
    RestorePosition(wheel)
    local background = Circle(wheel, "BACKGROUND", 200, 0.025, 0.04, 0.065, 0.32)
    background:SetPoint("CENTER", wheel, "CENTER", 0, 0)

    -- This visual has no protected parent/anchors and never performs actions.
    local cursor = CreateFrame("Frame", "EasyMarksCursor", UIParent)
    cursor:SetSize(30, 30)
    cursor:SetFrameStrata("TOOLTIP")
    cursor:EnableMouse(false)
    cursor:Hide()
    local cursorIcon = cursor:CreateTexture(nil, "OVERLAY")
    cursorIcon:SetAllPoints()
    cursor:SetScript("OnUpdate", Errors:Wrap("cursor", function(self)
        local x, y = GetCursorPosition()
        local scale = UIParent:GetEffectiveScale()
        self:ClearAllPoints()
        self:SetPoint("TOPLEFT", UIParent, "BOTTOMLEFT", x / scale + 18, y / scale - 12)
    end))

    -- Capture exactly the next click. @cursor targets the world beneath this
    -- transparent frame, so no arbitrary coordinates or delayed protected calls
    -- are necessary. All action attributes/transitions are set securely.
    local placement = CreateFrame("Button", "EasyMarksPlacement", UIParent,
        "SecureActionButtonTemplate,SecureHandlerShowHideTemplate")
    placement:SetAllPoints(UIParent)
    -- Keep wheel and minimap controls above the ground-click capture.
    placement:SetFrameStrata("HIGH")
    placement:EnableMouse(true)
    placement:RegisterForClicks("LeftButtonUp", "RightButtonUp")
    placement:SetAttribute("useOnKeyDown", false)
    placement:SetAttribute("*type1", "macro")
    placement:Hide()
    SecureHandlerSetFrameRef(placement, "wheel", wheel)
    SecureHandlerSetFrameRef(wheel, "placement", placement)
    placement:SetAttribute("_onshow", [[
        self:GetFrameRef("wheel"):SetBindingClick(true, "ESCAPE", self:GetName(), "RightButton")
    ]])
    placement:SetAttribute("_onhide", [[
        self:SetAttribute("*macrotext1", nil)
        self:SetAttribute("marker-id", nil)
        local wheel = self:GetFrameRef("wheel")
        wheel:ClearBindings()
    ]])
    -- Preserve the template's OnClick. Closing before it runs would swallow the
    -- action; closing on mouse-down could also allow the release through to WoW.
    -- postBody only runs when preBody returns a non-nil second value.
    -- Only left/right releases are registered, so each accepted click consumes
    -- the selection after its action (or cancellation) has been processed.
    SecureHandlerWrapScript(placement, "OnClick", placement, "return nil, true", [[
        self:Hide()
    ]])
    placement:HookScript("OnShow", Errors:Wrap("show selection", function(self)
        local marker = Markers.list[self:GetAttribute("marker-id")]
        if marker then
            cursorIcon:SetTexture(Markers.IconPath(marker))
        end
        GameTooltip:Hide()
        cursor:Show()
        SetCursor("PING_CURSOR")
    end))
    placement:HookScript("OnHide", Errors:Wrap("restore cursor", function()
        cursor:Hide()
        ResetCursor()
    end))
    placement:SetScript("OnEnter", function() SetCursor("PING_CURSOR") end)
    placement:SetScript("OnLeave", function() ResetCursor() end)

    AttachDragHandle(wheel, placement)

    wheel:SetAttribute("_onhide", [[
        self:ClearBindings()
        self:GetFrameRef("placement"):Hide()
        for id = 1, 8 do
            local clear = self:GetFrameRef("clear" .. id)
            if clear then
                clear:UnregisterAutoHide()
                clear:Hide()
            end
        end
    ]])

    -- The client provides localized slash names; numbers avoid localized ping
    -- names. Ping type 5 = Look / AlertNotThreat.
    local worldCommand = SLASH_WORLD_MARKER1 or "/wm"
    local pingCommand = SLASH_PING1 or "/ping"
    local targetCommand = SLASH_TARGET_MARKER1 or "/tm"
    local clearCommand = SLASH_CLEAR_WORLD_MARKER1 or "/cwm"
    local clickCommand = SLASH_CLICK1 or "/click"
    local clearTarget = CreateTargetClear(wheel, "EasyMarksClearTarget", "clear")
    local clearAllUnits = CreateTargetClear(wheel, "EasyMarksClearAllUnits", "clear-all")
    AttachClearAll(wheel, placement,
        Markers.BuildClearAllMacro(clearCommand, ALL or "All", clickCommand, clearAllUnits))
    for id, marker in ipairs(Markers.list) do
        local button = CreateFrame("Button", "EasyMarksColor" .. id, wheel,
            "SecureActionButtonTemplate")
        button:SetSize(42, 42)
        local angle = math.rad(90 - (id - 1) * 45)
        button:SetPoint("CENTER", wheel, "CENTER", math.cos(angle) * 68, math.sin(angle) * 68)
        local icon = button:CreateTexture(nil, "ARTWORK")
        icon:SetSize(29, 29)
        icon:SetPoint("CENTER")
        icon:SetTexture(Markers.IconPath(marker))
        local background, mask = Circle(button, "BACKGROUND", 40, 0.04, 0.06, 0.09, 0.35)
        background:SetPoint("CENTER")
        button:SetHighlightTexture("Interface\\Buttons\\ButtonHilight-Square", "ADD")
        button:GetHighlightTexture():AddMaskTexture(mask)
        button:RegisterForClicks("LeftButtonUp", "RightButtonUp")
        button:SetAttribute("useOnKeyDown", false)
        button:SetAttribute("*type2", "macro")
        button:SetAttribute("*macrotext2", Markers.BuildTargetMacro(id, targetCommand, pingCommand))
        SecureHandlerSetFrameRef(button, "placement", placement)
        button:SetAttribute("marker-id", id)
        button:SetAttribute("place-macro", Markers.BuildMacro(id, worldCommand, pingCommand))
        SecureHandlerWrapScript(button, "OnClick", button, [[
            local placement = self:GetFrameRef("placement")
            placement:Hide()
            if button == "LeftButton" then
                placement:SetAttribute("marker-id", self:GetAttribute("marker-id"))
                placement:SetAttribute("*macrotext1", self:GetAttribute("place-macro"))
                placement:Show()
            end
        ]])
        Tooltip(button, marker.name,
            "Left click: Ground - choose a point for marker + ping. Right click: Target - mark and ping your selected target.")
        AttachClearButton(button, wheel, placement, id, marker,
            Markers.BuildClearMacro(id, clearCommand, clickCommand, clearTarget))
    end

    local toggle = CreateFrame("Button", "EasyMarksToggle", Minimap,
        "SecureHandlerClickTemplate")
    toggle:SetSize(31, 31)
    toggle:SetPoint("CENTER", Minimap, "BOTTOMLEFT", 22, 22)
    toggle:SetFrameStrata("DIALOG")
    local rim, mask = Circle(toggle, "BACKGROUND", 31, 0.75, 0.58, 0.2, 0.95)
    rim:SetPoint("CENTER", toggle, "CENTER", 0, 0)
    local face = Circle(toggle, "BORDER", 27, 0.025, 0.04, 0.065, 0.97)
    face:SetPoint("CENTER", toggle, "CENTER", 0, 0)
    Text(toggle, "GameFontNormal", "EM", "CENTER", 0, 0)
    toggle:SetHighlightTexture("Interface\\Minimap\\UI-Minimap-ZoomButton-Highlight", "ADD")
    toggle:GetHighlightTexture():AddMaskTexture(mask)
    toggle:RegisterForClicks("LeftButtonUp", "RightButtonUp")
    SecureHandlerSetFrameRef(toggle, "wheel", wheel)
    SecureHandlerSetFrameRef(toggle, "placement", placement)
    toggle:SetAttribute("_onclick", [[
        if button == "LeftButton" then
            local wheel = self:GetFrameRef("wheel")
            self:GetFrameRef("placement"):Hide()
            if wheel:IsShown() then wheel:Hide() else wheel:Show() end
        end
    ]])
    toggle:HookScript("OnClick", Errors:Wrap("error viewer", function(_, button)
        if button == "RightButton" then Errors:Show() end
    end))
    Tooltip(toggle, "Easy Marks", "Left-click: toggle wheel. Right-click: view errors. Assign a keybind under Easy Marks in the keybinding settings.")

    return function()
        if InCombatLockdown() then
            return false
        end
        placement:Hide()
        wheel:SetShown(not wheel:IsShown())
        return true
    end
end

