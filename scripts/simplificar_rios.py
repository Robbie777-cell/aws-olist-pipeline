import json

print("Cargando GeoJSON...")
with open("rios_raw.geojson", "r", encoding="utf-8") as f:
    data = json.load(f)

print("Features originales:", len(data["features"]))

filtrados = []
contador = 0
for feat in data["features"]:
    orden = feat["properties"].get("RIV_ORD", 0)
    if orden >= 7:
        contador += 1
        if contador % 4 != 0:
            continue
        geom = feat["geometry"]
        if geom["type"] == "LineString":
            coords = geom["coordinates"]
            simplificado = [[round(c[0],3), round(c[1],3)] for c in coords[::8]]
            if len(simplificado) < 2:
                simplificado = [[round(c[0],3), round(c[1],3)] for c in coords]
            geom["coordinates"] = simplificado
        filtrados.append({"type": "Feature", "geometry": geom, "properties": {"o": orden}})

print("Features finales:", len(filtrados))

salida = {"type": "FeatureCollection", "features": filtrados}

with open("docs/rios_colombia.geojson", "w", encoding="utf-8") as f:
    json.dump(salida, f, ensure_ascii=False, separators=(",",":"))

import os
size = os.path.getsize("docs/rios_colombia.geojson")
print("Nuevo tamano:", round(size/1024, 1), "KB")
