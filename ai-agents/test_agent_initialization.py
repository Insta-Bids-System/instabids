#!/usr/bin/env python3
"""
Test script to reproduce agent initialization error
"""

import traceback
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

print("Testing agent initialization...")

# Test 1: Try importing EAA agent
try:
    print("1. Importing EAA agent...")
    from agents.eaa.agent import ExternalAcquisitionAgent
    print("   OK EAA import successful")
    
    print("2. Initializing EAA agent...")
    eaa = ExternalAcquisitionAgent()
    print("   OK EAA initialization successful")
    
except Exception as e:
    print(f"   ERROR EAA failed: {e}")
    print("   Traceback:")
    traceback.print_exc()

# Test 2: Try importing WFA agent
try:
    print("3. Importing WFA agent...")
    from agents.wfa.agent import WebsiteFormAutomationAgent
    print("   OK WFA import successful")
    
    print("4. Initializing WFA agent...")
    wfa = WebsiteFormAutomationAgent()
    print("   OK WFA initialization successful")
    
except Exception as e:
    print(f"   ERROR WFA failed: {e}")
    print("   Traceback:")
    traceback.print_exc()

# Test 3: Try orchestrator initialization
try:
    print("5. Testing orchestrator initialization...")
    from services.agent_orchestrator import AgentOrchestrator
    orchestrator = AgentOrchestrator()
    print("   OK Orchestrator initialization successful")
    
except Exception as e:
    print(f"   ERROR Orchestrator failed: {e}")
    print("   Traceback:")
    traceback.print_exc()

print("Testing complete!")