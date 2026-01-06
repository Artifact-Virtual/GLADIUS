# Contributing to Gladius

> Guidelines for contributing to the Gladius research repository

Thank you for your interest in contributing to Gladius! This is a **private research repository** focused on AI-driven trading systems, and contributions are managed carefully to maintain quality and security.

---

## 🔒 Repository Status

**This is a private, invitation-only repository.**

- Contributions are limited to authorized collaborators
- All changes must be reviewed by the Lead Developer
- Access requires explicit authorization from [`amuzetnoM`](https://github.com/amuzetnoM)

---

## 🤝 How to Contribute

### Types of Contributions

#### 1. Research Articles
Add new articles to [`dev_docs/articles/`](dev_docs/articles/):
- Follow existing article format
- Include proper citations and references
- Provide practical examples where applicable
- Cross-reference related articles

#### 2. Trading Strategies
Contribute to the [MQL5 Handbook](dev_docs/mql5_handbook/):
- Document strategy logic and implementation
- Include backtesting results
- Provide risk management considerations
- Add code examples

#### 3. Research Papers
Add papers to [`dev_docs/research/papers/`](dev_docs/research/papers/):
- Ensure proper licensing and attribution
- Include relevance to Gladius projects
- Add to the research index

#### 4. Documentation Improvements
Enhance existing documentation:
- Fix typos and clarify content
- Add examples and use cases
- Improve navigation and structure
- Update outdated information

#### 5. Project Development
Contribute to active projects:
- [GoldMax](projects/goldmax/) - Market analysis improvements
- [Cthulu](projects/cthulu/) - MQL5 implementation
- [Herald](projects/herald/) - Execution agent development

#### 6. Infrastructure
Improve deployment and operations:
- VM configuration scripts
- Monitoring and alerting
- Deployment automation
- Security hardening

---

## 📝 Contribution Process

### 1. Request Access
Contact [`amuzetnoM`](https://github.com/amuzetnoM) to request:
- Repository access
- Intended contribution area
- Proposed changes or additions

### 2. Create a Branch
```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Or for documentation
git checkout -b docs/documentation-update
```

### 3. Make Changes
Follow the guidelines below for your contribution type.

### 4. Submit a Pull Request
- **Title**: Clear, descriptive title
- **Description**: Explain what and why
- **Testing**: Document any testing performed
- **Related Issues**: Link to related issues if applicable

### 5. Review Process
- All PRs require Lead Developer approval
- Address review feedback promptly
- Ensure all checks pass

---

## ✅ Contribution Standards

### Code Quality
- **Clean Code**: Well-structured, readable code
- **Documentation**: Comment complex logic
- **Testing**: Test changes before submitting
- **Security**: No credentials or secrets in code

### Documentation
- **Clarity**: Write for your audience
- **Completeness**: Include all necessary information
- **Examples**: Provide practical examples
- **Links**: Cross-reference related content

### Research
- **Rigor**: Academically sound methodology
- **Citations**: Proper attribution of sources
- **Reproducibility**: Include code and data when possible
- **Relevance**: Connect to Gladius projects

### Security
- **No Secrets**: Never commit credentials
- **Review Code**: Check for vulnerabilities
- **Access Control**: Respect access boundaries
- **Audit Trail**: Maintain clear change history

---

## 📋 Style Guidelines

### Markdown Documents
```markdown
# Main Title (H1 - once per document)

## Section (H2)

### Subsection (H3)

- Bullet points for lists
- Use **bold** for emphasis
- Use `code` for inline code
- Use ```language blocks for code blocks
```

### Code Comments
```python
# Good: Explains why, not what
# Calculate risk-adjusted position size based on account balance
position_size = calculate_position(account_balance, risk_percent)

# Not needed: Obvious from code
# Set x to 5
x = 5
```

### File Naming
- Use lowercase with underscores: `file_name.md`
- Be descriptive: `vm_access_guide.md` not `guide.md`
- Group related files in directories

---

## 🚫 What Not to Contribute

### Prohibited Content
- **Credentials or Secrets**: API keys, passwords, tokens
- **Personal Information**: PII of any kind
- **Proprietary Code**: Code without permission to share
- **Unattributed Work**: Content without proper attribution
- **Malicious Code**: Any harmful or unsafe code

### Out of Scope
- **External Projects**: Unrelated to Gladius
- **Marketing Content**: Promotional material
- **Off-Topic Research**: Research not relevant to the projects
- **Low-Quality Content**: Incomplete or poorly written content

---

## 🔍 Review Criteria

Your contribution will be evaluated on:

### Technical Merit
- [ ] Technically sound and accurate
- [ ] Well-structured and organized
- [ ] Properly tested (if applicable)
- [ ] Follows best practices

### Documentation Quality
- [ ] Clear and well-written
- [ ] Appropriate level of detail
- [ ] Includes examples where helpful
- [ ] Properly formatted

### Security
- [ ] No secrets or credentials
- [ ] No security vulnerabilities
- [ ] Follows security best practices
- [ ] Respects access controls

### Integration
- [ ] Fits with existing structure
- [ ] Cross-referenced appropriately
- [ ] Doesn't duplicate existing content
- [ ] Updates indexes if needed

---

## 🤖 AI Collaboration Policy

### AI-Generated Content
This repository works with AI agents and accepts AI-generated content under these conditions:

1. **Explicit Attribution**: All AI-generated content must be clearly marked
2. **Human Review**: All AI content must be reviewed and approved by a human
3. **Quality Standards**: AI content must meet the same standards as human content
4. **Provenance**: Maintain clear record of AI involvement

### Authorized AI
- AI agents explicitly authorized by the Lead Developer
- Must identify themselves and their purpose
- Subject to the same review process as human contributors
- Restricted to designated areas (not `dev_dir/`)

---

## 📚 Resources for Contributors

### Getting Started
- [Quick Start Guide](QUICKSTART.md)
- [Documentation Index](dev_docs/SUMMARY.md)
- [Repository Structure](README.md#-repository-structure)

### Style and Format
- [Article Examples](dev_docs/articles/)
- [MQL5 Strategy Format](dev_docs/mql5_handbook/)
- [Research Paper Format](dev_docs/research/)

### Technical References
- [Architecture Documentation](dev_docs/docs/architectural_mandate.md)
- [VM Infrastructure](dev_docs/virtual_machine/)
- [Scripts and Utilities](dev_docs/scripts/)

---

## 🎯 Contribution Ideas

Looking for ways to contribute? Here are some ideas:

### Documentation
- [ ] Add more examples to existing articles
- [ ] Create tutorials for common tasks
- [ ] Improve navigation and cross-referencing
- [ ] Update outdated documentation

### Research
- [ ] Write new research articles
- [ ] Add research papers with summaries
- [ ] Create comparative analyses
- [ ] Document experimental results

### Projects
- [ ] Improve GoldMax chart generation
- [ ] Add new MQL5 strategies
- [ ] Enhance Herald execution logic
- [ ] Optimize VM deployment scripts

### Infrastructure
- [ ] Improve monitoring and alerting
- [ ] Add automated testing
- [ ] Enhance security measures
- [ ] Document operational procedures

---

## 📞 Questions or Issues?

### Before Contributing
- Review this guide thoroughly
- Check existing documentation
- Search for similar contributions
- Contact the Lead Developer if unsure

### Getting Help
- **General Questions**: Contact [`amuzetnoM`](https://github.com/amuzetnoM)
- **Technical Issues**: Document the issue clearly
- **Access Requests**: Provide justification for access needs
- **Collaboration Proposals**: Explain your goals and approach

---

## 📄 License

By contributing to Gladius, you agree that your contributions will be covered by the repository's proprietary license. See [LICENSE.md](docs/LICENSE.md) for details.

### Copyright
All contributions become part of the Gladius repository and are subject to its license terms. Contributors retain moral rights but grant usage rights to the repository owner.

### Attribution
Contributors will be acknowledged in:
- Commit history (automatic)
- Relevant documentation (where appropriate)
- Release notes (for significant contributions)

---

## 🙏 Acknowledgments

Thank you for contributing to Gladius! Your contributions help advance research in AI-driven trading systems and improve the quality of this repository.

---

*This contributing guide is subject to change. Last updated: 2026-01-06*
