import re
import logging
from datetime import datetime
from typing import List
# --- API Registry Updater (moved from update_api_registry.py) ---
class APIRegistryUpdater:
    """Updates the API registry document with discovered APIs"""
    def __init__(self, registry_file: str, discovery_root: str = "."):
        self.registry_file = Path(registry_file).resolve()
        self.discovery_root = Path(discovery_root).resolve()
        self.discovery = APIDiscovery(str(self.discovery_root))
        self.logger = logging.getLogger(__name__)

    
    def update_registry(self) -> bool:
        """Update the API registry document"""
        try:
            self.logger.info(f"Updating API registry: {self.registry_file}")
            apis = self.discovery.discover_apis()
            if not apis:
                self.logger.warning("No APIs discovered")
                return False
            if self.registry_file.exists():
                try:
                    with open(self.registry_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.logger.info(f"Read existing registry: {len(content)} characters")
                except Exception as e:
                    self.logger.error(f"Error reading registry file: {e}")
                    return False
            else:
                content = self._create_initial_registry()
                self.logger.info("Created initial registry structure")
                self.registry_file.parent.mkdir(parents=True, exist_ok=True)

            updated_content = self._update_inventory_table(content, apis)
            updated_content = self._update_timestamp(updated_content)

            try:
                with open(self.registry_file, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                print(f"✅ Updated {self.registry_file} with {len(apis)} APIs")
                self.logger.info(f"Successfully updated registry with {len(apis)} APIs")
                return True
            except Exception as e:
                self.logger.error(f"Error writing registry file: {e}")
                return False
        except Exception as e:
            self.logger.error(f"Error during registry update: {e}")
            print(f"❌ Error updating registry: {e}")
            return False

    def _create_initial_registry(self) -> str:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return f"""# Artifact Virtual - Servers and APIs Inventory\n\nThis document provides a living inventory of backend servers, frontend clients, and API endpoints within the Artifact Virtual workspace.\n\n*Last updated: {timestamp}*\n\n---\n\n## How to Discover All APIs and Servers\n\nArtifact Virtual is a rapidly evolving system. To ensure you have the latest API/server inventory:\n\n1. **Automated Discovery**\n   ```bash\n   # Run the discovery tool\n   python core/api_registry/api_discovery.py\n   ```\n\n2. **Manual Discovery Steps**\n   - Search for files named `main.py`, `app.py`, `server.py`, `index.js`, `app.ts`, etc.\n   - Check Docker Compose files for service definitions\n   - Review PM2/ecosystem configs for Node.js services\n   - Scan for open ports in dev/test environments\n\n---\n\n## API/Server Inventory\n\n<!-- API_TABLE_START -->\n| Name/Module | File/Entrypoint | Port(s) | Technology | Framework | Status | Purpose/Notes |\n|-------------|-----------------|---------|------------|-----------|---------|---------------|\n<!-- API_TABLE_END -->\n\n---\n\n## Port Conflict Warning\n\nMultiple services may default to the same port (e.g., 8000, 8080, 3000). Always check and configure ports to avoid conflicts when running multiple servers.\n\n---\n\n## Keeping This Document Up to Date\n\n- **Automate discovery:** Run the API discovery tool regularly\n- **Encourage developers** to document new APIs/servers in their module's README\n- **Review and update** this inventory before major deployments\n\n---\n\n*This document is automatically maintained by the API Discovery Tool.*\n"""

    def _update_inventory_table(self, content: str, apis: List[APIEndpoint]) -> str:
        try:
            table_rows = []
            for api in sorted(apis, key=lambda x: (x.technology, x.name)):
                status = "🟢 Running" if api.is_running else "🔴 Stopped"
                purpose = self._clean_description(api.description) or f"{api.framework} API server"
                file_path = api.file_path.replace('\\', '/')
                if len(file_path) > 50:
                    file_path = "..." + file_path[-47:]
                row = f"| {api.name} | `{file_path}` | {api.port or 'N/A'} | {api.technology} | {api.framework} | {status} | {purpose} |"
                table_rows.append(row)
            new_table_content = "\n".join(table_rows)
            table_start_marker = "<!-- API_TABLE_START -->"
            table_end_marker = "<!-- API_TABLE_END -->"
            if table_start_marker in content and table_end_marker in content:
                pattern = f"{re.escape(table_start_marker)}.*?{re.escape(table_end_marker)}"
                replacement = f"{table_start_marker}\n| Name/Module | File/Entrypoint | Port(s) | Technology | Framework | Status | Purpose/Notes |\n|-------------|-----------------|---------|------------|-----------|---------|---------------|\n{new_table_content}\n{table_end_marker}"
                content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            else:
                table_header = "| Name/Module | File/Entrypoint | Port(s) | Technology | Framework | Status | Purpose/Notes |"
                separator = "|-------------|-----------------|---------|------------|-----------|---------|---------------|"
                table_pattern = re.escape(table_header) + r'\s*\n' + re.escape(separator) + r'\s*\n(?:\|.*?\|\s*\n)*'
                new_table = f"{table_header}\n{separator}\n{new_table_content}\n"
                if re.search(table_pattern, content):
                    content = re.sub(table_pattern, new_table, content)
                else:
                    insert_pattern = r'(## .*?[Ii]nventory.*?\n)'
                    replacement = f'\\1\n{new_table}\n'
                    content = re.sub(insert_pattern, replacement, content)
            return content
        except Exception as e:
            self.logger.error(f"Error updating inventory table: {e}")
            return content

    def _clean_description(self, description: str) -> str:
        if not description:
            return ""
        cleaned = re.sub(r'\s+', ' ', description.strip())
        if len(cleaned) > 60:
            cleaned = cleaned[:57] + "..."
        return cleaned

    def _update_timestamp(self, content: str) -> str:
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            timestamp_pattern = r'\*Last updated:.*?\*'
            replacement = f'*Last updated: {timestamp}*'
            if re.search(timestamp_pattern, content):
                content = re.sub(timestamp_pattern, replacement, content)
            else:
                title_pattern = r'(# .*?\n)'
                replacement_with_timestamp = f'\\1\n*Last updated: {timestamp}*\n'
                content = re.sub(title_pattern, replacement_with_timestamp, content)
            return content
        except Exception as e:
            self.logger.error(f"Error updating timestamp: {e}")
            return content

    def validate_registry_path(self) -> bool:
        try:
            if not self.registry_file.parent.exists():
                self.registry_file.parent.mkdir(parents=True, exist_ok=True)
            if self.registry_file.exists():
                return os.access(self.registry_file, os.W_OK)
            else:
                return os.access(self.registry_file.parent, os.W_OK)
        except Exception as e:
            self.logger.error(f"Error validating registry path: {e}")
            return False
def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='API Discovery and Registry Updater')
    parser.add_argument(
        '--registry', '-r',
        default='docs/technical/api_registry.md',
        help='Path to API registry document')
    parser.add_argument(
        '--root', default='.',
        help='Root directory to scan')
    parser.add_argument(
        '--update-registry', action='store_true',
        help='Update the API registry document after discovery')
    parser.add_argument(
        '--verbose', '-v', action='store_true',
        help='Enable verbose logging')
    args = parser.parse_args()
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    try:
        if not Path(args.registry).is_absolute():
            script_dir = Path(__file__).parent
            registry_path = script_dir.parent.parent / args.registry
        else:
            registry_path = args.registry
        if not Path(args.root).is_absolute():
            root_path = Path.cwd() if args.root == '.' else Path(args.root)
        else:
            root_path = args.root
        logger.info(f"Registry file: {registry_path}")
        logger.info(f"Discovery root: {root_path}")
        if args.update_registry:
            updater = APIRegistryUpdater(str(registry_path), str(root_path))
            if not updater.validate_registry_path():
                print(f"❌ Cannot write to registry file: {registry_path}")
                return 1
            success = updater.update_registry()
            return 0 if success else 1
        else:
            # Just run discovery and print summary
            discovery = APIDiscovery(str(root_path))
            apis = discovery.discover_apis()
            print(f"Discovered {len(apis)} APIs:")
            for api in apis:
                print(f"- {api.name} ({api.framework}) at {api.file_path} port {api.port or 'N/A'}")
            return 0
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
import os
import re
import json
import yaml
import subprocess
import socket
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import argparse
import logging

@dataclass
class APIEndpoint:
    """Represents a discovered API endpoint"""
    name: str
    file_path: str
    port: Optional[int]
    technology: str
    framework: str
    host: Optional[str] = "localhost"
    endpoints: List[str] = None
    description: str = ""
    is_running: bool = False
    process_id: Optional[int] = None
    
    def __post_init__(self):
        if self.endpoints is None:
            self.endpoints = []

class APIDiscovery:
    """Comprehensive API discovery tool for Artifact Virtual system"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.apis = []
        self.logger = self._setup_logging()
        
        # Technology patterns for detection
        self.tech_patterns = {
            "FastAPI": {
                "patterns": [
                    r"from\s+fastapi\s+import",
                    r"FastAPI\(\)",
                    r"app\s*=\s*FastAPI",
                    r"@app\.(get|post|put|delete|patch)"
                ],
                "port_patterns": [
                    r"uvicorn\.run\([^,]*,\s*port\s*=\s*(\d+)",
                    r"host\s*=\s*[\"'][^\"']*[\"']\s*,\s*port\s*=\s*(\d+)",
                    r"--port\s+(\d+)"
                ]
            },
            "Flask": {
                "patterns": [
                    r"from\s+flask\s+import",
                    r"Flask\(__name__\)",
                    r"app\s*=\s*Flask",
                    r"@app\.route"
                ],
                "port_patterns": [
                    r"app\.run\([^)]*port\s*=\s*(\d+)",
                    r"host\s*=\s*[\"'][^\"']*[\"']\s*,\s*port\s*=\s*(\d+)"
                ]
            },
            "Express": {
                "patterns": [
                    r"express\(\)",
                    r"require\([\"']express[\"']\)",
                    r"import\s+express\s+from",
                    r"app\.listen\(",
                    r"server\.listen\("
                ],
                "port_patterns": [
                    r"\.listen\(\s*(\d+)",
                    r"port\s*:\s*(\d+)",
                    r"PORT\s*=\s*(\d+)"
                ]
            },
            "aiohttp": {
                "patterns": [
                    r"from\s+aiohttp\s+import",
                    r"aiohttp\.web\.",
                    r"web\.Application\(\)"
                ],
                "port_patterns": [
                    r"web\.run_app\([^,]*,\s*port\s*=\s*(\d+)",
                    r"port\s*=\s*(\d+)"
                ]
            },
            "Go HTTP": {
                "patterns": [
                    r"http\.ListenAndServe",
                    r"gin\.Default\(\)",
                    r"echo\.New\(\)"
                ],
                "port_patterns": [
                    r"ListenAndServe\([\"']:(\d+)[\"']",
                    r":\s*(\d+)[\"']\s*,\s*nil"
                ]
            }
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def discover_apis(self) -> List[APIEndpoint]:
        """Main discovery method"""
        self.logger.info(f"Starting API discovery in: {self.root_path}")
        
        # Discover APIs through multiple methods
        self._discover_by_file_patterns()
        self._discover_by_docker_configs()
        self._discover_by_package_configs()
        self._discover_running_services()
        
        # Enhance discovered APIs with additional info
        self._enhance_api_info()
        
        self.logger.info(f"Discovery complete. Found {len(self.apis)} APIs")
        return self.apis
    
    def _discover_by_file_patterns(self):
        """Discover APIs by scanning all files recursively for patterns"""
        self.logger.info("Scanning all files for API patterns...")
        for file_path in self.root_path.rglob("*"):
            if self._should_skip_path(file_path):
                continue
            if not file_path.is_file():
                continue
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                tech_info = self._detect_technology(content)
                if tech_info:
                    port = self._extract_port(content, tech_info['framework'])
                    endpoints = self._extract_endpoints(content, tech_info['framework'])
                    name = self._generate_api_name(file_path)
                    api = APIEndpoint(
                        name=name,
                        file_path=str(file_path.relative_to(self.root_path)),
                        port=port,
                        technology=tech_info['technology'],
                        framework=tech_info['framework'],
                        endpoints=endpoints,
                        description=self._extract_description(content, file_path)
                    )
                    self.apis.append(api)
            except Exception as e:
                self.logger.warning(f"Error analyzing {file_path}: {e}")
    
    def _should_skip_path(self, path: Path) -> bool:
        """Check if path should be skipped during discovery"""
        skip_dirs = {
            '.git', '__pycache__', 'node_modules', '.vscode', 
            'venv', '.env', 'dist', 'build', '.next'
        }
        return any(skip_dir in path.parts for skip_dir in skip_dirs)
    
    def _detect_technology(self, content: str) -> Optional[Dict[str, str]]:
        """Detect technology and framework from file content"""
        for framework, config in self.tech_patterns.items():
            for pattern in config['patterns']:
                if re.search(pattern, content, re.IGNORECASE):
                    return {
                        'framework': framework,
                        'technology': self._get_technology_category(framework)
                    }
        return None
    
    def _get_technology_category(self, framework: str) -> str:
        """Get technology category for framework"""
        categories = {
            'FastAPI': 'Python',
            'Flask': 'Python',
            'aiohttp': 'Python',
            'Express': 'Node.js',
            'Go HTTP': 'Go'
        }
        return categories.get(framework, 'Unknown')
    
    def _extract_port(self, content: str, framework: str) -> Optional[int]:
        """Extract port number from content"""
        if framework not in self.tech_patterns:
            return None
            
        for pattern in self.tech_patterns[framework]['port_patterns']:
            match = re.search(pattern, content)
            if match:
                try:
                    return int(match.group(1))
                except (ValueError, IndexError):
                    continue
        return None
    
    def _extract_endpoints(self, content: str, framework: str) -> List[str]:
        """Extract API endpoints from content"""
        endpoints = []
        
        endpoint_patterns = {
            'FastAPI': r'@app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
            'Flask': r'@app\.route\(["\']([^"\']+)["\']',
            'Express': r'app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
            'aiohttp': r'web\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']'
        }
        
        if framework in endpoint_patterns:
            pattern = endpoint_patterns[framework]
            matches = re.findall(pattern, content, re.IGNORECASE)
            
            for match in matches:
                if isinstance(match, tuple):
                    endpoints.append(match[1] if len(match) > 1 else match[0])
                else:
                    endpoints.append(match)
        
        return list(set(endpoints))  # Remove duplicates
    
    def _generate_api_name(self, file_path: Path) -> str:
        """Generate a descriptive name for the API"""
        # Use parent directory names to create meaningful name
        parts = file_path.parts
        relevant_parts = []
        
        for i, part in enumerate(parts):
            if part in ['src', 'app', 'api', 'server', 'backend']:
                continue
            if i >= len(parts) - 3:  # Include last few directory names
                relevant_parts.append(part)
        
        name = ' '.join(relevant_parts).replace('_', ' ').replace('-', ' ')
        return name.title() or file_path.stem.title()
    
    def _extract_description(self, content: str, file_path: Path) -> str:
        """Extract description from comments or docstrings"""
        # Look for module docstring
        docstring_match = re.search(r'"""([^"]+)"""', content)
        if docstring_match:
            return docstring_match.group(1).strip()
        
        # Look for comments at the top of file
        comment_match = re.search(r'^#\s*(.+)', content, re.MULTILINE)
        if comment_match:
            return comment_match.group(1).strip()
        
        return f"API server in {file_path.parent.name}"
    
    def _discover_by_docker_configs(self):
        """Discover APIs from Docker configurations"""
        self.logger.info("Scanning Docker configurations...")
        
        docker_files = list(self.root_path.rglob("docker-compose.yml")) + \
                      list(self.root_path.rglob("docker-compose.yaml")) + \
                      list(self.root_path.rglob("Dockerfile"))
        
        for docker_file in docker_files:
            try:
                if docker_file.name.startswith('docker-compose'):
                    self._parse_docker_compose(docker_file)
                else:
                    self._parse_dockerfile(docker_file)
            except Exception as e:
                self.logger.warning(f"Error parsing {docker_file}: {e}")
    
    def _parse_docker_compose(self, compose_file: Path):
        """Parse docker-compose file for services"""
        try:
            with open(compose_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            services = config.get('services', {})
            for service_name, service_config in services.items():
                ports = service_config.get('ports', [])
                for port_mapping in ports:
                    if isinstance(port_mapping, str):
                        port_parts = port_mapping.split(':')
                        if len(port_parts) >= 2:
                            external_port = int(port_parts[0])
                            
                            api = APIEndpoint(
                                name=f"Docker Service: {service_name}",
                                file_path=str(compose_file.relative_to(self.root_path)),
                                port=external_port,
                                technology="Docker",
                                framework="Docker Compose",
                                description=f"Service from {compose_file.name}"
                            )
                            self.apis.append(api)
        except Exception as e:
            self.logger.warning(f"Error parsing docker-compose {compose_file}: {e}")
    
    def _parse_dockerfile(self, dockerfile: Path):
        """Parse Dockerfile for exposed ports"""
        try:
            with open(dockerfile, 'r', encoding='utf-8') as f:
                content = f.read()
            
            expose_matches = re.findall(r'EXPOSE\s+(\d+)', content, re.IGNORECASE)
            for port in expose_matches:
                api = APIEndpoint(
                    name=f"Docker App: {dockerfile.parent.name}",
                    file_path=str(dockerfile.relative_to(self.root_path)),
                    port=int(port),
                    technology="Docker",
                    framework="Dockerfile",
                    description=f"Application from {dockerfile.parent.name}"
                )
                self.apis.append(api)
        except Exception as e:
            self.logger.warning(f"Error parsing Dockerfile {dockerfile}: {e}")
    
    def _discover_by_package_configs(self):
        """Discover APIs from package configuration files"""
        self.logger.info("Scanning package configurations...")
        
        # Check package.json files for scripts
        for package_file in self.root_path.rglob("package.json"):
            try:
                with open(package_file, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                
                scripts = package_data.get('scripts', {})
                for script_name, script_command in scripts.items():
                    if any(keyword in script_command.lower() for keyword in ['server', 'start', 'dev']):
                        # Try to extract port from script
                        port_match = re.search(r'--port\s+(\d+)', script_command)
                        port = int(port_match.group(1)) if port_match else None
                        
                        api = APIEndpoint(
                            name=f"NPM Script: {script_name}",
                            file_path=str(package_file.relative_to(self.root_path)),
                            port=port,
                            technology="Node.js",
                            framework="NPM Script",
                            description=f"Script: {script_command}"
                        )
                        self.apis.append(api)
            except Exception as e:
                self.logger.warning(f"Error parsing package.json {package_file}: {e}")
    
    def _discover_running_services(self):
        """Discover currently running services"""
        self.logger.info("Scanning for running services...")
        
        try:
            # Use netstat to find listening ports
            if os.name == 'nt':  # Windows
                result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
            else:  # Unix-like
                result = subprocess.run(['netstat', '-tlnp'], capture_output=True, text=True)
            
            if result.returncode == 0:
                self._parse_netstat_output(result.stdout)
        except Exception as e:
            self.logger.warning(f"Error running netstat: {e}")
    
    def _parse_netstat_output(self, output: str):
        """Parse netstat output to find listening services"""
        lines = output.strip().split('\n')
        for line in lines:
            if 'LISTENING' in line or 'LISTEN' in line:
                # Extract port from the line
                parts = line.split()
                for part in parts:
                    if ':' in part:
                        try:
                            port = int(part.split(':')[-1])
                            if 1000 <= port <= 65535:  # Reasonable port range
                                # Check if we already have this port
                                existing = any(api.port == port for api in self.apis)
                                if not existing:
                                    api = APIEndpoint(
                                        name=f"Running Service (Port {port})",
                                        file_path="Unknown",
                                        port=port,
                                        technology="Unknown",
                                        framework="Running Process",
                                        is_running=True,
                                        description=f"Active service on port {port}"
                                    )
                                    self.apis.append(api)
                        except ValueError:
                            continue
    
    def _enhance_api_info(self):
        """Enhance discovered APIs with additional information"""
        self.logger.info("Enhancing API information...")
        
        for api in self.apis:
            # Check if service is currently running
            if api.port and not api.is_running:
                api.is_running = self._is_port_open(api.port)
            
            # Try to get process information
            if api.is_running and api.port:
                api.process_id = self._get_process_by_port(api.port)
    
    def _is_port_open(self, port: int, host: str = 'localhost') -> bool:
        """Check if a port is open"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                return result == 0
        except Exception:
            return False
    
    def _get_process_by_port(self, port: int) -> Optional[int]:
        """Get process ID by port (platform specific)"""
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if f':{port}' in line and 'LISTENING' in line:
                        parts = line.split()
                        if parts:
                            return int(parts[-1])
            else:  # Unix-like
                result = subprocess.run(['lsof', '-t', f'-i:{port}'], capture_output=True, text=True)
                if result.stdout.strip():
                    return int(result.stdout.strip().split('\n')[0])
        except Exception:
            pass
        return None
    
    def generate_report(self, output_format: str = 'markdown') -> str:
        """Generate discovery report in specified format"""
        if output_format.lower() == 'json':
            return self._generate_json_report()
        elif output_format.lower() == 'html':
            return self._generate_html_report()
        else:
            return self._generate_markdown_report()
    
    def _generate_markdown_report(self) -> str:
        """Generate Markdown report"""
        report = f"""# Artifact Virtual - API Discovery Report

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Discovery Root: {self.root_path}
Total APIs Found: {len(self.apis)}

---

## Summary by Technology

"""
        
        # Group by technology
        tech_summary = {}
        for api in self.apis:
            tech = api.technology
            if tech not in tech_summary:
                tech_summary[tech] = []
            tech_summary[tech].append(api)
        
        for tech, apis in tech_summary.items():
            running_count = sum(1 for api in apis if api.is_running)
            report += f"- **{tech}**: {len(apis)} APIs ({running_count} running)\n"
        
        report += "\n---\n\n## Detailed API Inventory\n\n"
        report += "| Name | File Path | Port | Technology | Framework | Status | Endpoints |\n"
        report += "|------|-----------|------|------------|-----------|--------|----------|\n"
        
        for api in sorted(self.apis, key=lambda x: (x.technology, x.name)):
            status = "🟢 Running" if api.is_running else "🔴 Stopped"
            endpoints_str = ", ".join(api.endpoints[:3])  # Show first 3 endpoints
            if len(api.endpoints) > 3:
                endpoints_str += f" (+{len(api.endpoints) - 3} more)"
            
            report += f"| {api.name} | `{api.file_path}` | {api.port or 'N/A'} | {api.technology} | {api.framework} | {status} | {endpoints_str} |\n"
        
        report += "\n---\n\n## Port Usage Summary\n\n"
        
        used_ports = {}
        for api in self.apis:
            if api.port:
                if api.port not in used_ports:
                    used_ports[api.port] = []
                used_ports[api.port].append(api.name)
        
        for port in sorted(used_ports.keys()):
            apis_on_port = used_ports[port]
            if len(apis_on_port) > 1:
                report += f"⚠️  **Port {port}**: Potential conflict - {', '.join(apis_on_port)}\n"
            else:
                report += f"✅ **Port {port}**: {apis_on_port[0]}\n"
        
        report += "\n---\n\n## Running Services\n\n"
        running_apis = [api for api in self.apis if api.is_running]
        if running_apis:
            for api in running_apis:
                report += f"- **{api.name}** (Port {api.port})"
                if api.process_id:
                    report += f" - PID: {api.process_id}"
                report += "\n"
        else:
            report += "No running services detected.\n"
        
        report += f"\n---\n\n*Report generated by API Discovery Tool at {datetime.now()}*\n"
        
        return report
    
    def _generate_json_report(self) -> str:
        """Generate JSON report"""
        report_data = {
            "generated_at": datetime.now().isoformat(),
            "discovery_root": str(self.root_path),
            "total_apis": len(self.apis),
            "apis": [asdict(api) for api in self.apis],
            "summary": {
                "by_technology": {},
                "by_status": {
                    "running": len([api for api in self.apis if api.is_running]),
                    "stopped": len([api for api in self.apis if not api.is_running])
                },
                "port_conflicts": []
            }
        }
        
        # Add technology summary
        for api in self.apis:
            tech = api.technology
            if tech not in report_data["summary"]["by_technology"]:
                report_data["summary"]["by_technology"][tech] = 0
            report_data["summary"]["by_technology"][tech] += 1
        
        # Add port conflicts
        used_ports = {}
        for api in self.apis:
            if api.port:
                if api.port not in used_ports:
                    used_ports[api.port] = []
                used_ports[api.port].append(api.name)
        
        for port, apis in used_ports.items():
            if len(apis) > 1:
                report_data["summary"]["port_conflicts"].append({
                    "port": port,
                    "apis": apis
                })
        
        return json.dumps(report_data, indent=2)
    
    def _generate_html_report(self) -> str:
        """Generate HTML report"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Artifact Virtual - API Discovery Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .running {{ color: green; }}
        .stopped {{ color: red; }}
        .conflict {{ background-color: #ffeeee; }}
    </style>
</head>
<body>
    <h1>Artifact Virtual - API Discovery Report</h1>
    <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p><strong>Discovery Root:</strong> {self.root_path}</p>
    <p><strong>Total APIs Found:</strong> {len(self.apis)}</p>
    
    <h2>API Inventory</h2>
    <table>
        <tr>
            <th>Name</th>
            <th>File Path</th>
            <th>Port</th>
            <th>Technology</th>
            <th>Framework</th>
            <th>Status</th>
            <th>Endpoints</th>
        </tr>
"""
        
        for api in sorted(self.apis, key=lambda x: (x.technology, x.name)):
            status_class = "running" if api.is_running else "stopped"
            status_text = "Running" if api.is_running else "Stopped"
            endpoints_str = ", ".join(api.endpoints[:3])
            if len(api.endpoints) > 3:
                endpoints_str += f" (+{len(api.endpoints) - 3} more)"
            
            html += f"""        <tr>
            <td>{api.name}</td>
            <td><code>{api.file_path}</code></td>
            <td>{api.port or 'N/A'}</td>
            <td>{api.technology}</td>
            <td>{api.framework}</td>
            <td class="{status_class}">{status_text}</td>
            <td>{endpoints_str}</td>
        </tr>
"""
        
        html += """    </table>
</body>
</html>"""
        
        return html
    
    def save_report(self, filename: str, format: str = 'markdown'):
        """Save report to file"""
        report = self.generate_report(format)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        self.logger.info(f"Report saved to: {filename}")

def main():
    """Main CLI function (auto-structured and formatted output)"""
    import json
    import os
    parser = argparse.ArgumentParser(description='Discover APIs in Artifact Virtual system')
    parser.add_argument('--root', '-r', default='.', help='Root directory to scan')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--format', '-f', choices=['markdown', 'json', 'html'], 
                       default='markdown', help='Report format')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    args = parser.parse_args()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    # Initialize discovery
    discovery = APIDiscovery(args.root)
    apis = discovery.discover_apis()
    # Save standard report
    if args.output:
        output_path = Path(args.output)
    else:
        ext = 'md' if args.format == 'markdown' else args.format
        output_path = Path.cwd() / f"api_discovery_report.{ext}"
    discovery.save_report(str(output_path), args.format)
    # --- Custom: Save structured summary and data analysis ---
    summary = {
        "directory": str(Path(args.root).resolve()),
        "api_count": len(apis),
        "apis": [asdict(api) for api in apis],
        "metrics_files": [],
        "log_files": [],
        "report_files": [],
        "agent_scripts": [],
        "databases": [],
        "departments": {},
    }
    # Scan for metrics, logs, reports, agent scripts, dbs, departments
    for dirpath, dirnames, filenames in os.walk(args.root):
        rel_dir = os.path.relpath(dirpath, args.root)
        for fname in filenames:
            fpath = os.path.join(rel_dir, fname) if rel_dir != '.' else fname
            lcf = fname.lower()
            if lcf.endswith('.json') and 'activities' in lcf:
                summary['metrics_files'].append(fpath)
            if lcf.endswith('.log'):
                summary['log_files'].append(fpath)
            if lcf.endswith('.md') or lcf.endswith('.json') and 'report' in lcf:
                summary['report_files'].append(fpath)
            if lcf.endswith('.py') and 'agent' in lcf:
                summary['agent_scripts'].append(fpath)
            if lcf.endswith('.db'):
                summary['databases'].append(fpath)
        # Departmental structure
        parts = rel_dir.split(os.sep)
        if len(parts) > 1 and parts[0] not in ('__pycache__', 'node_modules', '.git', '.vscode', 'dist', 'build'):
            dept = parts[0]
            if dept not in summary['departments']:
                summary['departments'][dept] = []
            summary['departments'][dept].extend([os.path.join(rel_dir, f) for f in filenames])
    # Save structured summary as JSON in the same directory
    summary_path = Path(args.root).resolve() / 'api_discovery_structured_summary.json'
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    print(f"Structured API/data summary saved to: {summary_path}")
    print(f"API discovery report saved to: {output_path.resolve()}")


if __name__ == "__main__":
    main()