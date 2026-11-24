import json
import pytest
from promotion import promover


def crear_registro(tmp_path):
    ruta = tmp_path / "registro.json"
    datos = {
        "modelos": [
            {"id": "v1", "rmse": 12.0, "estado": "produccion"},
            {"id": "v2", "rmse": 9.0, "estado": "candidato"},
            {"id": "v3", "rmse": 20.0, "estado": "candidato"}
        ]
    }
    ruta.write_text(json.dumps(datos), encoding="utf-8")
    return ruta


def leer(ruta):
    return json.loads(ruta.read_text(encoding="utf-8"))


def test_promueve_candidato_que_cumple(tmp_path):
    ruta = crear_registro(tmp_path)
    assert promover(ruta, "v2", 10.0) is True
    datos = leer(ruta)["modelos"]
    assert next(m for m in datos if m["id"] == "v2")["estado"] == "produccion"
    assert next(m for m in datos if m["id"] == "v1")["estado"] == "archivado"


def test_no_promueve_si_rmse_supera_limite(tmp_path):
    ruta = crear_registro(tmp_path)
    antes = leer(ruta)
    assert promover(ruta, "v3", 10.0) is False
    assert leer(ruta) == antes


def test_promover_dos_veces_es_idempotente(tmp_path):
    ruta = crear_registro(tmp_path)
    assert promover(ruta, "v2", 10.0) is True
    despues_primera = leer(ruta)
    assert promover(ruta, "v2", 10.0) is True
    assert leer(ruta) == despues_primera


def test_candidato_inexistente_da_error_y_no_cambia_registro(tmp_path):
    ruta = crear_registro(tmp_path)
    antes = leer(ruta)
    with pytest.raises(ValueError):
        promover(ruta, "no-existe", 10.0)
    assert leer(ruta) == antes
