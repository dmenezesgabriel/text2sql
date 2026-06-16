# Vulture false positives, grouped by why they're not actually dead code.
# Each entry is a real, intentional symbol — see the reason on each group.

# Port methods with a concrete adapter and direct unit-test coverage; not yet
# called by any use case, but part of the designed interface contract.
_.call_with_tools  # i_language_model_provider.py / litellm_provider.py
_.can_handle  # i_tool_executor.py / sql_generator.py

# Domain entity/value-object behavior methods with direct unit tests proving
# their contract; not yet wired into a use case.
_.supports_tool
_.context_limit_is
_.kind_is
_.has_tool_calls
_.remove_tile
_.add_tile_from_question
_.rename
_.is_after
_.touch
_.column_count
_.has_numeric_columns

# Enum members representing forward-looking domain vocabulary, not yet
# produced/consumed by any code path.
TOOL  # MessageRole.TOOL
DATABASE  # DatasetKind.DATABASE
CSV  # FileFormat.CSV
PARQUET  # FileFormat.PARQUET
JSON  # FileFormat.JSON
DASHBOARD  # ResponseKind.DASHBOARD

# Tool-call parameter exposed to the LLM's function-calling schema; the LLM
# supplies it but the implementation intentionally ignores the value.
reasoning  # langgraph_orchestrator.py run_sql()

# Adapter for INotificationPort (see refresh_stale_questions.py), implemented
# and tested, but the use case it serves isn't wired into composition_root yet.
ConsoleNotifier

# Write-only monkeypatch on the external litellm module; read by litellm
# itself, never by our code.
_.suppress_debug_info

# Starlette middleware override, invoked by the framework's dispatch chain.
_.dispatch

# pynamodb Meta class attributes, read by pynamodb's own metaclass machinery.
region
aws_access_key_id
aws_secret_access_key
table_name
