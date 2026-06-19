"""GPX Catalog design tokens — single source of truth for colors and palette."""

PORTFOLIO_COLORS = (
    "#B4AFFF",  # purple
    "#FFB4AF",  # coral
    "#AFFFB4",  # mint
    "#EBFFB1",  # lime
    "#B1FFEC",  # cyan
    "#FFB1C4",  # pink
)

TEXT = "#000000"
MUTED = "#333333"
BG = "#FFFFFF"
PANEL = "#FFFFFF"

# Map route styling — aligned with the catalog UI palette.
PLAIN_ROUTE_COLOR = PORTFOLIO_COLORS[0]
ROUTE_OUTLINE_COLOR = TEXT

PORTFOLIO_CSS_VARS = {
    "text": TEXT,
    "muted": MUTED,
    "bg": BG,
    "panel": PANEL,
    "purple": PORTFOLIO_COLORS[0],
    "coral": PORTFOLIO_COLORS[1],
    "mint": PORTFOLIO_COLORS[2],
    "lime": PORTFOLIO_COLORS[3],
    "cyan": PORTFOLIO_COLORS[4],
    "pink": PORTFOLIO_COLORS[5],
}


def theme_css() -> str:
    """Return :root CSS custom properties for the catalog UI."""
    lines = [":root {"]
    for name, value in PORTFOLIO_CSS_VARS.items():
        lines.append(f"  --{name}: {value};")
    lines.append("}")
    return "\n".join(lines) + "\n"
