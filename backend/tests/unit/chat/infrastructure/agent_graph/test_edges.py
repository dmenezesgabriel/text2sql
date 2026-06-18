from __future__ import annotations

from src.chat.infrastructure.agent_graph.edges import route_intent, route_sql_result


def _state(**overrides: object) -> dict[str, object]:
    defaults: dict[str, object] = {
        "intent": "data_query",
        "clarification_question": "",
        "sql_error": "",
        "sql_retries": 0,
    }
    return {**defaults, **overrides}


class TestRouteIntent:
    def test_data_query_goes_to_generate_sql(self) -> None:
        assert route_intent(_state()) == "generate_sql"  # type: ignore[arg-type]

    def test_clarification_needed_routes_away(self) -> None:
        state = _state(intent="clarification_needed")
        assert route_intent(state) == "emit_clarification"  # type: ignore[arg-type]

    def test_empty_intent_defaults_to_generate_sql(self) -> None:
        assert route_intent(_state(intent="")) == "generate_sql"  # type: ignore[arg-type]


class TestRouteSqlResult:
    def test_no_error_goes_to_visualization(self) -> None:
        assert route_sql_result(_state()) == "choose_visualization"  # type: ignore[arg-type]

    def test_error_below_limit_goes_to_repair(self) -> None:
        state = _state(sql_error="syntax error", sql_retries=1)
        assert route_sql_result(state) == "repair_sql"  # type: ignore[arg-type]

    def test_error_at_limit_goes_to_clarification(self) -> None:
        state = _state(sql_error="timeout", sql_retries=3)
        assert route_sql_result(state) == "emit_clarification"  # type: ignore[arg-type]

    def test_error_above_limit_goes_to_clarification(self) -> None:
        state = _state(sql_error="still broken", sql_retries=10)
        assert route_sql_result(state) == "emit_clarification"  # type: ignore[arg-type]

    def test_error_with_missing_retries_key_defaults_to_repair(self) -> None:
        # sql_retries key absent → default 0 → 0 < 3 → repair_sql
        # Kills mutmut default=None (None >= 3 → TypeError)
        state = {"intent": "data_query", "sql_error": "oops"}
        assert route_sql_result(state) == "repair_sql"  # type: ignore[arg-type]
