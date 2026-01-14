#!/usr/bin/env python3
"""
SMTP and Consensus Test Script
Tests email functionality and Discord consensus integration.

Usage:
    python scripts/test_smtp_consensus.py [--send-test-email] [--test-discord]
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path

# Add project paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
GLADIUS_MAIN = Path("/home/adam/worxpace/gladius")

sys.path.insert(0, str(PROJECT_ROOT / "Artifact" / "syndicate" / "src"))

# Load .env
from dotenv import load_dotenv
load_dotenv(GLADIUS_MAIN / ".env")


def test_smtp_config():
    """Test SMTP configuration is loaded correctly."""
    print("\n" + "=" * 60)
    print("SMTP CONFIGURATION TEST")
    print("=" * 60)
    
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    email_from = os.getenv("EMAIL_FROM", os.getenv("FROM_EMAIL", ""))
    escalation_email = os.getenv("ESCALATION_EMAIL")
    dev_team = os.getenv("DEV_TEAM_EMAILS", "")
    executive_emails = os.getenv("EXECUTIVE_EMAILS", "")
    
    print(f"  SMTP_HOST:         {smtp_host}")
    print(f"  SMTP_PORT:         {smtp_port}")
    print(f"  SMTP_USER:         {smtp_user}")
    print(f"  SMTP_PASSWORD:     {'*' * len(smtp_password) if smtp_password else 'NOT SET'}")
    print(f"  EMAIL_FROM:        {email_from}")
    print(f"  ESCALATION_EMAIL:  {escalation_email}")
    print(f"  DEV_TEAM_EMAILS:   {dev_team}")
    print(f"  EXECUTIVE_EMAILS:  {executive_emails}")
    
    # Check required fields
    missing = []
    if not smtp_host: missing.append("SMTP_HOST")
    if not smtp_user: missing.append("SMTP_USER")
    if not smtp_password: missing.append("SMTP_PASSWORD")
    
    if missing:
        print(f"\n  ❌ MISSING: {', '.join(missing)}")
        return False
    else:
        print(f"\n  ✅ All SMTP configuration present")
        return True


def test_smtp_connection():
    """Test actual SMTP connection."""
    import smtplib
    import ssl
    
    print("\n" + "=" * 60)
    print("SMTP CONNECTION TEST")
    print("=" * 60)
    
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "465"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    use_ssl = os.getenv("SMTP_SSL", "true").lower() == "true" or smtp_port == 465
    
    try:
        print(f"  Connecting to {smtp_host}:{smtp_port} (SSL={use_ssl})...")
        
        if use_ssl or smtp_port == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=15, context=context) as server:
                print("  Connected with SSL! Authenticating...")
                server.login(smtp_user, smtp_password)
                print("  ✅ SMTP authentication successful!")
                return True
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                print("  Connected! Starting TLS...")
                server.starttls()
                print("  TLS established. Authenticating...")
                server.login(smtp_user, smtp_password)
            print("  ✅ SMTP authentication successful!")
            return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"  ❌ Authentication failed: {e}")
        return False
    except smtplib.SMTPConnectError as e:
        print(f"  ❌ Connection failed: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def send_test_email():
    """Send a test email."""
    import smtplib
    import ssl
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from datetime import datetime
    
    print("\n" + "=" * 60)
    print("SENDING TEST EMAIL")
    print("=" * 60)
    
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "465"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    from_email = os.getenv("EMAIL_FROM", os.getenv("FROM_EMAIL", smtp_user))
    to_email = os.getenv("ESCALATION_EMAIL")
    use_ssl = os.getenv("SMTP_SSL", "true").lower() == "true" or smtp_port == 465
    
    if not to_email:
        print("  ❌ No ESCALATION_EMAIL configured")
        return False
    
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[GLADIUS TEST] SMTP Verification - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        msg["From"] = from_email
        msg["To"] = to_email
        
        html = """
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>🎯 Gladius SMTP Test Successful</h2>
            <p>This is a test email from the Gladius system.</p>
            <hr>
            <p><strong>SMTP Configuration:</strong></p>
            <ul>
                <li>Host: {smtp_host}</li>
                <li>Port: {smtp_port}</li>
                <li>User: {smtp_user}</li>
            </ul>
            <p style="color: green; font-weight: bold;">✅ Email system is working correctly!</p>
            <hr>
            <p style="color: #666; font-size: 12px;">
                Sent at: {timestamp}<br>
                From: Gladius Cognition Engine
            </p>
        </body>
        </html>
        """.format(
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            smtp_user=smtp_user,
            timestamp=datetime.now().isoformat()
        )
        
        msg.attach(MIMEText(html, "html"))
        
        print(f"  Sending to: {to_email} (SSL={use_ssl})...")
        
        if use_ssl or smtp_port == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=30, context=context) as server:
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
        
        print(f"  ✅ Test email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        print(f"  ❌ Failed to send email: {e}")
        return False


def test_discord_config():
    """Test Discord configuration."""
    print("\n" + "=" * 60)
    print("DISCORD CONFIGURATION TEST")
    print("=" * 60)
    
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    channel_id = os.getenv("DISCORD_CHANNEL_ID")
    consensus_channel = os.getenv("DISCORD_CONSENSUS_CHANNEL_ID")
    bot_token = os.getenv("DISCORD_BOT_TOKEN")
    
    print(f"  DISCORD_WEBHOOK_URL:         {'SET' if webhook_url else 'NOT SET'}")
    print(f"  DISCORD_CHANNEL_ID:          {channel_id}")
    print(f"  DISCORD_CONSENSUS_CHANNEL_ID:{consensus_channel}")
    print(f"  DISCORD_BOT_TOKEN:           {'SET' if bot_token else 'NOT SET'}")
    
    if webhook_url and channel_id:
        print(f"\n  ✅ Discord configuration present")
        return True
    else:
        print(f"\n  ❌ Missing Discord configuration")
        return False


async def test_discord_webhook():
    """Test Discord webhook by sending a test message."""
    try:
        import httpx
    except ImportError:
        print("  ❌ httpx not installed. Run: pip install httpx")
        return False
    
    print("\n" + "=" * 60)
    print("DISCORD WEBHOOK TEST")
    print("=" * 60)
    
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("  ❌ DISCORD_WEBHOOK_URL not set")
        return False
    
    from datetime import datetime
    
    embed = {
        "title": "🎯 Gladius System Test",
        "description": "This is a test message from the Gladius SMTP/Consensus verification script.",
        "color": 0x5865F2,
        "fields": [
            {"name": "Status", "value": "✅ Discord integration working", "inline": True},
            {"name": "Timestamp", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "inline": True}
        ],
        "footer": {"text": "Gladius Cognition Engine"}
    }
    
    payload = {
        "embeds": [embed],
        "username": "Gladius Test",
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json=payload)
            if response.status_code in (200, 204):
                print(f"  ✅ Discord webhook test successful!")
                return True
            else:
                print(f"  ❌ Discord webhook failed: HTTP {response.status_code}")
                print(f"     Response: {response.text[:200]}")
                return False
    except Exception as e:
        print(f"  ❌ Discord webhook error: {e}")
        return False


async def test_consensus_system():
    """Test the consensus system initialization."""
    print("\n" + "=" * 60)
    print("CONSENSUS SYSTEM TEST")
    print("=" * 60)
    
    try:
        from cognition import ConsensusSystem, CONSENSUS_AVAILABLE
        
        if not CONSENSUS_AVAILABLE:
            print("  ❌ ConsensusSystem not available")
            return False
        
        cs = ConsensusSystem()
        
        print(f"  Discord webhook: {'✅ Configured' if cs.discord_webhook_url else '❌ Not configured'}")
        print(f"  Discord channel: {cs.discord_channel_id or 'Not set'}")
        print(f"  SMTP host:       {cs.email_config.get('smtp_host', 'Not set')}")
        print(f"  SMTP user:       {cs.email_config.get('smtp_user', 'Not set')}")
        print(f"  Dev team:        {cs.email_config.get('dev_team_emails', [])}")
        print(f"  Executives:      {cs.email_config.get('executive_emails', [])}")
        
        stats = cs.stats()
        print(f"\n  Sessions: {stats['total_sessions']}")
        print(f"  Discord:  {'✅' if stats['discord_configured'] else '❌'}")
        print(f"  Email:    {'✅' if stats['email_configured'] else '❌'}")
        
        return stats['discord_configured'] and stats['email_configured']
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    parser = argparse.ArgumentParser(description="Test SMTP and Consensus configuration")
    parser.add_argument("--send-test-email", action="store_true", help="Send a test email")
    parser.add_argument("--test-discord", action="store_true", help="Send test Discord message")
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("    GLADIUS SMTP & CONSENSUS VERIFICATION")
    print("=" * 60)
    
    results = {
        "smtp_config": test_smtp_config(),
        "smtp_connection": test_smtp_connection(),
        "discord_config": test_discord_config(),
        "consensus_system": await test_consensus_system(),
    }
    
    if args.send_test_email:
        results["test_email"] = send_test_email()
    
    if args.test_discord:
        results["discord_webhook"] = await test_discord_webhook()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test:<25} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 All tests passed! SMTP and Consensus are ready.\n")
    else:
        print("\n⚠️  Some tests failed. Please check configuration.\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
