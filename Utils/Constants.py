import os
# CONSTANTES
def construir_ruta(base, *paths):
    return os.path.join(base, *paths).replace("/", os.path.sep)

RUTA_ACTUAL = os.getcwd()
RUTA_REMOTA = "/Demiset"
RUTA_LOCAL_ZIPS = construir_ruta(RUTA_ACTUAL, "zips")
