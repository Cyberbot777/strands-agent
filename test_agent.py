"""
Local testing script for the Strands agent.
This file is NOT deployed to AWS AgentCore.
Run: python test_agent.py
"""
from my_agent import agent


def test_agent():
    """Test the agent with various prompts."""
    print("\n" + "=" * 60)
    print("TESTING STRANDS AGENT")
    print("=" * 60)
    
    test_prompts = [
        "Hello! What can you help me with?",
        "Can you make HTTP requests?",
        "What tools do you have access to?"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n[Test {i}/{len(test_prompts)}]")
        print(f"Prompt: {prompt}")
        print("-" * 60)
        
        try:
            result = agent(prompt)
            print(f"Response: {result.message}")
        except Exception as e:
            print(f"ERROR: {e}")
        
        print("-" * 60)
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETE")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    test_agent()

