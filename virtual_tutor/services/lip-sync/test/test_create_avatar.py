import requests
import os
import json
import time

# =============================================================================
# Create Avatar API Test
# =============================================================================

# 10.1 Create Avatar Successfully
def test_create_avatar_success():
    """
    Test successful Avatar creation
    Method:
      1. Ensure there is a valid video file
      2. Use a valid avatar name
      3. Send POST request to /create_avatar
    Expected Result:
      - Return 200 status code
      - Return success status and message, including: image_path information
    """
    print("\n=== 10.1 Create Avatar Successfully ===")
    url = "http://0.0.0.0:20000/create_avatar"
    params = {
        "avatar_name": "test_avatar_success",
        "video_path": "/workspace/share/yuntao/LiveTalking/ava_xu.mp4",
        "burr": False
    }
    
    try:
        print(f"Sending request to: {url}")
        print(f"Parameters: {params}")
        
        # Set a longer timeout because avatar creation is time-consuming
        response = requests.post(url, params=params, timeout=300)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response content: {result}")
            
            if result.get("status") == "success":
                image_path = result.get("image_path", "")
                if image_path:
                    print("✓ Avatar created successfully, received image path")
                    print(f"✓ Image path: {image_path}")
                    
                    # Verify if the image file exists
                    if os.path.exists(image_path):
                        print("✓ Image file exists")
                    else:
                        print("✗ Image file does not exist")
                else:
                    print("✗ Response missing image path information")
            else:
                print(f"✗ Creation failed: {result.get('message')}")
        else:
            print(f"✗ Request failed: {response.text}")
            
    except requests.Timeout:
        print("✗ Request timeout, avatar creation may take longer")
    except Exception as e:
        print(f"✗ Error occurred during test: {e}")

# 10.2 Create Avatar with Blur Processing
def test_create_avatar_with_burr():
    """
    Test Avatar creation with blur processing enabled
    Method:
      1. Use a valid video file
      2. Set burr=True
      3. Send POST request to /create_avatar
    Expected Result:
      - Return 200 status code
      - Successfully create avatar with blur processing
    """
    print("\n=== 10.2 Create Avatar with Blur Processing ===")
    url = "http://0.0.0.0:20000/create_avatar"
    params = {
        "avatar_name": "test_avatar_burr",
        "video_path": "/workspace/share/yuntao/LiveTalking/ava_xu.mp4",
        "burr": True
    }
    
    try:
        print(f"Sending request to: {url}")
        print(f"Parameters: {params}")
        
        response = requests.post(url, params=params, timeout=400)  # Blur processing takes more time
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response content: {result}")
            
            if result.get("status") == "success":
                print("✓ Avatar with blur processing created successfully")
                print(f"✓ Image path: {result.get('image_path')}")
            else:
                print(f"✗ Creation failed: {result.get('message')}")
        else:
            print(f"✗ Request failed: {response.text}")
            
    except requests.Timeout:
        print("✗ Request timeout, blur processing may take longer")
    except Exception as e:
        print(f"✗ Error occurred during test: {e}")

# 10.3 Create Avatar with Invalid Video Path
def test_create_avatar_invalid_video():
    """
    Test creating Avatar with invalid video path
    Method:
      1. Use non-existent video file path
      2. Send POST request to /create_avatar
    Expected Result:
      - Return 400 status code (Bad Request)
      - Return message containing file not found error information
    """
    print("\n=== 10.3 Create Avatar with Invalid Video Path ===")
    url = "http://0.0.0.0:20000/create_avatar"
    params = {
        "avatar_name": "test_avatar_invalid",
        "video_path": "/nonexistent/path/video.mp4",
        "burr": False
    }
    
    try:
        print(f"Sending request to: {url}")
        print(f"Parameters: {params}")
        
        response = requests.post(url, params=params, timeout=60)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 400:
            # Should now return 400 status code
            error_detail = response.json().get("detail", "")
            if "not exist" in error_detail or "file" in error_detail:
                print("✓ Correctly returned 400 status code and file not found error")
                print(f"✓ Error message: {error_detail}")
            else:
                print("✓ Returned 400 status code, but error message may not be clear enough")
                print(f"Error message: {error_detail}")
        elif response.status_code == 200:
            result = response.json()
            print(f"Response content: {result}")
            
            if result.get("status") == "error":
                message = result.get("message", "")
                if "not exist" in message or "file" in message:
                    print("✓ Correctly identified and returned file not found error")
                    print(f"✓ Error message: {message}")
                else:
                    print("✓ Returned error status, but error message may not be clear enough")
                    print(f"Error message: {message}")
            else:
                print("✗ Should return error status, but returned success")
        else:
            print(f"Request failed, status code: {response.status_code}")
            print(f"Response content: {response.text}")
            
    except Exception as e:
        print(f"✗ Error occurred during test: {e}")

