# Copyright (c) 2026, Harleen Lappano
# All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import ClassVar
import os
import sys
import shutil
import wallycore as wally
import threading
from cryptography.fernet import Fernet

# Global config instance
config_instance = None

class Config:
    APP_DIR: ClassVar[str] = ""
    WEB_ROOT: ClassVar[str] = ""
    DATA_DIR: ClassVar[str] = ""
    KEYS_WERE_GENERATED: ClassVar[bool] = False
    MIGRATED_FROM: ClassVar[str|None] = None
    TLS_CERT_PATH: ClassVar[str] = ""
    SERVER_KEY_PATH: ClassVar[str] = ""
    PINS_PATH: ClassVar[str] = ""
    SETTINGS_PATH: ClassVar[str] = ""
    SETTINGS_KEY: ClassVar[str] = ""
    HOSTS_FILE: ClassVar[str] = ""
    PORTS_FILE: ClassVar[str] = ""
    LISTEN_IP: ClassVar[any]
    LISTEN_ADDR: ClassVar[str] = "127.0.0.1"
    LISTEN_PORT: ClassVar[int] = 4443
    USING_TLS: ClassVar[bool] = False
    LOCAL_HOSTS: ClassVar[set[str]] = {"127.0.0.1", "localhost", "::1", "[::1]"}
    LOCAL_PORTS: ClassVar[set[str]] = {"4443", "5000"}
    PROXY_HOST: ClassVar[str] = ""
    PROXY_SERVER_PORT: ClassVar[str] = ""
    PROXY_WEB_PORT: ClassVar[str] = ""
    _allowed_hosts: set[str] = LOCAL_HOSTS
    _allowed_ports: set[str] = LOCAL_PORTS
    _settings_lock = threading.Lock()

    def _app_dir(self):
        """Directory holding bundled read-only assets (handles PyInstaller onefile)."""
        if getattr(sys, "frozen", False):
            return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        return os.path.dirname(os.path.abspath(__file__))

    def _data_dir(self):
        """Per-user writable dir for keys and pins - survives app updates."""
        env = os.environ.get("JADE_PIN_SERVER_DATA")
        if env:
            return env
        if sys.platform == "darwin":
            base = os.path.expanduser("~/Library/Application Support/JadePinServer")
        elif os.name == "nt":
            base = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")),
                                "JadePinServer")
        else:
            base = os.path.join(os.environ.get("XDG_DATA_HOME",
                                os.path.expanduser("~/.local/share")), "JadePinServer")
        return base

    def _migrate_legacy_data(self, data_dir):
        """Adopt a pre-existing ./key_data directory from the script-based layout.

        Upstream stored keys in a CWD-relative ./key_data. Silently generating a
        fresh keypair instead would leave an already-configured Jade unable to
        unlock, so any legacy directory found next to the app is copied across
        before key generation runs. The original is left untouched as a backup.
        """
        if os.path.isdir(os.path.join(data_dir, "server_keys")):
            return None  # already have data here; never overwrite it

        for candidate in (os.path.join(os.getcwd(), "key_data"),
                        os.path.join(self.APP_DIR, "key_data")):
            if not os.path.isdir(os.path.join(candidate, "server_keys")):
                continue

            os.makedirs(data_dir, exist_ok=True)
            for sub in ("server_keys", "pins"):
                src_sub = os.path.join(candidate, sub)
                if os.path.isdir(src_sub):
                    shutil.copytree(src_sub, os.path.join(data_dir, sub),
                                    dirs_exist_ok=True)

            print(f"Migrated existing key data from {candidate}")
            print(f"  -> {data_dir}  (original left in place as a backup)")
            return candidate

        return None

    def _generate_private_key(self):
        while True:
            private_key = bytearray(os.urandom(32))
            try:
                wally.ec_private_key_verify(private_key)
                break
            except Exception:
                pass

        return private_key

    def _get_static_server_key_pair(self):
        os.makedirs(self.SERVER_KEY_PATH, mode=0o700, exist_ok=True)
        private_key_path = os.path.join(self.SERVER_KEY_PATH, "private.key")
        public_key_path = os.path.join(self.SERVER_KEY_PATH, "public.key")

        if os.path.isfile(private_key_path):
            with open(private_key_path, "rb") as f:
                private_key = bytearray(f.read())
        else:
            self.KEYS_WERE_GENERATED = True
            private_key = self._generate_private_key()

            # Owner-only from the moment it exists.
            fd = os.open(private_key_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with os.fdopen(fd, "wb") as f:
                f.write(private_key)

        public_key = wally.ec_public_key_from_private_key(private_key)

        with open(public_key_path, "wb") as f:
            f.write(public_key)

        return private_key, public_key

    def _get_cipher(self):
        """
        Gets or creates a new settings key

        return Cipher
        """
        # Create new key if no file
        if not os.path.isfile(self.SETTINGS_KEY):
            key = Fernet.generate_key()
            os.makedirs(os.path.dirname(self.SETTINGS_KEY), mode=0o700, exist_ok=True)
            with open(os.open(self.SETTINGS_KEY, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), "wb") as key_file:
                key_file.write(key)
        else:
            with open(self.SETTINGS_KEY, "rb") as key_file:
                key = key_file.read()
        return Fernet(key)

    def _recover_hosts_from_file(self) ->set[str]|None:
        # Check if file exists
        if os.path.isfile(self.HOSTS_FILE):
            with open(self.HOSTS_FILE, "rb") as f:
                encrypted_data = f.read()
            cipher = self._get_cipher()
            plain_text = cipher.decrypt(encrypted_data).decode("utf-8")

            recovered_hosts_set = set(plain_text.splitlines())
            return recovered_hosts_set

        return None

    def _store_hosts_in_file(self, hosts: set[str]):
        hosts_string = "\n".join(hosts)
        cipher = self._get_cipher()
        encrypted_hosts = cipher.encrypt(hosts_string.encode("utf-8"))
        fd = os.open(self.HOSTS_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with open(fd, "wb") as file:
            file.write(encrypted_hosts)

    def _recover_ports_from_file(self) -> set[str]|None:
        # Check if file exists
        if os.path.isfile(self.PORTS_FILE):
            with open(self.PORTS_FILE, "rb") as f:
                encrypted_data = f.read()
            cipher = self._get_cipher()
            plain_text = cipher.decrypt(encrypted_data).decode("utf-8")

            recovered_ports_set = set(plain_text.splitlines())
            return recovered_ports_set
        return None

    def _store_ports_in_file(self, ports: set[str]):
        ports_string = "\n".join(ports)
        cipher = self._get_cipher()
        encrypted_ports = cipher.encrypt(ports_string.encode("utf-8"))
        fd = os.open(self.PORTS_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with open(fd, "wb") as file:
            file.write(encrypted_ports)

    def _load_allowed_hosts(self):
        """
        Load Allowed Hosts
        reads the hosts file and includes the allowed hosts
        """
        # lock settings mutex
        with self._settings_lock:
            # Create new allowed hosts set (defaults local_hosts)
            self._allowed_hosts = set(self.LOCAL_HOSTS)
            # Get hosts set from file
            hosts = self._recover_hosts_from_file()
            # if hosts is valid, add to the allowed hosts set
            if hosts is not None:
                self._allowed_hosts.update(hosts)

            # Add the Proxy Port setup by an environment variable
            proxy_host = os.getenv("PUBLIC_JADE_PROXY_HOST")
            if proxy_host:
                proxy_host = proxy_host.lower()
                self._allowed_hosts.add(proxy_host)
                self.PROXY_HOST = proxy_host

    def _load_allowed_ports(self):
        """
        Load allowed Ports
        reads the ports file and includes the allowed ports
        """
        # lock settings mutex
        with self._settings_lock:
            # Create new allowed ports set (defaults local_ports)
            self._allowed_ports = set(self.LOCAL_PORTS)

            # Get ports set from the file
            ports = self._recover_ports_from_file()
            # If ports set is valid, add them to the allowed ports set
            if ports is not None:
                self._allowed_ports.update(ports)

            # Add the Proxy Port setup by an environment variable
            proxy_server_port = os.getenv("PUBLIC_JADE_SERVER_PROXY_PORT")
            if proxy_server_port and proxy_server_port.isdigit():
                port_num = int(proxy_server_port)
                if 0 < port_num <= 65535:
                    self._allowed_ports.add(str(port_num))
                    self.PROXY_SERVER_PORT = str(port_num)
            proxy_web_port = os.getenv("PUBLIC_JADE_WEB_PROXY_PORT")
            if proxy_web_port and proxy_web_port.isdigit():
                port_num = int(proxy_web_port)
                if 0 < port_num <= 65535:
                    self._allowed_ports.add(str(port_num))
                    self.PROXY_WEB_PORT = str(port_num)
                    
                


    def init(self, args):
        print("Config Initialize")
        self.APP_DIR = self._app_dir()
        self.WEB_ROOT = os.path.join(self.APP_DIR, "web")
        self.DATA_DIR = self._data_dir()

        if args.data_dir:
            self.DATA_DIR = os.path.abspath(os.path.expanduser(args.data_dir))
        self.TLS_CERT_PATH = os.path.join(self.DATA_DIR, "server.pem")
        self.SERVER_KEY_PATH = os.path.join(self.DATA_DIR, "server_keys")
        self.PINS_PATH = os.path.join(self.DATA_DIR, "pins")
        self.SETTINGS_PATH = os.path.join(self.DATA_DIR, "settings")
        self.SETTINGS_KEY = os.path.join(self.SETTINGS_PATH, "secret.key")
        self.HOSTS_FILE = os.path.join(self.SETTINGS_PATH, "hosts")
        self.PORTS_FILE = os.path.join(self.SETTINGS_PATH, "ports")
        self.MIGRATED_FROM = self._migrate_legacy_data(self.DATA_DIR)
        self.LISTEN_IP = args.listen
        self.LISTEN_ADDR = self.LISTEN_IP
        self.LISTEN_PORT = args.port
        self.USING_TLS = args.tls

        # get static server keys (private and public)
        self.STATIC_SERVER_PRIVATE_KEY, self.STATIC_SERVER_PUBLIC_KEY = self._get_static_server_key_pair()
        # get the aes pin data
        self.STATIC_SERVER_AES_PIN_DATA = wally.hmac_sha256(self.STATIC_SERVER_PRIVATE_KEY, b'pin_data')

        # Load the allowed hosts and ports
        self._load_allowed_hosts()
        self._load_allowed_ports()

        print("Config Allowed Hosts: ", self.get_allowed_hosts())
        print("Config Allowed Ports; ", self.get_allowed_ports())

    def get_allowed_hosts(self) -> set[str]:
        return self._allowed_hosts

    def get_allowed_ports(self) -> set[str]:
        return self._allowed_ports

    def add_allowed_host(self, new_host:str) -> tuple[bool, str, int]:
        """
        Add Allowed Host
        Takes in the new_host name and adds it to the allowed_hosts list 
        as well as write it to the file
        """
        new_host = new_host.lower()

        # Lock settings mutex
        with self._settings_lock:

            if new_host in self.get_allowed_hosts():
                return False, "Host already exists", 409

            # Ensure directories are created
            os.makedirs(os.path.dirname(self.HOSTS_FILE), mode=0o700, exist_ok=True)
            # # Open file as append
            # with open(self.HOSTS_FILE, "a") as file:
            #     # Write new host to file
            #     file.write(new_host + "\n")
            #     # add new host to allowed set
            #     self._allowed_hosts.add(new_host)
            #     return True, "Success", 200

            # add new host to allowed set
            self._allowed_hosts.add(new_host)
            hosts_set = set(self._allowed_hosts) - self.LOCAL_HOSTS
            self._store_hosts_in_file(hosts_set)

            return True, "Success", 200

        return False, "Unknown Error", 400
    
    def add_allowed_port(self, new_port:str) -> tuple[bool, str, int]:
        """
        Add Allowed Port
        Takes in the new_port and adds it to the allowed_ports list
        as well as write it to the file for saving
        """
        # Lock settings mutex
        with self._settings_lock:

            if new_port in self.get_allowed_ports():
                return False, "Port already exists.", 409

            # Ensure directories are created
            os.makedirs(os.path.dirname(self.PORTS_FILE), mode=0o700, exist_ok=True)
            # # Open file as append
            # with open(self.PORTS_FILE, "a") as file:
            #     # Write new port to file
            #     file.write(new_port + "\n")
            #     # add new host to allowed set
            #     self._allowed_ports.add(new_port)
            #     return True, "Success", 200

            # add new host to allowed set
            self._allowed_ports.add(new_port)
            ports_set = set(self._allowed_ports) - self.LOCAL_PORTS
            self._store_ports_in_file(ports_set)
            
            return True, "Success", 200

        return False, "Unknown Error", 400

    def remove_allowed_host(self, host_to_remove:str) -> tuple[bool, str, int]:
        """
        Remove allowed host
        Removes the passed in host from the allowed_hosts set
        as well as removes it from the file for saving
        """
        # Lock settings mutex
        with self._settings_lock:

            if host_to_remove not in self.get_allowed_hosts():
                return False, "Host not in existing list", 409

            if host_to_remove in self.LOCAL_HOSTS:
                return False, "Localhosts can not be removed", 403

            if host_to_remove == self.PROXY_HOST:
                return False, "Host is a proxy host set as an environment variable.", 403

            # Check if Hosts file exist, otherwise, we do nothing
            if not os.path.isfile(self.HOSTS_FILE):
                return False, "File does not exist.", 400

            # Open hosts file
            # with open(self.HOSTS_FILE, "r") as file:

            #     # Get all hosts from file
            #     hosts = set(file.read().splitlines())
            #TODO: COMBINE TO FUNCTION
            hosts = self._recover_hosts_from_file()
            if hosts is not None:
                # Remove the host that was named
                hosts.discard(host_to_remove)
                self._store_hosts_in_file(hosts)

            # Remove the host that was named
            #hosts.discard(host_to_remove)

            # Open hosts file as write
            # with open(self.HOSTS_FILE, "w") as file:
            #     # For each host add the host to file
            #     for host in hosts:
            #         file.write(host + "\n")

            # remove host that was named from allowed hosts set
            self._allowed_hosts.discard(host_to_remove)
            return True, "Success", 200

    def remove_allowed_port(self, port_to_remove:str) -> tuple[bool, str, int]:
        """
        Remove allowed port
        Removes the passed in port from the allowed_ports set
        as well as removes it from the file for saving
        """
        # Lock settings mutex
        with self._settings_lock:

            if port_to_remove not in self.get_allowed_ports():
                return False, "Port is not in existing list", 409

            if port_to_remove in self.LOCAL_PORTS:
                return False, "Local ports can not be removed", 403

            if port_to_remove == self.PROXY_SERVER_PORT or port_to_remove == self.PROXY_WEB_PORT:
                return False, "Port is a proxy port set as an environment variable.", 403

            # check if ports file exists, if not we do nothing
            if not os.path.isfile(self.PORTS_FILE):
                return False, "Ports file does not exist", 400


            ports = self._recover_ports_from_file()
            if ports is not None:
                # remove the port that was named
                ports.discard(port_to_remove)
                self._store_ports_in_file(ports)

            # Open ports file as readonly
            # with open(self.PORTS_FILE, "r") as file:
            #     # get all ports from file
            #     ports = set(file.read().splitlines())

            # # remove the port that was named
            # ports.discard(port_to_remove)


            # # Open ports file as write
            # with open(self.PORTS_FILE, "w") as file:
            #     # For each port, add port to file
            #     for port in ports:
            #         file.write(port + "\n")

            # Remove port that was named from the allowed ports set
            self._allowed_ports.discard(port_to_remove)
            return True, "Success", 200

def get_config_instance():
    """
    Get Config Instance
    Acts as a singleton
    """
    global config_instance

    if config_instance is None:
        config_instance = Config()
    return config_instance