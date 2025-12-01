
## Usage Options

### Interactive Component Selection (GUI)
```bash
./install.sh --gui
```
This launches an interactive terminal UI where you can:
- Navigate with arrow keys (↑/↓)
- Toggle components with SPACE
- Select all with 'A', deselect all with 'N'
- Confirm with ENTER or cancel with Q/ESC

### List Available Components
```bash
./install.sh --list
```

### Install All Default Components
```bash
./install.sh
```

### Install Specific Components
```bash
./install.sh -c kamp overrides cleanup
# or
./install.sh --components kamp overrides cleanup
```

### Available Components

| Category | Component | Slug | Description |
|----------|-----------|------|-------------|
| Display & Interface | Guppy Screen | `guppyscreen` | Alternative touchscreen UI |
| Display & Interface | Mainsail | `mainsail` | Modern web interface for Klipper |
| Camera & Streaming | uStreamer | `ustreamer` | Lightweight MJPEG streaming |
| Camera & Streaming | Timelapse (MJPEG) | `timelapse` | Print timelapse with MJPEG encoder |
| Camera & Streaming | Timelapse (H264) | `timelapseh264` | Print timelapse with H264 encoder |
| Macros & Configuration | All Macros & Configs | `macros` | Complete macro set |
| Macros & Configuration | Macros Only | `macros_only` | Only macros.cfg |
| Macros & Configuration | Start Print Only | `start_print` | Only start_print.cfg |
| Macros & Configuration | Overrides Only | `overrides` | Only overrides.cfg |
| Macros & Configuration | KAMP | `kamp` | Adaptive Meshing & Purging |
| Calibration & Tuning | Resonance Tester | `resonance` | Custom resonance testing |
| Calibration & Tuning | ShakeTune | `shaketune` | Advanced input shaper analysis |
| System Services | Cleanup Service | `cleanup` | Automatic backup cleanup |
