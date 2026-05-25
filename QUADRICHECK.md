# QUADRI CHECK - Oracle Red Bull Racing

## 1. INTEGRIDAD DE DATOS

| Criterio | Verificado | Observacion |
|----------|-----------|-------------|
| Datos sin valores nulos criticos | [ ] | Verificar RACEID, DRIVERID, SCORE |
| Tipos de datos correctos | [ ] | int para IDs, float para metricas |
| Registros duplicados eliminados | [ ] | Clave unica: RACEID + DRIVERID + LAP |
| Outliers controlados | [ ] | Winsorizacion al 1% aplicada |

## 2. PROCESAMIENTO

| Criterio | Verificado | Observacion |
|----------|-----------|-------------|
| lt.py genera lt_mod.csv | [ ] | Tiempos por vuelta |
| ps.py genera ps_mod.csv | [ ] | Paradas en boxes |
| merge_script.py genera merged_dataset.csv | [ ] | Union por RACEID |
| 01.ipynb genera processed_dataset.csv | [ ] | Feature engineering |
| inyeccion-01.py sube a MongoDB | [ ] | Script de Ana |

## 3. MODELOS PREDICTIVOS

| Modelo | R2 | MAE | RMSE | Verificado |
|--------|----|-----|------|-----------|
| XGBoost | 0.7128 | 0.5941 | 0.7432 | [ ] |
| SVM | 0.4969 | 0.8229 | 0.9836 | [ ] |
| PyTorch NN | 0.3601 | 0.9298 | 1.1092 | [ ] |
| Random Forest | - | - | - | [ ] |
| Extra Trees | - | - | - | [ ] |
| Gradient Boosting | - | - | - | [ ] |

## 4. BASE DE DATOS (MongoDB)

| Criterio | Verificado | Observacion |
|----------|-----------|-------------|
| Conexion a MongoDB estable | [ ] | Verificar string conexion |
| Datos inyectados correctamente | [ ] | Script de Ana |
| Colecciones creadas | [ ] | ds, lt, ps, rcs, rts, sc |
| Indices optimizados | [ ] | Por RACEID y DRIVERID |

## 5. APLICACION WEB

| Criterio | Verificado | Observacion |
|----------|-----------|-------------|
| app.py master funciona | [ ] | Desarrollado por Ingrid y Liz |
| Conexion a MongoDB desde app | [ ] | Lectura de datos |
| Diseño pendiente (Andy) | [ ] | Se aplicara despues |
| Visualizaciones correctas | [ ] | Graficos y tablas |

## 6. REPOSITORIO

| Criterio | Verificado | Observacion |
|----------|-----------|-------------|
| README actualizado | [ ] | Instrucciones de ejecucion |
| .gitignore configurado | [ ] | Excluir __pycache__, .env |
| Ramas sincronizadas | [ ] | main, andy, liz, ingrid, ana |
| Scripts documentados | [ ] | Comentarios en cada archivo |

## 7. VALIDACION FINAL

| Criterio | Estado | Fecha | Responsable |
|----------|--------|-------|-------------|
| Pipelines de datos | Pendiente | - | Liz |
| Modelos exportados | Pendiente | - | Equipo |
| Inyeccion MongoDB | Pendiente | - | Ana |
| App funcional | Pendiente | - | Ingrid/Liz |
| Diseño completo | Pendiente | - | Andy |

**Responsable de calidad:** _________________
**Fecha de revision:** _________________
**Firma:** _________________
