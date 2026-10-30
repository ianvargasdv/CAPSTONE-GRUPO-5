"""Direcciones web autorizadas a consultar la API desde un navegador."""
from urllib.parse import urlsplit


def cargar_origenes(adicionales: str = "") -> list[str]:
    origenes = ["http://localhost:3000", "http://127.0.0.1:3000"]
    for valor in adicionales.split(","):
        valor = valor.strip()
        if not valor:
            continue
        try:
            partes = urlsplit(valor)
            puerto = partes.port
            valido = (
                partes.scheme in {"http", "https"}
                and partes.hostname
                and not partes.username and not partes.password
                and partes.path in {"", "/"}
                and not partes.query and not partes.fragment
                and not any(c.isspace() for c in valor)
                and "*" not in valor
            )
            if not valido:
                raise ValueError
            host = partes.hostname.lower()
            if ":" in host:
                host = f"[{host}]"
            sufijo = "" if puerto is None or (partes.scheme, puerto) in {("http", 80), ("https", 443)} else f":{puerto}"
            origen = f"{partes.scheme}://{host}{sufijo}"
        except ValueError:
            # El valor inválido puede contener credenciales: no se imprime.
            raise ValueError("CORS_ORIGINS debe contener orígenes HTTP/HTTPS separados por coma, sin rutas, credenciales ni comodines.") from None
        if origen not in origenes:
            origenes.append(origen)
    return origenes
