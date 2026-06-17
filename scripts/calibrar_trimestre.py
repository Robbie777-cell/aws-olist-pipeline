import ee
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone

GEE_PROJECT = "tingua-earth-engine"
BUFFER_M = 2000
CLOUD_MAX = 40
ANIO_ACTUAL = 2026
MES_INICIO = 4
MES_FIN = 6
UMBRAL_ALERTA = -0.06
UMBRAL_VIGILAR = -0.02

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

def enviar_alerta(alertas, vigilancias, fecha):
    gmail_pass = os.environ.get("GMAIL_APP_PASSWORD")
    alert_email = os.environ.get("ALERT_EMAIL")
    if not gmail_pass or not alert_email:
        print("SKIP: no hay credenciales de email")
        return
    if not alertas and not vigilancias:
        print("Sin alertas - no se envia email")
        return
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"TINGUA ALERTA - {len(alertas)} humedal(es) critico(s) - {fecha}"
    msg["From"] = alert_email
    msg["To"] = alert_email
    texto = f"TINGUA - Monitor de Humedales\nFecha: {fecha}\n\n"
    if alertas:
        texto += f"ALERTAS CRITICAS ({len(alertas)}):\n"
        for h in alertas:
            texto += f"  - {h['nombre']}: delta {h['delta']:+.3f}\n"
    if vigilancias:
        texto += f"\nVIGILANCIA ({len(vigilancias)}):\n"
        for h in vigilancias:
            texto += f"  - {h['nombre']}: delta {h['delta']:+.3f}\n"
    texto += f"\nhttps://robbie777-cell.github.io/aws-olist-pipeline/\n"
    msg.attach(MIMEText(texto, "plain"))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(alert_email, gmail_pass)
            server.sendmail(alert_email, alert_email, msg.as_string())
        print(f"Email enviado a {alert_email}")
    except Exception as e:
        print(f"Error enviando email: {e}")

def main():
    init_gee()
    wetlands = [
        {"id":"cienaga_grande","nombre":"Cienaga Grande de Santa Marta","lat":10.85,"lng":-74.35,"descripcion":"Mayor humedal costero de Colombia. Sitio RAMSAR."},
        {"id":"mallorquin","nombre":"Cienaga de Mallorquin","lat":11.045,"lng":-74.835,"descripcion":"Laguna costera norte de Barranquilla."},
        {"id":"totumo","nombre":"Cienaga de Totumo","lat":10.732,"lng":-75.229,"descripcion":"Humedal salobre con volcan de lodo activo."},
        {"id":"zapatosa","nombre":"Cienaga de Zapatosa","lat":8.95,"lng":-73.80,"descripcion":"Mayor humedal interior de Colombia."},
        {"id":"caimanera","nombre":"La Caimanera (Cispata)","lat":9.37,"lng":-75.78,"descripcion":"Complejo de manglares Cispata."}
    ]
    resultado = {
        "metadata": {
            "fuente": "Sentinel-2 SR Harmonized (COPERNICUS/S2_SR_HARMONIZED)",
            "metodologia": f"Buffer circular {BUFFER_M}m, cloud<{CLOUD_MAX}%, NDWI=(B3-B8)/(B3+B8), abr-jun",
            "periodo_historico": "2019-2025 (abr-jun)",
            "periodo_actual": f"{ANIO_ACTUAL} (abr-jun)",
            "generado": datetime.now(timezone.utc).isoformat(),
            "proyecto": "TINGUA"
        },
        "humedales": []
    }
    alertas = []
    vigilancias = []
    print("=" * 60)
    for w in wetlands:
        print(w["nombre"])
        geom = ee.Geometry.Point([w["lng"], w["lat"]]).buffer(BUFFER_M)
        val_actual, n_actual = ndwi_promedio(geom, ANIO_ACTUAL, ANIO_ACTUAL, MES_INICIO, MES_FIN)
        val_hist, n_hist = ndwi_promedio(geom, 2019, 2025, MES_INICIO, MES_FIN)
        delta = round(val_actual - val_hist, 4) if (val_actual is not None and val_hist is not None) else None
        print(f"  actual={val_actual} hist={val_hist} delta={delta}")
        entry = {"id":w["id"],"nombre":w["nombre"],"lat":w["lat"],"lng":w["lng"],"descripcion":w["descripcion"],"ndwi_actual":val_actual,"n_actual":n_actual,"ndwi_historico":val_hist,"n_historico":n_hist,"delta":delta}
        resultado["humedales"].append(entry)
        if delta is not None:
            if delta < UMBRAL_ALERTA:
                alertas.append(entry)
                print("  *** ALERTA CRITICA ***")
            elif delta < UMBRAL_VIGILAR:
                vigilancias.append(entry)
                print("  -- Vigilancia --")
    with open("docs/data/humedales.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    print("Guardado en docs/data/humedales.json")
    fecha = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    enviar_alerta(alertas, vigilancias, fecha)
    print("Listo.")

if __name__ == "__main__":
    main()
