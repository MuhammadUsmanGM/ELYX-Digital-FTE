"""
Global Node Redundancy Service for Platinum Tier
Handles health monitoring and automatic failover across global regions
"""
import time
import logging
import random
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from .distributed_file_sync import DistributedFileSyncService
from ..utils.logger import log_activity

class GlobalRedundancyService:
    """
    Service to ensure High Availability (HA) through global node redundancy
    """
    def __init__(self, regions: List[str], vault_path: str):
        self.regions = regions
        self.vault_path = Path(vault_path)
        self.primary_region = regions[0] if regions else "us-east-1"
        self.active_region = self.primary_region
        self.nodes_status = {region: "healthy" for region in regions}
        self.logger = logging.getLogger("GlobalRedundancy")
        
        # Initialize Distributed File Sync
        self.sync_service = DistributedFileSyncService(regions, base_path=str(self.vault_path / "distributed_storage"))
        
        self.last_sync_time = None
        self.last_health_check = None

    def check_nodes_health(self) -> Dict[str, str]:
        """
        Simulate health checks for all global nodes
        """
        self.last_health_check = datetime.now()
        for region in self.regions:
            # Simulate a 5% chance of node degradation for testing redundancy
            if random.random() < 0.05:
                self.nodes_status[region] = "degraded"
            else:
                self.nodes_status[region] = "healthy"
                
        self.logger.info(f"Global node health check completed: {self.nodes_status}")
        return self.nodes_status

    def perform_global_sync(self, files_to_sync: List[str]) -> bool:
        """
        Sync critical files to all healthy redundant nodes
        """
        success = True
        self.last_sync_time = datetime.now()
        
        healthy_regions = [r for r, status in self.nodes_status.items() if status == "healthy"]
        
        for file_path in files_to_sync:
            try:
                # Replicate to healthy regions
                sync_result = self.sync_service.sync_file_to_regions(file_path, healthy_regions)
                if not sync_result:
                    success = False
            except Exception as e:
                self.logger.error(f"Failed to sync {file_path}: {e}")
                success = False
                
        if success:
            log_activity("GLOBAL_REDUNDANCY", f"Synchronized {len(files_to_sync)} files across {len(healthy_regions)} healthy regions", str(self.vault_path))
        
        return success

    def initiate_failover(self) -> str:
        """
        Simulate a failover to a secondary region if primary is down
        """
        if self.nodes_status.get(self.active_region) != "healthy":
            # Find the next healthy region
            for region in self.regions:
                if self.nodes_status.get(region) == "healthy" and region != self.active_region:
                    old_region = self.active_region
                    self.active_region = region
                    log_activity("FAILOVER", f"Region {old_region} unstable. Failed over to {self.active_region}", str(self.vault_path))
                    return self.active_region
        return self.active_region

    def get_redundancy_status(self) -> Dict[str, Any]:
        """
        Get current redundancy status for dashboard
        """
        return {
            "active_region": self.active_region,
            "primary_region": self.primary_region,
            "node_count": len(self.regions),
            "healthy_nodes": len([r for r, s in self.nodes_status.items() if s == "healthy"]),
            "last_sync": self.last_sync_time.isoformat() if self.last_sync_time else None,
            "nodes": self.nodes_status
        }
