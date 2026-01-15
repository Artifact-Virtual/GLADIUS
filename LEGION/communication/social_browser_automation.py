#!/usr/bin/env python3
"""
Social Media Browser Automation System
Handles LinkedIn, Twitter, and Discord posting via browser automation
Uses headless browsing for autonomous posting and intelligent interaction
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import time

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
except ImportError:
    print("Selenium not installed. Run: pip install selenium")

logger = logging.getLogger("SocialMediaBrowser")

@dataclass
class SocialMediaAccount:
    """Social media account configuration"""
    platform: str
    username: str
    password: str
    profile_url: str
    last_login: Optional[datetime] = None
    session_valid: bool = False
    post_count_today: int = 0

@dataclass
class PostContent:
    """Content to be posted"""
    id: str
    title: str
    content: str
    platforms: List[str]
    hashtags: List[str]
    scheduled_time: datetime
    posted_platforms: List[str] = field(default_factory=list)
    failed_platforms: List[str] = field(default_factory=list)

class SocialMediaBrowserManager:
    """
    Browser-based social media automation system
    Handles intelligent posting and interaction across platforms
    """
    
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.accounts: Dict[str, SocialMediaAccount] = {}
        self.browsers: Dict[str, webdriver.Chrome] = {}
        self.content_queue: List[PostContent] = []
        
        # Load credentials from config
        self._load_credentials()
        
    def _load_credentials(self):
        """Load social media credentials from config"""
        try:
            creds_file = self.config_dir / "social_media_credentials.json"
            if creds_file.exists():
                with open(creds_file, 'r') as f:
                    creds = json.load(f)
                    
                for platform, config in creds.items():
                    self.accounts[platform] = SocialMediaAccount(
                        platform=platform,
                        username=config['username'],
                        password=config['password'],
                        profile_url=config.get('profile_url', '')
                    )
                    
            else:
                # Create template credentials file
                template = {
                    "linkedin": {
                        "username": "your_linkedin_email@example.com",
                        "password": "your_linkedin_password",
                        "profile_url": "https://linkedin.com/in/yourprofile"
                    },
                    "twitter": {
                        "username": "your_twitter_handle",
                        "password": "your_twitter_password",
                        "profile_url": "https://twitter.com/yourhandle"
                    },
                    "facebook": {
                        "username": "your_facebook_email@example.com",
                        "password": "your_facebook_password",
                        "profile_url": "https://facebook.com/yourprofile"
                    },
                    "instagram": {
                        "username": "your_instagram_username",
                        "password": "your_instagram_password",
                        "profile_url": "https://instagram.com/yourusername"
                    },
                    "discord": {
                        "username": "your_discord_email@example.com",
                        "password": "your_discord_password",
                        "profile_url": ""
                    }
                }
                
                with open(creds_file, 'w') as f:
                    json.dump(template, f, indent=2)
                    
                logger.info(f"Created template credentials file: {creds_file}")
                logger.info("Please update with your actual credentials")
                
        except Exception as e:
            logger.error(f"Error loading credentials: {e}")
    
    def _create_browser(self, headless: bool = True) -> webdriver.Chrome:
        """Create a new Chrome browser instance"""
        options = Options()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        driver = webdriver.Chrome(options=options)
        return driver
    
    async def initialize_browsers(self):
        """Initialize browser sessions for all platforms"""
        for platform in self.accounts.keys():
            try:
                browser = self._create_browser(headless=True)
                self.browsers[platform] = browser
                await self._login_to_platform(platform)
                logger.info(f"Initialized browser for {platform}")
            except Exception as e:
                logger.error(f"Failed to initialize browser for {platform}: {e}")
    
    async def _login_to_platform(self, platform: str):
        """Login to a specific social media platform"""
        if platform not in self.accounts or platform not in self.browsers:
            return False
            
        account = self.accounts[platform]
        browser = self.browsers[platform]
        
        try:
            if platform == "linkedin":
                return await self._login_linkedin(browser, account)
            elif platform == "twitter":
                return await self._login_twitter(browser, account)
            elif platform == "discord":
                return await self._login_discord(browser, account)
            elif platform == "instagram":
                return await self._login_instagram(browser, account)
            elif platform == "facebook":
                return await self._login_facebook(browser, account)
                
        except Exception as e:
            logger.error(f"Login failed for {platform}: {e}")
            return False
    
    async def _login_linkedin(self, browser: webdriver.Chrome, account: SocialMediaAccount) -> bool:
        """Login to LinkedIn"""
        try:
            browser.get("https://www.linkedin.com/login")
            await asyncio.sleep(2)
            
            # Find and fill email
            email_field = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field.send_keys(account.username)
            
            # Find and fill password
            password_field = browser.find_element(By.ID, "password")
            password_field.send_keys(account.password)
            
            # Click login button
            login_button = browser.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # Wait for redirect
            await asyncio.sleep(5)
            
            # Check if login successful
            if "feed" in browser.current_url or "mynetwork" in browser.current_url:
                account.session_valid = True
                account.last_login = datetime.now()
                logger.info("LinkedIn login successful")
                return True
            else:
                logger.error("LinkedIn login failed - no redirect to feed")
                return False
                
        except Exception as e:
            logger.error(f"LinkedIn login error: {e}")
            return False
    
    async def _login_twitter(self, browser: webdriver.Chrome, account: SocialMediaAccount) -> bool:
        """Login to Twitter/X"""
        try:
            browser.get("https://twitter.com/i/flow/login")
            await asyncio.sleep(3)
            
            # Find username field
            username_field = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.NAME, "text"))
            )
            username_field.send_keys(account.username)
            
            # Click next
            next_button = browser.find_element(By.XPATH, "//span[text()='Next']")
            next_button.click()
            await asyncio.sleep(2)
            
            # Find password field
            password_field = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            password_field.send_keys(account.password)
            
            # Click login
            login_button = browser.find_element(By.XPATH, "//span[text()='Log in']")
            login_button.click()
            
            await asyncio.sleep(5)
            
            # Check if login successful
            if "home" in browser.current_url:
                account.session_valid = True
                account.last_login = datetime.now()
                logger.info("Twitter login successful")
                return True
            else:
                logger.error("Twitter login failed")
                return False
                
        except Exception as e:
            logger.error(f"Twitter login error: {e}")
            return False
    
    async def _login_discord(self, browser: webdriver.Chrome, account: SocialMediaAccount) -> bool:
        """Login to Discord (for future integration)"""
        try:
            browser.get("https://discord.com/login")
            await asyncio.sleep(2)
            
            # Find email field
            email_field = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            email_field.send_keys(account.username)
            
            # Find password field
            password_field = browser.find_element(By.NAME, "password")
            password_field.send_keys(account.password)
            
            # Click login
            login_button = browser.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            await asyncio.sleep(5)
            
            # Check if login successful
            if "channels" in browser.current_url:
                account.session_valid = True
                account.last_login = datetime.now()
                logger.info("Discord login successful")
                return True
            else:
                logger.error("Discord login failed")
                return False
                
        except Exception as e:
            logger.error(f"Discord login error: {e}")
            return False
    
    async def _login_instagram(self, browser, account: SocialMediaAccount) -> bool:
        """Login to Instagram"""
        try:
            browser.get("https://www.instagram.com/accounts/login/")
            await asyncio.sleep(3)
            
            # Find username field
            username_field = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_field.send_keys(account.username)
            
            # Find password field
            password_field = browser.find_element(By.NAME, "password")
            password_field.send_keys(account.password)
            
            # Click login button
            login_button = browser.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            await asyncio.sleep(5)
            
            # Handle potential "Save Login Info" prompt
            try:
                not_now_button = WebDriverWait(browser, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[text()='Not Now']"))
                )
                not_now_button.click()
                await asyncio.sleep(2)
            except TimeoutException:
                pass  # No prompt appeared
            
            # Handle notifications prompt
            try:
                not_now_button = WebDriverWait(browser, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[text()='Not Now']"))
                )
                not_now_button.click()
                await asyncio.sleep(2)
            except TimeoutException:
                pass  # No prompt appeared
            
            # Check if login successful
            if "instagram.com" in browser.current_url and "login" not in browser.current_url:
                account.session_valid = True
                account.last_login = datetime.now()
                logger.info("Instagram login successful")
                return True
            else:
                logger.error("Instagram login failed")
                return False
                
        except Exception as e:
            logger.error(f"Instagram login error: {e}")
            return False
    
    async def _login_facebook(self, browser, account: SocialMediaAccount) -> bool:
        """Login to Facebook"""
        try:
            browser.get("https://www.facebook.com/login")
            await asyncio.sleep(3)
            
            # Find email field
            email_field = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            email_field.send_keys(account.username)
            
            # Find password field
            password_field = browser.find_element(By.ID, "pass")
            password_field.send_keys(account.password)
            
            # Click login button
            login_button = browser.find_element(By.NAME, "login")
            login_button.click()
            
            await asyncio.sleep(5)
            
            # Check if login successful
            if "facebook.com" in browser.current_url and "login" not in browser.current_url:
                account.session_valid = True
                account.last_login = datetime.now()
                logger.info("Facebook login successful")
                return True
            else:
                logger.error("Facebook login failed")
                return False
                
        except Exception as e:
            logger.error(f"Facebook login error: {e}")
            return False
    
    async def post_content(self, content: PostContent):
        """Post content to specified platforms"""
        for platform in content.platforms:
            if platform in self.browsers and self.accounts[platform].session_valid:
                try:
                    success = await self._post_to_platform(platform, content)
                    if success:
                        content.posted_platforms.append(platform)
                        self.accounts[platform].post_count_today += 1
                        logger.info(f"Posted to {platform}: {content.title}")
                    else:
                        content.failed_platforms.append(platform)
                        logger.error(f"Failed to post to {platform}: {content.title}")
                        
                except Exception as e:
                    logger.error(f"Error posting to {platform}: {e}")
                    content.failed_platforms.append(platform)
    
    async def _post_to_platform(self, platform: str, content: PostContent) -> bool:
        """Post to a specific platform"""
        if platform == "linkedin":
            return await self._post_linkedin(content)
        elif platform == "twitter":
            return await self._post_twitter(content)
        elif platform == "discord":
            return await self._post_discord(content)
        elif platform == "instagram":
            return await self._post_instagram(content)
        elif platform == "facebook":
            return await self._post_facebook(content)
        return False
    
    async def _post_linkedin(self, content: PostContent) -> bool:
        """Post to LinkedIn"""
        try:
            browser = self.browsers["linkedin"]
            browser.get("https://www.linkedin.com/feed/")
            await asyncio.sleep(3)
            
            # Click "Start a post" button
            start_post = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Start a post']"))
            )
            start_post.click()
            await asyncio.sleep(2)
            
            # Find text area and post content
            text_area = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@data-placeholder='What do you want to talk about?']"))
            )
            
            # Format content with hashtags
            full_content = f"{content.content}\n\n{' '.join(['#' + tag for tag in content.hashtags])}"
            text_area.send_keys(full_content)
            
            await asyncio.sleep(2)
            
            # Click post button
            post_button = browser.find_element(By.XPATH, "//span[text()='Post']")
            post_button.click()
            
            await asyncio.sleep(3)
            return True
            
        except Exception as e:
            logger.error(f"LinkedIn posting error: {e}")
            return False
    
    async def _post_twitter(self, content: PostContent) -> bool:
        """Post to Twitter"""
        try:
            browser = self.browsers["twitter"]
            browser.get("https://twitter.com/home")
            await asyncio.sleep(3)
            
            # Find tweet compose area
            compose_area = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@data-testid='tweetTextarea_0']"))
            )
            
            # Format content for Twitter (truncate if needed)
            tweet_content = content.content
            hashtags = ' '.join(['#' + tag for tag in content.hashtags])
            
            if len(tweet_content + hashtags) > 280:
                available_space = 280 - len(hashtags) - 5  # 5 for spacing
                tweet_content = tweet_content[:available_space] + "..."
            
            full_tweet = f"{tweet_content}\n\n{hashtags}"
            compose_area.send_keys(full_tweet)
            
            await asyncio.sleep(2)
            
            # Click tweet button
            tweet_button = browser.find_element(By.XPATH, "//div[@data-testid='tweetButtonInline']")
            tweet_button.click()
            
            await asyncio.sleep(3)
            return True
            
        except Exception as e:
            logger.error(f"Twitter posting error: {e}")
            return False
    
    async def _post_discord(self, content: PostContent) -> bool:
        """Post to Discord (placeholder for future integration)"""
        logger.info("Discord posting not yet implemented")
        return False
    
    async def _post_instagram(self, content: PostContent) -> bool:
        """Post to Instagram"""
        try:
            browser = self.browsers["instagram"]
            browser.get("https://www.instagram.com/")
            await asyncio.sleep(3)
            
            # Click "New post" button (plus icon)
            try:
                new_post_button = WebDriverWait(browser, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@role='menuitem']//span[text()='Create']"))
                )
                new_post_button.click()
                await asyncio.sleep(2)
                
                # For Instagram, we'll need to handle image upload
                # For now, we'll skip actual posting and log the intent
                logger.info(f"Instagram posting prepared for: {content.title}")
                logger.info("Note: Instagram requires image/video content. Text-only posts not supported.")
                return False  # Return False since we can't actually post text-only content
                
            except TimeoutException:
                # Try alternative selector for mobile view
                try:
                    new_post_button = browser.find_element(By.XPATH, "//a[@href='/create/select/']")
                    new_post_button.click()
                    await asyncio.sleep(2)
                    logger.info("Instagram posting interface accessed")
                    return False  # Still can't post without media
                except NoSuchElementException:
                    logger.error("Could not find Instagram new post button")
                    return False
            
        except Exception as e:
            logger.error(f"Instagram posting error: {e}")
            return False
    
    async def _post_facebook(self, content: PostContent) -> bool:
        """Post to Facebook"""
        try:
            browser = self.browsers["facebook"]
            browser.get("https://www.facebook.com/")
            await asyncio.sleep(3)
            
            # Find the "What's on your mind?" text area
            try:
                # Try the main composer
                composer = WebDriverWait(browser, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), \"What's on your mind\")]"))
                )
                composer.click()
                await asyncio.sleep(2)
                
                # Find the actual text input area
                text_area = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@role='textbox']"))
                )
                
                # Format content with hashtags
                full_content = f"{content.content}\n\n{' '.join(['#' + tag for tag in content.hashtags])}"
                text_area.send_keys(full_content)
                
                await asyncio.sleep(2)
                
                # Find and click post button
                post_button = WebDriverWait(browser, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='Post']"))
                )
                post_button.click()
                
                await asyncio.sleep(3)
                logger.info(f"Posted to Facebook: {content.title}")
                return True
                
            except TimeoutException:
                # Try alternative approach for different Facebook layout
                try:
                    # Look for different composer selectors
                    composer = browser.find_element(By.XPATH, "//div[@data-testid='status-attachment-mentions-input']")
                    composer.click()
                    await asyncio.sleep(2)
                    
                    full_content = f"{content.content}\n\n{' '.join(['#' + tag for tag in content.hashtags])}"
                    composer.send_keys(full_content)
                    
                    # Find post button
                    post_button = browser.find_element(By.XPATH, "//span[text()='Post']")
                    post_button.click()
                    
                    await asyncio.sleep(3)
                    return True
                    
                except NoSuchElementException:
                    logger.error("Could not find Facebook composer")
                    return False
            
        except Exception as e:
            logger.error(f"Facebook posting error: {e}")
            return False
    
    async def monitor_interactions(self):
        """Monitor and respond to interactions intelligently"""
        for platform in self.browsers.keys():
            if self.accounts[platform].session_valid:
                try:
                    await self._check_platform_interactions(platform)
                except Exception as e:
                    logger.error(f"Error monitoring {platform}: {e}")
    
    async def _check_platform_interactions(self, platform: str):
        """Check for interactions on a specific platform"""
        if platform == "linkedin":
            await self._check_linkedin_interactions()
        elif platform == "twitter":
            await self._check_twitter_interactions()
    
    async def _check_linkedin_interactions(self):
        """Check LinkedIn for new notifications and interactions"""
        try:
            browser = self.browsers["linkedin"]
            browser.get("https://www.linkedin.com/notifications/")
            await asyncio.sleep(3)
            
            # Look for unread notifications
            notifications = browser.find_elements(By.CLASS_NAME, "notification-card")
            
            for notification in notifications[:5]:  # Check top 5
                # Analyze notification type and respond appropriately
                # This would include intelligent comment responses, connection acceptance, etc.
                pass
                
        except Exception as e:
            logger.error(f"LinkedIn interaction check error: {e}")
    
    async def _check_twitter_interactions(self):
        """Check Twitter for mentions and interactions"""
        try:
            browser = self.browsers["twitter"]
            browser.get("https://twitter.com/notifications")
            await asyncio.sleep(3)
            
            # Check for mentions and replies
            mentions = browser.find_elements(By.XPATH, "//div[@data-testid='cellInnerDiv']")
            
            # Process recent mentions for potential responses
            for mention in mentions[:3]:  # Check top 3
                # Intelligent response logic would go here
                pass
                
        except Exception as e:
            logger.error(f"Twitter interaction check error: {e}")
    
    def cleanup(self):
        """Clean up browser sessions"""
        for browser in self.browsers.values():
            try:
                browser.quit()
            except:
                pass
        self.browsers.clear()

# Integration functions for the autonomous blog system
async def create_social_media_manager(config_dir: Path) -> SocialMediaBrowserManager:
    """Create and initialize social media manager"""
    manager = SocialMediaBrowserManager(config_dir)
    await manager.initialize_browsers()
    return manager

async def schedule_social_media_post(manager: SocialMediaBrowserManager, title: str, content: str, 
                                   platforms: List[str], hashtags: List[str], 
                                   scheduled_time: datetime) -> PostContent:
    """Schedule a social media post"""
    post_id = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    post_content = PostContent(
        id=post_id,
        title=title,
        content=content,
        platforms=platforms,
        hashtags=hashtags,
        scheduled_time=scheduled_time
    )
    
    manager.content_queue.append(post_content)
    return post_content
