#!/usr/bin/env python3
"""
Ocean Core v2 Deployment Package - Manifest Verification
Verifies all required deployment files are present and ready
"""

import os
import sys
from datetime import datetime
from pathlib import Path


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'

def check_file_exists(filepath):
    """Check if file exists and return status"""
    return os.path.isfile(filepath)

def format_file_size(size_bytes):
    """Format bytes to human readable"""
    for unit in ['B', 'KB', 'MB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f}GB"

def print_colored(text, color):
    """Print colored text"""
    print(f"{color}{text}{Colors.END}")

def main():
    print("\n")
    print_colored("╔══════════════════════════════════════════════════════════════╗", Colors.CYAN)
    print_colored("║  OCEAN CORE v2 DEPLOYMENT PACKAGE MANIFEST VERIFICATION      ║", Colors.CYAN)
    print_colored("║  Version: 2.0.0 - Production Ready                           ║", Colors.CYAN)
    print_colored("╚══════════════════════════════════════════════════════════════╝", Colors.CYAN)
    print()
    
    # Define deployment package structure
    DEPLOYMENT_FILES = {
        "Core Deployment Artifacts": [
            ("docker-compose.yml", "Docker Compose configuration (CRITICAL)"),
            ("ocean-core/Dockerfile", "Ocean Core Full container image"),
            ("ocean-core/Dockerfile.multimodal", "Ocean Core Multimodal container"),
            ("ocean-core/Dockerfile.strict-chat", "Ocean Core Strict Chat container"),
            ("ocean-core/Dockerfile.blerina", "Ocean Core Blerina container"),
        ],
        "Deployment Automation Scripts": [
            ("HETZNER_DEPLOY_v2.sh", "Bash deployment script (Linux/macOS)"),
            ("HETZNER_DEPLOY_v2.ps1", "PowerShell deployment script (Windows)"),
        ],
        "Verification Tools": [
            ("verify_ocean_core_v2.py", "Health verification utility"),
        ],
        "Documentation": [
            ("START_HERE_DEPLOYMENT_GUIDE.md", "Entry point guide - READ FIRST"),
            ("OCEAN_CORE_v2_DEPLOYMENT_READY.md", "Quick reference guide"),
            ("OCEAN_CORE_v2_HETZNER_GUIDE.md", "Complete deployment procedures"),
            ("OCEAN_CORE_v2_DEPLOYMENT_PACKAGE_SUMMARY.md", "Detailed package overview"),
            ("DEPLOYMENT_EXECUTION_CHECKLIST.md", "Step-by-step checklist"),
            ("DEPLOYMENT_COMPLETE_SUMMARY.md", "Final summary document"),
        ]
    }
    
    total_files = 0
    found_files = 0
    total_size = 0
    
    # Check each category
    for category, files in DEPLOYMENT_FILES.items():
        print_colored(f"\n📦 {category}", Colors.BLUE)
        print("-" * 70)
        
        for filepath, description in files:
            total_files += 1
            exists = check_file_exists(filepath)
            
            if exists:
                found_files += 1
                size = os.path.getsize(filepath)
                total_size += size
                size_str = format_file_size(size)
                print(f"  {Colors.GREEN}✅{Colors.END} {filepath:<30} ({size_str:>8}) - {description}")
            else:
                print(f"  {Colors.RED}❌{Colors.END} {filepath:<30} (MISSING) - {description}")
    
    # Summary
    print("\n" + "=" * 70)
    print_colored("📊 MANIFEST SUMMARY", Colors.BLUE)
    print("=" * 70)
    
    verification_status = found_files == total_files
    
    print(f"Total Files Expected: {total_files}")
    print(f"Files Found: {Colors.GREEN if found_files == total_files else Colors.RED}{found_files}{Colors.END}")
    print(f"Total Size: {format_file_size(total_size)}")
    print()
    
    if verification_status:
        print_colored("✅ ALL DEPLOYMENT FILES PRESENT AND ACCOUNTED FOR", Colors.GREEN)
        print_colored("🚀 DEPLOYMENT PACKAGE IS COMPLETE AND READY", Colors.GREEN)
    else:
        missing = total_files - found_files
        print_colored(f"❌ {missing} FILE(S) MISSING - DEPLOYMENT NOT READY", Colors.RED)
        return 1
    
    # Additional checks
    print("\n" + "=" * 70)
    print_colored("🔍 ADDITIONAL CHECKS", Colors.BLUE)
    print("=" * 70)
    
    # Check script permissions
    if check_file_exists("HETZNER_DEPLOY_v2.sh"):
        import stat
        mode = os.stat("HETZNER_DEPLOY_v2.sh").st_mode
        is_executable = bool(mode & stat.S_IXUSR)
        status = f"{Colors.GREEN}✅ Executable{Colors.END}" if is_executable else f"{Colors.YELLOW}⚠️ Not executable (run: chmod +x HETZNER_DEPLOY_v2.sh){Colors.END}"
        print(f"  Bash Script Permissions: {status}")
    
    # Check if verification script can be run
    if check_file_exists("verify_ocean_core_v2.py"):
        print(f"  {Colors.GREEN}✅{Colors.END} Verification script ready (python verify_ocean_core_v2.py --host <host>)")
    
    # Documentation presence
    doc_count = sum(1 for f, _ in DEPLOYMENT_FILES.get("Documentation", []) if check_file_exists(f))
    print(f"  Documentation: {Colors.GREEN}{doc_count} guides included{Colors.END}")
    
    print("\n" + "=" * 70)
    print_colored("🎯 QUICK START COMMANDS", Colors.BLUE)
    print("=" * 70)
    
    print("\n1. Read deployment guide first:")
    print_colored("   cat START_HERE_DEPLOYMENT_GUIDE.md", Colors.CYAN)
    
    print("\n2. Choose deployment method:")
    print_colored("   # Option 1 (Linux/macOS):", Colors.CYAN)
    print_colored("   chmod +x HETZNER_DEPLOY_v2.sh", Colors.CYAN)
    print_colored("   ./HETZNER_DEPLOY_v2.sh 46.225.14.83 root 22", Colors.CYAN)
    
    print_colored("   # Option 2 (Windows PowerShell):", Colors.CYAN)
    print_colored("   ./HETZNER_DEPLOY_v2.ps1 -HetznerHost 46.225.14.83 -HetznerUser root", Colors.CYAN)
    
    print("\n3. Verify deployment:")
    print_colored("   python verify_ocean_core_v2.py --host 46.225.14.83", Colors.CYAN)
    
    print("\n" + "=" * 70)
    print_colored("📋 DEPLOYMENT READINESS CHECKLIST", Colors.BLUE)
    print("=" * 70)
    
    checklist = [
        ("All deployment files present", verification_status),
        ("Docker Compose file exists", check_file_exists("docker-compose.yml")),
        ("Deployment scripts exist", 
         check_file_exists("HETZNER_DEPLOY_v2.sh") or check_file_exists("HETZNER_DEPLOY_v2.ps1")),
        ("Verification script exists", check_file_exists("verify_ocean_core_v2.py")),
        ("Documentation complete", doc_count >= 5),
    ]
    
    all_ready = all(status for _, status in checklist)
    
    for item, status in checklist:
        symbol = f"{Colors.GREEN}✅{Colors.END}" if status else f"{Colors.RED}❌{Colors.END}"
        print(f"  {symbol} {item}")
    
    print("\n" + "=" * 70)
    
    if all_ready:
        print_colored("✨ DEPLOYMENT PACKAGE IS 100% READY FOR PRODUCTION ✨", Colors.GREEN)
        print_colored("🚀 You can start deployment immediately!", Colors.GREEN)
    else:
        print_colored("⚠️  Some items missing - please review and prepare", Colors.YELLOW)
    
    print("\n" + "=" * 70)
    print(f"Verification Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_colored("Package Version: 2.0.0 - Production Ready", Colors.CYAN)
    print("=" * 70)
    print()
    
    return 0 if all_ready else 1

if __name__ == "__main__":
    sys.exit(main())
