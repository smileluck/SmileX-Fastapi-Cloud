#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import Field, dataclass
from enum import Enum
from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel

from core.i18n import t


class CustomCodeBase(Enum):
    """自定义状态码基类

    成员元组第二位为 i18n key（而非中文文案）。
    .msg 按当前请求语言懒翻译；.code 为数字状态码。
    """
    @property
    def code(self) -> int:
        """获取状态码"""
        assert isinstance(self.value[0], int), "状态码必须是整数"
        return self.value[0]
    @property
    def key(self) -> str:
        """获取 i18n 文案 key"""
        return self.value[1] if len(self.value) > 1 else ""
    @property
    def msg(self) -> str:
        """获取状态码信息（按当前请求语言翻译）"""
        key = self.key
        return t(key) if key else ""


class CustomResponseCode(CustomCodeBase):
    """自定义响应状态码"""
    HTTP_200 = (200, "response.http_200")
    HTTP_400 = (400, "response.http_400")
    HTTP_401 = (401, "response.http_401")
    HTTP_403 = (403, "response.http_403")
    HTTP_404 = (404, "response.http_404")
    HTTP_422 = (422, "response.http_422")
    HTTP_500 = (500, "response.http_500")


class CustomErrorCode(CustomCodeBase):
    SUCCESS = (0, "common.success")
    """自定义错误状态码"""
    # 用户相关10001-10100
    USER_NOT_FOUND = (10001, "error.user.not_found")
    USER_EXIST = (10002, "error.user.exist")
    USER_NOT_LOGIN = (10003, "error.user.not_login")
    USER_CAPTCHA_ERROR = (10004, "error.user.captcha_error")
    USER_NOT_ACTIVE = (10005, "error.user.not_active")
    USER_LOGIN_FAILED = (10006, "error.user.login_failed")
    INVALID_REFRESH_TOKEN = (10007, "error.user.invalid_refresh_token")
    EXPIRED_REFRESH_TOKEN = (10008, "error.user.expired_refresh_token")
    REFRESH_TOKEN_FAILED = (10009, "error.user.refresh_token_failed")
    USER_PHONE_FORMAT_ERROR = (10010, "error.user.phone_format_error")
    USER_SMS_SEND_ERROR = (10011, "error.user.sms_send_error")
    USER_SMS_SEND_TOO_FAST = (10012, "error.user.sms_send_too_fast")
    USER_DISABLED = (10013, "error.user.disabled")
    # 设备管理 10101-10200
    DEVICE_NOT_FOUND = (10101, "error.device.not_found")
    DEVICE_BIND_ERROR = (10102, "error.device.bind_error")
    DEVICE_BIND = (10103, "error.device.bind")
    DEVICE_NOT_PERMISSION = (10104, "error.device.not_permission")
    # 聊天管理 10201-10300
    CHAT_NOT_FOUND = (10201, "error.chat.not_found")
    CHAT_EXIST = (10202, "error.chat.exist")
    CHAT_NOT_PERMISSION = (10203, "error.chat.not_permission")
    # 机器人管理 10301-10400
    ROBOT_NOT_FOUND = (10301, "error.robot.not_found")
    ROBOT_EXIST = (10302, "error.robot.exist")
    ROBOT_NOT_PERMISSION = (10303, "error.robot.not_permission")
    ROBOT_NOT_BIND = (10304, "error.robot.not_bind")
    ROBOT_BIND = (10305, "error.robot.bind")
    ROBOT_STATUS_NOT_FOUND = (10306, "error.robot.status_not_found")
    # 紧急联系人管理 10401-10500
    EMERGENCY_CONTACT_NOT_FOUND = (10401, "error.emergency_contact.not_found")
    EMERGENCY_CONTACT_EXIST = (10402, "error.emergency_contact.exist")
    EMERGENCY_CONTACT_NOT_PERMISSION = (10403, "error.emergency_contact.not_permission")
    EMERGENCY_CONTACT_SAVE_ERROR = (10404, "error.emergency_contact.save_error")
    EMERGENCY_CONTACT_UPDATE_ERROR = (10405, "error.emergency_contact.update_error")
    EMERGENCY_CONTACT_DELETE_ERROR = (10406, "error.emergency_contact.delete_error")
    EMERGENCY_CONTACT_PHONE_DUPLICATED = (10407, "error.emergency_contact.phone_duplicated")
    EMERGENCY_CONTACT_LIMIT_REACHED = (10408, "error.emergency_contact.limit_reached")
    # 机器人任务 10501-10600
    ROBOT_TASK_NOT_FOUND = (10501, "error.robot_task.not_found")
    ROBOT_TASK_EXIST = (10502, "error.robot_task.exist")
    ROBOT_TASK_NOT_PERMISSION = (10503, "error.robot_task.not_permission")
    ROBOT_TASK_STATUS_NOT_FOUND = (10504, "error.robot_task.status_not_found")
    ROBOT_TASK_FAILED = (10505, "error.robot_task.failed")
    ROBOT_TASK_NETWORK_ERROR = (10506, "error.robot_task.network_error")
    ROBOT_TASK_RUNNING = (10507, "error.robot_task.running")
    ROBOT_TASK_COMPLETED = (10508, "error.robot_task.completed")
    # 限流与安全 10901-11000
    RATE_LIMIT_EXCEEDED = (10901, "error.rate_limit_exceeded")
    IP_BLOCKED = (10902, "error.ip_blocked")
    CAPTCHA_REQUIRED = (10911, "error.captcha_required")
    CAPTCHA_INVALID = (10912, "error.captcha_invalid")
    CAPTCHA_VERIFY_FAILED = (10913, "error.captcha_verify_failed")
    # 通知管理 10601-10700
    NOTICE_NOT_FOUND = (10601, "error.notice.not_found")
    NOTICE_ALREADY_PUBLISHED = (10602, "error.notice.already_published")
    # 开放API / 商户管理 11021-11040
    OPEN_API_MISSING_HEADER = (11021, "error.open_api.missing_header")
    OPEN_API_TIMESTAMP_EXPIRED = (11022, "error.open_api.timestamp_expired")
    OPEN_API_INVALID_NONCE = (11023, "error.open_api.invalid_nonce")
    OPEN_API_NONCE_REPLAY = (11024, "error.open_api.nonce_replay")
    OPEN_API_MERCHANT_NOT_FOUND = (11025, "error.open_api.merchant_not_found")
    OPEN_API_MERCHANT_DISABLED = (11026, "error.open_api.merchant_disabled")
    OPEN_API_SIGNATURE_INVALID = (11027, "error.open_api.signature_invalid")
    MERCHANT_NOT_FOUND = (11028, "error.merchant.not_found")
    MERCHANT_CODE_EXIST = (11029, "error.merchant.code_exist")
    MERCHANT_APP_ID_CONFLICT = (11030, "error.merchant.app_id_conflict")
