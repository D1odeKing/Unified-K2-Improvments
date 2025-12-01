#!/usr/bin/env python3
"""
Interactive GUI selector for component installation.

This module provides a curses-based interface that allows users to select
which components to install from the available options.
"""

import curses
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


@dataclass
class SelectableComponent:
    """A component that can be selected for installation."""
    name: str
    slug: str
    description: str
    selected: bool = False
    category: str = "General"


# Component definitions with descriptions and categories
COMPONENT_DEFINITIONS = [
    # Display & Interface
    SelectableComponent(
        name="Guppy Screen",
        slug="guppyscreen",
        description="Alternative touchscreen UI for the printer display",
        selected=True,
        category="Display & Interface",
    ),
    SelectableComponent(
        name="Mainsail",
        slug="mainsail",
        description="Modern web interface for Klipper",
        selected=True,
        category="Display & Interface",
    ),
    # Camera & Streaming
    SelectableComponent(
        name="uStreamer",
        slug="ustreamer",
        description="Lightweight MJPEG streaming server for camera",
        selected=True,
        category="Camera & Streaming",
    ),
    SelectableComponent(
        name="Timelapse (MJPEG)",
        slug="timelapse",
        description="Print timelapse recording with MJPEG encoder",
        selected=True,
        category="Camera & Streaming",
    ),
    SelectableComponent(
        name="Timelapse (H264)",
        slug="timelapseh264",
        description="Print timelapse recording with H264 encoder",
        selected=False,
        category="Camera & Streaming",
    ),
    # Macros & Configuration
    SelectableComponent(
        name="All Macros & Configs",
        slug="macros",
        description="Complete set of macros, start_print, and overrides",
        selected=True,
        category="Macros & Configuration",
    ),
    SelectableComponent(
        name="Macros Only",
        slug="macros_only",
        description="Install only macros.cfg",
        selected=False,
        category="Macros & Configuration",
    ),
    SelectableComponent(
        name="Start Print Only",
        slug="start_print",
        description="Install only start_print.cfg",
        selected=False,
        category="Macros & Configuration",
    ),
    SelectableComponent(
        name="Overrides Only",
        slug="overrides",
        description="Install only overrides.cfg",
        selected=False,
        category="Macros & Configuration",
    ),
    SelectableComponent(
        name="KAMP",
        slug="kamp",
        description="Klipper Adaptive Meshing & Purging",
        selected=False,
        category="Macros & Configuration",
    ),
    # Calibration & Tuning
    SelectableComponent(
        name="Resonance Tester",
        slug="resonance",
        description="Custom resonance testing for input shaping",
        selected=True,
        category="Calibration & Tuning",
    ),
    SelectableComponent(
        name="ShakeTune",
        slug="shaketune",
        description="Advanced input shaper analysis and tuning",
        selected=True,
        category="Calibration & Tuning",
    ),
    # System Services
    SelectableComponent(
        name="Cleanup Service",
        slug="cleanup",
        description="Automatic cleanup of old printer backups",
        selected=True,
        category="System Services",
    ),
]


