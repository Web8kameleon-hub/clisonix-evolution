#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
CLISONIX OCEAN CORE v2 - COMPREHENSIVE VERIFICATION SUITE
Purpose: Verify all Ocean Core deployments and health status
Version: 2.0.0
═══════════════════════════════════════════════════════════════════════════
"""

import json
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple

import requests

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class OceanService:
    name: str
    container: str
    port: int
    description: str

OCEAN_SERVICES = [
    OceanService("ocean-core", "clisonix-ocean-core", 8030, 
                 "Primary Brain (MegaLayerEngine, ResponseOrchestratorV5)"),
    OceanService("ocean-core-multimodal", "clisonix-ocean-core-multimodal", 8033,
                 "Vision/Audio/Document/Reasoning Processing"),
    OceanService("ocean-core-strict-chat", "clisonix-ocean-core-strict-chat", 8035,
                 "Admin Mode with IRON RULES Enforcement"),
    OceanService("ocean-core-blerina", "clisonix-ocean-core-blerina", 8032,
                 "Advanced Architecture (EAP, Gap Detection)"),
]

# Colors
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
NC = '\033[0m'  # No Color

# ═══════════════════════════════════════════════════════════════════════════
# LOGGING FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def log(message: str, level: str = "INFO", color: str = BLUE):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{color}[{level}]{NC} {timestamp} - {message}")

def log_success(message: str):
    log(message, "SUCCESS", GREEN)

def log_warning(message: str):
    log(message, "WARNING", YELLOW)

def log_error(message: str):
    log(message, "ERROR", RED)

def log_info(message: str):
    log(message, "INFO", CYAN)

# ═══════════════════════════════════════════════════════════════════════════
# VERIFICATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

class OceanCoreVerifier:
    def __init__(self, host: str = "localhost", remote: bool = False):
        self.host = host
        self.remote = remote
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "host": host,
            "services": {},
            "summary": {
                "total": 0,
                "healthy": 0,
                "unhealthy": 0,
                "unreachable": 0
            }
        }
    
    def ssh_exec(self, command: str) -> Tuple[bool, str]:
        """Execute command via SSH"""
        try:
            result = subprocess.run(
                f"ssh root@{self.host} '{command}'",
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "SSH command timed out"
        except Exception as e:
            return False, str(e)
    
    def check_docker_running(self, container: str) -> bool:
        """Check if Docker container is running"""
        try:
            if self.remote:
                success, output = self.ssh_exec(
                    f"docker ps --filter 'name={container}' --format '{{{{.State}}}}'",
                )
                return success and "running" in output.lower()
            else:
                result = subprocess.run(
                    ["docker", "ps", "--filter", f"name={container}", "--format", "{{.State}}"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return result.returncode == 0 and "running" in result.stdout.lower()
        except Exception as e:
            log_error(f"Error checking Docker: {e}")
            return False
    
    def check_health_endpoint(self, port: int, timeout: int = 5) -> Tuple[bool, int, str]:
        """Check health endpoint response"""
        url = f"http://{self.host}:{port}/health"
        try:
            response = requests.get(url, timeout=timeout)
            return True, response.status_code, response.text
        except requests.exceptions.Timeout:
            return False, 0, "Request timed out"
        except requests.exceptions.ConnectionError:
            return False, 0, "Connection refused"
        except Exception as e:
            return False, 0, str(e)
    
    def verify_service(self, service: OceanService) -> Dict:
        """Verify a single service"""
        log_info(f"Verifying {service.name}...")
        
        result = {
            "name": service.name,
            "container": service.container,
            "port": service.port,
            "description": service.description,
            "checks": {}
        }
        
        # Check 1: Docker container running
        docker_running = self.check_docker_running(service.container)
        result["checks"]["docker_running"] = docker_running
        
        if docker_running:
            log_success(f"  ✓ Docker container '{service.container}' running")
        else:
            log_error(f"  ✗ Docker container '{service.container}' NOT running")
        
        # Check 2: Health endpoint
        health_ok, status_code, response_text = self.check_health_endpoint(service.port)
        result["checks"]["health_endpoint"] = {
            "reachable": health_ok,
            "status_code": status_code,
            "response": response_text[:200] if response_text else ""
        }
        
        if health_ok and status_code == 200:
            log_success(f"  ✓ Health endpoint responding (HTTP {status_code})")
        else:
            if health_ok:
                log_warning(f"  ⚠ Health endpoint responding but status {status_code}")
            else:
                log_error(f"  ✗ Health endpoint unreachable: {response_text}")
        
        # Determine overall status
        is_healthy = docker_running and health_ok and status_code == 200
        result["status"] = "HEALTHY" if is_healthy else ("WARNING" if health_ok else "UNHEALTHY")
        
        return result
    
    def verify_all(self) -> Dict:
        """Verify all Ocean Core services"""
        log_info(f"Starting verification of Ocean Core services on {self.host}")
        log_info("=" * 70)
        
        self.results["summary"]["total"] = len(OCEAN_SERVICES)
        
        for service in OCEAN_SERVICES:
            service_result = self.verify_service(service)
            self.results["services"][service.name] = service_result
            
            if service_result["status"] == "HEALTHY":
                self.results["summary"]["healthy"] += 1
            elif service_result["status"] == "WARNING":
                self.results["summary"]["unhealthy"] += 1
            else:
                self.results["summary"]["unreachable"] += 1
            
            log_info("")
        
        return self.results
    
    def print_summary(self):
        """Print verification summary"""
        print(f"\n{CYAN}{'='*70}{NC}")
        print(f"{CYAN}OCEAN CORE v2 VERIFICATION SUMMARY{NC}")
        print(f"{CYAN}{'='*70}{NC}\n")
        
        summary = self.results["summary"]
        total = summary["total"]
        healthy = summary["healthy"]
        unhealthy = summary["unhealthy"]
        unreachable = summary["unreachable"]
        
        # Summary statistics
        print(f"Host: {self.results['host']}")
        print(f"Timestamp: {self.results['timestamp']}\n")
        
        print(f"Total Services: {total}")
        print(f"  {GREEN}✓ Healthy: {healthy}{NC}")
        print(f"  {YELLOW}⚠ Warning: {unhealthy}{NC}")
        print(f"  {RED}✗ Unhealthy: {unreachable}{NC}\n")
        
        # Service details
        print("Service Status:")
        print("-" * 70)
        
        for service_name, service_result in self.results["services"].items():
            status = service_result["status"]
            port = service_result["port"]
            
            if status == "HEALTHY":
                status_color = GREEN
                status_symbol = "✓"
            elif status == "WARNING":
                status_color = YELLOW
                status_symbol = "⚠"
            else:
                status_color = RED
                status_symbol = "✗"
            
            print(f"{status_color}{status_symbol}{NC} {service_name:30s} ({status_color}{status:10s}{NC}) Port {port}")
        
        print("-" * 70)
        
        # Overall result
        if healthy == total:
            log_success("✅ All Ocean Core services are HEALTHY!")
            return True
        elif healthy + unhealthy == total:
            log_warning("⚠️ Some services have warnings but are responding")
            return True
        else:
            log_error("❌ Some services are UNHEALTHY or unreachable")
            return False
    
    def export_json(self, filepath: str):
        """Export results to JSON"""
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        log_success(f"Results exported to {filepath}")
    
    def export_html(self, filepath: str):
        """Export results to HTML report"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Ocean Core v2 Verification Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .header {{ background-color: #1e3c72; color: white; padding: 20px; border-radius: 5px; }}
        .summary {{ margin: 20px 0; padding: 15px; background-color: white; border-radius: 5px; }}
        .service {{ margin: 10px 0; padding: 15px; background-color: white; border-left: 5px solid #ccc; }}
        .healthy {{ border-left-color: #28a745; background-color: #f8fff9; }}
        .warning {{ border-left-color: #ffc107; background-color: #fffbf0; }}
        .unhealthy {{ border-left-color: #dc3545; background-color: #fff8f8; }}
        .status-badge {{ 
            padding: 5px 10px; 
            border-radius: 3px; 
            font-weight: bold; 
            display: inline-block;
        }}
        .status-healthy {{ background-color: #28a745; color: white; }}
        .status-warning {{ background-color: #ffc107; color: black; }}
        .status-unhealthy {{ background-color: #dc3545; color: white; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🌊 Ocean Core v2 Verification Report</h1>
        <p>Host: {self.results['host']}</p>
        <p>Timestamp: {self.results['timestamp']}</p>
    </div>
    
    <div class="summary">
        <h2>Summary</h2>
        <p>Total Services: {self.results['summary']['total']}</p>
        <p><span style="color: #28a745;">✓ Healthy: {self.results['summary']['healthy']}</span></p>
        <p><span style="color: #ffc107;">⚠ Warning: {self.results['summary']['unhealthy']}</span></p>
        <p><span style="color: #dc3545;">✗ Unhealthy: {self.results['summary']['unreachable']}</span></p>
    </div>
    
    <h2>Services</h2>
"""
        
        for service_name, service_result in self.results["services"].items():
            status = service_result["status"].lower()
            status_class = f"status-{status if status != 'unhealthy' else 'unhealthy'}"
            service_class = f"service {status}"
            
            health_response = service_result["checks"]["health_endpoint"]["response"][:100]
            
            html += f"""
    <div class="{service_class}">
        <h3>{service_name}</h3>
        <p>Description: {service_result['description']}</p>
        <p>Port: {service_result['port']}</p>
        <p>Container: {service_result['container']}</p>
        <p>Status: <span class="{status_class}">{service_result['status'].upper()}</span></p>
        <p>Docker Running: {"✓ Yes" if service_result['checks']['docker_running'] else "✗ No"}</p>
        <p>Health Response: {health_response}</p>
    </div>
"""
        
        html += """
</body>
</html>
"""
        
        with open(filepath, 'w') as f:
            f.write(html)
        log_success(f"HTML report exported to {filepath}")


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Verify Ocean Core v2 deployment health and status"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Target host (IP or hostname). Default: localhost"
    )
    parser.add_argument(
        "--remote",
        action="store_true",
        help="Use SSH to connect (for remote verification)"
    )
    parser.add_argument(
        "--json",
        help="Export results to JSON file"
    )
    parser.add_argument(
        "--html",
        help="Export results to HTML report file"
    )
    
    args = parser.parse_args()
    
    # Create verifier
    verifier = OceanCoreVerifier(host=args.host, remote=args.remote)
    
    # Run verification
    print()
    print(f"{BLUE}╔════════════════════════════════════════════════════════════════════╗{NC}")
    print(f"{BLUE}║  OCEAN CORE v2 VERIFICATION SUITE                                 ║{NC}")
    print(f"{BLUE}║  Version 2.0.0                                                    ║{NC}")
    print(f"{BLUE}╚════════════════════════════════════════════════════════════════════╝{NC}")
    print()
    
    verifier.verify_all()
    success = verifier.print_summary()
    
    # Export if requested
    if args.json:
        verifier.export_json(args.json)
    
    if args.html:
        verifier.export_html(args.html)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
