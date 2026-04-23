from pydantic import BaseModel, ConfigDict, Field, field_validator


def _validate_email(value: str):
    cleaned_value = value.strip().lower()
    if "@" not in cleaned_value or "." not in cleaned_value.rsplit("@", 1)[-1]:
        raise ValueError("Correo invalido")
    return cleaned_value


def _validate_username(value: str):
    cleaned_value = value.strip()
    if not cleaned_value:
        raise ValueError("El nombre de usuario no puede estar vacio")
    return cleaned_value


class UserBase(BaseModel):
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
    password: str = Field(min_length=8, max_length=72)


class UserUpdate(BaseModel):
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
    id: int

    model_config = ConfigDict(from_attributes=True)
