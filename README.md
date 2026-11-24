# Parcial 4 – Rescate del sistema

## Archivos
- `train.py`: entrena un Random Forest de forma reproducible, separa los datos antes de imputar y registra información en MLflow.
- `promotion.py`: promueve un modelo si cumple el RMSE máximo.
- `test_promotion.py`: contiene cuatro pruebas del módulo de promoción.
- `Dockerfile` y `requirements.txt`: configuración de la imagen y dependencias.

## Cómo probar la promoción
Instala las dependencias y ejecuta:

```bash
pytest -q
```

## Cómo entrenar
Debe existir un CSV con una columna llamada `objetivo`:

```bash
python train.py datos.csv
```

El modelo candidato se guarda en `artifacts/modelo_candidato.pkl`. MLflow registra parámetros, RMSE y el hash SHA256 del CSV.
