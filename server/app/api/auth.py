# Copyright (c) 2026, Harleen Lappano
# All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from flask import Blueprint, jsonify, request
from app.config import get_config_instance
from functools import wraps
from urllib.parse import urlparse

# Create Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def is_allowed_host(host: str) -> bool:
    """
    Checks if the host is allowed against the configuration.

    Parameters:
        host (str): The host string from the request headers.

    Returns:
        bool: True if the host is allowed, False otherwise.
    """
    if not host:
        return False

    if host.startswith("["):
        name = host.split("]")[0] + "]"
    else:
        name = host.rsplit(":", 1)[0] if ":" in host else host

    name = name.lower()

    config = get_config_instance()
    allowed_hosts = config.get_allowed_hosts()
    return name in allowed_hosts

def is_local_origin(origin: str) -> bool:
    """
    Checks if the provided origin matches the local origin (e.g., localhost).

    Parameters:
        origin (str): The origin string from the request headers (e.g., 'http://localhost:8000').

    Returns:
        bool: True if the origin is considered local, False otherwise.
    """
    if origin is None:
        return True
    try:
        hostname = urlparse(origin).hostname
    except ValueError:
        return False

    hostname = hostname.lower()

    config = get_config_instance()
    allowed_hosts = config.get_allowed_hosts()
    return hostname in allowed_hosts

# Create a protector route
def protect_route():
    """
    Decorator factory that wraps routes to enforce security checks
    (e.g., host validation or origin validation).
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):

            # check host header
            host = request.headers.get("Host")
            if not is_allowed_host(host):
                print(f"Rejected Host")
                return jsonify({"error": "Forbidden: Host is not allowed."}), 403

            # Check origin
            origin = request.headers.get("Origin")
            if not is_local_origin(origin):
                print(f"Rejected cross-origin request from {origin!r}")
                return jsonify({"error": "Forbidden: Origin is not allowed"}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator