# Copyright (c) 2026, Harleen Lappano
# All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from flask import Blueprint, jsonify, request
from app.api.auth import protect_route
from app.services.pin_service import get_pin_service_instance

# Create blueprint
pin_bp = Blueprint("pin", __name__)

@pin_bp.route('/get_pin', methods=['POST'])
@protect_route()
def get_pin():
    """
    Get PIN route
    """

    # Get json data
    params = request.get_json()

    if not params or 'data' not in params:
        return jsonify({"error": "Bad request: 'data' field missing"}), 400

    try:
        encoded_data = params['data']
        pin_service = get_pin_service_instance()
        pin_str = pin_service.get_pin(encoded_data)
        return jsonify({"data": pin_str}), 200
    except Exception as e:
        return jsonify({"error": "Invalid base64 data"}), 400


@pin_bp.route('/set_pin', methods=['POST'])
@protect_route()
def set_pin():
    """
    Set PIN route
    """

    # Get josn data
    params = request.get_json()

    if not params or 'data' not in params:
        return jsonify({"error": "Bad request: 'data' field missing"}), 400

    try:
        encoded_data = params['data']
        pin_service = get_pin_service_instance()
        pin_str = pin_service.set_pin(encoded_data)

        return jsonify({"data": pin_str}), 200

    except Exception as e:
        print("Exception: ", e)
        return jsonify({"error": "Invalid base64 data"}), 400


@pin_bp.route('/get_pub', methods=['GET'])
@protect_route()
def get_pub_key():
    """
    Get the Public Key Route
    """
    pin_service = get_pin_service_instance()
    pub_key = pin_service.get_pub_key()
    return jsonify({"data": pub_key}), 200