from dataclasses import dataclass, fields
from datetime import datetime
from enum import Enum
from typing import Any, Union, get_args, get_origin


@dataclass
class BaseDataclass:
    """Base dataclass with ORM/dict conversion (primitives and datetime only)."""

    @classmethod
    def from_orm(cls, orm_object: Any):
        """Convert ORM object to dataclass instance (fails on missing fields)."""
        data = {}
        for field in fields(cls):
            if not hasattr(orm_object, field.name) and (get_origin(field.type) is not Union):
                raise AttributeError(f'Missing field in ORM object: {field.name}')
            if get_origin(field.type) is Union and not hasattr(orm_object, field.name):
                continue
            value = getattr(orm_object, field.name)
            data[field.name] = cls._convert_value(value, field.type)
        return cls(**data)

    @classmethod
    def from_dict(cls, data: dict) -> Any:
        """Convert dictionary to dataclass instance (ignores extra fields)."""
        init_data = {}
        for field in fields(cls):
            if field.name not in data and get_origin(field.type) is not Union:
                raise AttributeError(f'Missing field in Dict object: {field.name}')

            if field.name not in data:
                data[field.name] = None

            value = data[field.name]
            init_data[field.name] = cls._convert_value(value, field.type)
        return cls(**init_data)

    @classmethod
    def _convert_value(cls, value: Any, target_type: Any) -> Any:
        """Handle basic type conversions (datetime only)."""
        if value is None:
            return None

        origin = get_origin(target_type)
        if origin is list:
            type_args = get_args(target_type)
            if type_args:
                inner_type = type_args[0]
                return [cls._convert_value(item, inner_type) for item in value]
            return value

        if isinstance(value, Enum):
            return value.value

        if isinstance(target_type, type) and issubclass(target_type, BaseDataclass):
            if isinstance(value, dict):
                return target_type.from_dict(value)
            return target_type.from_orm(value)

        if isinstance(value, datetime) and target_type is str:
            try:
                return value.isoformat()
            except (ValueError, TypeError):
                return value

        return value
