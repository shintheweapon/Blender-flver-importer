# Changelog

All notable changes to this project will be documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.2.0] - 2026-03-19

### Added
- Blender 4.2 extension system support (`blender_manifest.toml`, drops `bl_info`)
- Connect Child Bones import option (enabled by default)
- Simplified Chinese (简体中文) UI translation

### Fixed
- Bone orientation now uses a geometric approach instead of rotation-matrix accumulation,
  fixing bones pointing in incorrect directions after import

## [0.1.1] - 2026-02-02

### Fixed
- Handle `EDGE_COMPRESSED` vertex data type in vertex buffer parsing

## [0.1.0] - 2026-02-01

### Added
- Initial release
- Import meshes and armatures from FLVER files
- Support for Bloodborne, Dark Souls 3, Elden Ring, and Elden Ring Nightreign
- Coordinate system selection (Z-up Blender / Y-up Native)
- No external tool dependencies
