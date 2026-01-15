"""
ERPIntegrationAgent: Integrates with external ERP systems (SAP, Oracle, Dynamics, Odoo, etc.)
- Supports both specific (Odoo, SAP, Oracle, Dynamics) and generic REST API ERP integration.
"""
import requests
from legion.core_framework import EnterpriseAgent

class ERPIntegrationAgent(EnterpriseAgent):
    def __init__(self, agent_id, department, config=None, capabilities=None):
        if capabilities is None:
            capabilities = [
                "odoo_integration", "sap_integration", "oracle_integration", "dynamics_integration", "generic_rest_integration"
            ]
        super().__init__(
            agent_id=agent_id,
            agent_type="erp_integration",
            department=department,
            config=config,
            capabilities=capabilities
        )
        self.erp_type = (config or {}).get("erp_type", "generic")
        self.credentials = (config or {}).get("credentials", {})
        self.endpoints = (config or {}).get("endpoints", {})
        self.api_key = self.credentials.get("api_key")
        self.oauth_token = self.credentials.get("oauth_token")

    def connect_odoo(self):
        """Connect to Odoo ERP using its public demo API (JSON-RPC)"""
        url = self.endpoints.get("odoo", "https://demo.odoo.com/jsonrpc")
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return {"status": "Connected to Odoo demo API", "data": response.json()}
            else:
                return {"status": f"Odoo API error: {response.status_code}", "error": response.text}
        except Exception as e:
            return {"status": "Odoo connection failed", "error": str(e)}

    def connect_sap(self):
        """Connect to SAP S/4HANA Cloud using its public sandbox API"""
        url = self.endpoints.get("sap", "https://sandbox.api.sap.com/s4hanacloud/")
        headers = {"APIKey": self.api_key} if self.api_key else {}
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                return {"status": "Connected to SAP sandbox API", "data": response.json()}
            else:
                return {"status": f"SAP API error: {response.status_code}", "error": response.text}
        except Exception as e:
            return {"status": "SAP connection failed", "error": str(e)}

    def connect_oracle(self):
        """Connect to Oracle Cloud ERP using its REST API"""
        url = self.endpoints.get("oracle", "https://<your-instance>.fa.em2.oraclecloud.com/fscmRestApi/resources/latest/")
        auth = (self.credentials.get("username"), self.credentials.get("password")) if self.credentials.get("username") else None
        try:
            response = requests.get(url, auth=auth, timeout=5)
            if response.status_code == 200:
                return {"status": "Connected to Oracle Cloud API", "data": response.json()}
            else:
                return {"status": f"Oracle API error: {response.status_code}", "error": response.text}
        except Exception as e:
            return {"status": "Oracle connection failed", "error": str(e)}

    def connect_dynamics(self):
        """Connect to Dynamics 365 Business Central using its API"""
        url = self.endpoints.get("dynamics", "https://api.businesscentral.dynamics.com/v2.0/<tenant>/sandbox/api/v2.0/")
        headers = {"Authorization": f"Bearer {self.oauth_token}"} if self.oauth_token else {}
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                return {"status": "Connected to Dynamics 365 API", "data": response.json()}
            else:
                return {"status": f"Dynamics API error: {response.status_code}", "error": response.text}
        except Exception as e:
            return {"status": "Dynamics connection failed", "error": str(e)}

    def connect_generic(self):
        """Connect to a generic ERP REST API endpoint"""
        url = self.endpoints.get("generic")
        if not url:
            return {"status": "No generic ERP endpoint configured"}
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return {"status": "Connected to generic ERP API", "data": response.json()}
            else:
                return {"status": f"Generic ERP API error: {response.status_code}", "error": response.text}
        except Exception as e:
            return {"status": "Generic ERP connection failed", "error": str(e)}

    def run(self):
        """Run the connection method based on the configured ERP type"""
        if self.erp_type == "odoo":
            return self.connect_odoo()
        if self.erp_type == "sap":
            return self.connect_sap()
        if self.erp_type == "oracle":
            return self.connect_oracle()
        if self.erp_type == "dynamics":
            return self.connect_dynamics()
        return self.connect_generic()
