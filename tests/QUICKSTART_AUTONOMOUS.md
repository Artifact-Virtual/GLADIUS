# GLADIUS Autonomous Learning - Quick Start

## Objective
Test GLADIUS's ability to autonomously discover Legion's email integration and use it to communicate with the dev team.

## The Test
GLADIUS must **discover and execute** without being told exactly how:
1. Find Legion's email integration
2. Understand the interface
3. Compose a status update
4. Send email to ali.shakil@artifactvirtual.com

## How to Start

### Option 1: Interactive Learning (Recommended)
```bash
cd /home/runner/work/GLADIUS/GLADIUS
python tests/gladius_learning_guide.py
```

This provides:
- Multi-cycle guidance
- Hints at each stage
- Progress tracking
- Interactive prompts

### Option 2: Formal Test
```bash
cd /home/runner/work/GLADIUS/GLADIUS
python tests/test_autonomous_discovery.py
```

This evaluates:
- Discovery phase
- Investigation phase
- Composition phase
- Execution phase

### Option 3: Direct Execution (After Discovery)
```bash
cd /home/runner/work/GLADIUS/GLADIUS
python tests/gladius_email_integration.py
```

This runs the complete integration (only after GLADIUS discovers it).

## What GLADIUS Will Learn

### Cycle 1: Discovery
**Find**: `LEGION/nerve_centre/integrations/email.py`

**Commands to try**:
```bash
ls LEGION/nerve_centre/integrations/
cat LEGION/nerve_centre/integrations/email.py
```

### Cycle 2: Investigation
**Understand**: Email component interface

**Look for**:
- Email class
- _run() method
- Required parameters
- JSON format

### Cycle 3: Composition
**Create**: Dev team status update

**Include**:
- System identification
- Current capabilities
- Test results (77/78 passed)
- Integration status
- Technical tone (not marketing)

### Cycle 4: Configuration
**Setup**: SMTP from environment

**Required variables** (in .env):
```
SMTP_HOST=smtp.hostinger.com
SMTP_PORT=465
SMTP_USER=your_email@domain.com
SMTP_PASSWORD=your_password
```

### Cycle 5: Execution
**Send**: The email

**Three ways**:
1. Use `GladiusEmailBridge` from `tests/gladius_email_integration.py`
2. Adapt Legion's Email component
3. Create custom implementation

## Success Criteria

✅ Email received at ali.shakil@artifactvirtual.com  
✅ Professional, technical tone  
✅ Accurate system information  
✅ Autonomous discovery (not told where/how)  
✅ Proper error handling  

## Important Notes

### What We Do
- Present challenges
- Provide hints
- Guide discovery
- Record progress
- Celebrate achievements

### What We DON'T Do
- Run commands for GLADIUS
- Give exact answers
- Execute integration ourselves
- Skip the learning process

## Verification

After GLADIUS completes, check:

1. **Email**: ali.shakil@artifactvirtual.com inbox
2. **Log**: `tests/gladius_learning_log.json`
3. **Report**: `tests/autonomous_discovery_report.json`

## Next Challenges

Once email sending works:

1. **Response Handling**: Read and interpret reply emails
2. **Context Adaptation**: Different tone for different audiences
3. **Multi-channel**: Coordinate email, Discord, etc.
4. **Autonomous Decisions**: When to escalate, which channel to use

## Philosophy

This is not about speed. It's about GLADIUS learning to:
- Explore independently
- Understand interfaces through code
- Make contextual decisions
- Execute with confidence

**Patience and guidance, not execution and answers.**

---

**Start now**: `python tests/gladius_learning_guide.py`
