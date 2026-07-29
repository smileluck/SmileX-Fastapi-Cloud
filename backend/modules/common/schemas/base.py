from pydantic import (
    BaseModel,
    ConfigDict,
    model_validator,
    field_validator,
    field_serializer,
    BeforeValidator,
)
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import ClassVar, Type, TypeVar, Optional, Annotated, Any

from core.i18n import t

T = TypeVar("T")


class BaseEntity(BaseModel):
    """基础实体模型"""

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.astimezone(ZoneInfo("Asia/Shanghai")).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        },
    )


class BaseReqEntity(BaseEntity):
    """基础请求实体模型

    在 mode='before' 阶段统一对字符串做 trim，并把空串 / 仅空格串收敛为 None，
    避免仅包含空格的字符串绕过 min_length=1 等校验。
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.astimezone(ZoneInfo("Asia/Shanghai")).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        },
    )

    @model_validator(mode="before")
    @classmethod
    def _trim_strings(cls, values: Any) -> Any:
        if not isinstance(values, dict):
            return values
        return {k: _trim_value(v) for k, v in values.items()}


class BaseRespEntity(BaseEntity):
    """基础响应实体模型"""

    # 处理输出转换：True→"1"，False→"2"
    @field_serializer("status", check_fields=False)
    def serialize_status_output(self, value: Any):
        if isinstance(value, bool):
            return "1" if value else "2"
        return value

    @field_serializer("is_system", check_fields=False)
    def serialize_is_system_output(self, value: Any):
        if isinstance(value, bool):
            return "1" if value else "2"
        return value

    JS_MAX_SAFE_INTEGER: ClassVar[int] = 9007199254740992  # 2^53

    @field_serializer("id", check_fields=False)
    def serialize_id_output(self, value: int):
        if isinstance(value, int) and value >= self.JS_MAX_SAFE_INTEGER:
            raise ValueError(t("validation.id_js_safe", value=value))
        return value


EMPTY_VALUES = {"", " ", "null", "undefined", None}


def _trim_value(value: Any) -> Any:
    """递归处理字符串、列表、字典，去除首尾空格并把空串收敛为 None"""
    if isinstance(value, str):
        stripped = value.strip()
        return None if stripped == "" else stripped
    if isinstance(value, list):
        return [_trim_value(item) for item in value]
    if isinstance(value, dict):
        return {k: _trim_value(v) for k, v in value.items()}
    return value


def parse_bool(value):
    # 统一转字符串处理
    if isinstance(value, str):
        value = value.strip().lower()

    if value in EMPTY_VALUES:
        return None

    true_set = {"1", "true", "yes", "y"}
    false_set = {"2", "false", "no", "n"}

    if value in true_set:
        return True
    if value in false_set:
        return False

    if isinstance(value, bool):
        return value

    raise ValueError(t("validation.status_invalid_value", value=value))


BoolField = Annotated[Optional[bool], BeforeValidator(parse_bool)]


def parse_optional_int(value):
    if isinstance(value, str):
        value = value.strip()
    if value in EMPTY_VALUES:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValueError(t("common.invalid_integer"))


OptionalIntField = Annotated[Optional[int], BeforeValidator(parse_optional_int)]
