"""
Enterprise Integration Endpoints - Free, Open-Source, and Headless Solutions
Provides connectors for CRM, Email, Finance, Project Management, and APIs
"""

import aiohttp
import smtplib
import json
import logging
import sqlite3
from datetime import datetime
from typing import Dict, List
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import os

logger = logging.getLogger(__name__)


class IntegrationManager:
    """Central manager for all external integrations"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "enterprise/config/integrations.json"
        self.config = self._load_config()
        self.session = None
        
    def _load_config(self) -> Dict:
        """Load integration configuration"""
        default_config = {
            "email": {
                "smtp_host": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "",
                "password": "",  # Use app password for Gmail
                "from_email": ""
            },
            "crm": {
                "db_path": "data/crm.db",
                "api_key": "",
                "webhook_url": ""
            },
            "finance": {
                "coingecko_api": "https://api.coingecko.com/api/v3",
                "frankfurter_api": "https://api.frankfurter.app",
                "marketstack_api": "http://api.marketstack.com/v1",
                "marketstack_key": "free_tier"
            },
            "project_management": {
                "db_path": "data/projects.db",
                "webhook_url": ""
            },
            "public_apis": {
                "spacex": "https://api.spacexdata.com/v4",
                "weather": "https://wttr.in",
                "news": "https://newsapi.org/v2",
                "github": "https://api.github.com"
            }
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
        except Exception as e:
            logger.warning(
                f"Could not load config from {self.config_path}: {e}"
            )
            
        return default_config
    
    async def initialize(self):
        """Initialize all integration connections"""
        self.session = aiohttp.ClientSession()
        await self._setup_databases()
        logger.info("Integration Manager initialized")
    
    async def close(self):
        """Close all connections"""
        if self.session:
            await self.session.close()
    
    async def _setup_databases(self):
        """Initialize local databases for CRM and Project Management"""
        # CRM Database
        crm_db_path = self.config["crm"]["db_path"]
        os.makedirs(os.path.dirname(crm_db_path), exist_ok=True)
        
        with sqlite3.connect(crm_db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    company TEXT,
                    phone TEXT,
                    status TEXT DEFAULT 'new',
                    source TEXT,
                    value REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lead_id INTEGER,
                    activity_type TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (lead_id) REFERENCES leads (id)
                )
            """)
        
        # Project Management Database
        pm_db_path = self.config["project_management"]["db_path"]
        os.makedirs(os.path.dirname(pm_db_path), exist_ok=True)
        
        with sqlite3.connect(pm_db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'planning',
                    priority TEXT DEFAULT 'medium',
                    start_date DATE,
                    end_date DATE,
                    budget REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'todo',
                    assignee TEXT,
                    due_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects (id)
                )
            """)


class CRMConnector:
    """Simple, local CRM system using SQLite"""
    
    def __init__(self, integration_manager: IntegrationManager):
        self.manager = integration_manager
        self.db_path = integration_manager.config["crm"]["db_path"]
    
    async def add_lead(self, lead_data: Dict) -> int:
        """Add a new lead to the CRM"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    INSERT INTO leads (name, email, company, phone, status, source, value)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    lead_data.get("name"),
                    lead_data.get("email"),
                    lead_data.get("company"),
                    lead_data.get("phone"),
                    lead_data.get("status", "new"),
                    lead_data.get("source"),
                    lead_data.get("value", 0)
                ))
                lead_id = cursor.lastrowid
                
            logger.info(f"Added new lead: {lead_data.get('name')} (ID: {lead_id})")
            return lead_id
            
        except Exception as e:
            logger.error(f"Error adding lead: {e}")
            return None
    
    async def get_leads(self, status: str = None) -> List[Dict]:
        """Get leads from CRM"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                if status:
                    cursor = conn.execute("SELECT * FROM leads WHERE status = ?", (status,))
                else:
                    cursor = conn.execute("SELECT * FROM leads ORDER BY created_at DESC")
                
                leads = [dict(row) for row in cursor.fetchall()]
                return leads
                
        except Exception as e:
            logger.error(f"Error getting leads: {e}")
            return []
    
    async def update_lead_status(self, lead_id: int, status: str) -> bool:
        """Update lead status"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE leads 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (status, lead_id))
                
                # Add activity record
                conn.execute("""
                    INSERT INTO activities (lead_id, activity_type, description)
                    VALUES (?, ?, ?)
                """, (lead_id, "status_change", f"Status changed to {status}"))
                
            logger.info(f"Updated lead {lead_id} status to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating lead status: {e}")
            return False

