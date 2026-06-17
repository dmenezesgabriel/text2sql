from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel


class _StrictSchema(BaseModel):
    """Forces all properties into JSON schema 'required' array.

    OpenAI strict structured-output mode (and GitHub Copilot) rejects schemas
    where optional-with-default fields are absent from 'required'.
    """

    @classmethod
    def model_json_schema(cls, *args: Any, **kwargs: Any) -> dict[str, Any]:
        schema = super().model_json_schema(*args, **kwargs)
        if "properties" in schema:
            schema["required"] = list(schema["properties"].keys())
        return schema


class Intent(_StrictSchema):
    intent: Literal["data_query", "clarification_needed"]
    clarification_question: str = ""


class GeneratedSQL(_StrictSchema):
    sql: str


class RepairedSQL(_StrictSchema):
    sql: str


class VizChoice(_StrictSchema):
    component: Literal[
        "BarChart",
        "LineChart",
        "PieChart",
        "Metric",
        "DataTable",
        "NarrativeText",
    ]
    label_column: str = ""
    value_column: str = ""
    narrative: str = ""
