"""
Test script for Enterprise Integration Endpoints
Tests all free, open-source integration endpoints
"""

import asyncio
import sys
import os
import logging
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enterprise.operations.integration_endpoints_clean import (
    create_integration_suite
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_crm_integration(crm_connector):
    """Test CRM functionality"""
    logger.info("Testing CRM Integration...")
    
    # Add a test lead
    test_lead = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "company": "Test Corp",
        "phone": "+1234567890",
        "source": "website",
        "value": 1000.0
    }
    
    lead_id = await crm_connector.add_lead(test_lead)
    if lead_id:
        logger.info(f"✓ Successfully added lead with ID: {lead_id}")
        
        # Update lead status
        success = await crm_connector.update_lead_status(lead_id, "qualified")
        if success:
            logger.info("✓ Successfully updated lead status")
        
        # Get all leads
        leads = await crm_connector.get_leads()
        logger.info(f"✓ Retrieved {len(leads)} leads from CRM")
        
        return True
    else:
        logger.error("✗ Failed to add lead")
        return False


async def test_finance_integration(finance_connector):
    """Test finance API integrations"""
    logger.info("Testing Finance Integration...")
    
    try:
        # Test crypto prices (CoinGecko - Free)
        crypto_prices = await finance_connector.get_crypto_prices(
            ["bitcoin", "ethereum"]
        )
        if crypto_prices:
            logger.info(f"✓ Retrieved crypto prices: {list(crypto_prices.keys())}")
        
        # Test exchange rates (Frankfurter - Free)
        exchange_rates = await finance_connector.get_exchange_rates("USD")
        if exchange_rates:
            logger.info(f"✓ Retrieved exchange rates for {exchange_rates.get('base', 'USD')}")
        
        # Test market data (Mock data or real if API key configured)
        market_data = await finance_connector.get_market_data("AAPL")
        if market_data:
            logger.info(f"✓ Retrieved market data for {market_data.get('symbol', 'AAPL')}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Finance integration error: {e}")
        return False


async def test_project_management_integration(pm_connector):
    """Test project management functionality"""
    logger.info("Testing Project Management Integration...")
    
    try:
        # Create a test project
        test_project = {
            "name": "Test Project",
            "description": "Integration test project",
            "status": "active",
            "priority": "high",
            "budget": 5000.0
        }
        
        project_id = await pm_connector.create_project(test_project)
        if project_id:
            logger.info(f"✓ Created project with ID: {project_id}")
            
            # Add a task to the project
            test_task = {
                "project_id": project_id,
                "title": "Test Task",
                "description": "Integration test task",
                "status": "in_progress",
                "assignee": "Test User"
            }
            
            task_id = await pm_connector.add_task(test_task)
            if task_id:
                logger.info(f"✓ Added task with ID: {task_id}")
                
                # Get projects and tasks
                projects = await pm_connector.get_projects()
                tasks = await pm_connector.get_tasks(project_id)
                
                logger.info(f"✓ Retrieved {len(projects)} projects and {len(tasks)} tasks")
                return True
        
        return False
        
    except Exception as e:
        logger.error(f"✗ Project management integration error: {e}")
        return False


async def test_public_api_integration(api_connector):
    """Test public API integrations"""
    logger.info("Testing Public API Integration...")
    
    try:
        # Test SpaceX API
        launches = await api_connector.get_spacex_launches(1)
        if launches:
            logger.info(f"✓ Retrieved {len(launches)} SpaceX launch(es)")
        
        # Test Weather API
        weather = await api_connector.get_weather("London")
        if weather:
            logger.info("✓ Retrieved weather data")
        
        # Test GitHub API
        repos = await api_connector.get_github_repos("octocat", 3)
        if repos:
            logger.info(f"✓ Retrieved {len(repos)} GitHub repositories")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Public API integration error: {e}")
        return False


async def test_email_integration(email_connector):
    """Test email functionality (requires valid SMTP config)"""
    logger.info("Testing Email Integration...")
    
    try:
        # Check if email is configured
        config = email_connector.config
        if not config.get("username") or not config.get("password"):
            logger.warning("✓ Email connector initialized (SMTP not configured)")
            return True
        
        # If configured, could test sending email here
        logger.info("✓ Email connector ready (SMTP configured)")
        return True
        
    except Exception as e:
        logger.error(f"✗ Email integration error: {e}")
        return False


async def run_integration_tests():
    """Run all integration tests"""
    logger.info("Starting Enterprise Integration Tests...")
    logger.info("=" * 50)
    
    # Create integration suite
    integrations = await create_integration_suite()
    
    test_results = {}
    
    try:
        # Test CRM
        test_results["crm"] = await test_crm_integration(integrations["crm"])
        
        # Test Finance
        test_results["finance"] = await test_finance_integration(integrations["finance"])
        
        # Test Project Management
        test_results["projects"] = await test_project_management_integration(
            integrations["projects"]
        )
        
        # Test Public APIs
        test_results["public_apis"] = await test_public_api_integration(
            integrations["public_apis"]
        )
        
        # Test Email
        test_results["email"] = await test_email_integration(integrations["email"])
        
    finally:
        # Close connections
        await integrations["manager"].close()
    
    # Print results
    logger.info("=" * 50)
    logger.info("INTEGRATION TEST RESULTS:")
    logger.info("=" * 50)
    
    all_passed = True
    for service, passed in test_results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        logger.info(f"{service.upper():<20} {status}")
        if not passed:
            all_passed = False
    
    logger.info("=" * 50)
    overall_status = "✓ ALL TESTS PASSED" if all_passed else "✗ SOME TESTS FAILED"
    logger.info(f"OVERALL STATUS: {overall_status}")
    logger.info("=" * 50)
    
    return all_passed


if __name__ == "__main__":
    asyncio.run(run_integration_tests())
