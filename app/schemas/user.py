from pydantic import BaseModel, ConfigDict, Field, field_validator


# --- FUNCIONES DE VALIDACION ---

def _validate_email(value: str):
    """Valida que el formato del correo electronico sea correcto."""
    cleaned_value = value.strip().lower()
    if "@" not in cleaned_value or "." not in cleaned_value.rsplit("@", 1)[-1]:
        raise ValueError("Correo invalido")
    return cleaned_value


def _validate_username(value: str):
    """Valida que el nombre de usuario no este vacio."""
    cleaned_value = value.strip()
    if not cleaned_value:
        raise ValueError("El nombre de usuario no puede estar vacio")
    return cleaned_value


# --- ESQUEMAS DE PYDANTIC ---

class UserBase(BaseModel):
    """
    ESQUEMA BASE DE USUARIOS
    Contiene los campos publicos que identifican a un usuario.
    """
    username: str
    email: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str):
        return _validate_username(value)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str):
        return _validate_email(value)


class UserCreate(UserBase):
    """
    ESQUEMA DE CREACION (Registro)
    Añade el campo password con reglas de longitud minima.
    """
    password: str = Field(min_length=8, max_length=72)


class UserUpdate(BaseModel):
    """
    ESQUEMA DE ACTUALIZACION
    Permite cambiar datos del perfil de forma opcional.
    """
    username: str | None = None
    email: str | None = None
    password: str | None = Field(default=None, min_length=8, max_length=72)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str | None):
        if value is None:
            return value
        return _validate_username(value)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None):
        if value is None:
            return value
        return _validate_email(value)


class UserRead(UserBase):
    """
    ESQUEMA DE RESPUESTA (Lectura)
    Mapea el objeto de base de datos a un formato JSON seguro.
    """
    id: int

    model_config = ConfigDict(from_attributes=True)
