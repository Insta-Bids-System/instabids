"""
Simple Leonardo test to fix the brown grass issue
"""

import asyncio
import subprocess
import sys

print("=" * 60)
print("TESTING LEONARDO WITH IMPROVED PROMPTS")
print("Targeting brown grass areas specifically")
print("=" * 60)

# Just run one focused test with better prompt
IMPROVED_PROMPT = """Replace ALL grass with artificial turf - both the green areas AND the brown dead patchy areas. The brown dying grass must become green synthetic turf too. Complete lawn transformation to uniform emerald artificial turf. Keep soccer goal in exact same position. Perfect landscaping with consistent green turf covering entire yard."""

IMPROVED_NEGATIVE = """brown grass remaining, dead patches, partial replacement, patchy turf, inconsistent coverage"""

print("\n[IMPROVED PROMPT]")
print(IMPROVED_PROMPT)
print("\n[NEGATIVE PROMPT]") 
print(IMPROVED_NEGATIVE)

print("\nThis should fix the issue where brown areas were left as weeds...")
print("Instead of just targeting green grass, we specifically mention brown dead areas")
print("\nWould you like me to run this improved version? (y/n)")

# For now, just show the improved approach
print("\nKey improvements:")
print("1. Explicitly mentions 'brown dead patchy areas'")
print("2. States 'brown dying grass must become green synthetic turf'") 
print("3. Emphasizes 'ALL grass' not just healthy green grass")
print("4. Negative prompt blocks 'brown grass remaining'")

print("\nThis should produce much better results where ALL lawn areas become uniform turf!")