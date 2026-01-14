# ERP Integrations System Mapping

> Module: `Artifact/deployment/automata/erp_integrations/`
> Last Updated: 2026-01-14

---

## Overview

The ERP Integrations module provides unified connectors for enterprise resource planning systems, enabling data synchronization and automation.

---

## Components

| File | Class | Purpose | Status |
|------|-------|---------|--------|
| `__init__.py` | Module exports | Connector loading | ✅ Active |
| `base_connector.py` | `ERPConnector` | Abstract base class | ✅ Production |
| `manager.py` | `ERPManager` | Orchestrates all ERP connections | ✅ Production |
| `connectors/sap_connector.py` | `SAPConnector` | SAP S/4HANA OData API | 🔲 Keys Pending |
| `connectors/odoo_connector.py` | `OdooConnector` | Odoo XML-RPC API | 🔲 Keys Pending |
| `connectors/netsuite_connector.py` | `NetSuiteConnector` | NetSuite SuiteScript/REST | 🔲 Keys Pending |
| `connectors/dynamics_connector.py` | `DynamicsConnector` | Microsoft Dynamics 365 | 🔲 Keys Pending |
| `connectors/salesforce_connector.py` | `SalesforceConnector` | Salesforce REST API | 🔲 Keys Pending |

---

## Entity Types

All connectors support these standard entity types:

| Entity | Method | Description |
|--------|--------|-------------|
| `customers` | `sync_customers()` | Customer/partner records |
| `products` | `sync_products()` | Product/service catalog |
| `orders` | `sync_orders()` | Sales orders/transactions |
| `inventory` | `sync_inventory()` | Stock/inventory levels |
| `financials` | `sync_financials()` | Financial summaries |

---

## SAP Commands

```python
from automata.erp_integrations.connectors.sap_connector import SAPConnector

config = {
    'api_url': 'https://your-sap-instance.com',
    'client': '100',
    'username': 'your_user',
    'password': 'your_pass'
}

connector = SAPConnector(config)
await connector.connect()

# Sync customers (Business Partners)
result = await connector.sync_customers()
# {'success': True, 'count': 150, 'customers': [...]}

# Sync products
result = await connector.sync_products()

# Sync sales orders
result = await connector.sync_orders()

# Check connection
is_ok = await connector.test_connection()
```

---

## Odoo Commands

```python
from automata.erp_integrations.connectors.odoo_connector import OdooConnector

config = {
    'url': 'https://your-odoo-instance.com',
    'database': 'your_db',
    'username': 'your_user',
    'password': 'your_pass'
}

connector = OdooConnector(config)
await connector.connect()

# Sync customers (res.partner)
result = await connector.sync_customers()

# Sync products (product.product)
result = await connector.sync_products()

# Sync sales orders (sale.order)
result = await connector.sync_orders()
```

---

## NetSuite Commands

```python
from automata.erp_integrations.connectors.netsuite_connector import NetSuiteConnector

config = {
    'account_id': 'your_account',
    'consumer_key': 'your_key',
    'consumer_secret': 'your_secret',
    'token_id': 'your_token',
    'token_secret': 'your_token_secret'
}

connector = NetSuiteConnector(config)
await connector.connect()

# Sync customers
result = await connector.sync_customers()

# Sync inventory items
result = await connector.sync_products()
```

---

## Dynamics 365 Commands

```python
from automata.erp_integrations.connectors.dynamics_connector import DynamicsConnector

config = {
    'tenant_id': 'your_tenant',
    'client_id': 'your_client',
    'client_secret': 'your_secret',
    'resource_url': 'https://your-org.crm.dynamics.com'
}

connector = DynamicsConnector(config)
await connector.connect()

# Sync accounts (customers)
result = await connector.sync_customers()

# Sync products
result = await connector.sync_products()

# Sync opportunities/orders
result = await connector.sync_orders()
```

---

## Salesforce Commands

