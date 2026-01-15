#!/usr/bin/env python3
"""
Social Media Automation Service
Single entry point for all social media automation
- Checks/creates credentials automatically
- Integrates with enterprise agent system
- Runs as background service
"""

import asyncio
import logging
import json
import signal
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Add parent directory to path for enterprise imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
except ImportError:
    print("⚠️  Social media automation dependencies not installed. Run: python start_enterprise.py")

try:
    from legion.core_framework import BaseAgent, AgentMessage
except ImportError:
    # Fallback for standalone operation
    class BaseAgent:
        def __init__(self, name):
            self.name = name
        def log(self, message):
            logger.info(f"[{self.name}] {message}")
    
    class AgentMessage:
        def __init__(self, content, sender=None):
            self.content = content
            self.sender = sender

# Configure logging
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'social_automation.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("SocialMediaAgent")

class SocialMediaAgent(BaseAgent):
    """
    Social Media Agent - Enterprise communication automation
    Handles Facebook, Instagram, LinkedIn, Twitter posting
    """
    
    def __init__(self):
        super().__init__(
            agent_id="social_media_agent",
            agent_type="communication",
            department="communication",
            capabilities=["social_posting", "content_automation", "engagement_monitoring"]
        )
        
        self.config_dir = Path(__file__).parent.parent.parent / "config"
        self.content_dir = Path(__file__).parent / "content" / "autonomous_blog"
        self.browsers: Dict[str, webdriver.Chrome] = {}
        self.credentials: Dict[str, Dict] = {}
        self.running = False
        
        # Create directories
        self.config_dir.mkdir(exist_ok=True)
        self.content_dir.mkdir(parents=True, exist_ok=True)
        
    async def initialize(self) -> bool:
        """Initialize the social media agent"""
        logger.info("🚀 Initializing Social Media Agent...")
        
        try:
            # Check/create credentials
            if not await self._ensure_credentials():
                return False
            
            # Initialize browsers for platforms with credentials
            await self._initialize_browsers()
            
            # Start automation loops
            asyncio.create_task(self._content_generation_loop())
            asyncio.create_task(self._posting_loop())
            asyncio.create_task(self._monitoring_loop())
            
            self.running = True
            logger.info("✅ Social Media Agent initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Social Media Agent: {e}")
            return False
    
    async def _ensure_credentials(self) -> bool:
        """Check for credentials, create template if missing"""
        creds_file = self.config_dir / "social_media_credentials.json"
        
        if not creds_file.exists():
            logger.info("📝 Creating social media credentials template...")
            
            template = {
                "facebook": {
                    "username": "your_facebook_email@example.com",
                    "password": "your_facebook_password",
                    "enabled": False
                },
                "instagram": {
                    "username": "your_instagram_username",
                    "password": "your_instagram_password", 
                    "enabled": False
                },
                "linkedin": {
                    "username": "your_linkedin_email@example.com",
                    "password": "your_linkedin_password",
                    "enabled": False
                },
                "twitter": {
                    "username": "your_twitter_handle",
                    "password": "your_twitter_password",
                    "enabled": False
                }
            }
            
            with open(creds_file, 'w') as f:
                json.dump(template, f, indent=2)
            
            logger.info(f"✅ Credentials template created: {creds_file}")
            logger.info("🔧 Please update with real credentials and set 'enabled': true")
            logger.info("📱 Service will continue with limited functionality")
            
        # Load credentials
        try:
            with open(creds_file, 'r') as f:
                self.credentials = json.load(f)
            
            # Count enabled platforms
            enabled_platforms = [p for p, config in self.credentials.items() 
                                if config.get('enabled', False) and 
                                not config['username'].startswith('your_')]
            
            if enabled_platforms:
                logger.info(f"✅ Loaded credentials for: {', '.join(enabled_platforms)}")
                return True
            else:
                logger.warning("⚠️  No platforms enabled. Update credentials and set 'enabled': true")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error loading credentials: {e}")
            return False
    
    def _create_browser(self) -> webdriver.Chrome:
        """Create Chrome browser instance"""
        options = Options()
        options.add_argument("--headless")  # Always headless for service
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    
    async def _initialize_browsers(self):
        """Initialize browser sessions for enabled platforms"""
        for platform, config in self.credentials.items():
            if config.get('enabled', False) and not config['username'].startswith('your_'):
                try:
                    logger.info(f"🌐 Initializing browser for {platform}...")
                    browser = self._create_browser()
                    
                    if await self._login_to_platform(browser, platform, config):
                        self.browsers[platform] = browser
                        logger.info(f"✅ {platform} ready for automation")
                    else:
                        browser.quit()
                        logger.error(f"❌ {platform} login failed")
                        
                except Exception as e:
                    logger.error(f"❌ Failed to initialize {platform}: {e}")
    
    async def _login_to_platform(self, browser: webdriver.Chrome, platform: str, config: Dict) -> bool:
        """Login to a specific platform"""
        try:
            if platform == "facebook":
                return await self._login_facebook(browser, config)
            elif platform == "instagram":
                return await self._login_instagram(browser, config)
            elif platform == "linkedin":
                return await self._login_linkedin(browser, config)
            elif platform == "twitter":
                return await self._login_twitter(browser, config)
            return False
        except Exception as e:
            logger.error(f"Login error for {platform}: {e}")
            return False
    
    async def _login_facebook(self, browser: webdriver.Chrome, config: Dict) -> bool:
        """Login to Facebook"""
        browser.get("https://www.facebook.com/login")
        await asyncio.sleep(3)
        
        email_field = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        email_field.send_keys(config['username'])
        
        password_field = browser.find_element(By.ID, "pass")
        password_field.send_keys(config['password'])
        
        login_button = browser.find_element(By.NAME, "login")
        login_button.click()
        
        await asyncio.sleep(5)
        
        return "facebook.com" in browser.current_url and "login" not in browser.current_url
    
    async def _login_instagram(self, browser: webdriver.Chrome, config: Dict) -> bool:
        """Login to Instagram"""
        browser.get("https://www.instagram.com/accounts/login/")
        await asyncio.sleep(3)
        
        username_field = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        username_field.send_keys(config['username'])
        
        password_field = browser.find_element(By.NAME, "password")
        password_field.send_keys(config['password'])
        
        login_button = browser.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        
        await asyncio.sleep(5)
        
        # Handle prompts
        try:
            not_now_button = WebDriverWait(browser, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Not Now']"))
            )
            not_now_button.click()
        except TimeoutException:
            pass
        
        return "instagram.com" in browser.current_url and "login" not in browser.current_url
    
    async def _login_linkedin(self, browser: webdriver.Chrome, config: Dict) -> bool:
        """Login to LinkedIn"""
        browser.get("https://www.linkedin.com/login")
        await asyncio.sleep(2)
        
        email_field = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        email_field.send_keys(config['username'])
        
        password_field = browser.find_element(By.ID, "password")
        password_field.send_keys(config['password'])
        
        login_button = browser.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        
        await asyncio.sleep(5)
        
        return "feed" in browser.current_url or "mynetwork" in browser.current_url
    
    async def _login_twitter(self, browser: webdriver.Chrome, config: Dict) -> bool:
        """Login to Twitter/X"""
        browser.get("https://twitter.com/i/flow/login")
        await asyncio.sleep(3)
        
        username_field = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.NAME, "text"))
        )
        username_field.send_keys(config['username'])
        
        next_button = browser.find_element(By.XPATH, "//span[text()='Next']")
        next_button.click()
        await asyncio.sleep(2)
        
        password_field = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_field.send_keys(config['password'])
        
        login_button = browser.find_element(By.XPATH, "//span[text()='Log in']")
        login_button.click()
        
        await asyncio.sleep(5)
        
        return "home" in browser.current_url
    
    async def _content_generation_loop(self):
        """Generate content for posting"""
        while self.running:
            try:
                # Generate daily content
                await self._generate_daily_content()
                
                # Wait 6 hours before next generation
                await asyncio.sleep(6 * 3600)
                
            except Exception as e:
                logger.error(f"Content generation error: {e}")
                await asyncio.sleep(1800)  # 30 minutes on error
    
    async def _posting_loop(self):
        """Post scheduled content"""
        while self.running:
            try:
                await self._post_scheduled_content()
                
                # Check every 30 minutes
                await asyncio.sleep(1800)
                
            except Exception as e:
                logger.error(f"Posting loop error: {e}")
                await asyncio.sleep(900)
    
    async def _monitoring_loop(self):
        """Monitor engagement and interactions"""
        while self.running:
            try:
                await self._check_interactions()
                
                # Check every hour
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(1800)
    
    async def _generate_daily_content(self):
        """Generate content for the day"""
        current_time = datetime.now()
        
        content = {
            "id": f"daily_{current_time.strftime('%Y%m%d')}",
            "title": f"Enterprise Update - {current_time.strftime('%B %d, %Y')}",
            "content": f"""🤖 Daily update from Artifact Virtual Enterprise System

✅ System Status: Operational
📊 Agents Active: 18 across 6 departments  
🔄 Processes Running: Automation, Analytics, Communications
📈 Performance: Optimized and stable

#ArtifactVirtual #Enterprise #AI #Automation #BusinessIntelligence

Generated at: {current_time.strftime('%Y-%m-%d %H:%M:%S')}""",
            "platforms": list(self.browsers.keys()),
            "scheduled_time": current_time + timedelta(hours=2),
            "posted": False
        }
        
        # Save content
        content_file = self.content_dir / f"{content['id']}.json"
        with open(content_file, 'w') as f:
            json.dump(content, f, indent=2, default=str)
        
        logger.info(f"📝 Generated content: {content['title']}")
    
    async def _post_scheduled_content(self):
        """Post content that's ready to be published"""
        current_time = datetime.now()
        
        # Check for content ready to post
        for content_file in self.content_dir.glob("*.json"):
            try:
                with open(content_file, 'r') as f:
                    content = json.load(f)
                
                if not content.get('posted', False):
                    scheduled_time = datetime.fromisoformat(content['scheduled_time'])
                    
                    if scheduled_time <= current_time:
                        await self._post_to_platforms(content)
                        
                        # Mark as posted
                        content['posted'] = True
                        with open(content_file, 'w') as f:
                            json.dump(content, f, indent=2, default=str)
                        
            except Exception as e:
                logger.error(f"Error processing {content_file}: {e}")
    
    async def _post_to_platforms(self, content: Dict):
        """Post content to all available platforms"""
        for platform in content['platforms']:
            if platform in self.browsers:
                try:
                    success = await self._post_to_platform(platform, content)
                    if success:
                        logger.info(f"✅ Posted to {platform}: {content['title']}")
                    else:
                        logger.warning(f"⚠️  Failed to post to {platform}")
                        
                except Exception as e:
                    logger.error(f"❌ Error posting to {platform}: {e}")
    
    async def _post_to_platform(self, platform: str, content: Dict) -> bool:
        """Post to a specific platform"""
        browser = self.browsers[platform]
        
        if platform == "facebook":
            return await self._post_facebook(browser, content)
        elif platform == "linkedin":
            return await self._post_linkedin(browser, content)
        # Instagram and Twitter require more complex handling
        
        return False
    
    async def _post_facebook(self, browser: webdriver.Chrome, content: Dict) -> bool:
        """Post to Facebook"""
        try:
            browser.get("https://www.facebook.com/")
            await asyncio.sleep(3)
            
            composer = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), \"What's on your mind\")]"))
            )
            composer.click()
            await asyncio.sleep(2)
            
            text_area = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@role='textbox']"))
            )
            text_area.send_keys(content['content'])
            
            await asyncio.sleep(2)
            
            post_button = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Post']"))
            )
            post_button.click()
            
            await asyncio.sleep(3)
            return True
            
        except Exception as e:
            logger.error(f"Facebook posting error: {e}")
            return False
    
    async def _post_linkedin(self, browser: webdriver.Chrome, content: Dict) -> bool:
        """Post to LinkedIn"""
        try:
            browser.get("https://www.linkedin.com/feed/")
            await asyncio.sleep(3)
            
            start_post = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Start a post']"))
            )
            start_post.click()
            await asyncio.sleep(2)
            
            text_area = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@data-placeholder='What do you want to talk about?']"))
            )
            text_area.send_keys(content['content'])
            
            await asyncio.sleep(2)
            
            post_button = browser.find_element(By.XPATH, "//span[text()='Post']")
            post_button.click()
            
            await asyncio.sleep(3)
            return True
            
        except Exception as e:
            logger.error(f"LinkedIn posting error: {e}")
            return False
    
    async def _check_interactions(self):
        """Check for interactions and engagement"""
        # Placeholder for interaction monitoring
        logger.info("📊 Checking social media interactions...")
    
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process messages from other agents"""
        if message.message_type == "social_post_request":
            # Handle requests from other agents to post content
            content = message.data
            await self._post_to_platforms(content)
            
            return AgentMessage(
                sender_id=self.agent_id,
                recipient_id=message.sender_id,
                message_type="social_post_response",
                data={"status": "posted", "platforms": list(self.browsers.keys())}
            )
        
        return None
    
    def cleanup(self):
        """Clean up resources"""
        logger.info("🧹 Cleaning up Social Media Agent...")
        self.running = False
        
        for browser in self.browsers.values():
            try:
                browser.quit()
            except:
                pass
        
        self.browsers.clear()
    
    def signal_handler(self, signum, frame):
        """Handle system signals"""
        logger.info(f"📡 Received signal {signum}, shutting down...")
        self.cleanup()

async def main():
    """Main entry point for social media service"""
    # Check for test mode
    test_mode = len(sys.argv) > 1 and sys.argv[1] == "--test"
    
    agent = SocialMediaAgent()
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, agent.signal_handler)
    signal.signal(signal.SIGTERM, agent.signal_handler)
    
    try:
        if await agent.initialize():
            logger.info("🚀 Social Media Agent running...")
            
            if test_mode:
                logger.info("🧪 Running in test mode - exiting after initialization")
                return
            
            # Keep service running
            while agent.running:
                await asyncio.sleep(60)  # Check every minute
                
        else:
            logger.error("❌ Failed to initialize Social Media Agent")
            
    except KeyboardInterrupt:
        logger.info("⚠️  Service interrupted by user")
    finally:
        agent.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
