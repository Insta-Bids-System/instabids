"""
Full Integration Test for COIA System
Tests complete flow from API request through background processing
"""

import asyncio
import aiohttp
import json
import time
import subprocess
from datetime import datetime

class COIAIntegrationTest:
    def __init__(self):
        self.session_id = f"integration-test-{int(time.time())}"
        self.base_url = "http://localhost:8008"
        self.results = []
        
    def log_result(self, test_name, status, details, duration_ms=None):
        """Log test result for final summary"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "duration_ms": duration_ms
        }
        self.results.append(result)
        
        status_emoji = "[PASSED]" if status == "PASSED" else "[FAILED]" if status == "FAILED" else "[INFO]"
        duration_text = f" ({duration_ms}ms)" if duration_ms else ""
        print(f"{status_emoji} {test_name}: {details}{duration_text}")
        
    async def test_fast_response(self):
        """Test 1: Fast response (<2 seconds)"""
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                response = await session.post(
                    f'{self.base_url}/api/coia/landing',
                    json={
                        'session_id': self.session_id,
                        'message': 'I run Integration Test Plumbing in Miami',
                        'company_name': 'Integration Test Plumbing',
                        'location': 'Miami, FL'
                    }
                )
                
                duration_ms = int((time.time() - start_time) * 1000)
                
                if response.status == 200:
                    response_data = await response.json()
                    if duration_ms < 2000:
                        self.log_result(
                            "Fast Response", 
                            "PASSED", 
                            f"Response time: {duration_ms}ms", 
                            duration_ms
                        )
                        return True
                    else:
                        self.log_result(
                            "Fast Response", 
                            "FAILED", 
                            f"Too slow: {duration_ms}ms (target: <2000ms)", 
                            duration_ms
                        )
                        return False
                else:
                    self.log_result(
                        "Fast Response", 
                        "FAILED", 
                        f"HTTP {response.status}", 
                        duration_ms
                    )
                    return False
                    
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self.log_result("Fast Response", "FAILED", f"Exception: {e}", duration_ms)
            return False
    
    async def test_websocket_updates(self):
        """Test 2: WebSocket status updates"""
        try:
            import websockets
            uri = f"ws://localhost:8008/api/coia/ws/{self.session_id}"
            
            async with websockets.connect(uri) as websocket:
                # Wait for status updates (max 15 seconds)
                messages = []
                start_time = time.time()
                
                while len(messages) < 3 and (time.time() - start_time) < 15:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                        data = json.loads(message)
                        messages.append(data)
                    except asyncio.TimeoutError:
                        continue
                
                if messages:
                    self.log_result(
                        "WebSocket Updates", 
                        "PASSED", 
                        f"Received {len(messages)} status updates"
                    )
                    return True
                else:
                    self.log_result(
                        "WebSocket Updates", 
                        "FAILED", 
                        "No status updates received"
                    )
                    return False
                    
        except Exception as e:
            self.log_result("WebSocket Updates", "FAILED", f"Exception: {e}")
            return False
    
    def check_docker_logs(self):
        """Test 3: Check for errors in Docker logs"""
        try:
            # Get logs from last 60 seconds
            result = subprocess.run(
                ['docker', 'logs', 'instabids-instabids-backend-1', '--since', '60s'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                self.log_result("Docker Logs", "FAILED", "Could not retrieve Docker logs")
                return False
            
            log_lines = result.stdout.split('\n')
            
            # Count different types of logs
            error_lines = [line for line in log_lines if 'ERROR' in line or 'RuntimeError' in line]
            perf_lines = [line for line in log_lines if 'PERF' in line]
            agent_lines = [line for line in log_lines if '[RESEARCH-AGENT]' in line or '[PROJECTS-AGENT]' in line]
            
            # Summary
            details = f"Errors: {len(error_lines)}, Perf logs: {len(perf_lines)}, Agent logs: {len(agent_lines)}"
            
            if len(error_lines) == 0:
                self.log_result("Docker Logs", "PASSED", details)
                return True
            else:
                self.log_result("Docker Logs", "FAILED", details)
                # Show first few errors
                for error in error_lines[:3]:
                    print(f"    ERROR: {error[:100]}...")
                return False
                
        except Exception as e:
            self.log_result("Docker Logs", "FAILED", f"Exception: {e}")
            return False
    
    async def test_background_processing(self):
        """Test 4: Background processing completion"""
        # Wait for background processing (up to 30 seconds)
        self.log_result("Background Processing", "INFO", "Waiting 30s for completion...")
        
        await asyncio.sleep(30)
        
        # Check logs for completion indicators
        try:
            result = subprocess.run(
                ['docker', 'logs', 'instabids-instabids-backend-1', '--since', '60s'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            log_content = result.stdout
            
            # Look for completion indicators
            research_completed = "RESEARCH-AGENT] SUCCESS" in log_content
            profile_completed = "profile_agent_live completed" in log_content
            projects_completed = "projects_agent_live completed" in log_content
            account_completed = "account_agent_live completed" in log_content
            
            completed_count = sum([research_completed, profile_completed, projects_completed, account_completed])
            
            if completed_count >= 2:  # At least 2 agents should complete
                self.log_result(
                    "Background Processing", 
                    "PASSED", 
                    f"{completed_count}/4 agents completed successfully"
                )
                return True
            else:
                self.log_result(
                    "Background Processing", 
                    "FAILED", 
                    f"Only {completed_count}/4 agents completed"
                )
                return False
                
        except Exception as e:
            self.log_result("Background Processing", "FAILED", f"Exception: {e}")
            return False
    
    def print_summary(self):
        """Print final test summary"""
        print("\n" + "=" * 60)
        print("COIA INTEGRATION TEST SUMMARY")
        print("=" * 60)
        
        passed = len([r for r in self.results if r["status"] == "PASSED"])
        failed = len([r for r in self.results if r["status"] == "FAILED"])
        info = len([r for r in self.results if r["status"] == "INFO"])
        
        print(f"Session ID: {self.session_id}")
        print(f"Total Tests: {len(self.results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Info: {info}")
        
        if failed == 0:
            print("\n[SUCCESS] All integration tests passed!")
            print("COIA system is working correctly.")
        else:
            print(f"\n[WARNING] {failed} test(s) failed")
            print("Review the failed tests above for issues to fix.")
        
        print("=" * 60)
        
        return failed == 0

async def main():
    """Run the full integration test suite"""
    test = COIAIntegrationTest()
    
    print("=" * 60)
    print("COIA FULL INTEGRATION TEST SUITE")
    print("=" * 60)
    print(f"Session: {test.session_id}")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)
    
    # Run tests in sequence
    await test.test_fast_response()
    await test.test_websocket_updates()
    test.check_docker_logs()
    await test.test_background_processing()
    
    # Final summary
    return test.print_summary()

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)