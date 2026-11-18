# Copyright (c) 2026, Harleen Lappano
# All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from flask import Flask, jsonify
from flask_cors import CORS
from app.api.api import api_bp
from app.config import get_config_instance

# Create app
app = Flask(__name__)
cors = None

def setup_app():
    # Register api
    app.register_blueprint(api_bp)

    # Get config instance
    config = get_config_instance()

    # Generate Allowed Origins for CORS
    allowed_origins = set[str]()
    # For each host
    for host in config.get_allowed_hosts():
        # For each port (not 80 or 443)
        for port in config.get_allowed_ports():
            if str(port) in ("80", "443"):
                continue
            # Create origin for http and https
            allowed_origins.add(f"http://{host}:{port}")
            allowed_origins.add(f"https://{host}:{port}")

    # Arrange CORS for our frontend
    global cors
    cors = CORS(app,
                supports_credentials=True,
                origins=list(allowed_origins)
                )

# Welcome Landing
@app.route("/")
def root():
    return jsonify({"message": "Welcome to SimpleJadePinServer" })