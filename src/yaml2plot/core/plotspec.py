"""
Pydantic-based plot specification models.

This module provides PlotSpec and YAxisSpec classes that replace PlotConfig
with structured validation and type safety.
"""

from typing import List, Optional, Dict, Any, Union
from pathlib import Path
import yaml
from pydantic import BaseModel, Field, ConfigDict, field_validator, ValidationError


class XAxisSpec(BaseModel):
    """X-axis configuration specification."""

    signal: str = Field(..., description="X-axis signal key")
    label: Optional[str] = Field(None, description="X-axis label")
    scale: Optional[str] = Field(None, description="Scale type: 'log' or 'linear'")
    unit: Optional[str] = Field(None, description="Unit for display")
    range: Optional[List[float]] = Field(None, description="[min, max] range")
    model_config = ConfigDict(extra="forbid")

    @field_validator("scale")
    @classmethod
    def validate_scale(cls, value: Optional[str]) -> Optional[str]:
        """Restrict scale values to known Plotly axis scale types."""
        if value is None:
            return value
        normalized = value.strip().lower()
        if normalized not in {"linear", "log"}:
            raise ValueError("scale must be one of: linear, log")
        return normalized

    @field_validator("range")
    @classmethod
    def validate_range(cls, value: Optional[List[float]]) -> Optional[List[float]]:
        """Validate explicit axis range values."""
        if value is None:
            return value
        if len(value) != 2:
            raise ValueError("range must contain exactly two numeric values: [min, max]")
        lower, upper = value
        if lower >= upper:
            raise ValueError("range must be strictly increasing: min < max")
        return value


class YAxisSpec(BaseModel):
    """Y-axis configuration specification."""

    label: str = Field(..., description="Y-axis label")
    signals: Dict[str, str] = Field(
        ..., min_length=1, description="Legend name -> signal key mapping"
    )
    scale: Optional[str] = Field(None, description="Scale type: 'log' or 'linear'")
    unit: Optional[str] = Field(None, description="Unit for display")
    range: Optional[List[float]] = Field(None, description="[min, max] range")
    color: Optional[str] = Field(None, description="Axis color")
    model_config = ConfigDict(extra="forbid")

    @field_validator("scale")
    @classmethod
    def validate_scale(cls, value: Optional[str]) -> Optional[str]:
        """Restrict scale values to known Plotly axis scale types."""
        if value is None:
            return value
        normalized = value.strip().lower()
        if normalized not in {"linear", "log"}:
            raise ValueError("scale must be one of: linear, log")
        return normalized

    @field_validator("range")
    @classmethod
    def validate_range(cls, value: Optional[List[float]]) -> Optional[List[float]]:
        """Validate explicit axis range values."""
        if value is None:
            return value
        if len(value) != 2:
            raise ValueError("range must contain exactly two numeric values: [min, max]")
        lower, upper = value
        if lower >= upper:
            raise ValueError("range must be strictly increasing: min < max")
        return value


class PlotSpec(BaseModel):
    """
    Pydantic-based plot specification with fluent API.

    Replaces PlotConfig with structured validation and composable workflow.
    """

    # Core configuration
    # Accept both lowercase (preferred) and uppercase aliases for backward compatibility
    x: XAxisSpec = Field(..., description="X-axis configuration", alias="X")
    y: List[YAxisSpec] = Field(
        ..., min_length=1, description="Y-axis specifications", alias="Y"
    )
    title: Optional[str] = Field(None, description="Plot title")
    raw: Optional[str] = Field(
        None, description="Path to SPICE raw file for self-contained specs"
    )

    # Styling options
    width: Optional[int] = Field(None, description="Plot width in pixels")
    height: Optional[int] = Field(None, description="Plot height in pixels")
    theme: Optional[str] = Field("plotly", description="Plot theme")

    # Title positioning
    title_x: float = Field(
        0.5, description="Title x position (0=left, 0.5=center, 1=right)"
    )
    title_xanchor: str = Field(
        "center", description="Title anchor: left, center, right"
    )

    # Advanced options
    show_legend: bool = Field(True, description="Show legend")
    grid: bool = Field(True, description="Show grid")
    show_rangeslider: bool = Field(True, description="Show range slider below X-axis")

    # Pydantic model configuration
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    # Factory methods
    @classmethod
    def from_yaml(cls, yaml_str: str) -> "PlotSpec":
        """Create PlotSpec from YAML string."""
        try:
            config_dict = yaml.safe_load(yaml_str)
            if isinstance(config_dict, list):
                raise ValueError("Multi-figure configurations not supported")
            if not isinstance(config_dict, dict):
                raise ValueError("YAML must define a mapping/object for a single plot spec")
            return cls.model_validate(config_dict)
        except ValidationError as e:
            raise ValueError(cls._format_validation_error(e)) from e
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML syntax: {e}") from e

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> "PlotSpec":
        """
        Create PlotSpec from YAML file.

        Args:
            file_path: Path to YAML configuration file

        Returns:
            PlotSpec instance

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If YAML is invalid or unsupported
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        try:
            yaml_content = file_path.read_text(encoding="utf-8")
            return cls.from_yaml(yaml_content)
        except ValueError as e:
            raise ValueError(f"Failed to load configuration from {file_path}: {e}") from e
        except Exception as e:
            raise ValueError(f"Failed to load configuration from {file_path}: {e}") from e

    # Configuration export methods
    def to_dict(self) -> Dict[str, Any]:
        """
        Export clean configuration dictionary for v1.0.0 plotting functions.

        Returns:
            Dict containing clean configuration suitable for standalone plotting functions
        """
        return self.model_dump(by_alias=False)

    @staticmethod
    def _format_validation_error(error: ValidationError) -> str:
        """Create compact and user-facing validation diagnostics."""
        issues: List[str] = []
        for item in error.errors():
            loc = ".".join(str(part) for part in item.get("loc", ()))
            msg = item.get("msg", "Invalid value")
            issues.append(f"{loc}: {msg}")
        return "Invalid plot specification:\n- " + "\n- ".join(issues)
