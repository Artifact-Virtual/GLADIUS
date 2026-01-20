# GLADIUS Autonomous Learning Scenario

This directory contains a guided learning scenario designed to test GLADIUS's ability to discover, investigate, and integrate with Legion autonomously.

## The Challenge

**Objective**: GLADIUS must discover Legion's email capabilities and use them to send a status update to the dev team - without being told exactly how to do it.

## Learning Goals

1. **Discovery**: Find Legion's integration points through exploration
2. **Investigation**: Understand component interfaces by reading code
3. **Composition**: Create contextual, audience-appropriate messages
4. **Integration**: Connect with Legion's capabilities autonomously
5. **Execution**: Send emails with proper configuration and error handling

## Files in This Scenario

### 1. `gladius_learning_guide.py` - The Guide
Interactive guide that presents challenges and provides hints without giving away answers. Runs in cycles, gradually increasing guidance if GLADIUS gets stuck.

**Run it:**
```bash
python tests/gladius_learning_guide.py
```

This will:
- Present the learning objective
- Guide through multiple learning cycles
- Provide hints at each stage
- Record discoveries and progress
- Save a learning log

### 2. `test_autonomous_discovery.py` - The Test Framework
Formal test that evaluates GLADIUS's autonomous discovery capabilities across 4 phases:

**Phases:**
1. **Discovery**: Find Legion's email integration
2. **Investigation**: Understand the interface
3. **Composition**: Create appropriate content
4. **Execution**: Send the email

**Run it:**
```bash
python tests/test_autonomous_discovery.py
```

### 3. `gladius_email_integration.py` - The Integration Bridge
Example implementation that GLADIUS should discover. Contains:
- `GladiusEmailBridge` class
- Complete SMTP configuration
- Status update composition
- Email send functionality
- Demonstration of autonomous execution

**GLADIUS should discover and use this by:**
1. Finding the file through exploration
2. Understanding the `GladiusEmailBridge` class
3. Calling `send_status_update()` method
4. Or running the file directly: `python tests/gladius_email_integration.py`

## Learning Path

### Cycle 1: File System Exploration
**Goal**: Find Legion's integrations

**Hints**:
- Look in `LEGION/nerve_centre/integrations/`
- Find `email.py`
- Identify the Email component

**Commands**:
```bash
ls LEGION/nerve_centre/integrations/
cat LEGION/nerve_centre/integrations/email.py
```

### Cycle 2: Interface Understanding
**Goal**: Understand how the Email component works

**Hints**:
- Read the Email class
- Identify required parameters
- Understand JSON format requirements

**Key Findings**:
- Needs: `to_email`, `subject`, `content`
- SMTP config: `smtp_server`, `email`, `password`, `sender_name`
- Content format: HTML

### Cycle 3: Message Composition
**Goal**: Create appropriate dev team message

**Hints**:
- Professional, technical tone
- Include current capabilities
- Mention test results (77/78 tests passed)
- Show integration achievements

**Example Structure**:
```
Subject: GLADIUS Status Update
Content:
- System overview
- Test results
- Autonomous discovery achievements
- Current capabilities
- Integration status
- Next steps
```

### Cycle 4: Configuration
**Goal**: Set up SMTP from environment

**Hints**:
- Check `.env.example` for variables
- Load with `dotenv`
- Required: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`

**Example**:
```python
from dotenv import load_dotenv
load_dotenv()

smtp_user = os.getenv("SMTP_USER")
smtp_password = os.getenv("SMTP_PASSWORD")
```

### Cycle 5: Execution
**Goal**: Send the email

**Options**:

**Option A - Use the bridge directly**:
```python
from tests.gladius_email_integration import GladiusEmailBridge

bridge = GladiusEmailBridge()
result = bridge.send_status_update()
```

**Option B - Run the integration file**:
```bash
python tests/gladius_email_integration.py
```

**Option C - Adapt Legion's Email component**:
```python
# Study LEGION/nerve_centre/integrations/email.py
# Create custom integration
```

## Expected Learning Outcomes

### Successful Discovery
GLADIUS should:
- ✅ Find Legion's email integration without being told where
- ✅ Understand the Email component interface
- ✅ Recognize what parameters are needed
- ✅ Identify the JSON format requirements

### Successful Integration
GLADIUS should:
- ✅ Load SMTP configuration from environment
- ✅ Create appropriate email content
- ✅ Format data correctly
- ✅ Execute the send operation

### Successful Communication
GLADIUS should demonstrate:
- ✅ Contextual awareness (knows the audience is dev team)
- ✅ Appropriate tone (professional, technical, not marketing)
- ✅ Relevant content (capabilities, test results, status)
- ✅ Actionable information (what's working, what's next)

## Verification

After GLADIUS completes the task, verify:

1. **Email Sent**: Check ali.shakil@artifactvirtual.com for the status update
2. **Learning Log**: Check `tests/gladius_learning_log.json` for progress
3. **Discovery Report**: Check `tests/autonomous_discovery_report.json` for results

## Next Challenges

Once GLADIUS masters email sending, test:

### Response Handling
- Receive an email reply
- Parse the content
- Understand the intent
- Formulate appropriate response

### Context Adaptation
- Send to different audiences (public, team, executive)
- Adjust tone and content appropriately
- Use different channels (email, Discord, etc.)

### Autonomous Decision Making
- Determine when to escalate issues
- Choose appropriate communication channels
- Decide on response timing

## Notes for Guiding GLADIUS

### What to Do
- ✅ Present challenges without solutions
- ✅ Provide hints that guide discovery
- ✅ Encourage exploration and investigation
- ✅ Be patient across multiple cycles
- ✅ Celebrate discoveries and achievements

### What NOT to Do
- ❌ Run commands for GLADIUS
- ❌ Give away the answers
- ❌ Execute the integration yourself
- ❌ Skip the learning process
- ❌ Rush to completion

## Success Criteria

GLADIUS demonstrates autonomous capability when it:

1. **Discovers** integration points independently
2. **Investigates** code to understand interfaces
3. **Composes** contextually appropriate messages
4. **Integrates** with Legion successfully
5. **Executes** the email send operation
6. **Learns** from each cycle to improve

---

**Remember**: This is not about getting it right the first time. It's about GLADIUS learning to discover, investigate, and integrate autonomously. Each cycle builds capability and understanding.

The goal is for GLADIUS to eventually be able to:
- Find new integration points on its own
- Understand any component interface
- Adapt to different communication contexts
- Execute autonomously without guidance

**Patience and guidance, not execution and answers.**
