local _, addon = ...
local Markers = {}
addon.Markers = Markers

-- World marker IDs and raid-target texture IDs are different.
Markers.list = {
    { name = "Blue · square", texture = 6 },
    { name = "Green · triangle", texture = 4 },
    { name = "Purple · diamond", texture = 3 },
    { name = "Red · cross", texture = 7 },
    { name = "Yellow · star", texture = 1 },
    { name = "Orange · circle", texture = 2 },
    { name = "Silver · moon", texture = 5 },
    { name = "White · skull", texture = 8 },
}

function Markers.IconPath(marker)
    return "Interface\\TargetingFrame\\UI-RaidTargetingIcon_" .. marker.texture
end

-- Pure construction: commands come from the WoW adapter, never global APIs.
function Markers.BuildMacro(id, worldCommand, pingCommand)
    assert(type(id) == "number" and Markers.list[id], "Unknown world marker")
    return worldCommand .. " [@cursor] " .. id .. "\n" .. pingCommand .. " [@cursor] 5"
end

function Markers.BuildTargetMacro(id, targetCommand, pingCommand)
    assert(type(id) == "number" and Markers.list[id], "Unknown world marker")
    -- Unit icons use texture IDs. Native ! keeps an already assigned symbol;
    -- both lines require a target, with no mouseover or ground fallback.
    return targetCommand .. " [@target,exists] !" .. Markers.list[id].texture
        .. "\n" .. pingCommand .. " [@target,exists] 5"
end

function Markers.BuildClearMacro(id, clearCommand, clickCommand, targetButton)
    assert(type(id) == "number" and Markers.list[id], "Unknown world marker")
    return clearCommand .. " " .. id
        .. "\n" .. clickCommand .. " [@target,exists] " .. targetButton .. " LeftButton"
end

function Markers.BuildClearAllMacro(clearCommand, allLabel, clickCommand, targetButton)
    -- The client's clear-world-marker parser uses the localized ALL label.
    return clearCommand .. " " .. allLabel
        .. "\n" .. clickCommand .. " " .. targetButton .. " LeftButton"
end
