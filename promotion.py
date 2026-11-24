"""Promoción simple y segura de modelos usando un registro JSON.

Especificación:
- Entrada: ruta del registro, id del candidato y RMSE máximo permitido.
- Precondición: el registro contiene una lista 'modelos'; cada modelo tiene
  'id', 'rmse' y 'estado'.
- Regla: solo se promueve si el candidato existe, su RMSE es numérico y
  menor o igual al máximo permitido.
- Postcondición: si se promueve, el candidato queda como único 'produccion'
  y el anterior queda 'archivado'.
- Idempotencia: promover el mismo candidato otra vez no cambia el resultado.
- Si el candidato no cumple, el registro queda exactamente igual.
"""

import json
import os
import tempfile


def promover(ruta_registro, id_candidato, rmse_maximo):
    with open(ruta_registro, "r", encoding="utf-8") as archivo:
        registro = json.load(archivo)

    modelos = registro.get("modelos", [])
    candidato = next((m for m in modelos if m.get("id") == id_candidato), None)

    if candidato is None:
        raise ValueError("No existe el modelo candidato")

    try:
        rmse = float(candidato["rmse"])
    except (KeyError, TypeError, ValueError):
        raise ValueError("El candidato no tiene un RMSE válido")

    if rmse > rmse_maximo:
        return False

    # Si ya es producción, no se vuelve a modificar el registro.
    if candidato.get("estado") == "produccion":
        return True

    # Se modifica una copia en memoria y se guarda al final.
    nuevo = json.loads(json.dumps(registro))
    for modelo in nuevo["modelos"]:
        if modelo.get("estado") == "produccion":
            modelo["estado"] = "archivado"

    for modelo in nuevo["modelos"]:
        if modelo.get("id") == id_candidato:
            modelo["estado"] = "produccion"

    carpeta = os.path.dirname(os.path.abspath(ruta_registro))
    fd, temporal = tempfile.mkstemp(prefix="registro_", suffix=".json", dir=carpeta)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as archivo:
            json.dump(nuevo, archivo, indent=2, ensure_ascii=False)
            archivo.flush()
            os.fsync(archivo.fileno())
        os.replace(temporal, ruta_registro)
    except Exception:
        if os.path.exists(temporal):
            os.remove(temporal)
        raise

    return True
