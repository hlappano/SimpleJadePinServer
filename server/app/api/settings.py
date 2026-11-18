# Copyright (c) 2026, Harleen Lappano
# All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from flask import Blueprint, jsonify, request
from app.api.auth import protect_route
from app.config import get_config_instance
from app.services.pin_service import get_pin_service_instance
import os

# Create blueprint
settings_bp = Blueprint("settings", __name__)

@settings_bp.route('/get_allowed_hosts', methods=['GET'])
@protect_route()
def get_allowed_hosts():
    config = get_config_instance()
    allowed_hosts = config.get_allowed_hosts()
    print(allowed_hosts)
    return jsonify({"allowed_hosts": list(allowed_hosts)}), 200

@settings_bp.route('/get_allowed_hosts_type', methods=['GET'])
@protect_route()
def get_allowed_hosts_type():
    config = get_config_instance()
    allowed_hosts = config.get_allowed_hosts()

    allowed_hosts_t = []
    i:int = 1

    for host in config.LOCAL_HOSTS:
        allowed_hosts_t.append({"id": i, "host": host, "type": 'local'})
        i+=1
    if config.PROXY_HOST:
        allowed_hosts_t.append({"id": i, "host": config.PROXY_HOST, "type": 'proxy'})
        i+=1

    for host in allowed_hosts:
        if host in config.LOCAL_HOSTS or host == config.PROXY_HOST:
            continue
        allowed_hosts_t.append({"id": i, "host": host, "type": 'custom'})
        i+=1

    return jsonify({"allowed_hosts": allowed_hosts_t}), 200


@settings_bp.route('/add_host', methods=['POST'])
@protect_route()
def add_host():
    """
    Add Allowed Host Route
    """

    # get json data
    params = request.get_json()

    if not params or 'host' not in params:
        return jsonify({"error": "Bad request: 'host' field missing"}), 400

    try:
        config = get_config_instance()
        new_host = params['host']

        success, message, code = config.add_allowed_host(new_host)
        if success:
            return jsonify({"message": message}), 200
        else:
            return jsonify({"error": message}), code
    except Exception as e:
        return jsonify({"error": f"Invalid request {e}"}), 400

@settings_bp.route('/remove_host', methods=['POST'])
@protect_route()
def remove_host():
    # get json data
    params = request.get_json()

    if not params or 'host' not in params:
        return jsonify({"error": "Bad request: 'host' field missing"}), 400

    try:
        config = get_config_instance()
        host_to_remove = params['host']
        success, message, code = config.remove_allowed_host(host_to_remove)
        if success:
            return jsonify({"message": message}), 200
        else:
            return jsonify({"error": message}), code
    except Exception as e:
        return jsonify({"error": f"Invalid request {e}"}), 400

@settings_bp.route('/get_allowed_ports', methods=['GET'])
@protect_route()
def get_allowed_ports():
    config = get_config_instance()
    allowed_ports = config.get_allowed_ports()
    return jsonify({"allowed_ports": list(allowed_ports)}), 200


@settings_bp.route('/get_allowed_ports_type', methods=['GET'])
@protect_route()
def get_allowed_ports_type():
    config = get_config_instance()
    allowed_ports = config.get_allowed_ports()

    allowed_ports_t = []
    i:int = 1

    for port in config.LOCAL_PORTS:
        allowed_ports_t.append({"id": i, "port": port, "type": 'local'})
        i +=1
    if config.PROXY_WEB_PORT:
        allowed_ports_t.append({"id": i, "port": config.PROXY_WEB_PORT, "type": 'proxy'})
        i +=1
    if config.PROXY_SERVER_PORT:
        allowed_ports_t.append({"id": i, "port": config.PROXY_SERVER_PORT, "type": 'proxy'})
        i +=1

    for port in allowed_ports:
        if port in config.LOCAL_PORTS or port == config.PROXY_SERVER_PORT or port == config.PROXY_WEB_PORT:
            continue
        allowed_ports_t.append({"id": i, "port": port, "type": 'custom'})
        i +=1

    return jsonify({"allowed_ports": allowed_ports_t}), 200



@settings_bp.route('/add_port', methods=['POST'])
@protect_route()
def add_port():
    """
    Add Allowed Port Route
    """

    # get json data
    params = request.get_json()

    if not params or 'port' not in params:
        return jsonify({"error": "Bad request: 'port' field missing"}), 400

    try:
        config = get_config_instance()
        new_port = params['port']
        success, message, code = config.add_allowed_port(new_port)
        if success:
            return jsonify({"message": message}), 200
        else:
            return jsonify({"error": message}), code
    except Exception as e:
        return jsonify({"error": f"Invalid request {e}"}), 400

@settings_bp.route('/remove_port', methods=['POST'])
@protect_route()
def remove_port():
    # get json data
    params = request.get_json()

    if not params or 'port' not in params:
        return jsonify({"error": "Bad request: 'port' field missing"}), 400

    try:
        config = get_config_instance()
        port_to_remove = params['port']
        success, message, code = config.remove_allowed_port(port_to_remove)
        if success:
            return jsonify({"message": message}), 200
        else:
            return jsonify({"error": message}), code
    except Exception as e:
        return jsonify({"error": f"Invalid request {e}"}), 400

@settings_bp.route('/get_current_state', methods=['GET'])
@protect_route()
def get_current_state():
    
    config = get_config_instance()

    try:
        pin_files = [f for f in os.listdir(config.PINS_PATH) if f.endswith(".pin")]
    except FileNotFoundError:
        pin_files = []

    pin_service = get_pin_service_instance()
    data = {
        "data_dir": config.DATA_DIR,
        "server_keys_dir": config.SERVER_KEY_PATH,
        "pins_dir": config.PINS_PATH,
        "public_key": pin_service.bytes2hex(config.STATIC_SERVER_PUBLIC_KEY),
        "pin_records": len(pin_files),
        "keys_created_this_run": config.KEYS_WERE_GENERATED,
        "migrated_from": config.MIGRATED_FROM
    }

    return jsonify({"data": data}), 200
