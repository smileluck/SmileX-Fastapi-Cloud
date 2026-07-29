#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Any, Generic, TypeVar
from dataclasses import dataclass
from fastapi import Response
from pydantic import BaseModel, Field
from typing import Optional, List

from .response_code import CustomResponse, CustomResponseCode, CustomErrorCode

SchemaT = TypeVar("SchemaT")
PageDataT = TypeVar('PageDataT')


class ResponseModel(BaseModel,Generic[SchemaT]):
    """
    不包含返回数据 schema 的通用型统一返回模型

    示例::

        @router.get('/test', response_model=ResponseModel)
        def test():
            return ResponseModel(data={'test': 'test'})


        @router.get('/test')
        def test() -> ResponseModel:
            return ResponseModel(data={'test': 'test'})


        @router.get('/test')
        def test() -> ResponseModel:
            res = CustomResponseCode.HTTP_200
            return ResponseModel(code=res.code, msg=res.msg, data={'test': 'test'})
    """

    code: int = Field(CustomResponseCode.HTTP_200.code, description="返回状态码")
    msg: str = Field("", description="返回信息")
    data: SchemaT = Field(None, description="返回数据")

    # 请求唯一标识（方便分布式系统追踪问题）
    request_id: Optional[str] = Field(
        default=None, description="请求唯一ID（用于日志追踪）"
    )
    # 业务错误码
    err_code: int | None = Field(default=None, description="业务状态码")



class ResponsePageDataModel(BaseModel, Generic[SchemaT]):
    """分页数据模型"""

    records: List[SchemaT] = Field(..., description="分页数据")  # 明确元素类型
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页条数")
    total: int = Field(..., description="总条数")
    total_pages: int = Field(..., description="总页数")


class ResponsePageModel(ResponseModel[ResponsePageDataModel[SchemaT]], Generic[SchemaT]):
    """
    包含分页数据 schema 的通用型统一返回模型

    示例::

        @router.get('/test', response_model=ResponsePageModel[GetApiDetail])
        def test():
            return ResponsePageModel[GetApiDetail](data=GetApiDetail(...))


        @router.get('/test')
        def test() -> ResponsePageModel[GetApiDetail]:
    """

    pass

    # def __init__(
    #     self,
    #     code: int = CustomResponseCode.HTTP_200.code,
    #     msg: str = CustomResponseCode.HTTP_200.msg,
    #     data: Any = None,
    # ):
    #     # 调用父类构造函数传递必要的参数
    #     super().__init__(code=code, msg=msg, data=data)
    #     # 设置分页信息
    #     self.page_info = page_info


class ResponseBase:
    """统一返回方法"""

    @staticmethod
    def __response(
        *,
        res: CustomResponseCode | CustomResponse,
        err_code: CustomErrorCode | None = None,
        msg: str | None,
        data: Any | None,
        request_id: str | None = None,
    ) -> ResponseModel:
        """
        请求返回通用方法

        :param res: 返回信息
        :param data: 返回数据
        :return:
        """
        err_code_code = err_code.code if err_code else None
        return ResponseModel(
            code=res.code,
            err_code=err_code_code,
            msg=msg or res.msg,
            data=data,
            request_id=request_id,
        )

    def success(
        self,
        *,
        res: CustomResponseCode | CustomResponse = CustomResponseCode.HTTP_200,
        msg: str | None = None,
        data: Any | None = None,
        request_id: str | None = None,
    ) -> ResponseModel:
        """
        成功响应

        :param res: 返回信息
        :param data: 返回数据
        :return:
        """
        return self.__response(res=res, msg=msg, data=data, request_id=request_id)

    def fail(
        self,
        *,
        res: CustomResponseCode | CustomResponse = CustomResponseCode.HTTP_500,
        err_code: CustomErrorCode | None = None,
        msg: str | None = None,
        data: Any = None,
        request_id: str | None = None,
    ) -> ResponseModel:
        """
        失败响应

        :param res: 返回信息
        :param data: 返回数据
        :return:
        """
        return self.__response(
            res=res, err_code=err_code, msg=msg, data=data, request_id=request_id
        )

    def page(
        self,
        *,
        res: CustomResponseCode | CustomResponse = CustomResponseCode.HTTP_200,
        data: ResponsePageDataModel[PageDataT],
        request_id: str | None = None,
    ) -> ResponsePageModel[PageDataT]:
        """
        分页响应
        :param res: 响应信息
        :param data: 分页数据模型
        :param request_id: 请求追踪ID
        :return:
        """
        return ResponsePageModel[PageDataT](
            code=res.code,
            msg=res.msg,
            data=data,
            request_id=request_id,
        )



response_base: ResponseBase = ResponseBase()
