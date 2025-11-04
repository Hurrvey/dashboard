"""
API 响应格式化
"""

from flask import jsonify
from typing import Any, Optional


def success_response(data: Any, message: str = "success") -> tuple:
    """
    成功响应
    
    Args:
        data: 响应数据
        message: 响应消息
    
    Returns:
        (JSON, status_code)
    """
    return jsonify({
        "code": 200,
        "message": message,
        "data": data
    }), 200


def error_response(code: int, message: str, data: Optional[Any] = None) -> tuple:
    """
    错误响应
    
    Args:
        code: 错误码
        message: 错误消息
        data: 附加数据
    
    Returns:
        (JSON, status_code)
    """
    return jsonify({
        "code": code,
        "message": message,
        "data": data
    }), code

