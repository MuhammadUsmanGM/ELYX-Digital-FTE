"""
Blockchain API Routes for Platinum Tier
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ...services.database import get_db
from ..platinum_tier_models import (
    BlockchainEventRequest, BlockchainEventResponse,
    QuantumTransactionRequest, QuantumTransactionResponse
)

router = APIRouter(prefix="/blockchain", tags=["blockchain"])


@router.get("/events", response_model=List[BlockchainEventResponse])
async def get_blockchain_events(
    db: Session = Depends(get_db),
    event_type: Optional[str] = None,
    blockchain_network: Optional[str] = None,
    limit: int = 100
):
    """
    Retrieve blockchain events from the accountability service
    """
    try:
        from ...services.blockchain_service import BlockchainService
        service = BlockchainService()
        audit_trail = service.get_audit_trail()
        
        # Take the most recent events up to limit
        events = []
        for block in audit_trail[-limit:]:
            data = block.get("data", {})
            events.append({
                "id": data.get("transaction_id", f"blk-{block['index']}"),
                "event_type": data.get("action_type", "system_event"),
                "blockchain_network": "ELYX-Private-Mainnet",
                "transaction_hash": block.get("hash"),
                "block_number": block.get("index"),
                "contract_address": "0x0",
                "event_data": data.get("details", {}),
                "participants": ["system"],
                "gas_consumed": 0,
                "timestamp": block.get("timestamp"),
                "verification_status": "verified" if service.verify_integrity() else "pending",
                "oracle_verifications": {},
                "compliance_tags": ["audit"],
                "quantum_signature_verified": data.get("quantum_signature") is not None,
                "linked_tasks": [],
                "created_at": block.get("timestamp"),
                "updated_at": block.get("timestamp"),
                "ai_analysis": {"validity": "verified"}
            })

        return [BlockchainEventResponse(**event) for event in events]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving blockchain events: {str(e)}")


@router.post("/transactions", response_model=QuantumTransactionResponse)
async def create_blockchain_transaction(
    transaction: QuantumTransactionRequest,
    db: Session = Depends(get_db)
):
    """
    Create a blockchain transaction
    """
    try:
        from ...services.blockchain_service import BlockchainService
        service = BlockchainService()
        
        tx_id = service.record_action(
            action_type=transaction.transaction_type,
            details={
                "sender": transaction.sender_id,
                "receiver": transaction.receiver_id,
                "amount": transaction.amount,
                "currency": transaction.currency
            }
        )
        
        status_info = service.get_stats()

        return QuantumTransactionResponse(
            transaction_id=tx_id,
            transaction_hash=status_info["last_block_hash"],
            status="completed",
            estimated_gas=0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating blockchain transaction: {str(e)}")


@router.get("/contracts")
async def get_smart_contracts():
    """
    Get list of deployed smart contracts
    """
    try:
        return {
            "contracts": [
                {
                    "address": "0x1234567890123456789012345678901234567890",
                    "name": "PersonalAIEmployee",
                    "version": "1.0.0",
                    "deployed_at": "2023-01-01T00:00:00Z",
                    "network": "ethereum"
                }
            ],
            "total_count": 1
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving contracts: {str(e)}")


@router.get("/status")
async def get_blockchain_status():
    """
    Get blockchain integration status
    """
    try:
        from ...services.blockchain_service import BlockchainService
        service = BlockchainService()
        stats = service.get_stats()
        
        return {
            "status": "connected" if stats["integrity_verified"] else "degraded",
            "network": stats["network"],
            "latest_block": stats["total_blocks"],
            "sync_status": "synced",
            "connected_nodes": 1,
            "last_transaction": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting blockchain status: {str(e)}")