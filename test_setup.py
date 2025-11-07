"""
Quick validation test for IEEE Paper Writer setup
"""

import os
import sys
from dotenv import load_dotenv

def test_setup():
    """Test that everything is configured correctly"""
    
    print("🔍 Testing Scientific Paper Writer Setup...")
    print("-" * 60)
    
    # Test 1: Environment file
    print("\n1. Checking .env file...")
    if os.path.exists(".env"):
        print("   ✅ .env file found")
    else:
        print("   ❌ .env file not found")
        print("   → Create it from .env.example")
        return False
    
    # Test 2: Load environment variables
    print("\n2. Loading environment variables...")
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if api_key and api_key != "your_gemini_api_key_here":
        print(f"   ✅ GOOGLE_API_KEY loaded (length: {len(api_key)})")
    else:
        print("   ❌ GOOGLE_API_KEY not configured")
        print("   → Add your API key to .env file")
        return False
    
    # Test 3: Import dependencies
    print("\n3. Testing imports...")
    try:
        from crewai import Agent, Task, Crew
        print("   ✅ crewai imported successfully")
    except ImportError as e:
        print(f"   ❌ crewai import failed: {e}")
        return False
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        print("   ✅ langchain_google_genai imported successfully")
    except ImportError as e:
        print(f"   ❌ langchain_google_genai import failed: {e}")
        print("   → Run: pip install --upgrade langchain-core langchain-google-genai")
        return False
    
    # Test 4: Initialize Gemini
    print("\n4. Testing Gemini connection...")
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.7,
            google_api_key=api_key
        )
        print("   ✅ Gemini LLM initialized")
        
        # Quick test invoke
        response = llm.invoke("Say 'Hello' in one word")
        print(f"   ✅ Gemini responding: {response.content[:50]}")
        
    except Exception as e:
        print(f"   ❌ Gemini connection failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nYou're ready to run: python ieee_paper_writer.py or scientific_paper_writer.py")
    return True

if __name__ == "__main__":
    success = test_setup()
    sys.exit(0 if success else 1)
