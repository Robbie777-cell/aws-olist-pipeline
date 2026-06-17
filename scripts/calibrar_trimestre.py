import ee
import json
from datetime import datetime, timezone

GEE_PROJECT = "tingua-earth-engine"
BUFFER_M = 2000
CLOUD_MAX = 40
AÃ‘O_ACTUAL = 2026
MES_INICIO = 4   # abril
MES_FIN = 6      # junio

def init_gee():
    import google.auth
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/earthengine"])
    ee.Initialize(credentials=credentials, project=GEE_PROJECT)
    print("GEE OK:", GEE_PROJECT)

def ndwi_promedio(geom, y1, y2, m1, m2):
    col = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
           .filterBounds(geom)
           .filter(ee.Filter.calendarRange(y1, y2, "year"))
           .filter(ee.Filter.calendarRange(m1, m2, "month"))
           .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", CLOUD_MAX)))

    def add_ndwi(img):
        return img.normalizedDifference(["B3","B8"]).rename("NDWI")

    ndwi_col = col.map(add_ndwi)
    n = ndwi_col.size().getInfo()
    if n == 0:
        return None, 0
    mean_img = ndwi_col.mean()
    val = mean_img.reduceRegion(reducer=ee.Reducer.mean(), geometry=geom, scale=20, maxPixels=1e9).get("NDWI")
    return round(val.getInfo(), 4), n

def main():
    init_gee()

    wetlands = [
        {"id":"cienaga_grande", "nombre":"CiÃ©naga Grande de Santa Marta", "lat":10.85, "lng":-74.35, "descripcion":"Mayor humedal costero de Colombia. Sitio RAMSAR."},
        {"id":"mallorquin", "nombre":"CiÃ©naga de MallorquÃ­n", "lat":11.045, "lng":-74.835, "descripcion":"Laguna costera norte de Barranquilla. Manglar denso."},
        {"id":"totumo", "nombre":"CiÃ©naga de Totumo", "lat":10.732, "lng":-75.229, "descripcion":"Humedal salobre con volcÃ¡n de lodo activo."},
        {"id":"zapatosa", "nombre":"CiÃ©naga de Zapatosa", "lat":8.95, "lng":-73.80, "descripcion":"Mayor humedal interior de Colombia (Cesar/Magdalena)."},
        {"id":"caimanera", "nombre":"La Caimanera (CispatÃ¡)", "lat":9.37, "lng":-75.78, "descripcion":"Complejo de manglares CispatÃ¡, Golfo de Morrosquillo."}
    ]

    resultado = {
        "metadata": {
            "fuente": "Sentinel-2 SR Harmonized (COPERNICUS/S2_SR_HARMONIZED)",
            "metodologia": f"Buffer circular {BUFFER_M}m por humedal, filtro cloud<{CLOUD_MAX}%, NDWI=(B3-B8)/(B3+B8), ventana trimestral abr-jun",
            "periodo_historico": "2019-2025 (abr-jun)",
            "periodo_actual": f"{AÃ‘O_ACTUAL} (abr-jun)",
            "generado": datetime.now(timezone.utc).isoformat(),
            "proyecto": "TINGUA"
        },
        "humedales": []
    }

    print("=" * 60)
    print(f"TINGUA - Calibracion TRIMESTRAL abr-jun (buffer={BUFFER_M}m, cloud<{CLOUD_MAX}%)")
    print("=" * 60)

    for w in wetlands:
        print()
        print(w["nombre"])
        geom = ee.Geometry.Point([w["lng"], w["lat"]]).buffer(BUFFER_M)

        val_actual, n_actual = ndwi_promedio(geom, AÃ‘O_ACTUAL, AÃ‘O_ACTUAL, MES_INICIO, MES_FIN)
        print(f"  Actual abr-jun {AÃ‘O_ACTUAL}: {val_actual} (n={n_actual})")

        val_hist, n_hist = ndwi_promedio(geom, 2019, 2025, MES_INICIO, MES_FIN)
        print(f"  Hist abr-jun 2019-2025: {val_hist} (n={n_hist})")

        delta = round(val_actual - val_hist, 4) if (val_actual is not None and val_hist is not None) else None
        print(f"  Delta: {delta}")

        resultado["humedales"].append({
            "id": w["id"],
            "nombre": w["nombre"],
            "lat": w["lat"],
            "lng": w["lng"],
            "descripcion": w["descripcion"],
            "ndwi_actual": val_actual,
            "n_actual": n_actual,
            "ndwi_historico": val_hist,
            "n_historico": n_hist,
            "delta": delta
        })

    with open("docs/data/humedales.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print()
    print("Guardado en docs/data/humedales.json")
    print("Listo.")

if __name__ == "__main__":
    main()

