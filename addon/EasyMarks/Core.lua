local ADDON_NAME, addon = ...
local Errors = addon.Errors
local toggleWheel, initializationError

BINDING_HEADER_EASYMARKS = "Easy Marks"
_G["BINDING_NAME_CLICK EasyMarksToggle:LeftButton"] = "Toggle marker wheel"

local function Message(text)
    DEFAULT_CHAT_FRAME:AddMessage("|cff79bcffEasy Marks:|r " .. text)
end

-- Register before constructing the UI so a startup failure stays diagnosable.
SLASH_EASYMARKS1 = "/emarks"
SLASH_EASYMARKS2 = "/easymarks"
SlashCmdList.EASYMARKS = function()
    if initializationError then
        Message("Could not start: " .. tostring(initializationError))
    elseif toggleWheel then
        if not toggleWheel() then
            Message("In combat, use the minimap icon or your keybind. Esc cancels placement.")
        end
    else
        Message("The interface is not ready yet.")
    end
end

local loader = CreateFrame("Frame")
loader:RegisterEvent("ADDON_LOADED")
loader:RegisterEvent("ADDON_ACTION_BLOCKED")
loader:RegisterEvent("ADDON_ACTION_FORBIDDEN")
loader:SetScript("OnEvent", function(self, event, name, functionName)
    if event == "ADDON_LOADED" and name == ADDON_NAME then
        self:UnregisterEvent("ADDON_LOADED")
        Errors:Initialize()
        local ok, result = Errors:Run("startup", addon.Wheel.Create)
        if ok then
            toggleWheel = result
            Message("Ready. Left-click the EM minimap icon to toggle the wheel; right-click to view errors.")
        else
            initializationError = result
        end
    elseif name == ADDON_NAME and (event == "ADDON_ACTION_BLOCKED" or event == "ADDON_ACTION_FORBIDDEN") then
        Errors:Record(event, functionName or "protected action")
    end
end)