```python
from automata.erp_integrations.connectors.salesforce_connector import SalesforceConnector

config = {
    'client_id': 'your_client_id',
    'client_secret': 'your_client_secret',
    'username': 'your_user',
    'password': 'your_pass',
    'security_token': 'your_token',
    'instance_url': 'https://your-org.salesforce.com'
}

connector = SalesforceConnector(config)
await connector.connect()

# Sync accounts
result = await connector.sync_customers()

# Sync products
result = await connector.sync_products()

# Sync opportunities
result = await connector.sync_orders()
```

---

## ERP Manager Commands

```python
from automata.erp_integrations.manager import ERPManager

manager = ERPManager(config)

# Start sync for all enabled ERP systems
await manager.start_sync()

# Sync specific entity from specific system
result = await manager.sync_entity("SAP", "customers")

# Get sync status
status = manager.get_sync_status()
# {'SAP': {'connected': True, 'last_sync': '2026-01-14T10:00:00Z'}, ...}

# Get analytics
analytics = manager.get_analytics()
```

---

## Environment Variables

### SAP S/4HANA
| Variable | Description |
|----------|-------------|
| `SAP_ENABLED` | Enable SAP integration |
| `SAP_API_URL` | SAP OData API base URL |
| `SAP_CLIENT` | SAP client number |
| `SAP_USERNAME` | SAP username |
| `SAP_PASSWORD` | SAP password |

### Odoo
| Variable | Description |
|----------|-------------|
| `ODOO_ENABLED` | Enable Odoo integration |
| `ODOO_URL` | Odoo instance URL |
| `ODOO_DATABASE` | Odoo database name |
| `ODOO_USERNAME` | Odoo username |
| `ODOO_PASSWORD` | Odoo password |

### NetSuite
| Variable | Description |
|----------|-------------|
| `NETSUITE_ENABLED` | Enable NetSuite integration |
| `NETSUITE_ACCOUNT_ID` | NetSuite account ID |
| `NETSUITE_CONSUMER_KEY` | OAuth consumer key |
| `NETSUITE_CONSUMER_SECRET` | OAuth consumer secret |
| `NETSUITE_TOKEN_ID` | Token ID |
| `NETSUITE_TOKEN_SECRET` | Token secret |

### Microsoft Dynamics 365
| Variable | Description |
|----------|-------------|
| `DYNAMICS_ENABLED` | Enable Dynamics integration |
| `DYNAMICS_TENANT_ID` | Azure AD tenant ID |
| `DYNAMICS_CLIENT_ID` | App registration client ID |
| `DYNAMICS_CLIENT_SECRET` | Client secret |
| `DYNAMICS_RESOURCE_URL` | Dynamics instance URL |

### Salesforce
| Variable | Description |
|----------|-------------|
| `SALESFORCE_ENABLED` | Enable Salesforce integration |
| `SALESFORCE_CLIENT_ID` | Connected app client ID |
| `SALESFORCE_CLIENT_SECRET` | Client secret |
| `SALESFORCE_USERNAME` | Salesforce username |
| `SALESFORCE_PASSWORD` | Salesforce password |
| `SALESFORCE_SECURITY_TOKEN` | Security token |
| `SALESFORCE_INSTANCE_URL` | Salesforce instance URL |

---

## Tool Registry Integration

The following ERP tools can be added to the cognition tool registry:

| Tool | Category | Description |
|------|----------|-------------|
| `erp_sync_customers` | erp | Sync customers from ERP |
| `erp_sync_products` | erp | Sync products from ERP |
| `erp_sync_orders` | erp | Sync orders from ERP |
| `erp_sync_inventory` | erp | Sync inventory from ERP |
| `erp_get_status` | erp | Get ERP connection status |
| `erp_create_customer` | erp | Create customer in ERP |
| `erp_create_order` | erp | Create order in ERP |
| `erp_update_inventory` | erp | Update inventory in ERP |

---

## Testing

```bash
# Test ERP connections
python -c "
import asyncio
from automata.erp_integrations.manager import ERPManager
# ... test code
"
```

---

*Generated by Gladius System Mapper*
