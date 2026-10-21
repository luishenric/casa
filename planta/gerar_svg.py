"""Gera <nome>.svg a partir de <nome>.json (padrão: planta). Uso: python3 gerar_svg.py [planta|reforma]"""
import json
import pathlib
import sys

aqui = pathlib.Path(__file__).parent
nome = sys.argv[1] if len(sys.argv) > 1 else "planta"
d = json.loads((aqui / f"{nome}.json").read_text())
S, M = 50, 70  # px por metro, margem
W, H = d["dimensoes_totais"]["largura"], d["dimensoes_totais"]["profundidade"]


def fmt(v):
    return f"{v:g}".replace(".", ",")


def cota(x1, y1, x2, y2, texto, tx, ty, anchor="middle"):
    vert = x1 == x2
    t = [(-5, 0, 5, 0) if vert else (0, -5, 0, 5)]
    out = [f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#888"/>']
    for px, py in ((x1, y1), (x2, y2)):
        a, b, c, e = t[0]
        out.append(f'<line x1="{px+a}" y1="{py+b}" x2="{px+c}" y2="{py+e}" stroke="#888"/>')
    out.append(f'<text x="{tx}" y="{ty}" font-size="11" text-anchor="{anchor}" fill="#555">{texto}</text>')
    return out


o = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W*S+2*M}" height="{H*S+2*M+30}" font-family="Helvetica,Arial,sans-serif">',
    '<rect width="100%" height="100%" fill="#fff"/>',
    f'<text x="{M}" y="30" font-size="18" font-weight="bold">{d.get("titulo", "Planta baixa")} — {fmt(W)} m × {fmt(H)} m</text>',
]
for c in d["comodos"]:
    x, y, w, h = M + c["x"] * S, M + c["y"] * S, c["largura"] * S, c["profundidade"] * S
    if c.get("externo"):
        fill = "#eef3e6"
    elif c.get("status") == "reformado":
        fill = "#e6eff8"
    elif c.get("medida") == "estimada":
        fill = "#fbf7ee"
    else:
        fill = "#f4f4f4"
    dash = ' stroke-dasharray="6 4"' if c.get("externo") else ""
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="#222" stroke-width="3"{dash}/>')
    cx, cy = x + w / 2, y + h / 2
    estreito = w < 100
    fs = 10 if estreito else 14
    area = fmt(round(c["largura"] * c["profundidade"], 2))
    dims = f'{fmt(c["largura"])}×{fmt(c["profundidade"])}'
    linhas = [dims + " m", area + " m²"] if estreito else [f"{dims} m · {area} m²"]
    o.append(f'<text x="{cx}" y="{cy-6}" font-size="{fs}" text-anchor="middle" font-weight="bold">{c["nome"]}</text>')
    for i, ln in enumerate(linhas):
        o.append(f'<text x="{cx}" y="{cy+9+i*12}" font-size="{fs-1}" text-anchor="middle" fill="#555">{ln}</text>')

# paredes removidas: cobre a linha e marca tracejado fino
for i in d.get("integracoes", []):
    x1, y1, x2, y2 = (M + i[k] * S for k in ("x1", "y1", "x2", "y2"))
    o.append(f'<line x1="{x1}" y1="{y1+2}" x2="{x2}" y2="{y2-2}" stroke="#e6eff8" stroke-width="5"/>')
    o.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#7a8aa0" stroke-width="1" stroke-dasharray="4 4"/>')

for c in d["comodos"]:
    if c["y"] == 0:
        x1, x2 = M + c["x"] * S, M + (c["x"] + c["largura"]) * S
        o += cota(x1, M - 15, x2, M - 15, fmt(c["largura"]), (x1 + x2) / 2, M - 20)
for y0, h in sorted({(c["y"], c["profundidade"]) for c in d["comodos"] if c["x"] == 0}):
    y1, y2 = M + y0 * S, M + (y0 + h) * S
    o += cota(M - 15, y1, M - 15, y2, fmt(h), M - 22, (y1 + y2) / 2 + 4, "end")

ly = M + H * S + 30
cs = d["comodos"]
legenda = [
    ("#fbf7ee", "", "medida estimada (sem cota no esboço)", any(c.get("medida") == "estimada" for c in cs)),
    ("#e6eff8", "", "cômodo novo / reformado", any(c.get("status") == "reformado" for c in cs)),
    ("#eef3e6", ' stroke-dasharray="3 2"', "área externa / muro", any(c.get("externo") for c in cs)),
]
lx = M
for cor, dash, texto, usar in legenda:
    if usar:
        o.append(f'<rect x="{lx}" y="{ly-10}" width="12" height="12" fill="{cor}" stroke="#222"{dash}/>')
        o.append(f'<text x="{lx+18}" y="{ly}" font-size="11">{texto}</text>')
        lx += 260
if d.get("integracoes"):
    o.append(f'<line x1="{lx}" y1="{ly-4}" x2="{lx+12}" y2="{ly-4}" stroke="#7a8aa0" stroke-dasharray="4 4"/>')
    o.append(f'<text x="{lx+18}" y="{ly}" font-size="11">ambiente integrado (sem parede)</text>')
o.append("</svg>")
(aqui / f"{nome}.svg").write_text("\n".join(o) + "\n")
