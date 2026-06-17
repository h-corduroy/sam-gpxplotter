"""Design tokens for the GPX Catalog neubrutalist UI and map routes."""

from __future__ import annotations

import json

# Core palette
TEXT_COLOR = "#000000"
MUTED_COLOR = "#333333"
BG_COLOR = "#ffffff"
BORDER_COLOR = "#000000"
SHADOW_COLOR = "#000000"

# Portfolio colors: (name, ui_pastel, route_richer)
# UI pastels are used in the catalog sidebar; route colors are slightly richer
# for visibility on the map basemap.
PORTFOLIO = (
    ("purple", "#b4afff", "#a090ff"),
    ("coral", "#ffb4af", "#ff948c"),
    ("mint", "#afffb4", "#7ae88a"),
    ("lime", "#ebffb1", "#d4e878"),
    ("cyan", "#b1ffec", "#5adccc"),
    ("pink", "#ffb1c4", "#ff94b0"),
)

PORTFOLIO_UI_COLORS = tuple(entry[1] for entry in PORTFOLIO)
PORTFOLIO_ROUTE_COLORS = tuple(entry[2] for entry in PORTFOLIO)

# Fixed accent surfaces in the catalog UI
ACCENT_UPLOAD = PORTFOLIO[0][1]
ACCENT_STATUS = PORTFOLIO[3][1]
ACCENT_PLACEHOLDER = PORTFOLIO[1][1]

# Map route styling
PLAIN_ROUTE_COLOR = PORTFOLIO_ROUTE_COLORS[0]
ROUTE_OUTLINE_COLOR = BORDER_COLOR
MAP_BACKGROUND_COLOR = BG_COLOR

# Neubrutalist depth
SHADOW_OFFSET_SM = "3px 3px"
SHADOW_OFFSET_MD = "4px 4px"
SHADOW_OFFSET_SIDEBAR = "4px 0"
BORDER_WIDTH = "2px"
BORDER_RADIUS = "5px"


def css_variables() -> str:
    """Return CSS custom properties for :root."""
    lines = [
        f"--text: {TEXT_COLOR};",
        f"--muted: {MUTED_COLOR};",
        f"--bg: {BG_COLOR};",
        f"--panel: {BG_COLOR};",
        f"--border: {BORDER_COLOR};",
        f"--shadow: {SHADOW_COLOR};",
        f"--accent-upload: {ACCENT_UPLOAD};",
        f"--accent-status: {ACCENT_STATUS};",
        f"--accent-placeholder: {ACCENT_PLACEHOLDER};",
        f"--shadow-sm: {SHADOW_OFFSET_SM} var(--shadow);",
        f"--shadow-md: {SHADOW_OFFSET_MD} var(--shadow);",
        f"--shadow-sidebar: {SHADOW_OFFSET_SIDEBAR} var(--shadow);",
        f"--radius: {BORDER_RADIUS};",
    ]
    for name, ui_color, _route_color in PORTFOLIO:
        lines.append(f"--{name}: {ui_color};")
    return "\n        ".join(lines)


def portfolio_colors_json() -> str:
    return json.dumps(list(PORTFOLIO_UI_COLORS))
