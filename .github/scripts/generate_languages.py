import urllib.request
import json
import os

TOKEN = os.environ.get("GITHUB_TOKEN")
USERNAME = "Wildann77"

HEADERS = {
    "User-Agent": "Wildann77-Language-Card",
    "Accept": "application/vnd.github.v3+json"
}
if TOKEN:
    HEADERS["Authorization"] = f"token {TOKEN}"

def fetch_json(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def get_languages():
    repos_url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&type=owner"
    repos = fetch_json(repos_url)
    
    ignored_repos = {"python_password", "Wildann77"}
    ignored_langs = {
        "HTML", "CSS", "Blade", "Shell", "Dockerfile", "Makefile",
        "PowerShell", "Batchfile", "CMake", "Meson", "ShaderLab", "HLSL",
        "Jupyter Notebook", "Mako", "Wolfram Language", "Hack", "Smarty",
        "PLpgSQL"
    }
    
    lang_totals = {}
    for r in repos:
        name = r["name"]
        if r.get("fork") or name in ignored_repos:
            continue
        lang_url = r["languages_url"]
        try:
            langs = fetch_json(lang_url)
            for l, b in langs.items():
                if l in ignored_langs:
                    continue
                lang_totals[l] = lang_totals.get(l, 0) + b
        except Exception:
            pass
            
    return sorted(lang_totals.items(), key=lambda x: x[1], reverse=True)

def generate_svg(languages, max_langs=10):
    langs = languages[:max_langs]
    if not langs:
        return ""
        
    width = 260
    title = "Languages"
    
    pad_x = 20
    start_y = 62
    row_height = 20.5
    bar_start_x = 114
    
    seg_width = 4.8
    seg_gap = 1.0
    bar_height = 11.5
    max_segments = 22
    
    top_bytes = langs[0][1]
    
    rows = []
    for i, (name, count) in enumerate(langs):
        y = start_y + i * row_height
        ratio = count / top_bytes
        num_segs = max(1, round((ratio ** 0.52) * max_segments))
        
        segments = []
        for s in range(num_segs):
            sx = bar_start_x + s * (seg_width + seg_gap)
            segments.append(f'<rect class="bar" x="{sx:.1f}" y="{y - 9.5:.1f}" width="{seg_width:.1f}" height="{bar_height:.1f}" />')
            
        segs_str = "\n    ".join(segments)
        rows.append(f"""  <!-- {name} -->
  <text class="lang-text" x="{pad_x}" y="{y:.1f}">{name}</text>
  <g>
    {segs_str}
  </g>""")
        
    dots_y = start_y + len(langs) * row_height + 1
    total_height = dots_y + 18
    
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{total_height}" viewBox="0 0 {width} {total_height}">
  <style>
    .title {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; font-size: 13px; font-weight: 500; fill: #ffffff; }}
    .lang-text {{ font-family: monospace, Courier New, Menlo, Consolas; font-size: 12px; fill: #ffffff; }}
    .bar {{ fill: #ffffff; }}
    .dots {{ font-family: monospace, Courier New, Menlo, Consolas; font-size: 14px; fill: #ffffff; }}
    @media (prefers-color-scheme: light) {{
      .title, .lang-text, .bar, .dots {{ fill: #24292f; }}
    }}
  </style>
  <rect width="{width}" height="{total_height}" fill="transparent" />
  <text class="title" x="{pad_x}" y="30">{title}</text>
{chr(10).join(rows)}
  <text class="dots" x="{pad_x}" y="{dots_y:.1f}">...</text>
</svg>"""
    return svg

if __name__ == "__main__":
    os.makedirs("images", exist_ok=True)
    langs = get_languages()
    svg = generate_svg(langs)
    with open("images/languages.svg", "w") as f:
        f.write(svg)
    print("Updated images/languages.svg with transparent background")
