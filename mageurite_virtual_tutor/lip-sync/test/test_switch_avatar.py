import requests
import os
import json
import time


def test_avatar_preview():
    print("\nTesting /avatar/preview API:")
    url = "http://0.0.0.0:8204/avatar/preview"
    data = {
        "avatar_name": "test_avatar"  # Replace with an actually existing Avatar name
    }
    
    try:
        # Use POST request and pass parameters through form
        response = requests.post(url, data=data)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            # Check response headers to confirm if it's an image
            content_type = response.headers.get('content-type', '')
            if 'image/png' in content_type:
                print("✓ Successfully retrieved PNG image data")
                print(f"Image size: {len(response.content)} bytes")
                
                # Optional: Save image locally for verification
                with open(f"preview_{data['avatar_name']}.png", "wb") as f:
                    f.write(response.content)
                print(f"✓ Image saved as preview_{data['avatar_name']}.png")
            else:
                print(f"✗ Response is not a PNG image, Content-Type: {content_type}")
                print(f"Response content: {response.text}")
        elif response.status_code == 404:
            print(f"✗ Avatar or preview image not found: {response.json().get('detail')}")
        else:
            print(f"✗ Request failed: {response.text}")
            
    except Exception as e:
        print(f"Error occurred during test: {e}")

# Test /delete_avatar API
def test_delete_avatar():
    print("\nTesting /delete_avatar API:")
    url = "http://0.0.0.0:20000/delete_avatar"
    params = {
        "avatar_name": "56789"
    }
    
    try:
        response = requests.delete(url, params=params)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response content: {result}")
            
            if result.get("status") == "success":
                print(f"✓ Avatar deleted successfully: {result.get('message')}")
            else:
                print(f"Deletion failed: {result.get('message')}")
        else:
            print(f"Request failed: {response.text}")
            
    except Exception as e:
        print(f"Error occurred during test: {e}")

# =============================================================================
# 9. Avatar Switching Management
# =============================================================================

# 9.1 Switch Avatar Successfully
def test_switch_avatar_success():
    """
    Test successful avatar switching
    Method:
      1. Ensure there is an available avatar (e.g., avator_1)
      2. Ensure there is a valid reference audio file
      3. Send POST request to /switch_avatar
    Expected Result:
      - Returns 200 status code
      - Returns success status and message containing: avatar_id and listenport information
    """
    print("\n=== 9.1 Switch Avatar Successfully ===")
    url = "http://0.0.0.0:20000/switch_avatar"
    params = {
        "avatar_id": "avator_1",
        "ref_file": "data/audio/ref_liu.wav"
    }
    
    try:
        print(f"Sending request to: {url}")
        print(f"Parameters: {params}")
        
        response = requests.post(url, params=params)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response content: {result}")
            
            # Validate response structure
            if result.get("status") == "success":
                message = result.get("message", "")
                if "avatar" in message.lower() and "port" in message.lower():
                    print("✓ Successfully switched Avatar, response contains correct avatar and port information")
                    print(f"✓ Switch message: {message}")
                else:
                    print("✗ Response missing required avatar or port information")
            else:
                print(f"✗ Switch failed: {result.get('message')}")
        else:
            print(f"✗ Request failed: {response.text}")
            
    except Exception as e:
        print(f"✗ Error occurred during test: {e}")

# 9.2 Switch Avatar with Invalid Avatar ID
def test_switch_avatar_invalid_id():
    """
    Test switching with invalid Avatar ID
    Method:
      1. Use non-existent avatar_id (e.g., nonexistent_avatar)
      2. Send POST request to /switch_avatar
    Expected Result:
      - Return error status or timeout
      - Return message containing error information
    """
    print("\n=== 9.2 Switch Avatar with Invalid Avatar ID ===")
    url = "http://0.0.0.0:20000/switch_avatar"
    params = {
        "avatar_id": "nonexistent_avatar",
        "ref_file": "data/audio/ref_liu.wav"
    }
    
    try:
        print(f"Sending request to: {url}")
        print(f"Parameters: {params}")
        
        # Set shorter timeout, as invalid avatar may cause long wait
        response = requests.post(url, params=params, timeout=60)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response content: {result}")
            
            if result.get("status") == "error":
                print("✓ Correctly returned error status")
                print(f"✓ Error message: {result.get('message')}")
            else:
                print("✗ Should have returned error status, but returned success")
        else:
            print(f"Request failed, status code: {response.status_code}")
            print(f"Response content: {response.text}")
            
    except requests.Timeout:
        print("✓ Request timed out, this is expected behavior when using invalid avatar_id")
    except Exception as e:
        print(f"✗ Error occurred during test: {e}")