class EmailConnector:
    """Email automation using SMTP"""
    
    def __init__(self, integration_manager: IntegrationManager):
        self.manager = integration_manager
        self.config = integration_manager.config["email"]
    
    async def send_email(self, to_email: str, subject: str, body: str, html_body: str = None) -> bool:
        """Send email via SMTP"""
        try:
            msg = MimeMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.config["from_email"]
            msg['To'] = to_email
            
            # Add text part
            text_part = MimeText(body, 'plain')
            msg.attach(text_part)
            
            # Add HTML part if provided
            if html_body:
                html_part = MimeText(html_body, 'html')
                msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.config["smtp_host"], self.config["smtp_port"]) as server:
                server.starttls()
                if self.config["username"] and self.config["password"]:
                    server.login(self.config["username"], self.config["password"])
                server.send_message(msg)
            
            logger.info(f"Email sent to {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    async def send_campaign(self, recipients: List[str], subject: str, template: str, data: Dict = None) -> Dict:
        """Send email campaign to multiple recipients"""
        results = {"sent": 0, "failed": 0, "errors": []}
        
        for recipient in recipients:
            # Replace template variables if data provided
            personalized_body = template
            if data:
                for key, value in data.items():
                    personalized_body = personalized_body.replace(f"{{{key}}}", str(value))
            
            success = await self.send_email(recipient, subject, personalized_body)
            if success:
                results["sent"] += 1
            else:
                results["failed"] += 1
                results["errors"].append(f"Failed to send to {recipient}")
        
        logger.info(f"Campaign complete: {results['sent']} sent, {results['failed']} failed")
        return results

class FinanceConnector:
    """Free financial data APIs integration"""
    
    def __init__(self, integration_manager: IntegrationManager):
        self.manager = integration_manager
        self.config = integration_manager.config["finance"]
    
    async def get_crypto_prices(self, coins: List[str] = None) -> Dict:
        """Get cryptocurrency prices from CoinGecko (free tier)"""
        try:
            if not coins:
                coins = ["bitcoin", "ethereum", "cardano", "polkadot"]
            
            coins_str = ",".join(coins)
            url = f"{self.config['coingecko_api']}/simple/price"
            params = {
                "ids": coins_str,
                "vs_currencies": "usd",
                "include_24hr_change": "true"
            }
            
            async with self.manager.session.get(url, params=params) as response:
                data = await response.json()
                return data
                
        except Exception as e:
            logger.error(f"Error getting crypto prices: {e}")
            return {}
    
    async def get_exchange_rates(self, base: str = "USD") -> Dict:
        """Get exchange rates from Frankfurter (free, no API key required)"""
        try:
            url = f"{self.config['frankfurter_api']}/latest"
            params = {"from": base}
            
            async with self.manager.session.get(url, params=params) as response:
                data = await response.json()
                return data
                
        except Exception as e:
            logger.error(f"Error getting exchange rates: {e}")
            return {}
    
    async def get_market_data(self, symbol: str = "AAPL") -> Dict:
        """Get stock market data (requires free API key for marketstack)"""
        try:
            if not self.config.get("marketstack_key") or self.config["marketstack_key"] == "free_tier":
                logger.warning("No Marketstack API key configured, using mock data")
                return {
                    "symbol": symbol,
                    "price": 150.00,
                    "change": 2.50,
                    "change_percent": 1.69,
                    "volume": 1000000,
                    "timestamp": datetime.now().isoformat()
                }
            
            url = f"{self.config['marketstack_api']}/eod/latest"
            params = {
                "access_key": self.config["marketstack_key"],
                "symbols": symbol
            }
            
            async with self.manager.session.get(url, params=params) as response:
                data = await response.json()
                return data
                
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            return {}

class ProjectManagementConnector:
    """Simple project management using SQLite"""
    
    def __init__(self, integration_manager: IntegrationManager):
        self.manager = integration_manager
        self.db_path = integration_manager.config["project_management"]["db_path"]
    
    async def create_project(self, project_data: Dict) -> int:
        """Create a new project"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    INSERT INTO projects (name, description, status, priority, start_date, end_date, budget)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    project_data.get("name"),
                    project_data.get("description"),
                    project_data.get("status", "planning"),
                    project_data.get("priority", "medium"),
                    project_data.get("start_date"),
                    project_data.get("end_date"),
                    project_data.get("budget", 0)
                ))
                project_id = cursor.lastrowid
                
            logger.info(f"Created new project: {project_data.get('name')} (ID: {project_id})")
            return project_id
            
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return None
    
    async def add_task(self, task_data: Dict) -> int:
        """Add a task to a project"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    INSERT INTO tasks (project_id, title, description, status, assignee, due_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    task_data.get("project_id"),
                    task_data.get("title"),
                    task_data.get("description"),
                    task_data.get("status", "todo"),
                    task_data.get("assignee"),
                    task_data.get("due_date")
                ))
                task_id = cursor.lastrowid
                
            logger.info(f"Added new task: {task_data.get('title')} (ID: {task_id})")
            return task_id
            
        except Exception as e:
            logger.error(f"Error adding task: {e}")
            return None
    
    async def get_projects(self, status: str = None) -> List[Dict]:
        """Get projects"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                if status:
                    cursor = conn.execute("SELECT * FROM projects WHERE status = ?", (status,))
                else:
                    cursor = conn.execute("SELECT * FROM projects ORDER BY created_at DESC")
                
                projects = [dict(row) for row in cursor.fetchall()]
                return projects
                
        except Exception as e:
            logger.error(f"Error getting projects: {e}")
            return []
    
    async def get_tasks(self, project_id: int = None, status: str = None) -> List[Dict]:
        """Get tasks"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                query = "SELECT * FROM tasks"
                params = []
                
                conditions = []
                if project_id:
                    conditions.append("project_id = ?")
                    params.append(project_id)
                if status:
                    conditions.append("status = ?")
                    params.append(status)
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
                
                query += " ORDER BY created_at DESC"
                
                cursor = conn.execute(query, params)
                tasks = [dict(row) for row in cursor.fetchall()]
                return tasks
                
        except Exception as e:
            logger.error(f"Error getting tasks: {e}")
            return []

