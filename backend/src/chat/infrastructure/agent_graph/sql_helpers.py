from __future__ import annotations

_SQL_ERROR_HINTS: list[tuple[tuple[str, ...], str]] = [
    (("column", "not found"), "Column name is wrong; use exact names from the schema."),
    (("table", "not found"), "View name is wrong; use only ds_XXXX names from the schema."),
    (("table", "does not exist"), "View name is wrong; use only ds_XXXX names from the schema."),
    (("syntax error",), "Syntax error; check commas, keywords, or unsupported functions."),
    (("ambiguous",), "Ambiguous column; qualify with ds_xxx.column_name."),
    (("type", "cast"), "Type mismatch; use CAST(col AS DOUBLE) or TRY_CAST."),
]
_SQL_HINT_FALLBACK = "Review the SQL for typos or unsupported DuckDB syntax and retry."


def sql_repair_hint(error: str) -> str:
    """Return a targeted fix hint based on common DuckDB SQL errors."""
    err = error.lower()
    hint = next((h for patterns, h in _SQL_ERROR_HINTS if all(p in err for p in patterns)), None)
    return hint or _SQL_HINT_FALLBACK
