#Copyright (c) 2026, Harleen Lappano
# All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from app.app import app, setup_app
from app.config import get_config_instance
from app.services.pin_service import get_pin_service_instance
from gevent.pywsgi import WSGIServer
import gevent
import sys
import argparse
import os
import ssl
import signal

# server
server = None

def shutdown():
    """
    Graceful shutdown for gevent server
    """
    print("Closure signal received. Starting graceful shutdown...")
    
    # 2. Stop accepting connections and wait up to 30 seconds for active ones to drain
    # Adjust the timeout based on your maximum expected request duration
    server.stop(timeout=30)
    
    print("Server stopped cleanly.")

if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(line_buffering=True)
        sys.stderr.reconfigure(line_buffering=True)
    except Exception:
        pass

    parser = argparse.ArgumentParser(
        description="Renewed simple reimplementation of the blind_pin_server for the Blockstream Jade, "
                    "along with a basic web interface"
    )
    parser.add_argument(
        "-p", "--port",
        type=int, default=4443,
        help="port number to listen on"
    )
    parser.add_argument(
        "--tls",
        action=argparse.BooleanOptionalAction, default=True,
        help="whether to use HTTPS (HTTP over TLS) for secure access, required by modern browsers "
                "to enable webcam access on non-localhost connections. "
                "Enabled by default; use --no-tls to disable."
    )
    parser.add_argument(
        "--data-dir",
        type=str, default=None,
        help="directory holding server_keys/ and pins/. Defaults to a per-user "
                "application data directory. Point this at a backup to restore an "
                "existing setup."
    )
    parser.add_argument(
        "--listen",
        type=str, default="127.0.0.1",
        help="address to bind. Defaults to 127.0.0.1 (this machine only). "
                "Use 0.0.0.0 only if the Jade or Green must reach this server "
                "across the network."
    )

    #
    # Parser for configuration
    #
    args = parser.parse_args()
    config = get_config_instance()
    config.init(args)
    setup_app()

    if config.LISTEN_IP not in ("127.0.0.1", "localhost", "::1"):
        config.ALLOW_ANY_HOST = True
        print("")
        print(f"  WARNING: listening on {config.LISTEN_IP}, beyond this machine.")
        print("  Anyone who can reach this port can submit PIN attempts against")
        print("  your stored records, and DNS-rebinding protection is relaxed.")
        print("  The default 127.0.0.1 is correct for almost every setup.")
        print("")

    
    if config.USING_TLS:
        if not os.path.isfile(config.TLS_CERT_PATH):
            print(
                f"TLS certificate not found at {config.TLS_CERT_PATH}. "
                "Either provide a certificate or use --no-tls to disable TLS. "
                "Note that TLS is required by modern browsers to enable webcam access on "
                "non-localhost connections."
            )
            sys.exit(1)
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(certfile=config.TLS_CERT_PATH)
        server = WSGIServer((config.LISTEN_IP, config.LISTEN_PORT), app, ssl_context=ssl_context)

    else:
        server = WSGIServer((config.LISTEN_IP, config.LISTEN_PORT), app)

    print(f"Server starting on {'https' if config.USING_TLS else 'http'}://{config.LISTEN_IP}:{config.LISTEN_PORT}")
    print(f"Data directory: {config.DATA_DIR}")
    pin_service_instance = get_pin_service_instance()
    print(f"Server public key: {pin_service_instance.bytes2hex(config.STATIC_SERVER_PUBLIC_KEY)}")
    if config.KEYS_WERE_GENERATED:
        print("")
        print("  A NEW server keypair was generated.")
        print("  An already-configured Jade will NOT unlock against this key.")
        print("  To use an existing Jade, stop the server and restore your")
        print("  server_keys/ and pins/ directories into the data directory above,")
        print("  or start with --data-dir pointing at your backup.")
        print("")

    print(f"READY {'https' if config.USING_TLS else 'http'}://{config.LISTEN_IP}:{config.LISTEN_PORT}")

    # Add shutdown signals
    gevent.signal_handler(signal.SIGTERM, shutdown)
    gevent.signal_handler(signal.SIGINT, shutdown)

    # Allow Python to catch KeyboardInterrupt
    signal.signal(signal.SIGINT, signal.default_int_handler)

    print("Starting server...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        shutdown()

