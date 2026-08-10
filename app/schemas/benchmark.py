"""Benchmark schemas and utilities."""

import json
from pathlib import Path
from pydantic import BaseModel

from app.core.config import settings

__all__ = ["Benchmark", "load_benchmark"]

class Benchmark(BaseModel):
    """A benchmark representing requirements for a specific niche and level."""
    model_config = {"frozen": True}
    
    niche: str
    version: str
    required_terms: list[str]
    benchmark_topics: list[str]
    title_formula: str
    portfolio_targets: int
    overview_targets: int
    rate_band: tuple[float, float]
    dimension_targets: dict[str, float]

def load_benchmark(niche: str, version: str, data_dir: Path | None = None) -> Benchmark:
    """Load and validate a benchmark from a JSON file."""
    dir_path = data_dir if data_dir is not None else settings.data_dir
    file_path = dir_path / "benchmarks" / f"{niche}_{version}.json"
    
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    return Benchmark.model_validate(data)