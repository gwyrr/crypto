from pydantic import BaseModel, ConfigDict, field_validator


# --- FUNCIONES DE LIMPIEZA Y VALIDACION ---

def _clean_name(value: str):
    """Elimina espacios en blanco y valida que el nombre no este vacio."""
    cleaned_value = value.strip()
    if not cleaned_value:
        raise ValueError("El nombre no puede estar vacio")
    return cleaned_value


def _clean_symbol(value: str):
    """Normaliza el simbolo a mayusculas y valida que no este vacio."""
    cleaned_value = value.strip().upper()
    if not cleaned_value:
        raise ValueError("El simbolo no puede estar vacio")
    return cleaned_value


def _clean_api_id(value: str):
    """Normaliza el api_id a minusculas y valida que no este vacio."""
    cleaned_value = value.strip().lower()
    if not cleaned_value:
        raise ValueError("El api_id no puede estar vacio")
    return cleaned_value


# --- ESQUEMAS DE PYDANTIC ---

class AssetBase(BaseModel):
    """
    ESQUEMA BASE DE ACTIVOS
    Define los campos comunes para cualquier activo (nombre y simbolo).
    """
    name: str
    symbol: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str):
        return _clean_name(value)

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, value: str):
        return _clean_symbol(value)


class CryptocurrencyCreate(AssetBase):
    """
    ESQUEMA DE CREACION (Criptomonedas)
    Anade el campo api_id necesario para consultar precios externos.
    """
    api_id: str

    @field_validator("api_id")
    @classmethod
    def validate_api_id(cls, value: str):
        return _clean_api_id(value)


class AssetUpdate(BaseModel):
    """
    ESQUEMA DE ACTUALIZACION
    Permite modificar cualquier campo del activo de forma opcional.
    """
    name: str | None = None
    symbol: str | None = None
    api_id: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None):
        if value is None:
            return value
        return _clean_name(value)

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, value: str | None):
        if value is None:
            return value
        return _clean_symbol(value)

    @field_validator("api_id")
    @classmethod
    def validate_api_id(cls, value: str | None):
        if value is None:
            return value
        return _clean_api_id(value)


class AssetRead(AssetBase):
    """
    ESQUEMA DE RESPUESTA (Lectura)
    Incluye el ID y el tipo, formateado para enviarse al frontend.
    """
    id: int
    type: str
    api_id: str | None = None

    # Permite a Pydantic leer datos directamente desde objetos de SQLAlchemy
    model_config = ConfigDict(from_attributes=True)
