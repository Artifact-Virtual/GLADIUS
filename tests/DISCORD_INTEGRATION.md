# GLADIUS Discord Integration

## Overview

GLADIUS now supports automatic forwarding of emails to Discord webhooks, enabling:
- **Multi-channel communication** training
- **Real-time notifications** of autonomous learning progress
- **Interactive feedback** capability (receive and interpret responses)
- **Discord platform** integration learning

## How It Works

When GLADIUS sends an email (in any mode: live, simulation, or test), it can automatically forward a formatted version to a Discord webhook. This allows you to:

1. **Receive** the email content in Discord
2. **Reply** in Discord (GLADIUS can learn to interpret responses)
3. **Execute** actions based on your feedback

## Configuration

### Option 1: Environment Variable

Add to your `.env` file:
```bash
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN
```

### Option 2: Pass Directly

```python
from tests.gladius_email_bridge_v2 import GladiusEmailBridgeV2

bridge = GladiusEmailBridgeV2(
    mode="auto",
    discord_webhook="https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"
)
```

### Option 3: Use Default (Current Setup)

The system is pre-configured with the webhook:
```
https://discord.com/api/webhooks/1463278624281989152/TgZH97Ilas36yYlbLQRwPf7o3Tnsf83XrrVLMxx9ECVRlx8JhrTqVxzFEw5Yx0iUrpcX
```

## Usage

### Basic Usage

```python
# Runs with default Discord webhook
python tests/gladius_email_bridge_v2.py
```

### Programmatic Usage

```python
from tests.gladius_email_bridge_v2 import GladiusEmailBridgeV2

# Initialize with Discord forwarding
bridge = GladiusEmailBridgeV2(
    mode="simulation",  # or "live", "test", "auto"
    discord_webhook="https://discord.com/api/webhooks/..."
)

# Send email (automatically forwards to Discord)
result = bridge.send_status_update("recipient@example.com")

# Check if Discord forwarding succeeded
if result.get('discord_forwarded'):
    print("Email sent to Discord!")
```

## Discord Message Format

GLADIUS sends Discord messages with:

- **Embed Title**: Email subject with 📧 icon
- **Embed Description**: 
  - Recipient information
  - Sender (GLADIUS AI System)
  - Email content (HTML stripped to plain text)
- **Color**: Purple (GLADIUS brand color)
- **Timestamp**: When the email was generated
- **Footer**: "GLADIUS Autonomous Learning System"
- **Username**: "GLADIUS AI"

## Learning Capabilities

### Current: Send to Discord ✅
- Autonomous email composition
- Automatic Discord forwarding
- Professional formatting
- Context-aware messaging

### Future: Response Handling
- **Receive** responses from Discord
- **Interpret** user feedback and commands
- **Execute** actions based on responses
- **Learn** from interaction patterns

Example future interaction:
```
User in Discord: "GLADIUS, please send me a detailed report on the test results"
GLADIUS: [Interprets request, generates report, sends via email and Discord]

User in Discord: "Great! Can you also update the documentation?"
GLADIUS: [Understands context, updates docs, reports back]
```

## Training GLADIUS

Each Discord interaction helps GLADIUS learn:

1. **Communication Patterns**: How developers communicate
2. **Context Understanding**: What information is relevant
3. **Tone Adaptation**: Professional vs casual contexts
4. **Action Recognition**: When to execute vs when to ask for clarification

## Example Output

When you run `python tests/gladius_email_bridge_v2.py`, you'll see:

```
✓ GladiusEmailBridge initialized in 'simulation' mode
✓ Discord webhook forwarding enabled

🚀 Executing autonomous email send...

📧 Email saved to file for review:
   JSON: tests/emails/email_20260120_211436.json
   HTML: tests/emails/email_20260120_211436.html
✅ Simulation mode execution successful!
✅ Email forwarded to Discord successfully!

📧 Email execution mode: simulation
📅 Timestamp: 2026-01-20T21:14:36.560654
📱 Discord: Forwarded to webhook ✓
   Training GLADIUS for Discord integration
```

## Troubleshooting

### Discord Message Not Received

1. **Check webhook URL**: Ensure it's valid and active
2. **Check internet connection**: GLADIUS needs network access
3. **Check webhook permissions**: Ensure webhook can post to channel
4. **Check rate limits**: Discord has rate limits for webhooks

### Content Truncation

Discord embeds have a 2000 character limit for descriptions. Long emails are automatically truncated with a note to check the full version in files.

## Next Steps

To enable response handling:

1. Set up a Discord bot to monitor the channel
2. Configure GLADIUS to listen for mentions
3. Implement response parsing and interpretation
4. Enable action execution based on feedback

This creates a full feedback loop for autonomous learning and task execution.

## Files Modified

- `tests/gladius_email_bridge_v2.py` - Enhanced with Discord forwarding
- `tests/DISCORD_INTEGRATION.md` - This documentation

## Testing

To test Discord integration:

```bash
# With default webhook
python tests/gladius_email_bridge_v2.py

# Check your Discord channel for the message!
```

The message will appear in the Discord channel configured for the webhook.

---

**GLADIUS is now learning Discord communication!** 🎉
