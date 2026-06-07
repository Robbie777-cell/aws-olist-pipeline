// ============================================
// SISTEMA TINGUA — Monitor de Humedales
// Script: NDWI Ciénaga Grande de Santa Marta
// Fuente: Sentinel-2 SR Harmonized (ESA/Copernicus)
// Autor: Rob Acosta — Data Analyst
// Fecha: 2026-06-06
// Proyecto GEE: tingua-earth-engine
// Resultados: 80 imágenes, NDWI_mean=-0.015
// ============================================

// 1. Área de interés — Ciénaga Grande de Santa Marta
var cienaga_grande = ee.Geometry.Rectangle([-74.6, 10.6, -74.1, 11.1]);

// 2. Colección Sentinel-2 filtrada
var sentinel2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterBounds(cienaga_grande)
  .filterDate('2026-01-01', '2026-06-06')
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
  .sort('system:time_start', true);

// 3. Función NDWI por imagen
// NDWI = (Green - NIR) / (Green + NIR)
// Sentinel-2: Green=B3, NIR=B8
var calcularNDWI = function(imagen) {
  var ndwi = imagen.normalizedDifference(['B3', 'B8']).rename('NDWI');
  
  var stats = ndwi.reduceRegion({
    reducer: ee.Reducer.mean()
      .combine(ee.Reducer.min(), '', true)
      .combine(ee.Reducer.max(), '', true)
      .combine(ee.Reducer.stdDev(), '', true),
    geometry: cienaga_grande,
    scale: 20,
    maxPixels: 1e9
  });
  
  return ee.Feature(null, {
    'fecha': imagen.date().format('YYYY-MM-dd'),
    'timestamp': imagen.date().format('YYYY-MM-dd HH:mm:ss'),
    'humedal': 'Cienaga Grande de Santa Marta',
    'sensor_id': 'SENTINEL2-GEE-001',
    'NDWI_mean': stats.get('NDWI_mean'),
    'NDWI_max': stats.get('NDWI_max'),
    'NDWI_min': stats.get('NDWI_min'),
    'NDWI_stdDev': stats.get('NDWI_stdDev'),
    'nubes_pct': imagen.get('CLOUDY_PIXEL_PERCENTAGE'),
    'fuente': 'Sentinel-2 SR Harmonized'
  });
};

// 4. Aplicar a toda la colección
var serie_temporal = sentinel2.map(calcularNDWI);

print('Total imágenes:', serie_temporal.size());
print('Primer registro:', serie_temporal.first());

// 5. Exportar a Google Drive → luego subir a S3
// s3://data-pipeline-rob-2026/tingua/gee/
Export.table.toDrive({
  collection: serie_temporal,
  description: 'tingua_ndwi_cienaga_grande_2026',
  folder: 'TINGUA',
  fileNamePrefix: 'tingua_ndwi_cienaga_grande',
  fileFormat: 'CSV'
});