class PublicAPIConnector:
    """Free public APIs integration"""
    
    def __init__(self, integration_manager: IntegrationManager):
        self.manager = integration_manager
        self.config = integration_manager.config["public_apis"]
    
    async def get_spacex_launches(self, limit: int = 5) -> List[Dict]:
        """Get recent SpaceX launches"""
        try:
            url = f"{self.config['spacex']}/launches/latest"
            async with self.manager.session.get(url) as response:
                data = await response.json()
                return [data] if isinstance(data, dict) else data[:limit]
                
        except Exception as e:
            logger.error(f"Error getting SpaceX data: {e}")
            return []
    
    async def get_weather(self, location: str = "New York") -> Dict:
        """Get weather data"""
        try:
            url = f"{self.config['weather']}/{location}?format=j1"
            async with self.manager.session.get(url) as response:
                data = await response.json()
                return data
                
        except Exception as e:
            logger.error(f"Error getting weather data: {e}")
            return {}
    
    async def get_github_repos(self, user: str, limit: int = 5) -> List[Dict]:
        """Get GitHub repositories for a user"""
        try:
            url = f"{self.config['github']}/users/{user}/repos"
            params = {"per_page": limit, "sort": "updated"}
            
            async with self.manager.session.get(url, params=params) as response:
                data = await response.json()
                return data
                
        except Exception as e:
            logger.error(f"Error getting GitHub repos: {e}")
            return []

# Factory function for easy integration setup
async def create_integration_suite(config_path: str = None) -> Dict:
    """Create a complete integration suite"""
    manager = IntegrationManager(config_path)
    await manager.initialize()
    
    return {
        "manager": manager,
        "crm": CRMConnector(manager),
        "email": EmailConnector(manager),
        "finance": FinanceConnector(manager),
        "projects": ProjectManagementConnector(manager),
        "public_apis": PublicAPIConnector(manager)
    }
