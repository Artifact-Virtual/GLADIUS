"""
ERP Manager coordinating all ERP system integrations.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

from .base_connector import ERPConnector
from .connectors.sap_connector import SAPConnector
from .connectors.netsuite_connector import NetSuiteConnector
from .connectors.odoo_connector import OdooConnector
from .connectors.dynamics_connector import DynamicsConnector
from .connectors.salesforce_connector import SalesforceConnector


class ERPManager:
    """
    Manages all ERP system integrations and data synchronization.
    
    Coordinates:
    - Multiple ERP system connections
    - Automated data synchronization
    - Data transformation and mapping
    - Error handling and retry logic
    """
    
    def __init__(self, config):
        """
        Initialize ERP Manager.
        
        Args:
            config: AutomationConfig instance
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.connectors: Dict[str, ERPConnector] = {}
        self.sync_tasks = []
        self.is_syncing = False
        
        # Initialize connectors for enabled systems
        self._initialize_connectors()
    
    def _initialize_connectors(self) -> None:
        """Initialize ERP connectors for enabled systems."""
        erp_config = self.config.config["erp_systems"]
        
        connector_map = {
            "SAP": SAPConnector,
            "NetSuite": NetSuiteConnector,
            "Odoo": OdooConnector,
            "Microsoft Dynamics": DynamicsConnector,
            "Salesforce": SalesforceConnector,
            # Add more as needed
        }
        # Add optional connectors if they are available (avoid NameError on import)
        try:
            connector_map["Oracle ERP Cloud"] = OracleERPConnector
        except NameError:
            self.logger.debug("OracleERPConnector not available; skipping")

        try:
            connector_map["Workday"] = WorkdayConnector
        except NameError:
            self.logger.debug("WorkdayConnector not available; skipping")
        
        for system_name, system_config in erp_config.items():
            if system_config.get("enabled", False):
                connector_class = connector_map.get(system_name)
                if connector_class:
                    try:
                        self.connectors[system_name] = connector_class(system_config)
                        self.logger.info(f"Initialized {system_name} connector")
                    except Exception as e:
                        self.logger.error(f"Failed to initialize {system_name}: {e}")
    
    async def start_sync(self) -> None:
        """Start automated synchronization for all ERP systems."""
        self.is_syncing = True
        self.logger.info("Starting ERP synchronization...")
        
        # Connect to all ERP systems
        for system_name, connector in self.connectors.items():
            try:
                connected = await connector.connect()
                if connected:
                    self.logger.info(f"Connected to {system_name}")
                else:
                    self.logger.warning(f"Failed to connect to {system_name}")
            except Exception as e:
                self.logger.error(f"Error connecting to {system_name}: {e}")
        
        # Start sync tasks
        for system_name, connector in self.connectors.items():
            if connector.is_connected():
                task = asyncio.create_task(
                    self._sync_loop(system_name, connector)
                )
                self.sync_tasks.append(task)
    
    async def _sync_loop(self, system_name: str, connector: ERPConnector) -> None:
        """
        Continuous synchronization loop for an ERP system.
        
        Args:
            system_name: Name of the ERP system
            connector: ERP connector instance
        """
        sync_interval = self.config.get(
            f"erp_systems.{system_name}.sync_interval",
            3600
        )
        sync_entities = self.config.get(
            f"erp_systems.{system_name}.sync_entities",
            []
        )
        
        while self.is_syncing:
            try:
                self.logger.info(f"Synchronizing {system_name}...")
                
                for entity in sync_entities:
                    try:
                        records = await connector.sync_entity(entity)
                        self.logger.info(
                            f"{system_name}: Synced {len(records)} {entity} records"
                        )
                    except Exception as e:
                        self.logger.error(
                            f"{system_name}: Error syncing {entity}: {e}"
                        )
                
                # Wait for next sync
                await asyncio.sleep(sync_interval)
                
            except Exception as e:
                self.logger.error(f"Error in {system_name} sync loop: {e}")
                await asyncio.sleep(60)  # Wait before retry
    
    async def sync_entity(self, system: str, entity_type: str) -> Dict[str, Any]:
        """
        Manually trigger synchronization of specific entity.
        
        Args:
            system: ERP system name
            entity_type: Entity type to sync
            
        Returns:
            Synchronization result
        """
        connector = self.connectors.get(system)
        if not connector:
            return {"error": f"System {system} not configured"}
        
        if not connector.is_connected():
            connected = await connector.connect()
            if not connected:
                return {"error": f"Failed to connect to {system}"}
        
        try:
            records = await connector.sync_entity(entity_type)
            return {
                "system": system,
                "entity_type": entity_type,
                "records_synced": len(records),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error syncing {entity_type} from {system}: {e}")
            return {"error": str(e)}
    
    def get_sync_status(self) -> Dict[str, Any]:
        """
        Get synchronization status for all ERP systems.
        
        Returns:
            Status dictionary
        """
        status = {}
        for system_name, connector in self.connectors.items():
            status[system_name] = {
                "connected": connector.is_connected(),
                "last_sync": connector.get_last_sync_time().isoformat() if connector.get_last_sync_time() else None
            }
        return status
    
    def get_analytics(self) -> Dict[str, Any]:
        """
        Get ERP integration analytics.
        
        Returns:
            Analytics dictionary
        """
        return {
            "total_systems": len(self.connectors),
            "connected_systems": sum(1 for c in self.connectors.values() if c.is_connected()),
            "sync_status": self.get_sync_status()
        }
