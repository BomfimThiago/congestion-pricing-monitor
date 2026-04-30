"""Typed configuration loader.

Pydantic validates the YAML at load time. A typo in settings.yaml
fails here, immediately, with a clear error -- not silently three
hours into a pipeline run.
"""

from datetime import date
from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class SourceConfig(BaseModel):
    name: str
    url: str
    page_size: int = 50000
    timeout_seconds: int = 60


class PathsConfig(BaseModel):
    raw: Path
    interim: Path
    processed: Path


class ProjectConfig(BaseModel):
    name: str
    treatment_date: date
    pre_period_start: date


class Settings(BaseModel):
    project: ProjectConfig
    paths: PathsConfig
    sources: dict[str, SourceConfig] = Field(default_factory=dict)


def load_settings(path: Path = Path("config/settings.yaml")) -> Settings:
    with path.open() as f:
        raw = yaml.safe_load(f)
    return Settings(**raw)
