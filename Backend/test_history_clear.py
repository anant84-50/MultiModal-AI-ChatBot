import requests

BASE_URL = "http://127.0.0.1:8000"

def test_history_clear():
    print("[1/3] Creating a test conversation...")
    chat_payload = {
        "message": "Hello, testing conversation creation for clear all test.",
        "enable_web_search": False,
        "speak_response": False
    }
    r = requests.post(f"{BASE_URL}/api/chat", json=chat_payload)
    assert r.status_code == 200, f"Chat call failed: {r.status_code} - {r.text}"
    convo_id = r.json()["conversation_id"]
    print(f"Created conversation: {convo_id}")

    print("[2/3] Checking conversations list...")
    r = requests.get(f"{BASE_URL}/api/conversations")
    assert r.status_code == 200
    convos = r.json()
    print(f"Active conversations before clear: {len(convos)}")
    assert len(convos) > 0, "Expected at least 1 conversation"

    print("[3/3] Testing DELETE /api/conversations (Clear All History)...")
    r = requests.delete(f"{BASE_URL}/api/conversations")
    assert r.status_code == 200, f"Clear all failed: {r.status_code} - {r.text}"
    print(f"Clear All Response: {r.json()}")

    # Verify conversations count is now 0
    r = requests.get(f"{BASE_URL}/api/conversations")
    assert r.status_code == 200
    convos_after = r.json()
    print(f"Active conversations after clear: {len(convos_after)}")
    assert len(convos_after) == 0, f"Expected 0 conversations, found {len(convos_after)}"

    print("\nHISTORY CLEAR ALL TEST PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_history_clear()