# 10.4 Create Avatar with Invalid Video Format
def test_create_avatar_invalid_format():
    """
    Test creating Avatar with unsupported video format
    Method:
      1. Use unsupported file format (e.g., .txt)
      2. Send POST request to /create_avatar
    Expected Result:
      - Return 400 status code (Bad Request)
      - Return message containing format not supported error information
    """
    print("\n=== 10.4 Create Avatar with Invalid Video Format ===")
    url = "http://0.0.0.0:20000/create_avatar"
    params = {
        "avatar_name": "test_avatar_format",
        "video_path": "/workspace/share/yuntao/LiveTalking/README.md",  # Use text file for testing
        "burr": False
    }
    
    try:
        print(f"Sending request to: {url}")
        print(f"Parameters: {params}")
        
        response = requests.post(url, params=params, timeout=60)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 400:
            # Should now return 400 status code
            error_detail = response.json().get("detail", "")
            if "format" in error_detail or "support" in error_detail:
                print("✓ Correctly returned 400 status code and format not supported error")
                print(f"✓ Error message: {error_detail}")
            else:
                print("✓ Returned 400 status code, but error message may not be clear enough")
                print(f"Error message: {error_detail}")
        elif response.status_code == 200:
            result = response.json()
            print(f"Response content: {result}")
            
            if result.get("status") == "error":
                message = result.get("message", "")
                if "format" in message or "support" in message:
                    print("✓ Correctly identified and returned format not supported error")
                    print(f"✓ Error message: {message}")
                else:
                    print("✓ Returned error status, but error message may not be clear enough")
                    print(f"Error message: {message}")
            else:
                print("✗ Should return error status, but returned success")
        else:
            print(f"Request failed, status code: {response.status_code}")
            print(f"Response content: {response.text}")
            
    except Exception as e:
        print(f"✗ Error occurred during test: {e}")

# 10.5 Create Avatar with Missing Parameters
def test_create_avatar_missing_params():
    """
    Test Avatar creation when missing required parameters
    Method:
      1. Send request missing avatar_name
      2. Send request missing video_path
    Expected Result:
      - Return 422 status code (Unprocessable Entity)
      - Return parameter validation error message
    """
    print("\n=== 10.5 Create Avatar with Missing Parameters ===")
    url = "http://0.0.0.0:20000/create_avatar"
    
    # Test missing avatar_name
    print("\n--- Testing missing avatar_name ---")
    params_missing_name = {
        "video_path": "/workspace/share/yuntao/LiveTalking/ava_xu_ref.mp4",
        "burr": False
    }
    
    try:
        response = requests.post(url, params=params_missing_name)
        print(f"Status code: {response.status_code}")
        print(f"Response content: {response.text}")
        
        if response.status_code == 422:
            print("✓ Correctly returned parameter validation error (422)")
        else:
            print(f"✗ Expected 422 status code, but received {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error occurred during test: {e}")
    
    # Test missing video_path
    print("\n--- Testing missing video_path ---")
    params_missing_path = {
        "avatar_name": "test_missing_path",
        "burr": False
    }
    
    try:
        response = requests.post(url, params=params_missing_path)
        print(f"Status code: {response.status_code}")
        print(f"Response content: {response.text}")
        
        if response.status_code == 422:
            print("✓ Correctly returned parameter validation error (422)")
        else:
            print(f"✗ Expected 422 status code, but received {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error occurred during test: {e}")

# 10.6 Create Avatar with Duplicate Name
def test_create_avatar_duplicate_name():
    """
    Test creating Avatar with duplicate name
    Method:
      1. Create one avatar
      2. Create another avatar using the same name
    Expected Result:
      - Second creation should succeed (overwrite the original)
      - Or return appropriate notification message
    """
    print("\n=== 10.6 Create Avatar with Duplicate Name ===")
    url = "http://0.0.0.0:20000/create_avatar"
    avatar_name = "test_duplicate_avatar"
    params = {
        "avatar_name": avatar_name,
        "video_path": "/workspace/share/yuntao/LiveTalking/ava_xu_ref.mp4",
        "burr": False
    }
    
    try:
        # First creation
        print("\n--- First Avatar creation ---")
        response1 = requests.post(url, params=params, timeout=300)
        print(f"First creation - Status code: {response1.status_code}")
        
        if response1.status_code == 200:
            result1 = response1.json()
            if result1.get("status") == "success":
                print("✓ First creation successful")
                
                # Second creation (same name)
                print("\n--- Second Avatar creation (duplicate name) ---")
                response2 = requests.post(url, params=params, timeout=300)
                print(f"Second creation - Status code: {response2.status_code}")
                
                if response2.status_code == 200:
                    result2 = response2.json()
                    if result2.get("status") == "success":
                        print("✓ Second creation successful (overwriting original avatar)")
                    else:
                        print(f"Second creation failed: {result2.get('message')}")
                else:
                    print(f"✗ Second creation request failed: {response2.text}")
            else:
                print(f"✗ First creation failed: {result1.get('message')}")
        else:
            print(f"✗ First creation request failed: {response1.text}")
            
    except requests.Timeout:
        print("✗ Request timeout")
    except Exception as e:
        print(f"✗ Error occurred during test: {e}")

