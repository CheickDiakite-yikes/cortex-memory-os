"""Helpers for loading contract fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)


def load_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_model(path: str | Path, model_type: type[ModelT]) -> ModelT:
    return model_type.model_validate(load_json(path))


def dump_jsonable(model: BaseModel) -> dict:
    return model.model_dump(mode="json")

