# SoT-Tool
this is a modified version of SoT HUD https://github.com/RedcubeGH/SoT-HUD please use at own risk this version may breake Sea of Thieves TOS

The program uses pixel scanning to update the overlay based on the in-game HUD which is then placed ontop of the pre-existing HUD.

The ImGui interface allows full customization of the HUD elements, including colours, font, position, and display options.


    Do not launch SoT HUD while Easy Anti-Cheat (EAC) is initializing, as this can cause the overlay to scale incorrectly.
    Start SoT HUD either before or after starting the game, if you did start it during EAC initialization just restart it.
    SoT HUD is optimized for fullscreen mode. Running in windowed mode may cause alignment issues.

Customization
 To use pre-made or shared configurations:

    Download a configuration .zip file from the Paks Discord.
    Place it inside the YourConfigs/ directory.
    In the ImGui menu, go to: File → Open Config → [Your Config].zip

Configurations can also be exported to .zip for easy sharing.


FEATURES                                                            MY OWN ADDED FEATURES

   • Dynamic health and regeneration indicators                     • AFK macro should exted time to 55 minutes   
   • Customizable colours, fonts, and display anchors               • travel freeze uses alt+enter alt+space bug
   • Health threshold indicators with colour transitions            • Engine.ini uses from 3 presets for custom graphics
   • Configurable skull icons for health state
   • Ammo tracking with automatic colour calibration
   • Optional static or dynamic crosshair
   • Live configuration reloading when Config/ files change
   • Save and load configuration profiles as .zip files
   • In-game ImGui configuration and testing interface
