"""
Hand-authored neofetch-style panel. Lines fade + slide in on a stagger.
Set STATIC=1 to emit a frozen (non-animated) frame for local previews.
"""
import os

LINES = [
    ("Name", "Muhammad Anas"),
    ("Role", "Full-Stack Web Developer"),
    ("Focus", "WordPress Specialist \u00b7 MERN Stack"),
    ("Stack", "React \u00b7 Node.js \u00b7 Express \u00b7 MongoDB"),
    ("CMS", "WordPress \u00b7 WooCommerce \u00b7 Shopify"),
    ("Now", "Building scalable React applications"),
    ("Next", "Learning Next.js and cloud fundamentals"),
    ("Focus2", "Clean backend architecture & API optimization"),
]

WIDTH = 490
HEIGHT = 40 + len(LINES) * 30 + 30
STATIC = os.environ.get("STATIC") == "1"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render():
    parts = [
        f'<svg viewBox="0 0 {WIDTH} {HEIGHT}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Consolas, Menlo, monospace">',
        f'<rect width="{WIDTH}" height="{HEIGHT}" rx="10" fill="#0d1117"/>',
        f'<rect x="0" y="0" width="{WIDTH}" height="30" rx="10" fill="#161b22"/>',
        f'<rect x="0" y="20" width="{WIDTH}" height="10" fill="#161b22"/>',
    ]
    for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{18 + i*16}" cy="15" r="5" fill="{c}"/>')
    parts.append(
        f'<text x="{WIDTH/2}" y="19" fill="#8b949e" font-size="11" '
        f'text-anchor="middle">anas@github ~ %</text>'
    )

    if not STATIC:
        parts += [
            "<style>",
            ".line { opacity: 0; }",
            "@keyframes fadein { from { opacity: 0; transform: translateX(-8px);} "
            "to { opacity: 1; transform: translateX(0);} }",
            "</style>",
        ]

    y = 60
    for i, (key, val) in enumerate(LINES):
        cls = "" if STATIC else 'class="line"'
        style = "" if STATIC else (
            f'style="animation: fadein 0.4s ease-out forwards; animation-delay: {i*0.15:.2f}s;"'
        )
        parts.append(
            f'<text x="24" y="{y}" {cls} {style}>'
            f'<tspan fill="#39d353" font-weight="bold">{esc(key)}:</tspan> '
            f'<tspan fill="#c9d1d9">{esc(val)}</tspan>'
            f"</text>"
        )
        y += 30

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    svg = render()
    with open("info-card.svg", "w") as f:
        f.write(svg)
    print("Wrote info-card.svg")


if __name__ == "__main__":
    main()
