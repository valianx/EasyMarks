# Easy Marks

A compact, movable marking wheel for **World of Warcraft Retail / Midnight**. Mark ground positions or your selected target, send attention pings, and clear markers from one place.

**Early alpha.** Marking is manual and follows the game's permissions and instance restrictions. Combat and instance-specific behavior still need in-game validation. Other players do not need the addon to see native markers and pings.

## Installation

1. Download or clone this repository.
2. Copy `addon/EasyMarks` into `World of Warcraft/_retail_/Interface/AddOns/`, then copy the root `LICENSE` into that `EasyMarks` folder.
3. Enable **Easy Marks** in the game's AddOns list. Restart WoW if this is your first installation; use `/reload` for updates.

The final path should be `Interface/AddOns/EasyMarks/EasyMarks.toc`.

## Controls

| Action | Result |
| --- | --- |
| Left-click **EM** on the minimap | Show or hide the wheel |
| Left-click a symbol, then click the ground | Place one ground marker and send a ping |
| Right-click a symbol | Mark and ping your selected target |
| Hover a symbol and click its **×** | Clear that ground marker and your current target's icon |
| Click **Clear all** | Clear all ground markers and icons assigned by the group |
| Press **Escape** or right-click the ground | Cancel placement and keep the wheel open |
| Drag the handle below **Clear all** | Move the wheel outside combat; its position is saved |
| Right-click **EM** | Open the addon error log |

Clearing does not send pings. Each ground selection ends after one placement.

## Contributing

Read the [contribution guide](CONTRIBUTING.md) for setup, tests, and pull requests, and follow the [code of conduct](CODE_OF_CONDUCT.md).

More details: [architecture](docs/ARCHITECTURE.md), [in-game testing](docs/PRUEBAS.md), [diagnostics](docs/DIAGNOSTICO.md), and [publishing](docs/PUBLICACION.md).

Licensed under [MIT](LICENSE). See [third-party notices](THIRD_PARTY_NOTICES.md).
