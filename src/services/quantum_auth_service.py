"""
Quantum-Safe Authentication Service for Platinum Tier
Implements cryptographic authentication using SHA3-512 hashing

Note: This service uses SHA3-512 for enhanced cryptographic security.
While designed with future quantum-resistance in mind, it has not been
formally verified against NIST PQC standards.
"""
import jwt
import secrets
import hashlib
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from enum import Enum
import uuid
from dataclasses import dataclass
from .quantum_random_service import get_quantum_rng
from ..utils.quantum_resistant_hash import QuantumResistantHasher


class AuthTokenType(Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    CRYPTOGRAPHIC = "cryptographic"


@dataclass
class AuthToken:
    """Authentication token with cryptographic properties"""
    token: str
    token_type: str
    user_id: str
    expires_at: datetime
    issued_at: datetime
    quantum_signature: str
    security_level: str
    scopes: list


class QuantumSafeAuthService:
    """
    Cryptographic authentication service with SHA3-512 hashing.
    
    This service provides:
    - User registration with salted SHA3-512 password hashing
    - JWT token generation with cryptographic signatures
    - Session tracking and token revocation
    - Account lockout after failed attempts
    
    Note: Uses SHA3-512 for enhanced security but has not been
    formally verified as quantum-resistant under NIST PQC standards.
    """

    def __init__(self, secret_key: Optional[str] = None):
        self.qrng = get_quantum_rng()
        self.hasher = QuantumResistantHasher()
        self.secret_key = secret_key or self._generate_quantum_safe_secret()
        self.token_store = {}  # In production, use a database or Redis
        self.session_store = {}  # Track active sessions

    def _generate_quantum_safe_secret(self) -> str:
        """Generate a cryptographically secure secret key using quantum entropy"""
        # Generate a cryptographically secure secret using the quantum random number generator
        secret_bytes = self.qrng.get_random_bytes(64)  # 512-bit secret
        return secret_bytes.hex()

    def register_user(self, username: str, password: str, email: str) -> Dict[str, Any]:
        """
        Register a new user with cryptographic password hashing

        Args:
            username: User's username
            password: User's password
            email: User's email

        Returns:
            Dictionary with user registration details
        """
        user_id = str(uuid.uuid4())
        created_at = datetime.utcnow()

        # Cryptographic password hashing using SHA3-512
        salt = self.qrng.get_random_bytes(32)
        hashed_password = self.hasher.pbkdf2_hash(
            password=password,
            salt=salt,
            iterations=150000,  # Higher iterations for security
            algorithm=self.hasher.algorithms.__class__.SHA3_512
        )

        # Store user data (in production, use a proper database)
        user_data = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "hashed_password": hashed_password.digest,
            "password_salt": hashed_password.salt,
            "created_at": created_at.isoformat() + "Z",
            "last_login": None,
            "failed_login_attempts": 0,
            "account_locked": False,
            "quantum_auth_enabled": True
        }

        # Store in a simple dict for this example (use database in production)
        if not hasattr(self, '_users'):
            self._users = {}
        self._users[user_id] = user_data

        return {
            "user_id": user_id,
            "username": username,
            "email": email,
            "created_at": created_at.isoformat() + "Z"
        }

    def authenticate_user(self, username: str, password: str) -> Optional[AuthToken]:
        """
        Authenticate a user using cryptographic methods

        Args:
            username: User's username
            password: User's password

        Returns:
            AuthToken if authentication succeeds, None otherwise
        """
        # Find user by username
        user = None
        for uid, udata in getattr(self, '_users', {}).items():
            if udata['username'] == username:
                user = udata
                break

        if not user:
            return None

        # Check if account is locked
        if user.get('account_locked', False):
            return None

        # Verify password using cryptographic hash
        salt = user['password_salt'].encode() if isinstance(user['password_salt'], str) else user['password_salt']
        provided_hash = self.hasher.pbkdf2_hash(
            password=password,
            salt=salt,
            iterations=150000,  # Same as during registration
            algorithm=self.hasher.algorithms.__class__.SHA3_512
        )

        if provided_hash.digest != user['hashed_password']:
            # Increment failed attempts
            user['failed_login_attempts'] = user.get('failed_login_attempts', 0) + 1
            if user['failed_login_attempts'] >= 5:  # Lock account after 5 failed attempts
                user['account_locked'] = True
            return None

        # Reset failed attempts on successful login
        user['failed_login_attempts'] = 0
        user['last_login'] = datetime.utcnow().isoformat() + "Z"

        # Generate quantum-safe access token
        return self.generate_access_token(user['user_id'])

    def generate_access_token(self, user_id: str, expires_in_minutes: int = 60) -> AuthToken:
        """
        Generate a cryptographic access token

        Args:
            user_id: ID of the user
            expires_in_minutes: Token expiration time in minutes

        Returns:
            AuthToken object
        """
        issued_at = datetime.utcnow()
        expires_at = issued_at + timedelta(minutes=expires_in_minutes)

        # Create payload
        payload = {
            "user_id": user_id,
            "iat": issued_at.timestamp(),
            "exp": expires_at.timestamp(),
            "type": AuthTokenType.ACCESS.value,
            "quantum_safe": True
        }

        # Generate cryptographic signature
        quantum_signature = self._generate_quantum_signature(payload)

        # Create JWT token
        token = jwt.encode(
            payload,
            self.secret_key,
            algorithm='HS256'  # We'll use our quantum-safe secret
        )

        # Create token record
        token_record = AuthToken(
            token=token,
            token_type=AuthTokenType.ACCESS.value,
            user_id=user_id,
            expires_at=expires_at,
            issued_at=issued_at,
            quantum_signature=quantum_signature,
            security_level="quantum_safe",
            scopes=["read", "write"]  # Default scopes
        )

        # Store token for revocation tracking
        self.token_store[token] = {
            "user_id": user_id,
            "expires_at": expires_at,
            "revoked": False
        }

        # Track session
        session_id = str(uuid.uuid4())
        self.session_store[session_id] = {
            "user_id": user_id,
            "token": token,
            "created_at": issued_at,
            "expires_at": expires_at
        }

        return token_record

    def _generate_quantum_signature(self, payload: Dict[str, Any]) -> str:
        """
        Generate a cryptographic signature for the token payload using SHA3-512

        Args:
            payload: Token payload to sign

        Returns:
            Cryptographic signature string
        """
        # Serialize payload
        payload_str = str(sorted(payload.items()))

        # Generate cryptographic hash
        hash_result = self.hasher.hash_with_salt(
            data=payload_str,
            algorithm=self.hasher.algorithms.__class__.SHA3_512,
            salt=self.qrng.get_random_bytes(32)
        )

        # Additional cryptographic transformation
        quantum_entropy = self.qrng.get_random_bytes(16)
        final_signature = self.hasher.hash(
            data=hash_result.digest.encode() + quantum_entropy,
            algorithm=self.hasher.algorithms.__class__.SHA3_256
        )

        return final_signature.digest

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify a cryptographic authentication token

        Args:
            token: Authentication token to verify

        Returns:
            Token payload if valid, None if invalid
        """
        # Check if token exists and is not revoked
        token_info = self.token_store.get(token)
        if not token_info or token_info.get('revoked', False):
            return None

        # Check if token is expired
        if datetime.utcnow() > token_info['expires_at']:
            # Mark as expired and remove
            del self.token_store[token]
            return None

        try:
            # Decode JWT token
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])

            # Verify cryptographic signature if present
            if 'quantum_signature' in payload:
                # Recreate signature and compare
                temp_payload = payload.copy()
                del temp_payload['quantum_signature']
                expected_signature = self._generate_quantum_signature(temp_payload)
                if expected_signature != payload['quantum_signature']:
                    return None

            return payload

        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def refresh_token(self, refresh_token: str) -> Optional[AuthToken]:
        """
        Refresh an access token using a refresh token

        Args:
            refresh_token: Refresh token to use

        Returns:
            New access token if refresh succeeds, None otherwise
        """
        # Verify the refresh token
        payload = self.verify_token(refresh_token)
        if not payload or payload.get('type') != AuthTokenType.REFRESH.value:
            return None

        # Generate new access token
        user_id = payload['user_id']
        return self.generate_access_token(user_id)

    def revoke_token(self, token: str) -> bool:
        """
        Revoke an authentication token

        Args:
            token: Token to revoke

        Returns:
            True if revocation succeeds, False otherwise
        """
        if token in self.token_store:
            self.token_store[token]['revoked'] = True
            return True
        return False

    def get_user_sessions(self, user_id: str) -> list:
        """
        Get all active sessions for a user

        Args:
            user_id: ID of the user

        Returns:
            List of active session IDs
        """
        sessions = []
        for session_id, session_data in self.session_store.items():
            if session_data['user_id'] == user_id and datetime.utcnow() < session_data['expires_at']:
                sessions.append(session_id)
        return sessions

    def logout_user(self, user_id: str) -> bool:
        """
        Logout user by revoking all their tokens

        Args:
            user_id: ID of the user to logout

        Returns:
            True if logout succeeds, False otherwise
        """
        # Revoke all tokens for this user
        for token, token_info in list(self.token_store.items()):
            if token_info['user_id'] == user_id:
                token_info['revoked'] = True

        # Remove all sessions for this user
        for session_id, session_data in list(self.session_store.items()):
            if session_data['user_id'] == user_id:
                del self.session_store[session_id]

        return True


# Example usage and testing
if __name__ == "__main__":
    # Initialize the quantum-safe authentication service
    auth_service = QuantumSafeAuthService()

    print("Testing Quantum-Safe Authentication Service...")

    # Register a user
    user_info = auth_service.register_user("testuser", "secure_password123", "test@example.com")
    print(f"Registered user: {user_info['username']} with ID: {user_info['user_id']}")

    # Authenticate the user
    auth_token = auth_service.authenticate_user("testuser", "secure_password123")
    if auth_token:
        print(f"Authentication successful. Token: {auth_token.token[:32]}...")
        print(f"Token expires at: {auth_token.expires_at}")
    else:
        print("Authentication failed!")

    # Verify the token
    if auth_token:
        verified_payload = auth_service.verify_token(auth_token.token)
        if verified_payload:
            print(f"Token verification successful. User ID: {verified_payload['user_id']}")
        else:
            print("Token verification failed!")

    # Test invalid credentials
    failed_auth = auth_service.authenticate_user("testuser", "wrong_password")
    if not failed_auth:
        print("Failed authentication correctly rejected.")

    # Test user sessions
    if auth_token:
        sessions = auth_service.get_user_sessions(user_info['user_id'])
        print(f"Active sessions for user: {len(sessions)}")

    # Test logout
    if auth_token:
        logout_success = auth_service.logout_user(user_info['user_id'])
        print(f"Logout successful: {logout_success}")

        # Verify token is now invalid
        verified_after_logout = auth_service.verify_token(auth_token.token)
        print(f"Token valid after logout: {verified_after_logout is not None}")