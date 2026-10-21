"""Gera planta.svg a partir de planta.json."""
import json
import pathlib

aqui = pathlib.Path(__file__).parent
d = json.loads((aqui / "planta.json").read_text())
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
    f'<text x="{M}" y="30" font-size="18" font-weight="bold">Planta baixa — {fmt(W)} m × {fmt(H)} m</text>',
]
for c in d["comodos"]:
    x, y, w, h = M + c["x"] * S, M + c["y"] * S, c["largura"] * S, c["profundidade"] * S
    fill = "#eef3e6" if c.get("externo") else ("#fbf7ee" if c["medida"] == "estimada" else "#f4f4f4")
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

for c in d["comodos"]:
    if c["y"] == 0:
        x1, x2 = M + c["x"] * S, M + (c["x"] + c["largura"]) * S
        o += cota(x1, M - 15, x2, M - 15, fmt(c["largura"]), (x1 + x2) / 2, M - 20)
for y0, h in ((0, 4), (4, 6)):
    y1, y2 = M + y0 * S, M + (y0 + h) * S
    o += cota(M - 15, y1, M - 15, y2, fmt(h), M - 22, (y1 + y2) / 2 + 4, "end")

ly = M + H * S + 30
o.append(f'<rect x="{M}" y="{ly-10}" width="12" height="12" fill="#fbf7ee" stroke="#222"/>')
o.append(f'<text x="{M+18}" y="{ly}" font-size="11">medida estimada (sem cota no esboço)</text>')
o.append(f'<rect x="{M+260}" y="{ly-10}" width="12" height="12" fill="#eef3e6" stroke="#222" stroke-dasharray="3 2"/>')
o.append(f'<text x="{M+278}" y="{ly}" font-size="11">área externa / muro</text>')
o.append("</svg>")
(aqui / "planta.svg").write_text("\n".join(o) + "\n")
