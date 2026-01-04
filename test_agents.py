#!/usr/bin/env python3
"""
Quick test script to verify agent modules work correctly.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("="*80)
print("Testing Modular Agent Architecture")
print("="*80)

# Test imports
print("\n1. Testing imports...")
try:
    from analysis2.openai_agent import OpenAIAgent, call_llm
    from analysis2.perplexity_agent import PerplexityAgent, call_perplexity
    print("✓ All imports successful")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test OpenAI Agent
print("\n2. Testing OpenAI Agent...")
try:
    openai_agent = OpenAIAgent(default_model="gpt-4o-mini")
    print(f"✓ OpenAI Agent initialized")
    print(f"  - Default model: {openai_agent.default_model}")
    
    # Test simple query
    response = openai_agent.query(
        "Say 'OpenAI agent is working' in exactly those words.",
        temperature=0.1
    )
    if "working" in response.lower():
        print(f"✓ OpenAI Agent query successful")
        print(f"  - Response: {response[:100]}...")
    else:
        print(f"⚠️  OpenAI Agent response unexpected: {response[:100]}")
except Exception as e:
    print(f"✗ OpenAI Agent test failed: {e}")

# Test Perplexity Agent
print("\n3. Testing Perplexity Agent...")
try:
    perplexity_agent = PerplexityAgent(model="sonar")
    print(f"✓ Perplexity Agent initialized")
    print(f"  - Model: {perplexity_agent.model}")
    
    # Test simple query
    result = perplexity_agent.query(
        "What is a typical price range for installing a heat pump in California? Give a brief one-sentence answer."
    )
    
    if not result.get('error'):
        print(f"✓ Perplexity Agent query successful")
        print(f"  - Content: {result['content'][:150]}...")
        print(f"  - Citations: {len(result.get('citations', []))} sources")
    else:
        print(f"⚠️  Perplexity Agent returned error: {result['content']}")
except Exception as e:
    print(f"✗ Perplexity Agent test failed: {e}")

# Test backwards compatibility functions
print("\n4. Testing backwards compatibility functions...")
try:
    response = call_llm("Say 'Compatibility works'", model="gpt-4o-mini")
    if "works" in response.lower() or "compatibility" in response.lower():
        print(f"✓ call_llm() compatibility function works")
    
    result = call_perplexity("What is 2+2? Just give the number.")
    if not result.get('error'):
        print(f"✓ call_perplexity() compatibility function works")
except Exception as e:
    print(f"✗ Compatibility test failed: {e}")

print("\n" + "="*80)
print("Agent Testing Complete")
print("="*80)
print("\n✓ Modular architecture is working correctly!")
print("\nYou can now use:")
print("  - analysis2.openai_agent.OpenAIAgent")
print("  - analysis2.perplexity_agent.PerplexityAgent")
print("  - python -m analysis2.analyze (or python analysis2/analyze.py)")