# 10.7 Create Avatar Performance Test
def test_create_avatar_performance():
    """
    Test Avatar creation performance
    Method:
      1. Record time taken to create avatar
      2. Verify if completed within reasonable time
    Expected Result:
      - Complete creation within reasonable time
      - Provide performance metrics
    """
    print("\n=== 10.7 Create Avatar Performance Test ===")
    url = "http://0.0.0.0:20000/create_avatar"
    params = {
        "avatar_name": "test_avatar_performance",
        "video_path": "/workspace/share/yuntao/LiveTalking/ava_xu_ref.mp4",
        "burr": False
    }
    
    try:
        print(f"Starting performance test...")
        print(f"Parameters: {params}")
        
        start_time = time.time()
        response = requests.post(url, params=params, timeout=600)  # 10 minutes timeout
        end_time = time.time()
        
        duration = end_time - start_time
        print(f"Creation time: {duration:.2f} seconds")
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print("✓ Avatar created successfully")
                
                # Performance evaluation
                if duration < 120:  # Under 2 minutes
                    print("✓ Excellent performance: Creation time less than 2 minutes")
                elif duration < 300:  # Under 5 minutes
                    print("✓ Good performance: Creation time between 2-5 minutes")
                elif duration < 600:  # Under 10 minutes
                    print("⚠️ Average performance: Creation time between 5-10 minutes")
                else:
                    print("✗ Poor performance: Creation time over 10 minutes")
            else:
                print(f"✗ Creation failed: {result.get('message')}")
        else:
            print(f"✗ Request failed: {response.text}")
            
    except requests.Timeout:
        print("✗ Request timeout (over 10 minutes), performance needs optimization")
    except Exception as e:
        print(f"✗ Error occurred during test: {e}")

# 10.8 Verify Created Avatar Usability
def test_created_avatar_usability():
    """
    Verify if created avatar can be used normally
    Method:
      1. Create an avatar
      2. Try to use that avatar to switch service
    Expected Result:
      - Created avatar can be normally used for switching service
    """
    print("\n=== 10.8 Verify Created Avatar Usability ===")
    
    create_url = "http://0.0.0.0:20000/create_avatar"
    switch_url = "http://0.0.0.0:20000/switch_avatar"
    avatar_name = "test_usability_avatar"
    
    # Create avatar parameters
    create_params = {
        "avatar_name": avatar_name,
        "video_path": "/workspace/share/yuntao/LiveTalking/ava_xu_ref.mp4",
        "burr": False
    }
    
    try:
        # Step 1: Create avatar
        print("\n--- Step 1: Creating Avatar ---")
        create_response = requests.post(create_url, params=create_params, timeout=300)
        print(f"Creation response status code: {create_response.status_code}")
        
        if create_response.status_code == 200:
            create_result = create_response.json()
            if create_result.get("status") == "success":
                print("✓ Avatar created successfully")
                
                # Step 2: Try switching to newly created avatar
                print("\n--- Step 2: Testing Avatar usability ---")
                switch_params = {
                    "avatar_id": avatar_name,
                    "ref_file": "data/audio/ref_liu.wav"
                }
                
                switch_response = requests.post(switch_url, params=switch_params, timeout=120)
                print(f"Switch response status code: {switch_response.status_code}")
                
                if switch_response.status_code == 200:
                    switch_result = switch_response.json()
                    if switch_result.get("status") == "success":
                        print("✓ Newly created Avatar can be used normally")
                        print("✓ Integration test passed")
                    else:
                        print(f"✗ Avatar switching failed: {switch_result.get('message')}")
                else:
                    print(f"✗ Switching request failed: {switch_response.text}")
            else:
                print(f"✗ Avatar creation failed: {create_result.get('message')}")
        else:
            print(f"✗ Creation request failed: {create_response.text}")
            
    except requests.Timeout:
        print("✗ Request timeout")
    except Exception as e:
        print(f"✗ Error occurred during test: {e}")

# Run all Create Avatar related tests
def run_create_avatar_tests():
    """Run all Create Avatar related tests"""
    print("\n" + "="*80)
    print("Starting Create Avatar API tests")
    print("="*80)
    
    # Basic functionality tests
    test_create_avatar_success()
    test_create_avatar_invalid_video()
    test_create_avatar_invalid_format()
    test_create_avatar_missing_params()
    
    # Advanced functionality tests (optional)
    # test_create_avatar_with_burr()  # Optional, because it takes longer
    # test_create_avatar_duplicate_name()  # Optional, because it takes longer
    # test_create_avatar_performance()  # Optional, because it takes much longer
    # test_created_avatar_usability()  # Optional, to avoid affecting existing services
    
    print("\n" + "="*80)
    print("Create Avatar API tests completed")
    print("="*80)

if __name__ == "__main__":
    # run Create Avatar tests
    run_create_avatar_tests()
