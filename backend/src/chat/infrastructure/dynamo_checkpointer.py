from __future__ import annotations

import base64
import os
from collections.abc import Iterator
from typing import Any, NamedTuple

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    ChannelVersions,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
)
from pynamodb.attributes import UnicodeAttribute
from pynamodb.models import Model


class _CheckpointModel(Model):
    """One item per (thread_id, checkpoint_ns) — stores only the latest checkpoint.

    No time travel or mid-request fault recovery. Provides conversation continuity
    across HTTP requests via thread_id.
    """

    class Meta:
        table_name = "langgraph_checkpoints"
        host = os.getenv("DYNAMODB_HOST", "http://localhost:8000")
        region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID", "fake")
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY", "fake")

    pk = UnicodeAttribute(hash_key=True)  # "{thread_id}|{ns}"
    checkpoint_id = UnicodeAttribute()
    parent_checkpoint_id = UnicodeAttribute(null=True)
    cp_type = UnicodeAttribute()
    cp_data = UnicodeAttribute()  # base64-encoded bytes
    meta_type = UnicodeAttribute()
    meta_data = UnicodeAttribute()  # base64-encoded bytes


class _ThreadKey(NamedTuple):
    tid: str
    ns: str


def _pk(thread_id: str, ns: str) -> str:
    return f"{thread_id}|{ns}"


def _b64enc(data: bytes) -> str:
    return base64.b64encode(data).decode()


def _b64dec(data: str) -> bytes:
    return base64.b64decode(data)


def _parse_config(config: RunnableConfig) -> tuple[str, str, str]:
    c = config.get("configurable", {})
    return (
        str(c.get("thread_id", "")),
        str(c.get("checkpoint_ns", "")),
        str(c.get("checkpoint_id", "")),
    )


def _model_to_tuple(
    serde: Any,
    model: _CheckpointModel,
    key: _ThreadKey,
) -> CheckpointTuple:
    cp = serde.loads_typed((model.cp_type, _b64dec(model.cp_data)))
    meta = serde.loads_typed((model.meta_type, _b64dec(model.meta_data)))
    parent_cfg: RunnableConfig | None = None
    if model.parent_checkpoint_id:
        parent_cfg = {
            "configurable": {
                "thread_id": key.tid,
                "checkpoint_ns": key.ns,
                "checkpoint_id": model.parent_checkpoint_id,
            },
        }
    return CheckpointTuple(
        config={
            "configurable": {
                "thread_id": key.tid,
                "checkpoint_ns": key.ns,
                "checkpoint_id": model.checkpoint_id,
            },
        },
        checkpoint=cp,
        metadata=meta,
        parent_config=parent_cfg,
        pending_writes=[],
    )


class DynamoCheckpointer(BaseCheckpointSaver):
    """DynamoDB-backed LangGraph checkpointer (latest checkpoint per thread).

    Example: DynamoCheckpointer() — uses DYNAMODB_HOST env var.
    """

    def get_tuple(self, config: RunnableConfig) -> CheckpointTuple | None:
        tid, ns, cp_id = _parse_config(config)
        try:
            model = _CheckpointModel.get(_pk(tid, ns))
        except _CheckpointModel.DoesNotExist:
            return None
        if cp_id and model.checkpoint_id != cp_id:
            return None
        return _model_to_tuple(self.serde, model, _ThreadKey(tid, ns))

    def list(
        self,
        config: RunnableConfig | None,
        *,
        filter: dict[str, Any] | None = None,
        before: RunnableConfig | None = None,
        limit: int | None = None,
    ) -> Iterator[CheckpointTuple]:
        if config is None:
            return
        result = self.get_tuple(config)
        if result:
            yield result

    def put(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        tid, ns, _ = _parse_config(config)
        parent = config.get("configurable", {}).get("checkpoint_id") or None
        cp_type, cp_bytes = self.serde.dumps_typed(checkpoint)
        meta_type, meta_bytes = self.serde.dumps_typed(metadata)
        _CheckpointModel(
            pk=_pk(tid, ns),
            checkpoint_id=checkpoint["id"],
            parent_checkpoint_id=parent,
            cp_type=cp_type,
            cp_data=_b64enc(cp_bytes),
            meta_type=meta_type,
            meta_data=_b64enc(meta_bytes),
        ).save()
        return {
            **config,
            "configurable": {
                **config.get("configurable", {}),
                "checkpoint_id": checkpoint["id"],
            },
        }

    def put_writes(
        self,
        config: RunnableConfig,
        writes: list[tuple[str, Any]],
        task_id: str,
        task_path: str = "",
    ) -> None:
        # No mid-request fault recovery; state is fully captured in put().
        pass
