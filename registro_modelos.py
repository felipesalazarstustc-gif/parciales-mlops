class RegistroModelos:
    def __init__(self, versiones):
        # Guardo una copia para que no modifiquen la lista original.
        self.__versiones = [v.copy() for v in versiones]
        self.__produccion = None

        for v in self.__versiones:
            if v.get("estado") == "produccion":
                if self.__produccion is not None:
                    raise ValueError("Hay mas de una version en produccion")
                self.__produccion = v["id"]

    def listar(self):
        # Devuelvo copias para proteger la lista interna.
        return [v.copy() for v in self.__versiones]

    def promover(self, id_version):
        nueva_lista = [v.copy() for v in self.__versiones]

        nueva = None
        for v in nueva_lista:
            if v["id"] == id_version:
                nueva = v
                break

        if nueva is None:
            raise ValueError("La version no existe")

        if nueva.get("estado") == "archivada":
            raise ValueError("No se puede promover una version archivada")

        # Hago los cambios en la copia, no en la lista original.
        for v in nueva_lista:
            if v["id"] == self.__produccion:
                v["estado"] = "archivada"

        nueva["estado"] = "produccion"

        # Actualizo todo al final para no dejarlo a medias.
        self.__versiones = nueva_lista
        self.__produccion = id_version

    def version_en_produccion(self):
        return self.__produccion


if __name__ == "__main__":
    registro = RegistroModelos([
        {"id": "v1", "estado": "produccion"},
        {"id": "v2", "estado": "candidata"}
    ])

    registro.promover("v2")
    print("Version en produccion:", registro.version_en_produccion())
    print(registro.listar())
