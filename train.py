import argparse
import hashlib
import os

import mlflow
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


def hash_archivo(ruta):
    """Calcula el SHA256 del CSV usado para entrenar."""
    sha = hashlib.sha256()
    with open(ruta, "rb") as archivo:
        for bloque in iter(lambda: archivo.read(8192), b""):
            sha.update(bloque)
    return sha.hexdigest()


def entrenar(ruta_csv, semilla=42, arboles=100):
    df = pd.read_csv(ruta_csv)

    if "objetivo" not in df.columns:
        raise ValueError("El CSV debe tener una columna llamada 'objetivo'")

    # No se inventan etiquetas: se quitan filas sin objetivo.
    df = df.dropna(subset=["objetivo"])
    X = df.drop(columns=["objetivo"])
    y = df["objetivo"]

    if len(df) < 5:
        raise ValueError("Se necesitan al menos 5 filas para entrenar")

    # La división se hace antes de calcular cualquier imputación.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=semilla
    )

    # El imputador aprende solo de entrenamiento gracias al Pipeline.
    modelo = Pipeline([
        ("imputador", SimpleImputer(strategy="mean")),
        ("bosque", RandomForestRegressor(
            n_estimators=arboles, random_state=semilla
        ))
    ])

    modelo.fit(X_train, y_train)
    predicciones = modelo.predict(X_test)
    rmse = float(np.sqrt(mean_squared_error(y_test, predicciones)))
    hash_datos = hash_archivo(ruta_csv)

    with mlflow.start_run():
        mlflow.log_param("semilla", semilla)
        mlflow.log_param("n_estimators", arboles)
        mlflow.log_param("test_size", 0.2)
        mlflow.log_param("modelo", "RandomForestRegressor con imputación")
        mlflow.log_metric("rmse", rmse)
        mlflow.log_param("dataset_sha256", hash_datos)
        mlflow.sklearn.log_model(modelo, artifact_path="modelo")

    os.makedirs("artifacts", exist_ok=True)
    import joblib
    joblib.dump(modelo, "artifacts/modelo_candidato.pkl")

    print("RMSE:", round(rmse, 4))
    print("SHA256 del CSV:", hash_datos)
    return rmse, hash_datos


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", help="Ruta al archivo CSV")
    parser.add_argument("--semilla", type=int, default=42)
    parser.add_argument("--arboles", type=int, default=100)
    args = parser.parse_args()
    entrenar(args.csv, args.semilla, args.arboles)
