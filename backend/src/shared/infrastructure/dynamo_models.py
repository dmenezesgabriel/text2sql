from __future__ import annotations

import os

from pynamodb.attributes import UnicodeAttribute
from pynamodb.models import Model


class BaseModel(Model):
    class Meta:
        host = os.getenv("DYNAMODB_HOST", "http://localhost:8000")
        region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID", "fake")
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY", "fake")


class ConversationModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "conversations"

    id = UnicodeAttribute(hash_key=True)
    state = UnicodeAttribute()
    title = UnicodeAttribute(null=True)
    updated_at = UnicodeAttribute()


class QuestionModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "questions"

    id = UnicodeAttribute(hash_key=True)
    title = UnicodeAttribute()
    sql = UnicodeAttribute()
    dataset_id = UnicodeAttribute()
    viz_component = UnicodeAttribute()
    viz_format = UnicodeAttribute(null=True)  # ResponseKind.name
    viz_props = UnicodeAttribute(null=True)  # JSON dict
    viz_children = UnicodeAttribute(null=True)  # JSON list
    created_at = UnicodeAttribute()
    updated_at = UnicodeAttribute()


class DatasetModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "datasets"

    id = UnicodeAttribute(hash_key=True)
    name = UnicodeAttribute()
    kind = UnicodeAttribute()
    schema = UnicodeAttribute(null=True)  # JSON list of {name, dtype, nullable}
    location = UnicodeAttribute(null=True)  # S3 URI: s3://bucket/file.parquet
    created_at = UnicodeAttribute()
    updated_at = UnicodeAttribute()


class DashboardModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "dashboards"

    id = UnicodeAttribute(hash_key=True)
    title = UnicodeAttribute()
    tiles = UnicodeAttribute(null=True)  # JSON list of tile snapshots
    filters = UnicodeAttribute(null=True)  # JSON list of filter binding snapshots
    created_at = UnicodeAttribute()
    updated_at = UnicodeAttribute()
