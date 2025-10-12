import unicodedata


def limpiar_nombre(nombre):
    nombre = nombre.strip().replace(" ", "-")
    nombre = unicodedata.normalize('NFKD', nombre).encode('ASCII', 'ignore').decode()
    return nombre

