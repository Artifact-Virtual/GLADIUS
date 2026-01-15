from legion.core_framework import EnterpriseAgent
import requests

class CRMIntegrationAgent(EnterpriseAgent):
    def __init__(self, agent_id, department, config=None, capabilities=None):
        if capabilities is None:
            capabilities = ["salesforce_integration", "hubspot_integration", "zoho_integration", "generic_crm_rest_integration"]
        super().__init__(
            agent_id=agent_id,
            agent_type="crm_integration",
            department=department,
            config=config,
            capabilities=capabilities
        )
        self.crm_type = (config or {}).get("crm_type", "generic")
        self.credentials = (config or {}).get("credentials", {})
        self.endpoints = (config or {}).get("endpoints", {})
        self.api_key = self.credentials.get("api_key")
        self.oauth_token = self.credentials.get("oauth_token")

    def connect_salesforce(self):
        url = self.endpoints.get("salesforce", "https://login.salesforce.com/services/data/v57.0/limits")
        headers = {"Authorization": f"Bearer {self.oauth_token}"} if self.oauth_token else {}
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                return {"status": "Connected to Salesforce API", "data": response.json()}
            else:
                return {"status": f"Salesforce API error: {response.status_code}", "error": response.text}
        except Exception as e:
            return {"status": "Salesforce connection failed", "error": str(e)}

    def connect_hubspot(self):
        url = self.endpoints.get("hubspot", "https://api.hubapi.com/crm/v3/objects/contacts")
        headers = {"Authorization": f"Bearer {self.oauth_token}"} if self.oauth_token else {}
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                return {"status": "Connected to HubSpot API", "data": response.json()}
            else:
                return {"status": f"HubSpot API error: {response.status_code}", "error": response.text}
        except Exception as e:
            return {"status": "HubSpot connection failed", "error": str(e)}

    def connect_zoho(self):
        url = self.endpoints.get("zoho", "https://www.zohoapis.com/crm/v2/Leads")
        headers = {"Authorization": f"Zoho-oauthtoken {self.oauth_token}"} if self.oauth_token else {}
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                return {"status": "Connected to Zoho CRM API", "data": response.json()}
            else:
                return {"status": f"Zoho CRM API error: {response.status_code}", "error": response.text}
        except Exception as e:
            return {"status": "Zoho CRM connection failed", "error": str(e)}

    def connect_generic(self):
        url = self.endpoints.get("generic")
        if not url:
            return {"status": "No generic CRM endpoint configured"}
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return {"status": "Connected to generic CRM API", "data": response.json()}
            else:
                return {"status": f"Generic CRM API error: {response.status_code}", "error": response.text}
        except Exception as e:
            return {"status": "Generic CRM connection failed", "error": str(e)}

    def run(self):
        if self.crm_type == "salesforce":
            return self.connect_salesforce()
        if self.crm_type == "hubspot":
            return self.connect_hubspot()
        if self.crm_type == "zoho":
            return self.connect_zoho()
        return self.connect_generic()
