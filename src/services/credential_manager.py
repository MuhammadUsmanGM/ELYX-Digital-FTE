import os
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Dict, Any, Optional
import getpass


class CredentialManager:
    # File to persist the random salt (generated once, reused across sessions)
    _SALT_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'secure_credentials', '.salt')

    def __init__(self, password: Optional[str] = None):
        """
        Initialize the credential manager

        Args:
            password: Optional password for encryption/decryption.
                     If not provided, will prompt for password.
        """
        if password is None:
            self.password = getpass.getpass("Enter encryption password: ")
        else:
            self.password = password

        # Load or generate a random salt
        self.salt = self._load_or_create_salt()

        # Generate encryption key from password
        self.key = self._derive_key(self.password.encode())
        self.cipher_suite = Fernet(self.key)

    def _load_or_create_salt(self) -> bytes:
        """Load existing salt from disk, or generate and persist a new random one.

        Raises RuntimeError if a new salt cannot be persisted, since a
        non-persistent salt would silently break decryption in future sessions.
        """
        salt_path = os.path.normpath(self._SALT_FILE)
        try:
            if os.path.exists(salt_path):
                with open(salt_path, 'rb') as f:
                    salt = f.read()
                if len(salt) == 32:
                    return salt
        except Exception:
            pass

        # Generate a cryptographically random 32-byte salt
        salt = os.urandom(32)
        try:
            os.makedirs(os.path.dirname(salt_path), exist_ok=True)
            with open(salt_path, 'wb') as f:
                f.write(salt)
            # Verify the write succeeded by reading it back
            with open(salt_path, 'rb') as f:
                saved = f.read()
            if saved != salt:
                raise IOError("Salt verification failed after write")
        except Exception as e:
            raise RuntimeError(
                f"Cannot persist encryption salt to {salt_path}: {e}. "
                "Future sessions will be unable to decrypt data. "
                "Ensure the directory is writable."
            )
        return salt

    def _derive_key(self, password: bytes) -> bytes:
        """
        Derive a key from the password using PBKDF2

        Args:
            password: Password as bytes

        Returns:
            Derived key as bytes
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key

    def encrypt_credential(self, credential_data: Dict[str, Any]) -> str:
        """
        Encrypt credential data

        Args:
            credential_data: Dictionary containing credential information

        Returns:
            Encrypted credential string
        """
        json_data = json.dumps(credential_data)
        encrypted_data = self.cipher_suite.encrypt(json_data.encode())
        return encrypted_data.decode()

    def decrypt_credential(self, encrypted_data: str) -> Dict[str, Any]:
        """
        Decrypt credential data

        Args:
            encrypted_data: Encrypted credential string

        Returns:
            Decrypted credential dictionary
        """
        decrypted_data = self.cipher_suite.decrypt(encrypted_data.encode())
        return json.loads(decrypted_data.decode())

    def save_encrypted_credentials(self, credentials: Dict[str, Any], filepath: str):
        """
        Save encrypted credentials to a file

        Args:
            credentials: Dictionary containing credential information
            filepath: Path to save the encrypted credentials
        """
        encrypted_credentials = self.encrypt_credential(credentials)
        with open(filepath, 'w') as f:
            f.write(encrypted_credentials)

    def load_encrypted_credentials(self, filepath: str) -> Dict[str, Any]:
        """
        Load and decrypt credentials from a file

        Args:
            filepath: Path to the encrypted credentials file

        Returns:
            Decrypted credential dictionary
        """
        with open(filepath, 'r') as f:
            encrypted_data = f.read()
        return self.decrypt_credential(encrypted_data)

    @staticmethod
    def get_credentials_from_env(env_prefix: str) -> Dict[str, Any]:
        """
        Get credentials from environment variables with a specific prefix

        Args:
            env_prefix: Prefix for environment variables (e.g., 'GMAIL_')

        Returns:
            Dictionary of credentials from environment variables
        """
        credentials = {}
        for key, value in os.environ.items():
            if key.startswith(env_prefix):
                # Convert environment variable name to lowercase key
                cred_key = key[len(env_prefix):].lower()
                credentials[cred_key] = value
        return credentials


class SecureCredentialStore:
    def __init__(self, storage_path: str = "./secure_credentials", password: Optional[str] = None):
        """
        Initialize a secure credential store

        Args:
            storage_path: Path to store encrypted credentials
            password: Optional password for encryption/decryption
        """
        self.storage_path = storage_path
        self.password = password
        self.credential_manager = CredentialManager(password)

        # Create storage directory if it doesn't exist
        os.makedirs(storage_path, exist_ok=True)

    def store_credential_set(self, service_name: str, credentials: Dict[str, Any]):
        """
        Store a set of credentials for a specific service

        Args:
            service_name: Name of the service (e.g., 'gmail', 'linkedin', 'whatsapp')
            credentials: Dictionary containing credential information
        """
        filepath = os.path.join(self.storage_path, f"{service_name}_credentials.enc")
        self.credential_manager.save_encrypted_credentials(credentials, filepath)

    def retrieve_credential_set(self, service_name: str) -> Dict[str, Any]:
        """
        Retrieve a set of credentials for a specific service

        Args:
            service_name: Name of the service (e.g., 'gmail', 'linkedin', 'whatsapp')

        Returns:
            Dictionary containing credential information
        """
        filepath = os.path.join(self.storage_path, f"{service_name}_credentials.enc")
        return self.credential_manager.load_encrypted_credentials(filepath)

    def has_credential_set(self, service_name: str) -> bool:
        """
        Check if credentials exist for a specific service

        Args:
            service_name: Name of the service

        Returns:
            True if credentials exist, False otherwise
        """
        filepath = os.path.join(self.storage_path, f"{service_name}_credentials.enc")
        return os.path.exists(filepath)

    def store_from_env(self, service_name: str, env_prefix: str):
        """
        Store credentials from environment variables

        Args:
            service_name: Name of the service
            env_prefix: Prefix for environment variables
        """
        credentials = CredentialManager.get_credentials_from_env(env_prefix)
        if credentials:
            self.store_credential_set(service_name, credentials)


# Convenience functions for common services
def get_gmail_credentials_from_env() -> Dict[str, Any]:
    """Get Gmail credentials from environment variables"""
    return CredentialManager.get_credentials_from_env("GMAIL_")

def get_linkedin_credentials_from_env() -> Dict[str, Any]:
    """Get LinkedIn credentials from environment variables"""
    return CredentialManager.get_credentials_from_env("LINKEDIN_")

def get_whatsapp_credentials_from_env() -> Dict[str, Any]:
    """Get WhatsApp credentials from environment variables"""
    return CredentialManager.get_credentials_from_env("WHATSAPP_")


# Example usage
if __name__ == "__main__":
    # Example of how to use the credential manager
    print("Credential Manager Example")

    # Get credentials from environment (these would need to be set)
    gmail_creds = get_gmail_credentials_from_env()
    if gmail_creds:
        print(f"Found Gmail credentials: {list(gmail_creds.keys())}")

    linkedin_creds = get_linkedin_credentials_from_env()
    if linkedin_creds:
        print(f"Found LinkedIn credentials: {list(linkedin_creds.keys())}")

    whatsapp_creds = get_whatsapp_credentials_from_env()
    if whatsapp_creds:
        print(f"Found WhatsApp credentials: {list(whatsapp_creds.keys())}")