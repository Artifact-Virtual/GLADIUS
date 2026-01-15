# Troubleshooting Guide

[![Common Issues](https://img.shields.io/badge/issues-documented-blue.svg)]()

Solutions to common SENTINEL issues.

## Installation Issues

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'psutil'`

**Solution**:
```bash
pip3 install -r requirements.txt --upgrade
```

### Permission Denied

**Problem**: Permission errors when starting

**Solution**:
```bash
sudo python3 asas_cli.py start
```

## Runtime Issues

### Components Show OFFLINE

**Problem**: Components show as OFFLINE in status

**Solution**:
1. Start the system: `python3 asas_cli.py start`
2. Wait 5 seconds
3. Check status: `python3 asas_cli.py status`

### High Memory Usage

**Problem**: SENTINEL using too much memory

**Solution**:
1. Reduce monitoring interval in config
2. Limit target count
3. Disable unused features

### High CPU Usage

**Problem**: High CPU usage during monitoring

**Solution**:
1. Increase monitoring interval
2. Reduce scan frequency
3. Disable deep scans

## Target Management Issues

### Target Not Found

**Problem**: Target check fails

**Solution**:
1. Verify target ID: `python3 asas_cli.py target-list`
2. Check target exists on system
3. Verify permissions

### Target Shows Compromised

**Problem**: Target incorrectly marked compromised

**Solution**:
1. Check target status: `python3 asas_cli.py target-check <ID>`
2. Review events: `python3 asas_cli.py target-info <ID> --events`
3. Verify target still exists

## Database Issues

### Database Locked

**Problem**: SQLite database locked error

**Solution**:
1. Stop SENTINEL: `python3 asas_cli.py stop`
2. Wait 5 seconds
3. Restart: `python3 asas_cli.py start`

### Corrupt Database

**Problem**: Database corruption

**Solution**:
```bash
# Backup
cp data/targets.db data/targets.db.backup

# Remove and recreate
rm data/targets.db
python3 asas_cli.py status
```

## Performance Issues

### Slow Scans

**Problem**: Scans taking too long

**Solution**:
1. Use quick scan for regular checks
2. Run full scans less frequently
3. Reduce target count

### Slow Startup

**Problem**: System takes long to start

**Solution**:
1. Reduce target count
2. Disable unused components
3. Check system resources

## Logging Issues

### No Logs Generated

**Problem**: Logs directory empty

**Solution**:
1. Check permissions on logs directory
2. Verify logging enabled in config
3. Check disk space

### Log Files Too Large

**Problem**: Log files consuming disk space

**Solution**:
1. Enable log rotation
2. Reduce log level
3. Set retention policy

## Common Error Messages

### "Failed to initialize components"

**Cause**: Missing dependencies or config

**Fix**:
```bash
pip3 install -r requirements.txt
python3 asas_cli.py status
```

### "Target monitoring failed"

**Cause**: Permission issues or invalid target

**Fix**:
1. Check target exists
2. Verify permissions
3. Review target configuration

## Getting Help

If issues persist:

1. Check logs: `python3 asas_cli.py logs --tail 100`
2. Review [documentation](../README.md)
3. Open [GitHub issue](https://github.com/Artifact-Virtual/SENTINEL/issues)
4. Include:
   - SENTINEL version
   - Operating system
   - Error messages
   - Steps to reproduce

---

<div align="center">
  <p><em>Most issues resolved in minutes</em></p>
</div>
