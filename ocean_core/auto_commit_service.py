#!/usr/bin/env python3
"""
🔄 CLISONIX AUTO-COMMIT SERVICE
================================
Bën commit automatik çdo 10 minuta

Funksione:
- Monitoron ndryshimet në learned_knowledge/
- Commit automatik çdo 10 minuta
- Nuk kërkon ndërhyrje manuale
"""

import subprocess
import time
import os
import sys
from datetime import datetime
from pathlib import Path

# Konfigurimi
COMMIT_INTERVAL_MINUTES = 10
REPO_PATH = Path(__file__).parent.parent  # Clisonix-cloud root
KNOWLEDGE_PATH = Path(__file__).parent / "learned_knowledge"

def run_git_command(args: list, cwd: str = None) -> tuple:
    """Ekzekuto komandë git"""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd or str(REPO_PATH),
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def check_git_repo() -> bool:
    """Kontrollo nëse jemi në git repo"""
    success, _, _ = run_git_command(["status"])
    return success

def get_changes() -> list:
    """Merr listën e ndryshimeve"""
    success, output, _ = run_git_command(["status", "--porcelain"])
    if success and output:
        return output.split('\n')
    return []

def get_knowledge_changes() -> list:
    """Merr ndryshimet vetëm në knowledge folder"""
    changes = get_changes()
    knowledge_changes = [c for c in changes if 'learned_knowledge' in c or 'auto_learned' in c]
    return knowledge_changes

def auto_commit():
    """Bën commit automatik"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Stage vetëm knowledge files
    run_git_command(["add", "ocean-core/learned_knowledge/"])
    run_git_command(["add", "ocean-core/auto_learned*.json"])
    
    # Kontrollo nëse ka ndryshime të staged
    success, output, _ = run_git_command(["diff", "--cached", "--name-only"])
    
    if not output:
        return False, "Asnjë ndryshim për commit"
    
    # Commit
    files_count = len(output.split('\n'))
    commit_msg = f"🧠 Auto-learn: {files_count} file(s) @ {timestamp}"
    
    success, stdout, stderr = run_git_command(["commit", "-m", commit_msg])
    
    if success:
        return True, f"Commit i suksesshëm: {commit_msg}"
    else:
        return False, f"Gabim: {stderr}"

def print_status():
    """Printo statusin aktual"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n" + "=" * 60)
    print("🔄 CLISONIX AUTO-COMMIT SERVICE")
    print("=" * 60)
    print(f"📁 Repo: {REPO_PATH}")
    print(f"⏱️  Interval: {COMMIT_INTERVAL_MINUTES} minuta")
    print(f"📅 Started: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60 + "\n")

def run_forever():
    """Ekzekuto pa fund"""
    if not check_git_repo():
        print("❌ Nuk jemi në git repository!")
        return
    
    print_status()
    commit_count = 0
    
    try:
        while True:
            # Afisho countdown
            for remaining in range(COMMIT_INTERVAL_MINUTES * 60, 0, -1):
                mins, secs = divmod(remaining, 60)
                
                # Merr info
                changes = get_knowledge_changes()
                changes_count = len(changes)
                
                # Status line
                status = f"\r⏳ Commit në: {mins:02d}:{secs:02d} | "
                status += f"📝 Ndryshime: {changes_count} | "
                status += f"✅ Commits: {commit_count}"
                
                sys.stdout.write(status + " " * 10)
                sys.stdout.flush()
                
                time.sleep(1)
            
            # Koha për commit
            print("\n")
            print("─" * 60)
            print(f"🔄 Duke bërë commit @ {datetime.now().strftime('%H:%M:%S')}")
            
            success, message = auto_commit()
            
            if success:
                commit_count += 1
                print(f"✅ {message}")
            else:
                print(f"ℹ️  {message}")
            
            print("─" * 60 + "\n")
            
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("🛑 AUTO-COMMIT NDALUR")
        print(f"📊 Total commits: {commit_count}")
        print("=" * 60)

def main():
    """Entry point"""
    global COMMIT_INTERVAL_MINUTES
    
    # Mundësi për interval custom
    if len(sys.argv) > 1:
        try:
            COMMIT_INTERVAL_MINUTES = int(sys.argv[1])
        except ValueError:
            pass
    
    print(f"\n🔄 Auto-commit çdo {COMMIT_INTERVAL_MINUTES} minuta")
    print("(Run with: python auto_commit_service.py <minutes>)\n")
    time.sleep(1)
    
    run_forever()

if __name__ == "__main__":
    main()
