#!/usr/bin/env python3
"""
Generate 68 CSS overflow-N classes with colors sampled from a perceptually
uniform colormap. The line grows from subtle at overflow-1 to alarming at
overflow-68, progressing through the selected colormap.

Usage:
  python3 gen-overflow-colors.py cividis    # Generate with cividis (default)
  python3 gen-overflow-colors.py inferno    # Generate with inferno
  python3 gen-overflow-colors.py plasma     # Generate with plasma
  python3 gen-overflow-colors.py magma      # Generate with magma
  python3 gen-overflow-colors.py viridis    # Generate with viridis

Outputs CSS rules to stdout. Redirect to a file to use.
"""

import sys
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex


NUM_STOPS = 68                # one class per pixel of overflow
GLOW_THRESHOLD = 30           # add box-shadow glow starting at severity N
OPACITY_MIN = 0.25
OPACITY_MAX = 0.95
HEIGHT_MIN = 1.0              # px (overflow-1: very thin)
HEIGHT_MAX = 3.5              # px (overflow-68: noticeably thick)

COLORMAPS = [
    "cividis", "inferno", "magma", "plasma", "viridis",
    "turbo", "coolwarm", "Spectral", "RdYlGn",
]


def build_css(colormap_name: str) -> str:
    cmap = plt.get_cmap(colormap_name)
    lines = []
    lines.append(f"/* Auto-generated with: gen-overflow-colors.py {colormap_name} */")
    lines.append(f"/* Colormap: {colormap_name} -- {NUM_STOPS} severity levels */")
    lines.append("")

    for i in range(1, NUM_STOPS + 1):
        t = (i - 1) / (NUM_STOPS - 1) if NUM_STOPS > 1 else 0
        hex_color = to_hex(cmap(t), keep_alpha=False)

        t_opacity = (i - 1) / (NUM_STOPS - 1) if NUM_STOPS > 1 else 0
        opacity = round(OPACITY_MIN + t_opacity * (OPACITY_MAX - OPACITY_MIN), 3)

        t_height = (i - 1) / (NUM_STOPS - 1) if NUM_STOPS > 1 else 0
        height = round(HEIGHT_MIN + t_height * (HEIGHT_MAX - HEIGHT_MIN), 1)

        glow = ""
        if i >= GLOW_THRESHOLD:
            glow_strength = round((i - GLOW_THRESHOLD) / max(NUM_STOPS - GLOW_THRESHOLD, 1), 2)
            blur = round(4 + glow_strength * 12, 1)
            glow_rgba = f"color-mix(in srgb, {hex_color} {int(glow_strength * 60)}%, transparent)"
            glow = f"  box-shadow: 0 0 {blur}px {hex_color};\n"

        rule = (
            f"section.overflow-{i}::before {{\n"
            f"  display: block;\n"
            f"  height: {height}px;\n"
            f"  opacity: {opacity};\n"
            f"  background: linear-gradient(90deg,\n"
            f"    transparent 0%,\n"
            f"    {hex_color} 15%,\n"
            f"    {hex_color} 85%,\n"
            f"    transparent 100%\n"
            f"  );\n"
            f"{glow}"
            f"}}\n"
        )
        lines.append(rule)

    output = "\n".join(lines)
    # Check for duplicate hex colors (if NUM_STOPS > cmap resolution)
    seen = set()
    for i in range(1, NUM_STOPS + 1):
        c = to_hex(cmap((i - 1) / (NUM_STOPS - 1)), keep_alpha=False)
        if c in seen:
            print(f"Warning: duplicate color {c} at overflow-{i}", file=sys.stderr)
        seen.add(c)

    return output


def main():
    colormap = sys.argv[1] if len(sys.argv) > 1 else "cividis"
    if colormap not in plt.colormaps():
        print(f"Error: unknown colormap '{colormap}'", file=sys.stderr)
        print(f"Available: {', '.join(COLORMAPS)}", file=sys.stderr)
        sys.exit(1)

    print(build_css(colormap))


if __name__ == "__main__":
    main()