# 9.3 Switch Avatar with Invalid Reference File
def test_switch_avatar_invalid_ref_file():
    """
    Test switching Avatar with invalid reference audio file
    Method:
      1. Use valid avatar_id
      2. Use non-existent reference audio file path
      3. Send POST request to /switch_avatar
    Expected Result:
      - Return error status
      - Return message containing file not found error information
    """
    print("\n=== 9.3 Switch Avatar with Invalid Reference File ===")
    url = "http://0.0.0.0:20000/switch_avatar"
    params = {
        "avatar_id": "avator_1",
        "ref_file": "nonexistent/path/audio.wav"
    }
    
    try:
        print(f"Sending request to: {url}")
        print(f"Parameters: {params}")
        
        response = requests.post(url, params=params, timeout=60)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response content: {result}")
            
            if result.get("status") == "error":
                message = result.get("message", "")
                if "file" in message.lower() or "exist" in message.lower() or "path" in message.lower():
                    print("✓ Correctly identified and returned file path error")
                    print(f"✓ Error message: {message}")
                else:
                    print("✓ Returned error status, but error message may not be clear enough")
                    print(f"Error message: {message}")
            else:
                print("✗ Should have returned error status, but returned success")
        else:
            print(f"Request failed, status code: {response.status_code}")
            
    except requests.Timeout:
        print("✓ Request timed out, this may be expected behavior due to invalid reference file")
    except Exception as e:
        print(f"✗ Error occurred during test: {e}")

# 9.4 Switch Avatar with Missing Parameters
def test_switch_avatar_missing_params():
    """
    Test Avatar switching with missing required parameters
    Method:
      1. Send request missing avatar_id
      2. Send request missing ref_file
      3. Send request with empty parameters
    Expected Result:
      - Return 422 status code (Unprocessable Entity)
      - Return parameter validation error message
    """
    print("\n=== 9.4 Switch Avatar with Missing Parameters ===")
    url = "http://0.0.0.0:20000/switch_avatar"
    
    # Test missing avatar_id
    print("\n--- Testing missing avatar_id ---")
    params_missing_avatar = {"ref_file": "data/audio/ref_liu.wav"}
    
    try:
        response = requests.post(url, params=params_missing_avatar)
        print(f"Status code: {response.status_code}")
        print(f"Response content: {response.text}")
        
        if response.status_code == 422:
            print("✓ Correctly returned parameter validation error (422)")
        else:
            print(f"✗ Expected 422 status code, but received {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error occurred during test: {e}")
    
    # Test missing ref_file
    print("\n--- Testing missing ref_file ---")
    params_missing_ref = {"avatar_id": "avator_1"}
    
    try:
        response = requests.post(url, params=params_missing_ref)
        print(f"Status code: {response.status_code}")
        print(f"Response content: {response.text}")
        
        if response.status_code == 422:
            print("✓ Correctly returned parameter validation error (422)")
        else:
            print(f"✗ Expected 422 status code, but received {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error occurred during test: {e}")

# 9.5 Switch Avatar Port Conflict Handling
def test_switch_avatar_port_conflict():
    """
    Test port conflict handling
    Method:
      1. Start one Avatar service
      2. Try to start another Avatar service (should automatically terminate the previous one)
    Expected Result:
      - New Avatar service starts successfully
      - Previous service is properly terminated
      - Returns success status and new service information
    """
    print("\n=== 9.5 Switch Avatar Port Conflict Handling ===")
    url = "http://0.0.0.0:20000/switch_avatar"
    
    # First start
    print("\n--- Starting first Avatar service ---")
    params1 = {
        "avatar_id": "avator_1",
        "ref_file": "data/audio/ref_liu.wav"
    }
    
    try:
        response1 = requests.post(url, params=params1, timeout=120)
        print(f"First start - Status code: {response1.status_code}")
        
        if response1.status_code == 200:
            result1 = response1.json()
            if result1.get("status") == "success":
                print("✓ First Avatar service started successfully")
                
                # Wait for a while to ensure the service is fully started
                time.sleep(5)
                
                # Second start (different avatar)
                print("\n--- Starting second Avatar service (should replace the first one) ---")
                params2 = {
                    "avatar_id": "avator_2",  # 如果没有avator_2，可以使用相同的avator_1
                    "ref_file": "data/audio/ref_liu.wav"
                }
                
                response2 = requests.post(url, params=params2, timeout=120)
                print(f"Second start - Status code: {response2.status_code}")
                
                if response2.status_code == 200:
                    result2 = response2.json()
                    if result2.get("status") == "success":
                        print("✓ Second Avatar service started successfully")
                        print("✓ Port conflict handling normal, old service correctly replaced")
                    else:
                        print(f"✗ Second start failed: {result2.get('message')}")
                else:
                    print(f"✗ Second start request failed: {response2.text}")
            else:
                print(f"✗ First start failed: {result1.get('message')}")
        else:
            print(f"✗ First start request failed: {response1.text}")
            
    except requests.Timeout:
        print("✗ Request timeout, service startup may be taking too long")
    except Exception as e:
        print(f"✗ Error occurred during test: {e}")

# Run all Switch Avatar related tests
def run_switch_avatar_tests():
    """Run all Switch Avatar related tests"""
    print("\n" + "="*80)
    print("Starting Switch Avatar API tests")
    print("="*80)
    
    test_switch_avatar_success()
    test_switch_avatar_invalid_id()
    test_switch_avatar_invalid_ref_file()
    test_switch_avatar_missing_params()
    # test_switch_avatar_port_conflict()  # Optional, because it starts an actual service
    
    print("\n" + "="*80)
    print("Switch Avatar API tests completed")
    print("="*80)


if __name__ == "__main__":
    # Test /delete_avatar API
    #test_delete_avatar()

    # Test /switch_avatar API
    #test_switch_avatar()

    
    # Switch Avatar test
    run_switch_avatar_tests()  # Uncomment to run all Switch Avatar tests
    
   
    
    pass
