# Copyright (c) 2026, Harleen Lappano
# All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from hashlib import sha256
from app.config import get_config_instance
import base64
import wallycore as wally
import os

# Global Pin Service
pin_service_instance = None

class PinService:

    def _generate_ec_key_pair(self, replay_counter, cke):
        config = get_config_instance()
        tweak = sha256(wally.hmac_sha256(cke, replay_counter)).digest()
        private_key = wally.ec_private_key_bip341_tweak(config.STATIC_SERVER_PRIVATE_KEY, tweak, 0)
        wally.ec_private_key_verify(private_key)
        public_key = wally.ec_public_key_from_private_key(private_key)

        return private_key, public_key

    def _load_pin_fields(self, pin_pubkey_hash, pin_pubkey):
        config = get_config_instance()
        with open(os.path.join(config.PINS_PATH, self.bytes2hex(pin_pubkey_hash) + ".pin"), "rb") as f:
            data = f.read()

        assert len(data) == 129
        version_bytes = data[:1]
        assert version_bytes[0] == 1
        hmac_received = data[1:33]
        encrypted = data[33:]
        pin_auth_key = wally.hmac_sha256(config.STATIC_SERVER_AES_PIN_DATA, pin_pubkey_hash)
        hmac_payload = wally.hmac_sha256(pin_auth_key, version_bytes + encrypted)
        assert hmac_payload == hmac_received

        storage_aes_key = wally.hmac_sha256(config.STATIC_SERVER_AES_PIN_DATA, pin_pubkey)
        iv = encrypted[:16]
        plaintext = wally.aes_cbc(storage_aes_key, iv, encrypted[16:], wally.AES_FLAG_DECRYPT)
        assert len(plaintext) == 32 + 32 + 1 + 4

        saved_hash_pin_secret = plaintext[:32]
        saved_key = plaintext[32:64]
        counter = plaintext[64]
        replay_counter_persisted = plaintext[65:69]

        return saved_hash_pin_secret, saved_key, counter, replay_counter_persisted

    def _save_pin_fields(self, pin_pubkey_hash, hash_pin_secret, aes_key, pin_pubkey, counter, replay_counter):
        config = get_config_instance()
        storage_aes_key = wally.hmac_sha256(config.STATIC_SERVER_AES_PIN_DATA, pin_pubkey)
        count_bytes = counter.to_bytes(1)
        plaintext = hash_pin_secret + aes_key + count_bytes + replay_counter
        iv = os.urandom(16)
        encrypted = iv + wally.aes_cbc(storage_aes_key, iv, plaintext, wally.AES_FLAG_ENCRYPT)
        pin_auth_key = wally.hmac_sha256(config.STATIC_SERVER_AES_PIN_DATA, pin_pubkey_hash)
        version_bytes = b'\x01'
        hmac_payload = wally.hmac_sha256(pin_auth_key, version_bytes + encrypted)

        os.makedirs(config.PINS_PATH, mode=0o700, exist_ok=True)

        with open(os.path.join(config.PINS_PATH, self.bytes2hex(pin_pubkey_hash) + ".pin"), "wb") as f:
            f.write(version_bytes + hmac_payload + encrypted)

    def bytes2hex(self, byte_array):
        return ''.join('{:02x}'.format(x) for x in byte_array)

    def get_pin(self, encoded_data:any) ->str:

        data = base64.b64decode(encoded_data)
        assert len(data) > 37
        cke = data[:33]
        replay_counter = data[33:37]
        encrypted_data = data[37:]

        private_key, public_key = self._generate_ec_key_pair(replay_counter, cke)

        payload = wally.aes_cbc_with_ecdh_key(private_key, None, encrypted_data, cke, b'blind_oracle_request', wally.AES_FLAG_DECRYPT)

        # get_pin
        assert len(payload) == 32 + 65
        pin_secret = payload[:32]
        sig = payload[32:]
        signed_msg = bytearray(sha256(cke + replay_counter + pin_secret).digest())
        pin_pubkey = wally.ec_sig_to_public_key(signed_msg, sig)

        pin_pubkey_hash = sha256(pin_pubkey).digest()

        try:
            saved_hash_pin_secret, saved_key, counter, replay_local = self._load_pin_fields(pin_pubkey_hash, pin_pubkey)

            # Enforce anti replay (client counter must be greater than the server counter)
            client_counter = int.from_bytes(replay_counter, byteorder='little', signed=False)
            server_counter = int.from_bytes(replay_local, byteorder='little', signed=False)
            assert client_counter > server_counter
        except FileNotFoundError:
            # Return a random incorrect key to the Jade
            saved_key = os.urandom(32)

        aes_key = wally.hmac_sha256(saved_key, pin_secret)

        iv = os.urandom(16)
        encrypted_key = wally.aes_cbc_with_ecdh_key(private_key, iv, aes_key, cke, b'blind_oracle_response', wally.AES_FLAG_ENCRYPT)

        b64_bytes = base64.b64encode(encrypted_key)
        return b64_bytes.decode('utf-8')

    def set_pin(self, encoded_data:any) -> str:

        data = base64.b64decode(encoded_data);

        assert len(data) > 37
        cke = data[:33]
        replay_counter = data[33:37]
        encrypted_data = data[37:]

        private_key, public_key = self._generate_ec_key_pair(replay_counter, cke)

        payload = wally.aes_cbc_with_ecdh_key(private_key, None, encrypted_data, cke, b'blind_oracle_request', wally.AES_FLAG_DECRYPT)

        # set_pin requires client-passed entropy
        assert len(payload) == 32 + 32 + 65
        pin_secret = payload[:32]
        entropy = payload[32:64]
        sig = payload[64:]
        signed_msg = bytearray(sha256(cke + replay_counter + pin_secret + entropy).digest())
        pin_pubkey = wally.ec_sig_to_public_key(signed_msg, sig)

        pin_pubkey_hash = sha256(pin_pubkey).digest()

        replay_local = None
        try:
            _, _, _, replay_local = self._load_pin_fields(pin_pubkey_hash, pin_pubkey)

            # Enforce anti replay (client counter must be greater than the server counter)
            client_counter = int.from_bytes(replay_counter, byteorder='little', signed=False)
            server_counter = int.from_bytes(replay_local, byteorder='little', signed=False)
            assert client_counter > server_counter
        except FileNotFoundError:
            pass
        our_random = os.urandom(32)
        new_key = wally.hmac_sha256(our_random, entropy)

        hash_pin_secret = sha256(pin_secret).digest()
        replay_bytes = b'\x00\x00\x00\x00'
        self._save_pin_fields(pin_pubkey_hash, hash_pin_secret, new_key, pin_pubkey, 0, replay_bytes)
        aes_key = wally.hmac_sha256(new_key, pin_secret)

        iv = os.urandom(16)
        encrypted_key = wally.aes_cbc_with_ecdh_key(private_key, iv, aes_key, cke, b'blind_oracle_response', wally.AES_FLAG_ENCRYPT)
        b64_bytes = base64.b64encode(encrypted_key)
        return b64_bytes.decode('utf-8')

    def get_pub_key(self):
        config = get_config_instance()
        pub_key = config.STATIC_SERVER_PUBLIC_KEY
        return self.bytes2hex(pub_key)


def get_pin_service_instance():
    """
    Get Pin Service Instance
    """
    global pin_service_instance

    if pin_service_instance is None:
        pin_service_instance = PinService()
    return pin_service_instance