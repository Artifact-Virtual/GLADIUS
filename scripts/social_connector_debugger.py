#!/usr/bin/env python3
"""
Social Connector Debugger - Systematically tests and debugs all social media platform connectors.

This script:
1. Tests authentication for each platform
2. Validates API credentials
3. Tests basic API operations
4. Reports issues with specific error messages
5. Provides remediation steps

Run with: python scripts/social_connector_debugger.py
"""

import os
import sys
import asyncio
import logging
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add project paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
AUTOMATA_DIR = PROJECT_ROOT / "Artifact" / "deployment" / "automata"
GLADIUS_MAIN = Path("/home/adam/worxpace/gladius")

sys.path.insert(0, str(AUTOMATA_DIR))
sys.path.insert(0, str(PROJECT_ROOT / "Artifact" / "deployment"))

# Load .env from main gladius directory
from dotenv import load_dotenv
load_dotenv(GLADIUS_MAIN / ".env")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(PROJECT_ROOT / "logs" / "social_debugger.log", mode='a')
    ]
)
logger = logging.getLogger("SocialDebugger")


class SocialConnectorDebugger:
    """Debugger for all social media platform connectors."""
    
    def __init__(self):
        self.results: Dict[str, Dict[str, Any]] = {}
        self.issues: List[Dict[str, Any]] = []
        
    def _get_env_config(self) -> Dict[str, Any]:
        """Build config from environment variables."""
        return {
            'social_media': {
                'Twitter/X': {
                    'enabled': os.getenv('TWITTER_ENABLED', 'false').lower() == 'true',
                    'api_key': os.getenv('TWITTER_API_KEY', ''),
                    'api_secret': os.getenv('TWITTER_API_SECRET', ''),
                    'access_token': os.getenv('TWITTER_ACCESS_TOKEN', ''),
                    'access_token_secret': os.getenv('TWITTER_ACCESS_TOKEN_SECRET', ''),
                    'bearer_token': os.getenv('TWITTER_BEARER_TOKEN', ''),
                },
                'LinkedIn': {
                    'enabled': os.getenv('LINKEDIN_ENABLED', 'false').lower() == 'true',
                    'client_id': os.getenv('LINKEDIN_CLIENT_ID', ''),
                    'client_secret': os.getenv('LINKEDIN_CLIENT_SECRET', ''),
                    'access_token': os.getenv('LINKEDIN_ACCESS_TOKEN', ''),
                    'organization_id': os.getenv('LINKEDIN_ORGANIZATION_ID', ''),
                },
                'Facebook': {
                    'enabled': os.getenv('FACEBOOK_ENABLED', 'false').lower() == 'true',
                    'page_id': os.getenv('FACEBOOK_PAGE_ID', ''),
                    'access_token': os.getenv('FACEBOOK_ACCESS_TOKEN', ''),
                    'app_id': os.getenv('FACEBOOK_APP_ID', ''),
                    'app_secret': os.getenv('FACEBOOK_APP_SECRET', ''),
                },
                'Instagram': {
                    'enabled': os.getenv('INSTAGRAM_ENABLED', 'false').lower() == 'true',
                    'account_id': os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID', ''),
                    'access_token': os.getenv('INSTAGRAM_ACCESS_TOKEN', ''),
                },
                'YouTube': {
                    'enabled': os.getenv('YOUTUBE_ENABLED', 'false').lower() == 'true',
                    'client_id': os.getenv('YOUTUBE_CLIENT_ID', ''),
                    'client_secret': os.getenv('YOUTUBE_CLIENT_SECRET', ''),
                    'refresh_token': os.getenv('YOUTUBE_REFRESH_TOKEN', ''),
                    'channel_id': os.getenv('YOUTUBE_CHANNEL_ID', ''),
                },
            }
        }
    
    async def test_twitter(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test Twitter/X connector."""
        platform = "Twitter/X"
        result = {
            'platform': platform,
            'enabled': config.get('enabled', False),
            'auth_status': 'not_tested',
            'api_status': 'not_tested',
            'issues': [],
            'remediation': []
        }
        
        if not config.get('enabled'):
            result['auth_status'] = 'disabled'
            return result
        
        # Check required credentials
        bearer_token = config.get('bearer_token', '')
        if not bearer_token:
            result['issues'].append('Missing TWITTER_BEARER_TOKEN')
            result['remediation'].append('Set TWITTER_BEARER_TOKEN in .env')
            result['auth_status'] = 'missing_credentials'
            return result
        
        # URL decode if needed
        if '%' in bearer_token:
            import urllib.parse
            bearer_token = urllib.parse.unquote(bearer_token)
        
        try:
            from automata.social_media.platforms.twitter_connector import TwitterConnector
            
            connector = TwitterConnector({
                'bearer_token': bearer_token,
                'api_key': config.get('api_key'),
                'api_secret': config.get('api_secret'),
                'access_token': config.get('access_token'),
                'access_token_secret': config.get('access_token_secret'),
            })
            
            auth_success = await connector.authenticate()
            
            if auth_success:
                result['auth_status'] = 'success'
                result['username'] = connector.username
                result['user_id'] = connector.user_id
                
                # Test account info fetch
                try:
                    account_info = await connector.get_account_info()
                    result['api_status'] = 'success'
                    result['account_info'] = account_info
                except Exception as e:
                    result['api_status'] = 'partial'
                    result['issues'].append(f'Account info fetch failed: {e}')
            else:
                result['auth_status'] = 'failed'
                result['issues'].append('Authentication failed - check bearer token')
                result['remediation'].append('Regenerate bearer token from Twitter Developer Portal')
            
            if connector.session:
                await connector.session.close()
                
        except ImportError as e:
            result['issues'].append(f'Import error: {e}')
            result['remediation'].append('Install aiohttp: pip install aiohttp')
        except Exception as e:
            result['auth_status'] = 'error'
            result['issues'].append(f'Exception: {str(e)}')
            
        return result
    
    async def test_linkedin(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test LinkedIn connector."""
        platform = "LinkedIn"
        result = {
            'platform': platform,
            'enabled': config.get('enabled', False),
            'auth_status': 'not_tested',
            'api_status': 'not_tested',
            'issues': [],
            'remediation': []
        }
        
        if not config.get('enabled'):
            result['auth_status'] = 'disabled'
            return result
        
        access_token = config.get('access_token', '')
        if not access_token:
            result['issues'].append('Missing LINKEDIN_ACCESS_TOKEN')
            result['remediation'].append('Complete OAuth flow to get access token')
            result['auth_status'] = 'missing_credentials'
            return result
        
        try:
            from automata.social_media.platforms.linkedin_connector import LinkedInConnector
            
            connector = LinkedInConnector(config)
            auth_success = await connector.authenticate()
            
            if auth_success:
                result['auth_status'] = 'success'
                
                # Test connection
                try:
                    connection_ok = await connector.test_connection()
                    if connection_ok:
                        result['api_status'] = 'success'
                    else:
                        result['api_status'] = 'failed'
                        result['issues'].append('API connection test failed - token may be expired')
                        result['remediation'].append('LinkedIn access tokens expire in 60 days - refresh OAuth')
                except Exception as e:
                    result['api_status'] = 'error'
                    result['issues'].append(f'Connection test error: {e}')
            else:
                result['auth_status'] = 'failed'
                result['issues'].append('Authentication failed')
                
        except ImportError as e:
            result['issues'].append(f'Import error: {e}')
        except Exception as e:
            result['auth_status'] = 'error'
            result['issues'].append(f'Exception: {str(e)}')
            
        return result
    
    async def test_facebook(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test Facebook connector."""
        platform = "Facebook"
        result = {
            'platform': platform,
            'enabled': config.get('enabled', False),
            'auth_status': 'not_tested',
            'api_status': 'not_tested',
            'issues': [],
            'remediation': []
        }
        
        if not config.get('enabled'):
            result['auth_status'] = 'disabled'
            return result
        
        access_token = config.get('access_token', '')
        page_id = config.get('page_id', '')
        
        if not access_token:
            result['issues'].append('Missing FACEBOOK_ACCESS_TOKEN')
            result['remediation'].append('Generate page access token from Facebook Developer Portal')
            result['auth_status'] = 'missing_credentials'
            return result
            
        if not page_id:
            result['issues'].append('Missing FACEBOOK_PAGE_ID')
            result['remediation'].append('Set FACEBOOK_PAGE_ID in .env')
        
        try:
            from automata.social_media.platforms.facebook_connector import FacebookConnector
            
            connector = FacebookConnector(config)
            auth_success = await connector.authenticate()
            
            if auth_success:
                result['auth_status'] = 'success'
                
                # Test connection
                try:
                    connection_ok = await connector.test_connection()
                    if connection_ok:
                        result['api_status'] = 'success'
                    else:
                        result['api_status'] = 'failed'
                        result['issues'].append('Page access failed - check page token permissions')
                        result['remediation'].append('Ensure token has pages_read_engagement, pages_manage_posts permissions')
                except Exception as e:
                    result['api_status'] = 'error'
                    result['issues'].append(f'Connection test error: {e}')
            else:
                result['auth_status'] = 'failed'
                
        except ImportError as e:
            result['issues'].append(f'Import error: {e}')
        except Exception as e:
            result['auth_status'] = 'error'
            result['issues'].append(f'Exception: {str(e)}')
            
        return result
    
    async def test_instagram(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test Instagram connector."""
        platform = "Instagram"
        result = {
            'platform': platform,
            'enabled': config.get('enabled', False),
            'auth_status': 'not_tested',
            'api_status': 'not_tested',
            'issues': [],
            'remediation': []
        }
        
        if not config.get('enabled'):
            result['auth_status'] = 'disabled'
            return result
        
        access_token = config.get('access_token', '')
        account_id = config.get('account_id', '')
        
        if not access_token:
            result['issues'].append('Missing INSTAGRAM_ACCESS_TOKEN')
            result['auth_status'] = 'missing_credentials'
            return result
            
        if not account_id:
            result['issues'].append('Missing INSTAGRAM_BUSINESS_ACCOUNT_ID')
            result['remediation'].append('Get Instagram Business Account ID from Facebook Business Suite')
        
        try:
            from automata.social_media.platforms.instagram_connector import InstagramConnector
            
            connector = InstagramConnector(config)
            auth_success = await connector.authenticate()
            
            if auth_success:
                result['auth_status'] = 'success'
                
                try:
                    connection_ok = await connector.test_connection()
                    if connection_ok:
                        result['api_status'] = 'success'
                    else:
                        result['api_status'] = 'failed'
                        result['issues'].append('Instagram Graph API connection failed')
                        result['remediation'].append('Ensure Instagram account is linked to Facebook Business Page')
                except Exception as e:
                    result['api_status'] = 'error'
                    result['issues'].append(f'Connection test error: {e}')
            else:
                result['auth_status'] = 'failed'
                
        except ImportError as e:
            result['issues'].append(f'Import error: {e}')
        except Exception as e:
            result['auth_status'] = 'error'
            result['issues'].append(f'Exception: {str(e)}')
            
        return result
    
    async def test_youtube(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test YouTube connector."""
        platform = "YouTube"
        result = {
            'platform': platform,
            'enabled': config.get('enabled', False),
            'auth_status': 'not_tested',
            'api_status': 'not_tested',
            'issues': [],
            'remediation': []
        }
        
        if not config.get('enabled'):
            result['auth_status'] = 'disabled'
            return result
        
        refresh_token = config.get('refresh_token', '')
        client_id = config.get('client_id', '')
        
        if not refresh_token or not client_id:
            result['issues'].append('Missing YouTube OAuth credentials')
            result['remediation'].append('Complete OAuth flow at console.cloud.google.com')
            result['auth_status'] = 'missing_credentials'
            return result
        
        try:
            from automata.social_media.platforms.youtube_connector import YouTubeConnector
            
            connector = YouTubeConnector(config)
            auth_success = await connector.authenticate()
            
            if auth_success:
                result['auth_status'] = 'success'
                
                try:
                    connection_ok = await connector.test_connection()
                    if connection_ok:
                        result['api_status'] = 'success'
                    else:
                        result['api_status'] = 'failed'
                except Exception as e:
                    result['api_status'] = 'error'
                    result['issues'].append(f'Connection test error: {e}')
            else:
                result['auth_status'] = 'failed'
                result['issues'].append('YouTube OAuth refresh failed')
                
        except ImportError as e:
            result['issues'].append(f'Import error: {e}')
        except Exception as e:
            result['auth_status'] = 'error'
            result['issues'].append(f'Exception: {str(e)}')
            
        return result
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run tests on all configured platforms."""
        config = self._get_env_config()
        social_config = config['social_media']
        
        logger.info("=" * 60)
        logger.info("SOCIAL CONNECTOR DEBUGGER - Starting diagnostics")
        logger.info("=" * 60)
        
        # Test each platform
        tests = [
            ('Twitter/X', self.test_twitter(social_config['Twitter/X'])),
            ('LinkedIn', self.test_linkedin(social_config['LinkedIn'])),
            ('Facebook', self.test_facebook(social_config['Facebook'])),
            ('Instagram', self.test_instagram(social_config['Instagram'])),
            ('YouTube', self.test_youtube(social_config['YouTube'])),
        ]
        
        for platform, test_coro in tests:
            try:
                result = await test_coro
                self.results[platform] = result
                
                status_icon = "✅" if result['auth_status'] == 'success' else "❌" if result['auth_status'] in ['failed', 'error'] else "⚠️"
                logger.info(f"{status_icon} {platform}: auth={result['auth_status']}, api={result['api_status']}")
                
                if result['issues']:
                    for issue in result['issues']:
                        logger.warning(f"   Issue: {issue}")
                        self.issues.append({'platform': platform, 'issue': issue})
                        
            except Exception as e:
                logger.error(f"❌ {platform}: Test failed with exception: {e}")
                self.results[platform] = {
                    'platform': platform,
                    'auth_status': 'error',
                    'issues': [str(e)]
                }
        
        return self._generate_report()
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate summary report."""
        total = len(self.results)
        working = sum(1 for r in self.results.values() if r.get('auth_status') == 'success')
        disabled = sum(1 for r in self.results.values() if r.get('auth_status') == 'disabled')
        failed = total - working - disabled
        
        report = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'summary': {
                'total_platforms': total,
                'working': working,
                'disabled': disabled,
                'failed': failed,
            },
            'platforms': self.results,
            'all_issues': self.issues,
        }
        
        logger.info("=" * 60)
        logger.info(f"SUMMARY: {working}/{total} platforms working, {disabled} disabled, {failed} failed")
        logger.info("=" * 60)
        
        return report


async def main():
    """Main entry point."""
    # Ensure logs directory exists
    logs_dir = PROJECT_ROOT / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    debugger = SocialConnectorDebugger()
    report = await debugger.run_all_tests()
    
    # Save report
    report_file = logs_dir / "social_debug_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    logger.info(f"Report saved to: {report_file}")
    
    # Print remediation steps if issues found
    if report['all_issues']:
        print("\n" + "=" * 60)
        print("REMEDIATION STEPS REQUIRED:")
        print("=" * 60)
        
        for platform, result in report['platforms'].items():
            if result.get('remediation'):
                print(f"\n{platform}:")
                for step in result['remediation']:
                    print(f"  → {step}")
    
    return report


if __name__ == "__main__":
    report = asyncio.run(main())
    
    # Exit with error code if any platforms failed
    if report['summary']['failed'] > 0:
        sys.exit(1)
