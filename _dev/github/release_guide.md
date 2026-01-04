# GitHub Release Management Guide

This guide covers the systematic process for creating and managing GitHub releases for any project.

## 📋 Release Checklist

### Pre-Release
- [ ] Update version in `pyproject.toml`
- [ ] Update version in documentation and release notes
- [ ] Run full test suite: `pytest tests/`
- [ ] Update `CHANGELOG.md` with new version details
- [ ] Create release notes in `docs/releases/X.Y.Z.md`
- [ ] Update `docs/releases/index.md` with new release

### Creating Release
- [ ] Commit all changes: `git commit -am "chore: prepare for vX.Y.Z release"`
- [ ] Create and push git tag: `git tag -a vX.Y.Z -m "Herald vX.Y.Z - Brief Description"`
- [ ] Push tag: `git push origin vX.Y.Z`
- [ ] Create GitHub release using script: `.\scripts\create_github_releases.ps1 -Version X.Y.Z`

### Post-Release
- [ ] Verify GitHub release is published
- [ ] Test installation: `pip install git+https://github.com/USER/REPO.git@vX.Y.Z` (for Python projects)
- [ ] Update documentation links if needed
- [ ] Announce release (if applicable)

## 🛠️ Tools and Scripts

### GitHub Release Script
```powershell
# From project root, using canonical script location
C:\workspace\_dev\github\create_github_releases.ps1 -Version 3.1.0

# Create all missing releases  
C:\workspace\_dev\github\create_github_releases.ps1 -AllReleases

# Dry run to preview
C:\workspace\_dev\github\create_github_releases.ps1 -AllReleases -DryRun

# Specify project name if auto-detection fails
C:\workspace\_dev\github\create_github_releases.ps1 -Version 2.0.0 -ProjectName MyProject
```

### Manual Git Tag Creation
```bash
# Create annotated tag
git tag -a v3.1.0 -m "Herald v3.1.0 - Trade Management

Key Features:
- External trade adoption
- CLI trade management tools  
- Enhanced configuration validation
- Observability improvements"

# Push tag
git push origin v3.1.0

# View tag details
git show v3.1.0
```

## 📁 File Structure

Release documentation should follow this structure:

```
docs/releases/
├── index.md              # Release overview and navigation
├── 1.0.0.md             # v1.0.0 release notes
├── 2.0.0.md             # v2.0.0 release notes  
├── 3.0.0.md             # v3.0.0 release notes
└── 3.1.0.md             # v3.1.0 release notes
```

## 📝 Release Note Template

Each release note should include:

```markdown
---
title: vX.Y.Z — YYYY-MM-DD
sidebar_position: N
---

# Herald vX.Y.Z — Release Title

Release Date: YYYY-MM-DD  
Git Tag: `vX.Y.Z`  
Commit: `xxxxxxx`

## Highlights
- Key feature 1
- Key feature 2
- Key improvement 3

## Key Changes
### Added
- New feature descriptions with technical details

### Changed  
- Modified behavior and improvements

### Fixed
- Bug fixes and issue resolutions

### Security
- Security improvements and patches

## Technical Improvements
- Performance enhancements
- Architecture improvements

## Migration Guide
### From vPREV.VERSION
1. Configuration changes needed
2. Database migrations required
3. Dependencies to update

## CLI Usage Examples (if applicable)
```bash
# Command examples
```

## Production Notes
- Deployment considerations
- Performance characteristics
- Known limitations

## Breaking Changes
- List any breaking changes

## Known Issues
- Current limitations or bugs

## What's Next
- Preview of upcoming features
```

## 🔄 Version Strategy

Herald follows [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Breaking changes, major architecture updates
- **MINOR** (X.Y.0): New features, backwards-compatible functionality
- **PATCH** (X.Y.Z): Bug fixes, small improvements

### Example Release Line
- **v1.0.0**: Initial stable release
- **v2.0.0**: Major feature additions  
- **v3.0.0**: Architecture improvements
- **v3.1.0**: Bug fixes and minor features
- **v3.2.0**: (Planned) Performance improvements
- **v4.0.0**: (Planned) Breaking changes and new architecture

## 🚀 GitHub Integration

### Prerequisites
- Install GitHub CLI: `winget install GitHub.cli`
- Authenticate: `gh auth login`
- Repository access: Ensure push permissions to your GitHub repository

### Release Creation Process
1. **Automated**: Use `create_github_releases.ps1` script
2. **Manual**: Via GitHub web interface or CLI
3. **Validation**: Verify release appears at https://github.com/USER/REPO/releases

### Release Assets
Consider adding these to future releases:
- `herald-X.Y.Z-win64.zip` - Windows distribution
- `requirements-X.Y.Z.txt` - Pinned dependencies
- `CHANGELOG-X.Y.Z.md` - Standalone changelog

## 📊 Tracking and Metrics

### Git Tags
```bash
# List all tags
git tag --list

# Tags with dates  
git tag --list --format='%(refname:short) %(creatordate:short)'

# Tag commit details
git show --name-only vX.Y.Z
```

### Release Analytics
- GitHub release download counts
- Documentation page views
- User feedback and issues

## 🔧 Troubleshooting

### Common Issues
1. **Missing Git Tag**: Create tag before GitHub release
2. **Release Notes Missing**: Ensure `docs/releases/X.Y.Z.md` exists
3. **GitHub CLI Auth**: Re-run `gh auth login`
4. **Tag Push Failed**: Check repository permissions

### Recovery Steps
```bash
# Delete local tag
git tag -d vX.Y.Z

# Delete remote tag  
git push origin --delete vX.Y.Z

# Recreate tag on correct commit
git tag -a vX.Y.Z COMMIT_HASH -m "Release message"
git push origin vX.Y.Z
```