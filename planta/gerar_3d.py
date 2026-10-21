"""Gera casa3d.html (visualização 3D) a partir de casa3d.template.html e dos JSONs das plantas."""
import json
import pathlib

aqui = pathlib.Path(__file__).parent
dados = {n: json.loads((aqui / f"{n}.json").read_text()) for n in ("planta", "reforma", "terreo_sobrado", "primeiro_andar")}
modelo = (aqui / "casa3d.template.html").read_text()
(aqui / "casa3d.html").write_text(modelo.replace("/*DADOS*/null", json.dumps(dados, ensure_ascii=False)))
