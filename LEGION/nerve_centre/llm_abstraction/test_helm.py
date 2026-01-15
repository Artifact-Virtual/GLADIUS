#!/usr/bin/env python3
"""
Helm Charts Test
Tests the Kubernetes deployment charts functionality
"""

import logging
import sys
import subprocess
import yaml
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_helm_structure():
    """Test Helm chart structure"""
    logger.info("Testing Helm chart structure...")
    
    try:
        # Check foundry helm directory
        foundry_path = Path(__file__).parent.parent / 'foundry'
        helm_path = foundry_path / 'helm'
        
        if not helm_path.exists():
            logger.error("❌ Helm directory not found in foundry")
            return False
        
        logger.info("✅ Helm directory found in foundry")
        
        # Check for required Helm files
        required_files = [
            'Chart.yaml',
            'values.yaml',
            '.helmignore'
        ]
        
        for file_name in required_files:
            file_path = helm_path / file_name
            if file_path.exists():
                size = file_path.stat().st_size
                logger.info(f"✅ Found {file_name} ({size} bytes)")
            else:
                logger.warning(f"⚠️ Missing {file_name}")
        
        # Check for templates directory
        templates_path = helm_path / 'templates'
        if templates_path.exists():
            template_files = list(templates_path.glob("*.yaml"))
            logger.info(f"✅ Found templates directory with {len(template_files)} YAML files")
            
            for template in template_files[:5]:  # Show first 5
                logger.info(f"  - {template.name}")
        else:
            logger.warning("⚠️ Missing templates directory")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Helm structure test failed: {e}")
        return False


def test_helm_chart_yaml():
    """Test Chart.yaml validity"""
    logger.info("Testing Chart.yaml...")
    
    try:
        helm_path = Path(__file__).parent.parent / 'foundry' / 'helm'
        chart_file = helm_path / 'Chart.yaml'
        
        if not chart_file.exists():
            logger.error("❌ Chart.yaml not found")
            return False
        
        # Parse YAML
        with open(chart_file, 'r') as f:
            chart_data = yaml.safe_load(f)
        
        # Check required fields
        required_fields = ['apiVersion', 'name', 'description', 'type', 'version', 'appVersion']
        found_fields = []
        
        for field in required_fields:
            if field in chart_data:
                found_fields.append(field)
                logger.info(f"✅ Found field: {field} = {chart_data[field]}")
            else:
                logger.warning(f"⚠️ Missing field: {field}")
        
        logger.info(f"✅ Chart.yaml contains {len(found_fields)}/{len(required_fields)} required fields")
        
        # Validate specific values
        if chart_data.get('apiVersion') == 'v2':
            logger.info("✅ Using Helm API version v2")
        else:
            logger.warning("⚠️ Not using recommended Helm API version v2")
        
        if chart_data.get('type') == 'application':
            logger.info("✅ Chart type is 'application'")
        else:
            logger.warning("⚠️ Chart type is not 'application'")
        
        return len(found_fields) >= 4  # At least most fields should be present
        
    except yaml.YAMLError as e:
        logger.error(f"❌ Chart.yaml YAML parsing failed: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Chart.yaml test failed: {e}")
        return False


def test_helm_values_yaml():
    """Test values.yaml validity"""
    logger.info("Testing values.yaml...")
    
    try:
        helm_path = Path(__file__).parent.parent / 'foundry' / 'helm'
        values_file = helm_path / 'values.yaml'
        
        if not values_file.exists():
            logger.error("❌ values.yaml not found")
            return False
        
        # Parse YAML
        with open(values_file, 'r') as f:
            values_data = yaml.safe_load(f)
        
        logger.info("✅ values.yaml is valid YAML")
        
        # Check structure
        if isinstance(values_data, dict):
            logger.info(f"✅ values.yaml contains {len(values_data)} top-level sections")
            
            # Log top-level keys
            for key in list(values_data.keys())[:10]:  # First 10 keys
                logger.info(f"  - {key}")
        else:
            logger.warning("⚠️ values.yaml is not a dictionary structure")
        
        # Check file size
        size = values_file.stat().st_size
        logger.info(f"✅ values.yaml size: {size} bytes")
        
        return True
        
    except yaml.YAMLError as e:
        logger.error(f"❌ values.yaml YAML parsing failed: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ values.yaml test failed: {e}")
        return False


