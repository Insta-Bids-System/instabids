import requests
import time

def test_response_times():
    """Test COIA response time consistency"""
    print("Testing COIA Response Times...")
    
    times = []
    for i in range(5):
        start = time.time()
        response = requests.post('http://localhost:8008/api/coia/landing', 
                               json={'message': f'Turn {i+1} message', 'session_id': f'test-timing-{i}'})
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"Turn {i+1}: {elapsed:.2f}s - Status {response.status_code}")
    
    print(f"\nResponse times: {[f'{t:.2f}s' for t in times]}")
    print(f"Average: {sum(times)/len(times):.2f}s")
    print(f"Range: {min(times):.2f}s - {max(times):.2f}s")
    print(f"Variation: {max(times)-min(times):.2f}s")
    
    return times

if __name__ == "__main__":
    test_response_times()