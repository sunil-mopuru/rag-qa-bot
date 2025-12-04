"""
Example script to test the Q&A bot
"""
import requests
import json
import sys


def test_health():
    """Test the health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    response = requests.get("http://localhost:8000/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_ask_question(question: str):
    """Test asking a question"""
    print(f"\n=== Testing Question: {question} ===")
    
    payload = {
        "question": question,
        "top_k": 3
    }
    
    response = requests.post(
        "http://localhost:8000/api/ask",
        json=payload
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nAnswer:\n{result['answer']}")
        print(f"\nSources ({len(result['sources'])}):")
        for i, source in enumerate(result['sources'], 1):
            print(f"\n{i}. {source['title']}")
            print(f"   URL: {source['url']}")
            print(f"   Snippet: {source['snippet']}")
    else:
        print(f"Error: {response.text}")


def test_stats():
    """Test the stats endpoint"""
    print("\n=== Testing Stats Endpoint ===")
    response = requests.get("http://localhost:8000/api/stats")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def main():
    """Main test function"""
    print("RAG Q&A Bot Test Script")
    print("=" * 50)
    
    # Test health
    if not test_health():
        print("\nError: API server is not healthy. Please check if it's running.")
        sys.exit(1)
    
    # Test stats
    test_stats()
    
    # Test questions
    if len(sys.argv) > 1:
        # Use command line argument
        question = " ".join(sys.argv[1:])
        test_ask_question(question)
    else:
        # Use example questions
        example_questions = [
            "What is this website about?",
            "How can I get started?",
            "What are the main features?"
        ]
        
        for question in example_questions:
            test_ask_question(question)
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to API server.")
        print("Please make sure the server is running with: python main.py")
        sys.exit(1)
