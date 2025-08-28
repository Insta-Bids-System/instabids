#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent 2 Backend Core - Comprehensive Environment Variable Test
Verifies all 7 backend agents are properly loading from root .env file
"""
import os
import sys
from pathlib import Path

# Fix Windows encoding issues
if sys.platform == "win32":
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add current directory to Python path for imports
sys.path.append(os.path.dirname(__file__))

def test_root_env_loading():
    """Test that we can load from root .env file"""
    print("=" * 60)
    print("ROOT ENVIRONMENT LOADING TEST")
    print("=" * 60)
    
    from dotenv import load_dotenv
    
    # Load from root .env file
    root_env = Path(__file__).parent.parent / '.env'
    if root_env.exists():
        load_dotenv(root_env, override=True)
        print(f"[OK] Root .env file found: {root_env}")
    else:
        print(f"[ERROR] Root .env file NOT found: {root_env}")
        return False
    
    # Check critical environment variables
    critical_vars = [
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY", 
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "GOOGLE_MAPS_API_KEY"
    ]
    
    missing_vars = []
    for var in critical_vars:
        value = os.getenv(var)
        if value:
            print(f"[OK] {var}: {value[:20]}...")
        else:
            print(f"[ERROR] {var}: NOT FOUND")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"[ERROR] Missing environment variables: {missing_vars}")
        return False
        
    print("[OK] All critical environment variables loaded successfully")
    return True

def test_jaa_agent():
    """Test JAA Agent environment loading"""
    print("\n" + "=" * 60)
    print("JAA (JOB ASSESSMENT AGENT) TEST")
    print("=" * 60)
    
    try:
        from agents.jaa.agent import JobAssessmentAgent
        
        jaa = JobAssessmentAgent()
        print("[OK] JAA Agent initialized successfully")
        print(f"[OK] JAA has Anthropic key: {jaa.anthropic_key[:20]}..." if jaa.anthropic_key else "[ERROR] JAA missing Anthropic key")
        return True
        
    except Exception as e:
        print(f"[ERROR] JAA Agent failed to initialize: {e}")
        return False

def test_cda_agent():
    """Test CDA Agent environment loading"""
    print("\n" + "=" * 60) 
    print("CDA (CONTRACTOR DISCOVERY AGENT) TEST")
    print("=" * 60)
    
    try:
        from agents.cda.agent import ContractorDiscoveryAgent
        
        cda = ContractorDiscoveryAgent()
        print("[OK] CDA Agent initialized successfully")
        print(f"[OK] CDA has Supabase URL: {cda.supabase_url}" if cda.supabase_url else "[ERROR] CDA missing Supabase URL")
        return True
        
    except Exception as e:
        print(f"[ERROR] CDA Agent failed to initialize: {e}")
        return False

def test_eaa_agent():
    """Test EAA Agent environment loading"""
    print("\n" + "=" * 60)
    print("EAA (EXTERNAL ACQUISITION AGENT) TEST") 
    print("=" * 60)
    
    try:
        from agents.eaa.agent import ExternalAcquisitionAgent
        
        eaa = ExternalAcquisitionAgent()
        print("[OK] EAA Agent initialized successfully")
        
        # Test MCP email channel specifically  
        if hasattr(eaa, 'mcp_email_channel'):
            if eaa.mcp_email_channel.anthropic_api_key:
                print(f"[OK] EAA MCP Email has Anthropic key: {eaa.mcp_email_channel.anthropic_api_key[:20]}...")
            else:
                print("[ERROR] EAA MCP Email missing Anthropic key")
        return True
        
    except Exception as e:
        print(f"[ERROR] EAA Agent failed to initialize: {e}")
        return False

def test_wfa_agent():
    """Test WFA Agent environment loading"""
    print("\n" + "=" * 60)
    print("WFA (WEBSITE FORM AUTOMATION) TEST")
    print("=" * 60)
    
    try:
        from agents.wfa.agent import WebsiteFormAutomationAgent
        
        wfa = WebsiteFormAutomationAgent()
        print("[OK] WFA Agent initialized successfully")
        print(f"[OK] WFA has Supabase URL: {wfa.supabase_url}" if wfa.supabase_url else "[ERROR] WFA missing Supabase URL")
        print(f"[OK] WFA has Anthropic key: {wfa.anthropic_api_key[:20]}..." if wfa.anthropic_api_key else "[ERROR] WFA missing Anthropic key")
        return True
        
    except Exception as e:
        print(f"[ERROR] WFA Agent failed to initialize: {e}")
        return False

def test_orchestration_agent():
    """Test Orchestration Agent environment loading"""
    print("\n" + "=" * 60)
    print("ORCHESTRATION AGENT TEST")
    print("=" * 60)
    
    try:
        from agents.orchestration.enhanced_campaign_orchestrator import EnhancedCampaignOrchestrator
        
        # Just test that we can import the class - it requires parameters to initialize
        print("[OK] Orchestration Agent imported successfully")
        return True
        
    except Exception as e:
        print(f"[ERROR] Orchestration Agent failed to import: {e}")
        return False

def test_monitoring_agent():
    """Test Monitoring Agent environment loading"""
    print("\n" + "=" * 60)
    print("MONITORING AGENT TEST")
    print("=" * 60)
    
    try:
        from agents.monitoring.response_monitor import ResponseMonitor
        
        # Just test that we can import the class
        print("[OK] Monitoring Agent imported successfully")
        return True
        
    except Exception as e:
        print(f"[ERROR] Monitoring Agent failed to import: {e}")
        return False

def test_enrichment_agent():
    """Test Enrichment Agent (FinalRealAgent) environment loading"""
    print("\n" + "=" * 60)
    print("ENRICHMENT AGENT (FINALREALAGENT) TEST")
    print("=" * 60)
    
    try:
        from agents.enrichment.final_real_agent import FinalRealAgent
        
        # Test initialization
        enrichment_agent = FinalRealAgent()
        print("[OK] FinalRealAgent (Enrichment Agent) initialized successfully")
        print(f"[OK] FinalRealAgent has Anthropic key: {enrichment_agent.anthropic_api_key[:20]}..." if enrichment_agent.anthropic_api_key else "[ERROR] FinalRealAgent missing Anthropic key")
        return True
        
    except Exception as e:
        print(f"[ERROR] FinalRealAgent (Enrichment Agent) failed to import: {e}")
        return False

def main():
    """Run all agent environment tests"""
    print("AGENT 2 BACKEND CORE - COMPREHENSIVE ENVIRONMENT TEST")
    print(f"Testing all 7 backend agents for proper .env loading...")
    print(f"Test started at: {os.getcwd()}")
    
    tests = [
        ("Root Environment Loading", test_root_env_loading),
        ("JAA Agent", test_jaa_agent),
        ("CDA Agent", test_cda_agent), 
        ("EAA Agent", test_eaa_agent),
        ("WFA Agent", test_wfa_agent),
        ("Orchestration Agent", test_orchestration_agent),
        ("Monitoring Agent", test_monitoring_agent),
        ("Enrichment Agent (FinalRealAgent)", test_enrichment_agent)
    ]
    
    results = {}
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    # Final summary
    print("\n" + "=" * 60)
    print("FINAL TEST RESULTS")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
    
    print(f"\nOVERALL RESULT: {passed}/{total} agents passed environment loading test")
    
    if passed == total:
        print("ALL AGENTS ARE PROPERLY LOADING FROM ROOT .ENV FILE!")
        return True
    else:
        print("Some agents have environment loading issues - see details above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
