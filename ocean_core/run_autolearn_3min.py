#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Auto-Learning Runner - 3 minuta
Ekzekuto: python run_autolearn_3min.py
"""
import time
import sys

# Add path
sys.path.insert(0, '.')

from auto_learning_loop import AutoLearningLoop

def main():
    duration = 180  # 3 minuta
    start_time = time.time()
    
    print("=" * 70)
    print("🧠 AUTO-LEARNING - 3 MINUTA")
    print("=" * 70)
    
    loop = AutoLearningLoop()
    loop.print_header()
    
    cycle = 0
    while time.time() - start_time < duration:
        cycle += 1
        elapsed = int(time.time() - start_time)
        remaining = duration - elapsed
        
        print(f"\n⏱️ Cycle {cycle} | {elapsed}s elapsed | {remaining}s remaining")
        
        try:
            question = loop.generate_question()
            result = loop.learn(question)
            q_short = question[:50] + "..." if len(question) > 50 else question
            print(f"✅ Learned: {q_short}")
        except Exception as e:
            print(f"⚠️ Error: {e}")
        
        time.sleep(8)
    
    print("\n" + "=" * 70)
    print("✅ AUTO-LEARNING COMPLETED!")
    print(f"📚 Total cycles: {cycle}")
    entries = loop.knowledge.get("entries", [])
    print(f"📖 Knowledge entries: {len(entries)}")
    print("=" * 70)

if __name__ == "__main__":
    main()
