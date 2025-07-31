"""
Master Test Runner for Phase 5
Executes all tests for the bid card system in proper sequence
"""
import subprocess
import os
import time
import json
from datetime import datetime, timezone
import sys


class Phase5TestRunner:
    """Orchestrates all Phase 5 tests"""
    
    def __init__(self):
        self.test_results = {
            "start_time": datetime.now(timezone.utc).isoformat(),
            "tests_run": [],
            "overall_status": "pending",
            "summary": {}
        }
        self.test_servers_pid = None
        
    def start_test_servers(self):
        """Start all test contractor websites"""
        print("\n=== Starting Test Servers ===")
        
        # Check if servers are already running
        try:
            import requests
            response = requests.get("http://localhost:8001", timeout=2)
            print("[OK] Test servers already running")
            return True
        except:
            pass
        
        # Start servers
        print("Starting test contractor websites...")
        
        # Change to test-sites directory
        test_sites_dir = os.path.join(os.path.dirname(__file__), '..', 'test-sites')
        
        if os.name == 'nt':  # Windows
            # Use start command to launch in new windows
            subprocess.Popen([
                'cmd', '/c', 'start', 'Simple Contractor', '/D', test_sites_dir,
                'python', '-m', 'http.server', '8001'
            ], cwd=os.path.join(test_sites_dir, 'simple-contractor'))
            
            subprocess.Popen([
                'cmd', '/c', 'start', 'Pro Contractor', '/D', test_sites_dir,
                'python', '-m', 'http.server', '8002'
            ], cwd=os.path.join(test_sites_dir, 'pro-contractor'))
            
            subprocess.Popen([
                'cmd', '/c', 'start', 'Enterprise Contractor', '/D', test_sites_dir,
                'python', '-m', 'http.server', '8003'
            ], cwd=os.path.join(test_sites_dir, 'enterprise-contractor'))
            
            subprocess.Popen([
                'cmd', '/c', 'start', 'Modern Contractor', '/D', test_sites_dir,
                'python', '-m', 'http.server', '8004'
            ], cwd=os.path.join(test_sites_dir, 'modern-contractor'))
        else:  # Unix/Linux/Mac
            # Use terminal commands for other OS
            subprocess.Popen(['python', '-m', 'http.server', '8001'],
                           cwd=os.path.join(test_sites_dir, 'simple-contractor'))
            subprocess.Popen(['python', '-m', 'http.server', '8002'],
                           cwd=os.path.join(test_sites_dir, 'pro-contractor'))
            subprocess.Popen(['python', '-m', 'http.server', '8003'],
                           cwd=os.path.join(test_sites_dir, 'enterprise-contractor'))
            subprocess.Popen(['python', '-m', 'http.server', '8004'],
                           cwd=os.path.join(test_sites_dir, 'modern-contractor'))
        
        # Wait for servers to start
        print("Waiting for servers to start...")
        time.sleep(5)
        
        # Verify servers are running
        servers_ok = True
        for port in [8001, 8002, 8003, 8004]:
            try:
                import requests
                response = requests.get(f"http://localhost:{port}", timeout=2)
                print(f"[OK] Server on port {port} is running")
            except:
                print(f"[FAIL] Server on port {port} failed to start")
                servers_ok = False
        
        return servers_ok
    
    def start_api_server(self):
        """Start the main API server"""
        print("\n=== Starting API Server ===")
        
        # Check if already running
        try:
            import requests
            response = requests.get("http://localhost:8000", timeout=2)
            print("[OK] API server already running")
            return None
        except:
            pass
        
        # Start API server
        print("Starting API server on port 8000...")
        api_process = subprocess.Popen(
            [sys.executable, 'main.py'],
            cwd=os.path.dirname(__file__)
        )
        
        # Wait for server to start
        time.sleep(5)
        
        # Verify it's running
        try:
            import requests
            response = requests.get("http://localhost:8000")
            print("[OK] API server started successfully")
            return api_process
        except:
            print("[FAIL] Failed to start API server")
            return None
    
    def run_test(self, test_name, test_file, description):
        """Run a single test and capture results"""
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print(f"Description: {description}")
        print('='*60)
        
        start_time = time.time()
        
        try:
            # Run the test
            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(__file__)
            )
            
            duration = time.time() - start_time
            
            # Determine success
            success = result.returncode == 0
            
            # Store result
            test_result = {
                "name": test_name,
                "file": test_file,
                "description": description,
                "success": success,
                "duration": f"{duration:.2f}s",
                "return_code": result.returncode
            }
            
            if success:
                print(f"[OK] {test_name} completed successfully in {duration:.2f}s")
                
                # Try to extract key metrics from output
                if "Success Rate:" in result.stdout:
                    for line in result.stdout.split('\n'):
                        if "Success Rate:" in line:
                            test_result["success_rate"] = line.strip()
            else:
                print(f"[FAIL] {test_name} failed with return code {result.returncode}")
                print(f"Error output: {result.stderr[:500]}...")
                test_result["error"] = result.stderr[:1000]
            
            self.test_results["tests_run"].append(test_result)
            return success
            
        except Exception as e:
            print(f"[FAIL] Failed to run {test_name}: {str(e)}")
            self.test_results["tests_run"].append({
                "name": test_name,
                "file": test_file,
                "success": False,
                "error": str(e)
            })
            return False
    
    def run_all_tests(self):
        """Run all Phase 5 tests in sequence"""
        print("\n" + "="*60)
        print("PHASE 5 COMPREHENSIVE TEST SUITE")
        print("="*60)
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Define test sequence
        tests = [
            {
                "name": "API Endpoint Test",
                "file": "test_bid_card_api.py",
                "description": "Test bid card REST API endpoints"
            },
            {
                "name": "Multi-Channel Display Test", 
                "file": "test_multi_channel_display.py",
                "description": "Test bid card component across web, email, SMS"
            },
            {
                "name": "WFA Form Automation Test",
                "file": "test_wfa_all_sites.py", 
                "description": "Test WFA on all 4 contractor test sites"
            },
            {
                "name": "End-to-End Flow Test",
                "file": "test_bid_card_e2e.py",
                "description": "Test complete CIA→JAA→CDA→WFA flow"
            }
        ]
        
        # Setup environment
        print("\n=== Environment Setup ===")
        
        # 1. Start test servers
        if not self.start_test_servers():
            print("[FAIL] Failed to start test servers. Aborting.")
            return False
        
        # 2. Start API server
        api_process = self.start_api_server()
        
        # 3. Create test results directory
        os.makedirs("test_results", exist_ok=True)
        
        # Run tests
        total_tests = len(tests)
        passed_tests = 0
        
        for test in tests:
            if self.run_test(test["name"], test["file"], test["description"]):
                passed_tests += 1
            
            # Brief pause between tests
            time.sleep(2)
        
        # Generate summary
        self.test_results["end_time"] = datetime.now(timezone.utc).isoformat()
        self.test_results["overall_status"] = "passed" if passed_tests == total_tests else "failed"
        self.test_results["summary"] = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": total_tests - passed_tests,
            "success_rate": f"{passed_tests/total_tests*100:.0f}%"
        }
        
        # Save master report
        with open("test_results/phase5_master_report.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        # Print summary
        print("\n" + "="*60)
        print("TEST SUITE SUMMARY")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {passed_tests/total_tests*100:.0f}%")
        print(f"\nEnd Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # List failed tests
        if passed_tests < total_tests:
            print("\nFailed Tests:")
            for test in self.test_results["tests_run"]:
                if not test["success"]:
                    print(f"  - {test['name']}: {test.get('error', 'Unknown error')[:100]}")
        
        print(f"\nDetailed reports saved in: test_results/")
        print(f"Master report: test_results/phase5_master_report.json")
        
        # Cleanup
        if api_process:
            print("\nStopping API server...")
            api_process.terminate()
        
        return passed_tests == total_tests
    
    def quick_test_mode(self):
        """Run a quick subset of tests for rapid validation"""
        print("\n=== QUICK TEST MODE ===")
        print("Running essential tests only...")
        
        # Just run API and WFA tests
        quick_tests = [
            {
                "name": "API Test",
                "file": "test_bid_card_api.py",
                "description": "Quick API validation"
            },
            {
                "name": "WFA Test", 
                "file": "test_wfa_all_sites.py",
                "description": "Test form automation"
            }
        ]
        
        # Start servers
        self.start_test_servers()
        api_process = self.start_api_server()
        
        # Run quick tests
        for test in quick_tests:
            self.run_test(test["name"], test["file"], test["description"])
        
        print("\nQuick test complete!")
        
        if api_process:
            api_process.terminate()


def main():
    """Main test runner entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Phase 5 comprehensive tests')
    parser.add_argument('--quick', action='store_true', help='Run quick test subset')
    parser.add_argument('--no-servers', action='store_true', help='Skip starting servers')
    
    args = parser.parse_args()
    
    runner = Phase5TestRunner()
    
    if args.quick:
        runner.quick_test_mode()
    else:
        # Full test suite
        success = runner.run_all_tests()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()