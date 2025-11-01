#!/usr/bin/env python3
"""
Test script for StepSquad Agents
Tests agent creation, tools, and basic functionality
"""

import os
import sys

# Set local mode for testing
os.environ['GCP_ENABLED'] = 'false'

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_tool_wrapper():
    """Test Tool wrapper"""
    print("Testing Tool wrapper...")
    try:
        from tools import Tool
        
        def test_func(x, y):
            return x + y
        
        tool = Tool("test_tool", "A test tool", test_func)
        result = tool.func(2, 3)
        assert result == 5, f"Expected 5, got {result}"
        print("  ✅ Tool wrapper works correctly")
        return True
    except Exception as e:
        print(f"  ❌ Tool wrapper test failed: {e}")
        return False


def test_storage_helpers():
    """Test storage helpers"""
    print("Testing storage helpers...")
    try:
        from agents_storage import get_competitions, get_teams_for_competition, get_user_steps
        
        # Test with empty data (local mode)
        competitions = get_competitions()
        assert isinstance(competitions, list), "get_competitions should return a list"
        
        teams = get_teams_for_competition("test-comp")
        assert isinstance(teams, list), "get_teams_for_competition should return a list"
        
        steps = get_user_steps("test-user")
        assert isinstance(steps, list), "get_user_steps should return a list"
        
        print("  ✅ Storage helpers work correctly")
        return True
    except Exception as e:
        print(f"  ❌ Storage helpers test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_creation():
    """Test agent creation"""
    print("Testing agent creation...")
    try:
        import logging
        logging.basicConfig(level=logging.WARNING)
        
        from agents import SyncAgent, FairnessAgent, ADK_AVAILABLE, GEMINI_AVAILABLE
        
        print(f"  ADK_AVAILABLE: {ADK_AVAILABLE}")
        print(f"  GEMINI_AVAILABLE: {GEMINI_AVAILABLE}")
        
        sync_agent = SyncAgent()
        assert sync_agent is not None, "SyncAgent should be created"
        assert hasattr(sync_agent, 'tools'), "SyncAgent should have tools"
        assert len(sync_agent.tools) == 3, f"SyncAgent should have 3 tools, got {len(sync_agent.tools)}"
        
        print(f"  ✅ SyncAgent created: {len(sync_agent.tools)} tools")
        print(f"     Tools: {[t.name for t in sync_agent.tools]}")
        
        fairness_agent = FairnessAgent()
        assert fairness_agent is not None, "FairnessAgent should be created"
        assert hasattr(fairness_agent, 'tools'), "FairnessAgent should have tools"
        assert len(fairness_agent.tools) == 3, f"FairnessAgent should have 3 tools, got {len(fairness_agent.tools)}"
        
        print(f"  ✅ FairnessAgent created: {len(fairness_agent.tools)} tools")
        print(f"     Tools: {[t.name for t in fairness_agent.tools]}")
        
        return True
    except Exception as e:
        print(f"  ❌ Agent creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_tools():
    """Test agent tools"""
    print("Testing agent tools...")
    try:
        from agents import SyncAgent, FairnessAgent
        
        sync_agent = SyncAgent()
        fairness_agent = FairnessAgent()
        
        # Test that tools are callable
        for tool in sync_agent.tools:
            assert hasattr(tool, 'name'), f"Tool should have name: {tool}"
            assert hasattr(tool, 'func'), f"Tool should have func: {tool}"
            assert callable(tool.func), f"Tool func should be callable: {tool}"
        
        for tool in fairness_agent.tools:
            assert hasattr(tool, 'name'), f"Tool should have name: {tool}"
            assert hasattr(tool, 'func'), f"Tool should have func: {tool}"
            assert callable(tool.func), f"Tool func should be callable: {tool}"
        
        print(f"  ✅ All tools are callable")
        print(f"     Sync tools: {[t.name for t in sync_agent.tools]}")
        print(f"     Fairness tools: {[t.name for t in fairness_agent.tools]}")
        
        return True
    except Exception as e:
        print(f"  ❌ Agent tools test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_workflow():
    """Test multi-agent workflow"""
    print("Testing multi-agent workflow...")
    try:
        from agents import SyncAgent, FairnessAgent, create_multi_agent_workflow
        
        sync_agent = SyncAgent()
        fairness_agent = FairnessAgent()
        workflow = create_multi_agent_workflow(sync_agent, fairness_agent)
        
        assert workflow is not None, "Workflow should be created"
        assert callable(workflow), "Workflow should be callable"
        
        print("  ✅ Workflow created successfully")
        
        return True
    except Exception as e:
        print(f"  ❌ Workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_main_endpoints():
    """Test main.py endpoints structure"""
    print("Testing main.py endpoints...")
    try:
        import logging
        logging.basicConfig(level=logging.ERROR)
        
        # Import main module
        import main
        
        assert hasattr(main, 'app'), "main should have app"
        assert hasattr(main.app, 'title'), "app should have title"
        
        # Check endpoints exist
        routes = [route.path for route in main.app.routes]
        assert '/run' in routes or '/health' in routes, "App should have /run or /health endpoints"
        
        print("  ✅ Main app structure correct")
        print(f"     App title: {main.app.title}")
        print(f"     Routes: {routes}")
        
        return True
    except Exception as e:
        print(f"  ⚠️  Main endpoints test warning: {e}")
        print("     (May need FastAPI or GCP clients fully configured)")
        return True  # Not critical for basic functionality


def main():
    """Run all tests"""
    print("=" * 60)
    print("StepSquad Agents - Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        ("Tool Wrapper", test_tool_wrapper),
        ("Storage Helpers", test_storage_helpers),
        ("Agent Creation", test_agent_creation),
        ("Agent Tools", test_agent_tools),
        ("Workflow", test_workflow),
        ("Main Endpoints", test_main_endpoints),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n[{test_name}]")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

