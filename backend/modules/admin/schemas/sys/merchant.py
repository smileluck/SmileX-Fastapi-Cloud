#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Optional, Annotated
from zoneinfo import ZoneInfo

from pydantic import Field, ConfigDict, BeforeValidator

from modules.common.schemas.base import BaseEntity, BaseRespEntity, BoolField
from modules.common.schemas.page import PageRequest


def _format_datetime(v):
    if isinstance(v, datetime):
        return v.astimezone(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S")
    return v


class SysMerchantQueryParams(PageRequest):
    """系统商户查询参数模型"""

    name: Optional[str] = Field(None, description="商户名称，支持模糊查询")
    code: Optional[str] = Field(None, description="商户编码，支持模糊查询")
    app_id: Optional[str] = Field(None, description="AppId，支持模糊查询")
    status: BoolField = Field(None, description="商户状态：True-启用，False-禁用")


class SysMerchantCreate(BaseEntity):
    """系统商户创建请求模型（app_id/app_secret 由系统生成，不接受外部传入）"""

    name: str = Field(..., description="商户名称", min_length=1, max_length=100)
    code: Optional[str] = Field(None, description="商户编码", max_length=100)
    contact_name: Optional[str] = Field(None, description="联系人姓名", max_length=50)
    contact_phone: Optional[str] = Field(None, description="联系电话", max_length=30)
    contact_email: Optional[str] = Field(None, description="联系邮箱", max_length=100)
    status: bool = Field(True, description="商户状态：True-启用，False-禁用")
    remark: Optional[str] = Field(None, description="备注", max_length=500)
    sort: int = Field(0, description="排序号", ge=0)


class SysMerchantUpdate(BaseEntity):
    """系统商户更新请求模型（不允许通过更新修改 app_secret，密钥走 reset-secret）"""

    name: Optional[str] = Field(None, description="商户名称", min_length=1, max_length=100)
    code: Optional[str] = Field(None, description="商户编码", max_length=100)
    contact_name: Optional[str] = Field(None, description="联系人姓名", max_length=50)
    contact_phone: Optional[str] = Field(None, description="联系电话", max_length=30)
    contact_email: Optional[str] = Field(None, description="联系邮箱", max_length=100)
    status: BoolField = Field(None, description="商户状态：True-启用，False-禁用")
    remark: Optional[str] = Field(None, description="备注", max_length=500)
    sort: Optional[int] = Field(None, description="排序号", ge=0)


class SysMerchantResponseData(BaseRespEntity):
    """系统商户详细响应模型（正常响应不含 app_secret 明文）"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="商户ID")
    name: str = Field(..., description="商户名称")
    code: Optional[str] = Field(None, description="商户编码")
    contact_name: Optional[str] = Field(None, description="联系人姓名")
    contact_phone: Optional[str] = Field(None, description="联系电话")
    contact_email: Optional[str] = Field(None, description="联系邮箱")
    app_id: str = Field(..., description="AppId")
    status: bool = Field(True, description="商户状态")
    remark: Optional[str] = Field(None, description="备注")
    sort: int = Field(..., description="排序号")
    secret_updated_at: Annotated[Optional[str], BeforeValidator(_format_datetime)] = Field(
        None, description="密钥最近一次重置时间"
    )
    created_at: Annotated[Optional[str], BeforeValidator(_format_datetime)] = Field(
        None, description="创建时间"
    )
    updated_at: Annotated[Optional[str], BeforeValidator(_format_datetime)] = Field(
        None, description="更新时间"
    )


class SysMerchantWithSecret(SysMerchantResponseData):
    """创建商户后的响应：附带一次性明文 app_secret（仅此一次返回）"""

    # SysMerchant ORM 仅有 app_secret_encrypted，无 app_secret 属性，
    # model_validate(merchant) 时该字段取默认值；端点随后立即赋真实明文（见 create_merchant 端点），
    # 故响应恒为真实值。不能用“先 validate base 再 model_dump 重建”的写法——
    # BaseRespEntity 会把 status 序列化为 "1"/"2"，重新校验 bool 时 "2" 会被 Pydantic 拒绝。
    app_secret: str = Field(default="", description="明文 app_secret（仅创建/重置时返回一次，请立即妥善保存）")


class SysMerchantSecretResetResponse(BaseEntity):
    """重置商户密钥后的响应：返回新的明文 app_secret（仅此一次）"""

    app_id: str = Field(..., description="AppId")
    app_secret: str = Field(..., description="新的明文 app_secret（仅本次返回，请立即妥善保存）")
    secret_updated_at: Annotated[Optional[str], BeforeValidator(_format_datetime)] = Field(
        None, description="密钥最近一次重置时间"
    )