def test_helm_templates():
    """Test Helm templates"""
    logger.info("Testing Helm templates...")
    
    try:
        helm_path = Path(__file__).parent.parent / 'foundry' / 'helm'
        templates_path = helm_path / 'templates'
        
        if not templates_path.exists():
            logger.error("❌ Templates directory not found")
            return False
        
        # Get all YAML template files
        template_files = list(templates_path.glob("*.yaml"))
        
        if not template_files:
            logger.warning("⚠️ No YAML template files found")
            return False
        
        logger.info(f"✅ Found {len(template_files)} template files")
        
        valid_templates = 0
        
        for template_file in template_files:
            try:
                # Try to parse each template as YAML (basic validation)
                with open(template_file, 'r') as f:
                    content = f.read()
                
                # Check for Helm template syntax
                if '{{' in content and '}}' in content:
                    logger.info(f"✅ {template_file.name} contains Helm template syntax")
                    valid_templates += 1
                else:
                    logger.info(f"ℹ️ {template_file.name} is static YAML (no templates)")
                    valid_templates += 1
                
                # Check for Kubernetes resource structure
                if 'apiVersion:' in content and 'kind:' in content:
                    logger.info(f"✅ {template_file.name} appears to be a valid Kubernetes resource")
                else:
                    logger.warning(f"⚠️ {template_file.name} may not be a valid Kubernetes resource")
                
            except Exception as e:
                logger.error(f"❌ Template {template_file.name} validation failed: {e}")
        
        logger.info(f"✅ {valid_templates}/{len(template_files)} templates appear valid")
        
        return valid_templates > 0
        
    except Exception as e:
        logger.error(f"❌ Helm templates test failed: {e}")
        return False


def test_helm_cli():
    """Test Helm CLI availability"""
    logger.info("Testing Helm CLI...")
    
    try:
        # Check if helm command is available
        result = subprocess.run(['helm', 'version', '--short'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            version = result.stdout.strip()
            logger.info(f"✅ Helm CLI available: {version}")
            return True
        else:
            logger.warning("⚠️ Helm CLI not available or not working")
            logger.info("  Install Helm from: https://helm.sh/docs/intro/install/")
            return False
            
    except FileNotFoundError:
        logger.warning("⚠️ Helm CLI not found in PATH")
        logger.info("  Install Helm from: https://helm.sh/docs/intro/install/")
        return False
    except subprocess.TimeoutExpired:
        logger.warning("⚠️ Helm CLI command timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Helm CLI test failed: {e}")
        return False


def test_helm_lint():
    """Test Helm chart linting (if Helm CLI available)"""
    logger.info("Testing Helm chart linting...")
    
    try:
        helm_path = Path(__file__).parent.parent / 'foundry' / 'helm'
        
        # Try to lint the chart
        result = subprocess.run(['helm', 'lint', str(helm_path)], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            logger.info("✅ Helm chart passed linting")
            logger.info(f"Lint output: {result.stdout.strip()}")
            return True
        else:
            logger.warning("⚠️ Helm chart failed linting")
            logger.warning(f"Lint errors: {result.stderr.strip()}")
            return False
            
    except FileNotFoundError:
        logger.info("ℹ️ Helm CLI not available, skipping lint test")
        return True  # Don't fail if Helm isn't installed
    except subprocess.TimeoutExpired:
        logger.warning("⚠️ Helm lint command timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Helm lint test failed: {e}")
        return False


def main():
    """Main test function"""
    print("=" * 60)
    print("⛵ HELM CHARTS TEST")
    print("=" * 60)
    
    tests = [
        ("Structure Test", test_helm_structure),
        ("Chart.yaml Test", test_helm_chart_yaml),
        ("values.yaml Test", test_helm_values_yaml),
        ("Templates Test", test_helm_templates),
        ("Helm CLI Test", test_helm_cli),
        ("Helm Lint Test", test_helm_lint),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            logger.error(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 60)
    print("📊 HELM CHARTS TEST RESULTS")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
