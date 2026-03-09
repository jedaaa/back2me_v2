"""
Response Utility - Rebuild v2.1
Standardizes API output.
"""
from flask import jsonify

def api_success(data=None, message=None, status=200):
    response = {"success": True}
    if data is not None:
        response["data"] = data
    if message:
        response["message"] = message
    return jsonify(response), status

def api_error(message, code="ERROR", status=400, details=None):
    response = {
        "success": False,
        "error": {
            "message": message,
            "code": code
        }
    }
    if details:
        response["error"]["details"] = details
    return jsonify(response), status
