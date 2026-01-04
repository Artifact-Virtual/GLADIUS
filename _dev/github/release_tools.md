# GitHub Release Management Tools

Canonical workspace tools for systematic GitHub release management across all repositories.

## 🛠️ Available Tools

### `create_github_releases.ps1`
PowerShell script to automatically create GitHub releases from git tags and documentation.

**Features:**
- Auto-detects project name from git remote
- Extracts release notes from `docs/releases/X.Y.Z.md` files  
- Creates releases for single version or all missing versions
- Dry-run mode for testing
- Works with any repository structure

**Usage:**
```powershell
# From any project root directory
C:\workspace\_dev\github\create_github_releases.ps1 -Version 3.1.0
C:\workspace\_dev\github\create_github_releases.ps1 -AllReleases -DryRun
C:\workspace\_dev\github\create_github_releases.ps1 -AllReleases -ProjectName MyProject
```

### `RELEASE_MANAGEMENT_GUIDE.md`
Comprehensive guide covering:
- Release checklists and workflows
- Semantic versioning strategy
- Documentation templates
- Git tagging best practices
- Troubleshooting common issues

## 📋 Prerequisites

1. **GitHub CLI**: `winget install GitHub.cli`
2. **Authentication**: `gh auth login`
3. **Repository Access**: Push permissions to target repository

## 🚀 Quick Start

1. **Prepare Release Documentation** (optional but recommended):
   ```
   docs/releases/
   ├── 1.0.0.md
   ├── 2.0.0.md
   └── 3.0.0.md
   ```

2. **Create Git Tags**:
   ```bash
   git tag -a v3.1.0 -m "Release v3.1.0 - Brief Description"
   git push origin v3.1.0
   ```

3. **Generate GitHub Releases**:
   ```powershell
   C:\workspace\_dev\github\create_github_releases.ps1 -AllReleases
   ```

## 📁 Expected Repository Structure

The tools work best with this structure but adapt to various layouts:

```
your-project/
├── docs/
│   └── releases/           # Optional: Enhanced release notes
│       ├── 1.0.0.md
│       ├── 2.0.0.md
│       └── index.md
├── .git/
├── pyproject.toml          # Version detection (Python projects)
├── package.json            # Version detection (Node.js projects)
└── README.md
```

## 🔧 Customization

The script automatically adapts to different project types:
- **Python**: Reads version from `pyproject.toml`
- **Node.js**: Reads version from `package.json`  
- **Generic**: Uses git tags and project directory name
- **Custom**: Override with `-ProjectName` parameter

## 💡 Tips

- **Dry Run First**: Always test with `-DryRun` before creating actual releases
- **Batch Processing**: Use `-AllReleases` to catch up on multiple versions
- **Documentation**: Rich release notes in `docs/releases/` improve release quality
- **Automation**: Consider integrating into CI/CD pipelines

## 🎯 Used Successfully With

- Herald (Trading System)
- Vector Database
- MCP Publisher
- Flex Audit

## 📞 Support

These are workspace-canonical tools. For project-specific issues, consult the individual project documentation.