@dataclass
class CustomResponse:
    """
    提供开放式响应状态码，而不是枚举，如果你想自定义响应信息，这可能很有用
    """
    code: int
    msg: str
    data: Any = None
@dataclass(frozen=True)
class StandardResponseCode:
    """标准响应状态码"""
    """
    HTTP codes
    See HTTP Status Code Registry:
    https://www.iana.org/assignments/http-status-codes/http-status-codes.xhtml
    And RFC 2324 - https://tools.ietf.org/html/rfc2324
    """
    HTTP_100 = 100  # CONTINUE: 继续
    HTTP_101 = 101  # SWITCHING_PROTOCOLS: 协议切换
    HTTP_102 = 102  # PROCESSING: 处理中
    HTTP_103 = 103  # EARLY_HINTS: 提示信息
    HTTP_200 = 200  # OK: 请求成功
    HTTP_201 = 201  # CREATED: 已创建
    HTTP_202 = 202  # ACCEPTED: 已接受
    HTTP_203 = 203  # NON_AUTHORITATIVE_INFORMATION: 非权威信息
    HTTP_204 = 204  # NO_CONTENT: 无内容
    HTTP_205 = 205  # RESET_CONTENT: 重置内容
    HTTP_206 = 206  # PARTIAL_CONTENT: 部分内容
    HTTP_207 = 207  # MULTI_STATUS: 多状态
    HTTP_208 = 208  # ALREADY_REPORTED: 已报告
    HTTP_226 = 226  # IM_USED: 使用了
    HTTP_300 = 300  # MULTIPLE_CHOICES: 多种选择
    HTTP_301 = 301  # MOVED_PERMANENTLY: 永久移动
    HTTP_302 = 302  # FOUND: 临时移动
    HTTP_303 = 303  # SEE_OTHER: 查看其他位置
    HTTP_304 = 304  # NOT_MODIFIED: 未修改
    HTTP_305 = 305  # USE_PROXY: 使用代理
    HTTP_307 = 307  # TEMPORARY_REDIRECT: 临时重定向
    HTTP_308 = 308  # PERMANENT_REDIRECT: 永久重定向
    HTTP_400 = 400  # BAD_REQUEST: 请求错误
    HTTP_401 = 401  # UNAUTHORIZED: 未授权
    HTTP_402 = 402  # PAYMENT_REQUIRED: 需要付款
    HTTP_403 = 403  # FORBIDDEN: 禁止访问
    HTTP_404 = 404  # NOT_FOUND: 未找到
    HTTP_405 = 405  # METHOD_NOT_ALLOWED: 方法不允许
    HTTP_406 = 406  # NOT_ACCEPTABLE: 不可接受
    HTTP_407 = 407  # PROXY_AUTHENTICATION_REQUIRED: 需要代理身份验证
    HTTP_408 = 408  # REQUEST_TIMEOUT: 请求超时
    HTTP_409 = 409  # CONFLICT: 冲突
    HTTP_410 = 410  # GONE: 已删除
    HTTP_411 = 411  # LENGTH_REQUIRED: 需要内容长度
    HTTP_412 = 412  # PRECONDITION_FAILED: 先决条件失败
    HTTP_413 = 413  # REQUEST_ENTITY_TOO_LARGE: 请求实体过大
    HTTP_414 = 414  # REQUEST_URI_TOO_LONG: 请求 URI 过长
    HTTP_415 = 415  # UNSUPPORTED_MEDIA_TYPE: 不支持的媒体类型
    HTTP_416 = 416  # REQUESTED_RANGE_NOT_SATISFIABLE: 请求范围不符合要求
    HTTP_417 = 417  # EXPECTATION_FAILED: 期望失败
    HTTP_418 = 418  # UNUSED: 闲置
    HTTP_421 = 421  # MISDIRECTED_REQUEST: 被错导的请求
    HTTP_422 = 422  # UNPROCESSABLE_CONTENT: 无法处理的实体
    HTTP_423 = 423  # LOCKED: 已锁定
    HTTP_424 = 424  # FAILED_DEPENDENCY: 依赖失败
    HTTP_425 = 425  # TOO_EARLY: 太早
    HTTP_426 = 426  # UPGRADE_REQUIRED: 需要升级
    HTTP_427 = 427  # UNASSIGNED: 未分配
    HTTP_428 = 428  # PRECONDITION_REQUIRED: 需要先决条件
    HTTP_429 = 429  # TOO_MANY_REQUESTS: 请求过多
    HTTP_430 = 430  # Unassigned: 未分配
    HTTP_431 = 431  # REQUEST_HEADER_FIELDS_TOO_LARGE: 请求头字段太大
    HTTP_451 = 451  # UNAVAILABLE_FOR_LEGAL_REASONS: 由于法律原因不可用
    HTTP_500 = 500  # INTERNAL_SERVER_ERROR: 服务器内部错误
    HTTP_501 = 501  # NOT_IMPLEMENTED: 未实现
    HTTP_502 = 502  # BAD_GATEWAY: 错误的网关
    HTTP_503 = 503  # SERVICE_UNAVAILABLE: 服务不可用
    HTTP_504 = 504  # GATEWAY_TIMEOUT: 网关超时
    HTTP_505 = 505  # HTTP_VERSION_NOT_SUPPORTED: HTTP 版本不支持
    HTTP_506 = 506  # VARIANT_ALSO_NEGOTIATES: 变体也会协商
    HTTP_507 = 507  # INSUFFICIENT_STORAGE: 存储空间不足
    HTTP_508 = 508  # LOOP_DETECTED: 检测到循环
    HTTP_509 = 509  # UNASSIGNED: 未分配
    HTTP_510 = 510  # NOT_EXTENDED: 未扩展
    HTTP_511 = 511  # NETWORK_AUTHENTICATION_REQUIRED: 需要网络身份验证
    """
    WebSocket codes
    https://www.iana.org/assignments/websocket/websocket.xml#close-code-number
    https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent
    """
    WS_1000 = 1000  # NORMAL_CLOSURE: 正常闭合
    WS_1001 = 1001  # GOING_AWAY: 正在离开
    WS_1002 = 1002  # PROTOCOL_ERROR: 协议错误
    WS_1003 = 1003  # UNSUPPORTED_DATA: 不支持的数据类型
    WS_1005 = 1005  # NO_STATUS_RCVD: 没有接收到状态
    WS_1006 = 1006  # ABNORMAL_CLOSURE: 异常关闭
    WS_1007 = 1007  # INVALID_FRAME_PAYLOAD_DATA: 无效的帧负载数据
    WS_1008 = 1008  # POLICY_VIOLATION: 策略违规
    WS_1009 = 1009  # MESSAGE_TOO_BIG: 消息太大
    WS_1010 = 1010  # MANDATORY_EXT: 必需的扩展
    WS_1011 = 1011  # INTERNAL_ERROR: 内部错误
    WS_1012 = 1012  # SERVICE_RESTART: 服务重启
    WS_1013 = 1013  # TRY_AGAIN_LATER: 请稍后重试
    WS_1014 = 1014  # BAD_GATEWAY: 错误的网关
    WS_1015 = 1015  # TLS_HANDSHAKE: TLS握手错误
    WS_3000 = 3000  # UNAUTHORIZED: 未经授权