class ComponentSelector:
    """Curses-based component selector interface."""

    def __init__(self, stdscr, components: List[SelectableComponent]):
        self.stdscr = stdscr
        self.components = components
        self.current_index = 0
        self.scroll_offset = 0
        self.cancelled = False
        
        # Initialize curses settings
        curses.curs_set(0)  # Hide cursor
        curses.use_default_colors()
        
        # Initialize color pairs
        if curses.has_colors():
            curses.init_pair(1, curses.COLOR_GREEN, -1)   # Selected items
            curses.init_pair(2, curses.COLOR_CYAN, -1)    # Headers
            curses.init_pair(3, curses.COLOR_YELLOW, -1)  # Highlighted
            curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLUE)  # Current item
            curses.init_pair(5, curses.COLOR_RED, -1)     # Cancel
        
        self.COLOR_SELECTED = curses.color_pair(1) if curses.has_colors() else curses.A_BOLD
        self.COLOR_HEADER = curses.color_pair(2) if curses.has_colors() else curses.A_BOLD
        self.COLOR_HIGHLIGHT = curses.color_pair(3) if curses.has_colors() else curses.A_REVERSE
        self.COLOR_CURRENT = curses.color_pair(4) if curses.has_colors() else curses.A_REVERSE
        self.COLOR_CANCEL = curses.color_pair(5) if curses.has_colors() else curses.A_BOLD

    def get_visible_rows(self) -> int:
        """Calculate number of visible component rows."""
        max_y, _ = self.stdscr.getmaxyx()
        # Reserve lines for header (4) and footer (4)
        return max(1, max_y - 8)

    def draw_header(self) -> None:
        """Draw the header section."""
        max_y, max_x = self.stdscr.getmaxyx()
        
        title = "3D Printer Component Installer"
        subtitle = "Select components to install"
        
        # Draw title
        self.stdscr.attron(self.COLOR_HEADER | curses.A_BOLD)
        self.stdscr.addstr(0, max(0, (max_x - len(title)) // 2), title[:max_x-1])
        self.stdscr.attroff(self.COLOR_HEADER | curses.A_BOLD)
        
        # Draw subtitle
        self.stdscr.addstr(1, max(0, (max_x - len(subtitle)) // 2), subtitle[:max_x-1])
        
        # Draw separator
        self.stdscr.addstr(2, 0, "─" * (max_x - 1))

    def draw_footer(self) -> None:
        """Draw the footer with instructions."""
        max_y, max_x = self.stdscr.getmaxyx()
        
        instructions = [
            "↑/↓: Navigate   SPACE: Toggle   A: Select All   N: Deselect All",
            "ENTER: Confirm and Install   Q/ESC: Cancel"
        ]
        
        # Draw separator
        self.stdscr.addstr(max_y - 4, 0, "─" * (max_x - 1))
        
        for i, instruction in enumerate(instructions):
            y = max_y - 3 + i
            if y < max_y:
                self.stdscr.addstr(y, max(0, (max_x - len(instruction)) // 2), instruction[:max_x-1])
        
        # Show selection count
        selected_count = sum(1 for c in self.components if c.selected)
        count_str = f"Selected: {selected_count}/{len(self.components)}"
        if max_y - 1 >= 0:
            self.stdscr.addstr(max_y - 1, max(0, (max_x - len(count_str)) // 2), count_str[:max_x-1])

    def draw_components(self) -> None:
        """Draw the component list."""
        max_y, max_x = self.stdscr.getmaxyx()
        visible_rows = self.get_visible_rows()
        start_y = 3
        
        # Group components by category for display
        current_category = None
        display_items = []
        
        for i, component in enumerate(self.components):
            if component.category != current_category:
                display_items.append(("category", component.category, i))
                current_category = component.category
            display_items.append(("component", component, i))
        
        # Calculate scroll position
        # Find the actual display index of current component
        current_display_idx = 0
        for idx, item in enumerate(display_items):
            if item[0] == "component" and item[2] == self.current_index:
                current_display_idx = idx
                break
        
        # Adjust scroll offset
        if current_display_idx < self.scroll_offset:
            self.scroll_offset = current_display_idx
        elif current_display_idx >= self.scroll_offset + visible_rows:
            self.scroll_offset = current_display_idx - visible_rows + 1
        
        # Draw visible items
        y = start_y
        for idx in range(self.scroll_offset, min(len(display_items), self.scroll_offset + visible_rows)):
            if y >= max_y - 4:
                break
                
            item = display_items[idx]
            
            if item[0] == "category":
                # Draw category header
                category_name = f"── {item[1]} ──"
                self.stdscr.attron(self.COLOR_HEADER | curses.A_BOLD)
                self.stdscr.addstr(y, 2, category_name[:max_x-3])
                self.stdscr.attroff(self.COLOR_HEADER | curses.A_BOLD)
            else:
                component = item[1]
                component_idx = item[2]
                is_current = (component_idx == self.current_index)
                
                # Build the line
                checkbox = "[X]" if component.selected else "[ ]"
                name = component.name
                desc = component.description
                
                # Calculate available space for description
                name_part = f"  {checkbox} {name}"
                available_width = max_x - len(name_part) - 5
                
                if available_width > 10:
                    if len(desc) > available_width:
                        desc = desc[:available_width-3] + "..."
                    line = f"{name_part} - {desc}"
                else:
                    line = name_part
                
                # Truncate if needed
                line = line[:max_x-1]
                
                # Apply styling
                if is_current:
                    self.stdscr.attron(self.COLOR_CURRENT)
                    self.stdscr.addstr(y, 0, " " * (max_x - 1))
                    self.stdscr.addstr(y, 0, line)
                    self.stdscr.attroff(self.COLOR_CURRENT)
                else:
                    if component.selected:
                        self.stdscr.attron(self.COLOR_SELECTED)
                    self.stdscr.addstr(y, 0, line)
                    if component.selected:
                        self.stdscr.attroff(self.COLOR_SELECTED)
            
            y += 1

    def draw(self) -> None:
        """Draw the entire interface."""
        self.stdscr.clear()
        self.draw_header()
        self.draw_components()
        self.draw_footer()
        self.stdscr.refresh()

    def toggle_current(self) -> None:
        """Toggle selection state of current component."""
        self.components[self.current_index].selected = not self.components[self.current_index].selected

    def select_all(self) -> None:
        """Select all components."""
        for component in self.components:
            component.selected = True

    def deselect_all(self) -> None:
        """Deselect all components."""
        for component in self.components:
            component.selected = False

    def move_up(self) -> None:
        """Move selection up."""
        if self.current_index > 0:
            self.current_index -= 1

    def move_down(self) -> None:
        """Move selection down."""
        if self.current_index < len(self.components) - 1:
            self.current_index += 1

    def run(self) -> Optional[List[str]]:
        """Run the selector and return list of selected component slugs."""
        while True:
            self.draw()
            
            try:
                key = self.stdscr.getch()
            except KeyboardInterrupt:
                self.cancelled = True
                return None
            
            if key in (curses.KEY_UP, ord('k')):
                self.move_up()
            elif key in (curses.KEY_DOWN, ord('j')):
                self.move_down()
            elif key == ord(' '):
                self.toggle_current()
            elif key in (ord('a'), ord('A')):
                self.select_all()
            elif key in (ord('n'), ord('N')):
                self.deselect_all()
            elif key in (ord('\n'), curses.KEY_ENTER, 10, 13):
                # Confirm selection
                selected = [c.slug for c in self.components if c.selected]
                return selected
            elif key in (ord('q'), ord('Q'), 27):  # 27 is ESC
                self.cancelled = True
                return None
            elif key == curses.KEY_RESIZE:
                # Handle terminal resize
                pass


def run_selector(stdscr) -> Optional[List[str]]:
    """Entry point for curses wrapper."""
    components = [SelectableComponent(
        name=c.name,
        slug=c.slug,
        description=c.description,
        selected=c.selected,
        category=c.category,
    ) for c in COMPONENT_DEFINITIONS]
    
    selector = ComponentSelector(stdscr, components)
    return selector.run()


def select_components() -> Optional[List[str]]:
    """
    Launch the interactive component selector.
    
    Returns:
        List of selected component slugs, or None if cancelled.
    """
    try:
        return curses.wrapper(run_selector)
    except Exception as e:
        print(f"Error running selector: {e}", file=sys.stderr)
        return None


def print_components_list() -> None:
    """Print available components to stdout (non-interactive fallback)."""
    print("\nAvailable components:")
    print("=" * 60)
    
    current_category = None
    for comp in COMPONENT_DEFINITIONS:
        if comp.category != current_category:
            print(f"\n{comp.category}:")
            current_category = comp.category
        
        default = "[default]" if comp.selected else ""
        print(f"  {comp.slug:15} - {comp.name} {default}")
        print(f"                    {comp.description}")
    
    print("\n" + "=" * 60)
    print("Use: ./install.sh --components <slug1> <slug2> ...")
    print("Or run: ./install.sh --gui for interactive selection")


def main() -> None:
    """Main entry point when run directly."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Interactive component selector for 3D printer installation"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available components without interactive mode"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show selected components without installing"
    )
    
    args = parser.parse_args()
    
    if args.list:
        print_components_list()
        sys.exit(0)
    
    # Check if we have a terminal
    if not sys.stdin.isatty():
        print("Error: Interactive mode requires a terminal.", file=sys.stderr)
        print("Use --list to see available components.", file=sys.stderr)
        sys.exit(1)
    
    selected = select_components()
    
    if selected is None:
        print("\nInstallation cancelled.")
        sys.exit(0)
    
    if not selected:
        print("\nNo components selected.")
        sys.exit(0)
    
    print(f"\nSelected components: {', '.join(selected)}")
    
    if args.dry_run:
        print("Dry run - not installing.")
        sys.exit(0)
    
    # Launch the actual installer with selected components
    from lib.paths import REPO_ROOT
    install_script = REPO_ROOT / "scripts" / "install.py"
    
    if os.geteuid() != 0:
        print("ERROR: Installation must be run as root (use sudo)")
        sys.exit(1)
    
    # Execute the installer
    os.execv(
        sys.executable,
        [sys.executable, str(install_script), "--components"] + selected
    )


if __name__ == "__main__":
    main()
