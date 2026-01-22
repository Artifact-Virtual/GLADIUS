#!/usr/bin/env python3
"""
Example: Policy Configuration Scenarios

This file shows different policy configurations for various use cases.
"""

import json

# Scenario 1: Maximum Security (Read-only, minimal commands)
POLICY_MAXIMUM_SECURITY = {
    "allowed_commands": ["ls", "cat", "pwd"],
    "write_enabled": False,
    "max_file_size": 100000
}

# Scenario 2: Development Environment (More permissive)
POLICY_DEVELOPMENT = {
    "allowed_commands": [
        "ls", "cat", "pwd", "echo", "grep", "find",
        "head", "tail", "wc", "sort", "uniq", "diff",
        "git"
    ],
    "write_enabled": True,
    "max_file_size": 500000
}

# Scenario 3: Analysis Only (No writes, expanded read commands)
POLICY_ANALYSIS = {
    "allowed_commands": [
        "ls", "cat", "pwd", "grep", "find", "head", "tail",
        "wc", "sort", "uniq", "du", "stat", "file"
    ],
    "write_enabled": False,
    "max_file_size": 1000000
}

# Scenario 4: Restricted Write (Specific directory only - requires code changes)
POLICY_RESTRICTED_WRITE = {
    "allowed_commands": ["ls", "cat", "pwd", "echo", "grep"],
    "write_enabled": True,
    "max_file_size": 200000,
    "write_directory": "./output"  # Custom field - requires implementation
}


def save_policy(policy, filename):
    """Save a policy configuration to a file"""
    with open(filename, 'w') as f:
        json.dump(policy, f, indent=2)
    print(f"Saved policy to {filename}")


if __name__ == "__main__":
    print("Policy Configuration Examples\n")
    
    print("1. Maximum Security Policy:")
    print(json.dumps(POLICY_MAXIMUM_SECURITY, indent=2))
    
    print("\n2. Development Environment Policy:")
    print(json.dumps(POLICY_DEVELOPMENT, indent=2))
    
    print("\n3. Analysis Only Policy:")
    print(json.dumps(POLICY_ANALYSIS, indent=2))
    
    print("\n4. Restricted Write Policy:")
    print(json.dumps(POLICY_RESTRICTED_WRITE, indent=2))
    
    # Optionally save policies to files
    # save_policy(POLICY_MAXIMUM_SECURITY, "policy.max_security.json")
    # save_policy(POLICY_DEVELOPMENT, "policy.dev.json")
    # save_policy(POLICY_ANALYSIS, "policy.analysis.json")
