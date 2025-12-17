 #!/usr/bin/env python3
"""
simplified API interface test script
"""

import requests
import json
import time
from datetime import datetime

def test_streaming_api():
    """test streaming API interface"""
    print("=== test streaming API interface ===")
    
    # API endpoint
    url = "http://localhost:8100/chat/stream"
    
    # test data
    test_data = {
        "user_id": "test",
        "session_id": "test_session_006",
        "input": "这门课的course staff"
    }
    
    print(f"send request to: {url}")
    print(f"request data: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
    final_response = ""
    try:
        # send streaming request
        response = requests.post(
            url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            stream=True
        )
        
        if response.status_code == 200:
            print("✅ request successful, start receiving streaming data...")
            
            # process streaming response
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])
                            print(f"📦 [{datetime.now().isoformat()}] received data: {json.dumps(data, ensure_ascii=False, indent=2)}")
                            final_response += json.dumps(data, ensure_ascii=False, indent=2)
                            # check if finished
                            if data.get('status') == 'finished':
                                print("✅ streaming transmission finished")
                                print(f"final response: {final_response}")
                                break
                            
                            # check if there is an error
                            if data.get('status') == 'error':
                                print(f"❌ error: {data.get('error')}")
                                break
                                
                        except json.JSONDecodeError as e:
                            print(f"⚠️ JSON parse error: {e}")
                            print(f"original data: {line_str}")
            
        else:
            print(f"❌ request failed, status code: {response.status_code}")
            print(f"response content: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ connection failed - please ensure the API server is running (python api_interface.py)")
    except Exception as e:
        print(f"❌ error during test: {e}")

def test_health_check():
    """test health check interface"""
    print("\n=== test health check interface ===")
    
    try:
        response = requests.get("http://localhost:5000/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ health check passed: {data}")
        else:
            print(f"❌ health check failed, status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ connection failed - please ensure the API server is running")
    except Exception as e:
        print(f"❌ health check error: {e}")

def main():
    """main test function"""
    print("🚀 start simplified API interface test")
    print("=" * 50)
    
    # test health check
    # test_health_check()
    
    # test streaming API
    test_streaming_api()
    
    print("\n" + "=" * 50)
    print("✅ test completed")
    print("\n💡 tips:")
    print("1. ensure the API server is running: python api_interface.py")
    print("2. visit http://localhost:5000 to view the frontend interface")
    print("3. use browser developer tools to view the streaming effect")

if __name__ == "__main__":
    main()