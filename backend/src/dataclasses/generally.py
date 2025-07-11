from dataclasses import dataclass, fields


@dataclass
class BaseDataclass:
    """Base dataclass with constructor from ORM object."""

    @classmethod
    def from_orm(cls, orm_obj):
        """Create dataclass instance from ORM object."""
        field_names = {f.name for f in fields(cls)}
        data = {k: getattr(orm_obj, k) for k in field_names if hasattr(orm_obj, k)}
        return cls(**data)
