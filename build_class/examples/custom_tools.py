#!/usr/bin/env python3
"""
Example: Creating Custom Tools

This example demonstrates how to add custom tools to the nanocode system.
"""

import os
import json
import subprocess


def tool_git_status():
    """Example tool: Get git status"""
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout
    except Exception as e:
        return f"Error: {str(e)}"


def tool_file_count(directory="."):
    """Example tool: Count files in a directory"""
    try:
        result = subprocess.run(
            ["find", directory, "-type", "f"],
            capture_output=True,
            text=True,
            timeout=10
        )
        count = len(result.stdout.strip().split('\n'))
        return f"Found {count} files in {directory}"
    except Exception as e:
        return f"Error: {str(e)}"


def tool_search_code(pattern, file_type="*.py"):
    """Example tool: Search for pattern in code files"""
    try:
        result = subprocess.run(
            ["grep", "-r", "--include", file_type, pattern, "."],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout[:2000]  # Truncate output
    except Exception as e:
        return f"Error: {str(e)}"


# To use these tools with nanocode, add them to the TOOLS dictionary:
#
# from nanocode import TOOLS
# TOOLS["git_status"] = tool_git_status
# TOOLS["file_count"] = tool_file_count
# TOOLS["search_code"] = tool_search_code


if __name__ == "__main__":
    print("Example custom tools for nanocode")
    print("\nTesting tools:")
    print("\n1. Git Status:")
    print(tool_git_status())
    print("\n2. File Count:")
    print(tool_file_count("."))
    print("\n3. Code Search (searching for 'def'):")
    print(tool_search_code("def", "*.py")[:200] + "...")
