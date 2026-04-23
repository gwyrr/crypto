from pydantic import BaseModel, ConfigDict, field_validator


def _clean_name(value: str):
    cleaned_value = value.strip()
    if not cleaned_value:
        raise ValueError("El nombre no puede estar vacio")
    return cleaned_value


def _clean_symbol(value: str):
    cleaned_value = value.strip().upper()
    if not cleaned_value:
        raise ValueError("El simbolo no puede estar vacio")
    return cleaned_value


def _clean_api_id(value: str):
    cleaned_value = value.strip().lower()
    if not cleaned_value:
        raise ValueError("El api_id no puede estar vacio")
    return cleaned_value


class AssetBase(BaseModel):
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
    api_id: str

    @field_validator("api_id")
    @classmethod
    def validate_api_id(cls, value: str):
        return _clean_api_id(value)


class AssetUpdate(BaseModel):
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
    id: int
    type: str
    api_id: str | None = None

    model_config = ConfigDict(from_attributes=True)
