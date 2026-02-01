# FLVER Importer for Blender 4.0+

A Blender addon for importing FLVER model files from FromSoftware games. This is an updated and streamlined version of the original [FromSoftware-Blender-Importer](https://github.com/FelixBenter/FromSoftware-Blender-Importer).

## Features

- Direct `.flver` file import
- Blender 4.0+ compatibility
- Armature/rig import with bone weights
- Coordinate system selection (Z-up Blender / Y-up Native)
- Support for newer games including Elden Ring Nightreign
- No external tool dependencies

## Tested Games

- Bloodborne
- Dark Souls 3
- Elden Ring
- Elden Ring Nightreign

## Installation

1. Download the `io_import_flver.zip` file
2. In Blender, go to **Edit > Preferences > Add-ons**
3. Click **"Install..."** and select the zip file
4. Enable the addon by checking the checkbox

## Usage

1. Go to **File > Import > FromSoftware FLVER (.flver)**
2. Select the coordinate system:
   - **Z-up (Blender)** - Converts to Blender's coordinate system
   - **Y-up (Native)** - Keeps FromSoftware's original coordinate system
3. Select one or multiple `.flver` files to import

## Removed Features

This addon has been streamlined from the original. The following features have been removed:

- **DCX unpacking** - Use [WitchyBND](https://github.com/ividyon/WitchyBND) by Ividyon to unpack `.dcx`
  archives before importing
- **Texture import** - Textures are not imported; this addon focuses on mesh and rig only
- **Yabber dependency** - No longer required
- **texconv.exe dependency** - No longer required

## References

This addon is based on and takes reference from:

- [FromSoftware-Blender-Importer](https://github.com/FelixBenter/FromSoftware-Blender-Importer) - Original addon by Felix Benter
- [SoulsFormats](https://github.com/JKAnderson/SoulsFormats) - .NET library for FromSoftware formats by JKAnderson
- [SoulsFormatsNEXT](https://github.com/soulsmods/SoulsFormatsNEXT) - Community continuation of SoulsFormats by SoulsMods
- [Smithbox](https://github.com/vawser/Smithbox) - FromSoftware game editor by Vawser
- [Aqua Toolset](https://github.com/Shadowth117/Aqua-Toolset) - Model conversion tools by Shadowth117
