"""
Blockchain Accountability Service for Platinum Tier
Implements immutable logging of critical actions and high-impact tasks
"""
import hashlib
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid

class BlockchainService:
    """
    Simulation of a blockchain-based accountability system for AI actions
    """
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self._create_genesis_block()

    def _create_genesis_block(self):
        """Create the first block in the chain"""
        genesis_data = {
            "message": "Platinum Tier Genesis Block",
            "timestamp": time.time(),
            "version": "1.0.0"
        }
        self._add_block(previous_hash="0" * 64, data=genesis_data)

    def _add_block(self, previous_hash: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new block to the chain"""
        block = {
            "index": len(self.chain) + 1,
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "previous_hash": previous_hash,
            "nonce": 0
        }
        
        # Simple Proof of Work simulation
        block["hash"] = self._calculate_hash(block)
        self.chain.append(block)
        return block

    def _calculate_hash(self, block: Dict[str, Any]) -> str:
        """Calculate the SHA-256 hash of a block"""
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def record_action(self, action_type: str, details: Dict[str, Any], quantum_signature: Optional[str] = None) -> str:
        """
        Record a critical action on the blockchain
        """
        tx_id = str(uuid.uuid4())
        data = {
            "transaction_id": tx_id,
            "action_type": action_type,
            "details": details,
            "quantum_signature": quantum_signature,
            "recorded_at": datetime.now().isoformat()
        }
        
        previous_hash = self.chain[-1]["hash"] if self.chain else "0"
        self._add_block(previous_hash, data)
        return tx_id

    def get_audit_trail(self) -> List[Dict[str, Any]]:
        """Return the full history of recorded actions"""
        return self.chain

    def verify_integrity(self) -> bool:
        """Verify the validity of the blockchain"""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            
            # Check current hash
            recalculated = self._calculate_hash({k: v for k, v in current.items() if k != "hash"})
            if current["hash"] != recalculated:
                return False
                
            # Check link to previous
            if current["previous_hash"] != previous["hash"]:
                return False
        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get summary statistics for the dashboard"""
        return {
            "total_blocks": len(self.chain),
            "last_block_hash": self.chain[-1]["hash"] if self.chain else None,
            "integrity_verified": self.verify_integrity(),
            "network": "ELYX-Private-Mainnet"
        }
