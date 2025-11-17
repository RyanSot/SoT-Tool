Author:Redcube
       RyanSoT

## SOT TOOL is fully external 

Please report any issues asap so i can fix them

The program uses macro wich may breake TOS & pixel scanning to update the overlay based on the in-game HUD which is then placed ontop of the pre-existing HUD.

The program doesn't interact with the Sea of Thieves Client at all except for Screen Capture and overlaying images on it which are both Code of Conduct compliant due to OBS and Crosshair X working the same.

Based on my interpretation of the Code of Conduct this software is safe to use but still may result in ban

Have in mind this branch is using SOT HUD as main core i got some help from Cube and i do not take any responsibility for your account being banned

<br>

### How to use/fix
to open just extract and launch exe BUT must keep exe in 

* to fix just open _internal and drag in one or both of DLLs
* on 90% youll be missing GLFW3 lib get from top of this page 
* and probably miss msvcr120 get from top too


> **Note:**
>
> * Do not launch SoT HUD while Easy Anti-Cheat (EAC) is initializing, as this can cause the overlay to scale incorrectly. Start SoT HUD either before or after starting the game, if you did start it during EAC initialization just restart it. 
> * SoT HUD is optimized for **fullscreen mode**. Running in windowed mode may cause alignment issues.
---
<br>

## Hotkeys

| Key        | Action                              |
| ---------- | ----------------------------------- |
| **Insert** | Toggle the ImGui configuration menu |
| **Delete** | Exit SoT HUD and save configuration |

## Customization

The ImGui interface allows full customization of the HUD elements, including colours, font, position, and display options.

To use pre-made or shared configurations:

1. Download a configuration `.zip` file from the [Paks Discord](https://discord.gg/swm3jwrN6M). or zips we share on main/this page
2. Place it inside the `YourConfigs/` directory.
3. In the ImGui menu, go to:
   `File → Open Config → [Your Config].zip`

Configurations can also be exported to `.zip` for easy sharing.

## My own added features
 
* AFK macro should exted time to 55 minutes
* Travel freeze uses alt+enter alt+space bug
* Engine.ini uses from 3 presets for custom graphics

## Features

* Dynamic health and regeneration indicators
* Customizable colours, fonts, and display anchors            
* Health threshold indicators with colour transitions
* Configurable skull icons for health state
* Ammo tracking with automatic colour calibration
* Optional static or dynamic crosshair
* Live configuration reloading when `Config/` files change
* Save and load configuration profiles as `.zip` files
* In-game ImGui configuration and testing interface


## License

This project is provided as-is for personal and educational use.

All trademarks and game assets belong to their respective owners (Sea of Thieves © Microsoft / Rare Ltd).
