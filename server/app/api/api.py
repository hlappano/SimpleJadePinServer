# Copyright (c) 2026, Harleen Lappano
# All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from flask import Blueprint, jsonify

from app.api.auth import auth_bp
from app.api.pin import pin_bp
from app.api.settings import settings_bp


# Create the api parent blueprint
api_bp = Blueprint('api', __name__, url_prefix="/")

# Register sub-blueprints
api_bp.register_blueprint(auth_bp)
api_bp.register_blueprint(pin_bp)
api_bp.register_blueprint(settings_bp)

@api_bp.route("")
def root():
    """
    Root Welocm Page
    """
    return jsonify({"message": "Welcome to SimpleJadePinServer API"})