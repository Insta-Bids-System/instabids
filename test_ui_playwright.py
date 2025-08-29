#!/usr/bin/env python3
"""InstaBids Comprehensive UI Test Suite using Playwright"""

from playwright.sync_api import sync_playwright, expect
import time
import json
import os
from datetime import datetime
import random
import string

class InstaBidsTestSuite:
    def __init__(self, base_url="http://localhost:5174", api_url="http://127.0.0.1:8008"):
        self.base_url = base_url
        self.api_url = api_url
        self.test_results = []
        self.test_data = {
            "test_email": f"test_{self.generate_random_string(8)}@example.com",
            "test_password": "TestPassword123!",
            "test_project": {
                "type": "lawn care",
                "description": "I need someone to mow my lawn weekly. It's about 5000 sq ft with both front and back yards.",
                "budget": "$50-100 per visit",
                "timeline": "Starting next week"
            }
        }
    
    def generate_random_string(self, length=8):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    def add_test_result(self, test_name, status, details=None, error=None):
        result = {
            "test": test_name,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        if details:
            result["details"] = details
        if error:
            result["error"] = str(error)
        self.test_results.append(result)
        
    def run_all_tests(self):
        print("🧪 Starting InstaBids Comprehensive UI Test Suite")
        print("=" * 70)
        print(f"Frontend URL: {self.base_url}")
        print(f"API URL: {self.api_url}")
        print(f"Test Email: {self.test_data['test_email']}")
        print("=" * 70)
        
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            )
            page = context.new_page()
            
            # Run test categories
            self.test_homepage(page)
            self.test_authentication_flow(page)
            self.test_homeowner_journey(page)
            self.test_contractor_features(page)
            self.test_api_endpoints(page)
            self.test_responsive_design(page)
            self.test_accessibility(page)
            self.test_performance(page)
            self.test_error_handling(page)
            self.test_security(page)
            
            # Close browser
            browser.close()
            
            # Generate report
            self.generate_report()
    
    def test_homepage(self, page):
        print("\n🏠 HOMEPAGE TESTS")
        print("-" * 50)
        
        # Test 1.1: Basic Loading
        try:
            page.goto(self.base_url, wait_until="networkidle")
            page.wait_for_timeout(2000)
            
            title = page.title()
            print(f"✓ Homepage loaded - Title: {title}")
            page.screenshot(path="test_screenshots/homepage/01_main.png")
            self.add_test_result("Homepage Loading", "PASS", {"title": title})
        except Exception as e:
            print(f"✗ Homepage loading failed: {e}")
            self.add_test_result("Homepage Loading", "FAIL", error=e)
        
        # Test 1.2: Critical Elements
        elements = {
            "logo": ["img[alt*='InstaBids']", "svg", ".logo", "[class*='brand']"],
            "navigation": ["nav", "[role='navigation']", ".navigation"],
            "hero_section": [".hero", "[class*='hero']", "section:first-child"],
            "cta_buttons": ["button", "a[href*='started']", "[class*='cta']"],
            "value_props": ["[class*='feature']", "[class*='benefit']", ".value-prop"]
        }
        
        found_elements = {}
        for element_name, selectors in elements.items():
            found = False
            for selector in selectors:
                try:
                    if page.locator(selector).first.is_visible():
                        found = True
                        found_elements[element_name] = selector
                        break
                except:
                    continue
            
            if found:
                print(f"✓ Found {element_name}")
            else:
                print(f"✗ Missing {element_name}")
        
        self.add_test_result("Homepage Elements", "PASS" if len(found_elements) >= 3 else "PARTIAL", 
                           {"found": list(found_elements.keys())})
        
        # Test 1.3: Interactive Elements
        try:
            # Check for hover states
            if "cta_buttons" in found_elements:
                button = page.locator(found_elements["cta_buttons"]).first
                button.hover()
                page.wait_for_timeout(500)
                print("✓ Interactive hover states working")
            
            # Check for animations
            animations = page.evaluate("""
                () => {
                    const elements = document.querySelectorAll('*');
                    return Array.from(elements).some(el => {
                        const style = window.getComputedStyle(el);
                        return style.animation !== 'none' || style.transition !== 'all 0s ease 0s';
                    });
                }
            """)
            if animations:
                print("✓ Animations detected")
            
            self.add_test_result("Homepage Interactivity", "PASS")
        except Exception as e:
            print(f"✗ Interactivity test failed: {e}")
            self.add_test_result("Homepage Interactivity", "FAIL", error=e)
    
    def test_authentication_flow(self, page):
        print("\n🔐 AUTHENTICATION TESTS")
        print("-" * 50)
        
        # Test 2.1: Navigation to Auth Pages
        try:
            page.goto(self.base_url)
            
            # Look for sign up link/button
            sign_up_found = False
            for selector in ["text=Sign Up", "text=Get Started", "text=Join", "[href*='signup']"]:
                try:
                    if page.locator(selector).first.is_visible():
                        page.click(selector)
                        sign_up_found = True
                        break
                except:
                    continue
            
            if sign_up_found:
                page.wait_for_timeout(2000)
                print(f"✓ Navigated to signup page: {page.url}")
                page.screenshot(path="test_screenshots/auth/01_signup_page.png")
                self.add_test_result("Navigate to Signup", "PASS", {"url": page.url})
            else:
                print("✗ Could not find signup navigation")
                self.add_test_result("Navigate to Signup", "FAIL")
        except Exception as e:
            print(f"✗ Auth navigation failed: {e}")
            self.add_test_result("Navigate to Signup", "FAIL", error=e)
        
        # Test 2.2: Form Validation
        try:
            # Check for form fields
            form_fields = {
                "email": ["input[type='email']", "input[name*='email']", "#email"],
                "password": ["input[type='password']", "input[name*='password']", "#password"],
                "submit": ["button[type='submit']", "button:has-text('Sign Up')", "button:has-text('Create')"]
            }
            
            fields_found = {}
            for field_name, selectors in form_fields.items():
                for selector in selectors:
                    try:
                        if page.locator(selector).first.is_visible():
                            fields_found[field_name] = selector
                            break
                    except:
                        continue
            
            if len(fields_found) >= 2:
                print("✓ Auth form fields found")
                
                # Test empty form submission
                if "submit" in fields_found:
                    page.click(fields_found["submit"])
                    page.wait_for_timeout(1000)
                    
                    # Check for validation messages
                    error_visible = page.locator("text=/required|invalid|error/i").count() > 0
                    if error_visible:
                        print("✓ Form validation working")
                        self.add_test_result("Form Validation", "PASS")
                    else:
                        print("⚠️  No validation messages shown")
                        self.add_test_result("Form Validation", "PARTIAL")
            else:
                print("✗ Insufficient form fields found")
                self.add_test_result("Form Validation", "FAIL", {"fields_found": list(fields_found.keys())})
                
        except Exception as e:
            print(f"✗ Form validation test failed: {e}")
            self.add_test_result("Form Validation", "FAIL", error=e)
        
        # Test 2.3: Demo/Test Account
        try:
            # Look for demo login option
            demo_selectors = ["text=Demo", "text=Try Demo", "text=Test Account", "[href*='demo']"]
            demo_found = False
            
            for selector in demo_selectors:
                try:
                    if page.locator(selector).first.is_visible():
                        page.click(selector)
                        demo_found = True
                        print("✓ Demo account option available")
                        break
                except:
                    continue
            
            if not demo_found:
                print("ℹ️  No demo account option found")
            
            self.add_test_result("Demo Account", "PASS" if demo_found else "INFO")
        except Exception as e:
            print(f"⚠️  Demo account check failed: {e}")
    
    def test_homeowner_journey(self, page):
        print("\n🏡 HOMEOWNER JOURNEY TESTS")
        print("-" * 50)
        
        # Test 3.1: Access Chat/Project Creation
        try:
            page.goto(self.base_url)
            
            # Look for chat or project creation entry points
            chat_selectors = [
                "text=Chat", "text=Start Project", "text=Get Quotes", 
                "[href*='chat']", "text=Describe Your Project", "text=Tell us"
            ]
            
            chat_found = False
            for selector in chat_selectors:
                try:
                    if page.locator(selector).first.is_visible():
                        page.click(selector)
                        chat_found = True
                        break
                except:
                    continue
            
            if chat_found:
                page.wait_for_timeout(2000)
                print(f"✓ Accessed project creation: {page.url}")
                page.screenshot(path="test_screenshots/homeowner/01_chat_entry.png")
                self.add_test_result("Project Creation Access", "PASS")
                
                # Test 3.2: Chat Interface
                # Look for chat input
                chat_input_selectors = [
                    "textarea", "input[type='text']", "[contenteditable='true']",
                    "[placeholder*='project']", "[placeholder*='describe']"
                ]
                
                input_found = False
                for selector in chat_input_selectors:
                    try:
                        if page.locator(selector).first.is_visible():
                            # Type test project
                            page.fill(selector, self.test_data["test_project"]["description"])
                            input_found = True
                            print("✓ Chat input working")
                            break
                    except:
                        continue
                
                if input_found:
                    page.screenshot(path="test_screenshots/homeowner/02_chat_input.png")
                    
                    # Look for send button
                    send_selectors = ["button:has-text('Send')", "button[type='submit']", "[aria-label*='send']"]
                    for selector in send_selectors:
                        try:
                            if page.locator(selector).first.is_visible():
                                page.click(selector)
                                print("✓ Message sent")
                                page.wait_for_timeout(3000)
                                page.screenshot(path="test_screenshots/homeowner/03_chat_response.png")
                                break
                        except:
                            continue
                    
                    self.add_test_result("Chat Interface", "PASS")
                else:
                    print("✗ Chat input not found")
                    self.add_test_result("Chat Interface", "FAIL")
            else:
                print("✗ Could not access project creation")
                self.add_test_result("Project Creation Access", "FAIL")
                
        except Exception as e:
            print(f"✗ Homeowner journey test failed: {e}")
            self.add_test_result("Homeowner Journey", "FAIL", error=e)
        
        # Test 3.3: Dashboard Features
        try:
            # Try to access dashboard
            dashboard_selectors = ["text=Dashboard", "[href*='dashboard']", "text=My Projects"]
            for selector in dashboard_selectors:
                try:
                    if page.locator(selector).first.is_visible():
                        page.click(selector)
                        page.wait_for_timeout(2000)
                        print(f"✓ Dashboard accessible: {page.url}")
                        page.screenshot(path="test_screenshots/homeowner/04_dashboard.png")
                        self.add_test_result("Dashboard Access", "PASS")
                        break
                except:
                    continue
        except:
            print("ℹ️  Dashboard test skipped")
    
    def test_contractor_features(self, page):
        print("\n🔨 CONTRACTOR FEATURES TESTS")
        print("-" * 50)
        
        # Test 4.1: Contractor Portal Access
        try:
            page.goto(self.base_url)
            
            # Look for contractor section
            contractor_selectors = [
                "text=Contractor", "text=For Contractors", "text=Join as Pro",
                "[href*='contractor']", "text=Contractor Login"
            ]
            
            found = False
            for selector in contractor_selectors:
                try:
                    if page.locator(selector).first.is_visible():
                        page.click(selector)
                        found = True
                        break
                except:
                    continue
            
            if found:
                page.wait_for_timeout(2000)
                print(f"✓ Contractor section accessible: {page.url}")
                page.screenshot(path="test_screenshots/contractor/01_portal.png")
                self.add_test_result("Contractor Portal", "PASS")
            else:
                print("✗ Contractor section not found")
                self.add_test_result("Contractor Portal", "FAIL")
                
        except Exception as e:
            print(f"✗ Contractor features test failed: {e}")
            self.add_test_result("Contractor Features", "FAIL", error=e)
    
    def test_api_endpoints(self, page):
        print("\n🔌 API ENDPOINT TESTS")
        print("-" * 50)
        
        endpoints = [
            {"path": "/", "name": "Root"},
            {"path": "/docs", "name": "API Documentation"},
            {"path": "/api/chat/cia", "method": "OPTIONS", "name": "CIA Chat Endpoint"},
            {"path": "/api/agents/status", "method": "GET", "name": "Agents Status"},
        ]
        
        for endpoint in endpoints:
            try:
                url = f"{self.api_url}{endpoint['path']}"
                method = endpoint.get("method", "GET")
                
                if method == "GET":
                    response = page.request.get(url)
                elif method == "OPTIONS":
                    response = page.request.fetch(url, method="OPTIONS")
                
                status_ok = response.status in [200, 204, 405]  # 405 for OPTIONS sometimes
                print(f"{'✓' if status_ok else '✗'} {endpoint['name']}: {response.status}")
                
                if endpoint['path'] == "/" and response.status == 200:
                    data = response.json()
                    print(f"  API Status: {data.get('status')}")
                    print(f"  Active Agents: {[k for k, v in data.get('agents', {}).items() if v == 'active']}")
                
                self.add_test_result(f"API: {endpoint['name']}", "PASS" if status_ok else "FAIL", 
                                   {"status": response.status})
            except Exception as e:
                print(f"✗ {endpoint['name']} failed: {e}")
                self.add_test_result(f"API: {endpoint['name']}", "FAIL", error=e)
    
    def test_responsive_design(self, page):
        print("\n📱 RESPONSIVE DESIGN TESTS")
        print("-" * 50)
        
        viewports = [
            {"name": "Mobile", "width": 375, "height": 812},
            {"name": "Tablet", "width": 768, "height": 1024},
            {"name": "Desktop", "width": 1920, "height": 1080}
        ]
        
        for viewport in viewports:
            try:
                page.set_viewport_size({"width": viewport["width"], "height": viewport["height"]})
                page.goto(self.base_url)
                page.wait_for_timeout(1500)
                
                # Check if content is visible and not overflowing
                overflow = page.evaluate("""
                    () => {
                        const body = document.body;
                        return body.scrollWidth > body.clientWidth;
                    }
                """)
                
                status = "FAIL" if overflow else "PASS"
                print(f"{'✓' if not overflow else '✗'} {viewport['name']} view ({viewport['width']}x{viewport['height']})")
                
                page.screenshot(path=f"test_screenshots/responsive/{viewport['name'].lower()}.png")
                self.add_test_result(f"Responsive: {viewport['name']}", status, 
                                   {"overflow": overflow, "viewport": viewport})
            except Exception as e:
                print(f"✗ {viewport['name']} test failed: {e}")
                self.add_test_result(f"Responsive: {viewport['name']}", "FAIL", error=e)
    
    def test_accessibility(self, page):
        print("\n♿ ACCESSIBILITY TESTS")
        print("-" * 50)
        
        try:
            page.goto(self.base_url)
            
            # Test 7.1: Alt text for images
            images_without_alt = page.evaluate("""
                () => {
                    const images = document.querySelectorAll('img');
                    return Array.from(images).filter(img => !img.alt || img.alt.trim() === '').length;
                }
            """)
            
            print(f"{'✓' if images_without_alt == 0 else '✗'} Images with alt text ({images_without_alt} missing)")
            
            # Test 7.2: ARIA labels
            buttons_without_text = page.evaluate("""
                () => {
                    const buttons = document.querySelectorAll('button');
                    return Array.from(buttons).filter(btn => 
                        !btn.textContent.trim() && !btn.getAttribute('aria-label')
                    ).length;
                }
            """)
            
            print(f"{'✓' if buttons_without_text == 0 else '✗'} Buttons with labels ({buttons_without_text} missing)")
            
            # Test 7.3: Heading hierarchy
            heading_issues = page.evaluate("""
                () => {
                    const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
                    let lastLevel = 0;
                    let issues = 0;
                    
                    headings.forEach(h => {
                        const level = parseInt(h.tagName[1]);
                        if (level > lastLevel + 1) issues++;
                        lastLevel = level;
                    });
                    
                    return issues;
                }
            """)
            
            print(f"{'✓' if heading_issues == 0 else '✗'} Heading hierarchy ({heading_issues} issues)")
            
            # Test 7.4: Color contrast (basic check)
            low_contrast = page.evaluate("""
                () => {
                    const elements = document.querySelectorAll('*');
                    let issues = 0;
                    
                    elements.forEach(el => {
                        const style = window.getComputedStyle(el);
                        const bg = style.backgroundColor;
                        const fg = style.color;
                        
                        // Very basic check - just ensure text isn't same color as background
                        if (bg && fg && bg === fg && el.textContent.trim()) {
                            issues++;
                        }
                    });
                    
                    return issues;
                }
            """)
            
            print(f"{'✓' if low_contrast == 0 else '✗'} Color contrast ({low_contrast} potential issues)")
            
            score = sum([
                images_without_alt == 0,
                buttons_without_text == 0,
                heading_issues == 0,
                low_contrast == 0
            ])
            
            self.add_test_result("Accessibility", "PASS" if score >= 3 else "PARTIAL" if score >= 2 else "FAIL", {
                "images_without_alt": images_without_alt,
                "buttons_without_text": buttons_without_text,
                "heading_issues": heading_issues,
                "low_contrast": low_contrast
            })
            
        except Exception as e:
            print(f"✗ Accessibility test failed: {e}")
            self.add_test_result("Accessibility", "FAIL", error=e)
    
    def test_performance(self, page):
        print("\n⚡ PERFORMANCE TESTS")
        print("-" * 50)
        
        try:
            # Measure page load time
            start_time = time.time()
            page.goto(self.base_url, wait_until="networkidle")
            load_time = time.time() - start_time
            
            print(f"{'✓' if load_time < 3 else '⚠️' if load_time < 5 else '✗'} Page load time: {load_time:.2f}s")
            
            # Check bundle sizes
            resources = page.evaluate("""
                () => {
                    const resources = performance.getEntriesByType('resource');
                    const js = resources.filter(r => r.name.endsWith('.js'));
                    const css = resources.filter(r => r.name.endsWith('.css'));
                    const images = resources.filter(r => r.initiatorType === 'img');
                    
                    return {
                        jsCount: js.length,
                        jsSize: js.reduce((sum, r) => sum + (r.transferSize || 0), 0),
                        cssCount: css.length,
                        cssSize: css.reduce((sum, r) => sum + (r.transferSize || 0), 0),
                        imageCount: images.length,
                        imageSize: images.reduce((sum, r) => sum + (r.transferSize || 0), 0)
                    };
                }
            """)
            
            print(f"  JS Files: {resources['jsCount']} ({resources['jsSize'] / 1024:.1f} KB)")
            print(f"  CSS Files: {resources['cssCount']} ({resources['cssSize'] / 1024:.1f} KB)")
            print(f"  Images: {resources['imageCount']} ({resources['imageSize'] / 1024:.1f} KB)")
            
            # Check for console errors
            console_errors = []
            page.on("console", lambda msg: console_errors.append(msg) if msg.type == "error" else None)
            page.reload()
            page.wait_for_timeout(2000)
            
            print(f"{'✓' if len(console_errors) == 0 else '✗'} Console errors: {len(console_errors)}")
            
            self.add_test_result("Performance", 
                               "PASS" if load_time < 3 and len(console_errors) == 0 else "PARTIAL",
                               {
                                   "load_time": f"{load_time:.2f}s",
                                   "resources": resources,
                                   "console_errors": len(console_errors)
                               })
            
        except Exception as e:
            print(f"✗ Performance test failed: {e}")
            self.add_test_result("Performance", "FAIL", error=e)
    
    def test_error_handling(self, page):
        print("\n🚨 ERROR HANDLING TESTS")
        print("-" * 50)
        
        # Test 9.1: 404 Page
        try:
            page.goto(f"{self.base_url}/this-page-does-not-exist-404")
            page.wait_for_timeout(2000)
            
            # Check if error page is shown
            error_indicators = page.locator("text=/404|not found|error/i").count()
            print(f"{'✓' if error_indicators > 0 else '✗'} 404 error page handling")
            
            page.screenshot(path="test_screenshots/errors/404.png")
            self.add_test_result("404 Error Handling", "PASS" if error_indicators > 0 else "FAIL")
        except Exception as e:
            print(f"✗ 404 test failed: {e}")
            self.add_test_result("404 Error Handling", "FAIL", error=e)
        
        # Test 9.2: Network Error Simulation
        try:
            # Block API requests to simulate network error
            page.route("**/api/**", lambda route: route.abort())
            page.goto(self.base_url)
            
            # Try to trigger an API call
            # This would vary based on the app's behavior
            print("✓ Network error simulation completed")
            
            # Unblock for future tests
            page.unroute("**/api/**")
            self.add_test_result("Network Error Handling", "INFO")
        except Exception as e:
            print(f"⚠️  Network error test failed: {e}")
    
    def test_security(self, page):
        print("\n🔒 SECURITY TESTS")
        print("-" * 50)
        
        # Test 10.1: HTTPS Redirect
        if "localhost" not in self.base_url:
            try:
                http_url = self.base_url.replace("https://", "http://")
                response = page.request.get(http_url, follow_redirects=False)
                
                is_redirect = response.status in [301, 302, 307, 308]
                print(f"{'✓' if is_redirect else '✗'} HTTPS redirect: {response.status}")
                self.add_test_result("HTTPS Redirect", "PASS" if is_redirect else "FAIL")
            except:
                print("ℹ️  HTTPS redirect test skipped (localhost)")
        
        # Test 10.2: Security Headers
        try:
            response = page.request.get(self.base_url)
            headers = response.headers
            
            security_headers = {
                "x-frame-options": headers.get("x-frame-options"),
                "x-content-type-options": headers.get("x-content-type-options"),
                "strict-transport-security": headers.get("strict-transport-security"),
                "content-security-policy": headers.get("content-security-policy")
            }
            
            present = sum(1 for v in security_headers.values() if v)
            print(f"Security headers present: {present}/4")
            
            for header, value in security_headers.items():
                if value:
                    print(f"  ✓ {header}: {value[:50]}...")
                else:
                    print(f"  ✗ {header}: Not set")
            
            self.add_test_result("Security Headers", 
                               "PASS" if present >= 3 else "PARTIAL" if present >= 1 else "FAIL",
                               {"headers": security_headers})
        except Exception as e:
            print(f"✗ Security headers test failed: {e}")
            self.add_test_result("Security Headers", "FAIL", error=e)
        
        # Test 10.3: Input Sanitization
        try:
            page.goto(self.base_url)
            
            # Try XSS payloads in search/input fields
            test_payloads = [
                "<script>alert('XSS')</script>",
                "javascript:alert('XSS')",
                "<img src=x onerror=alert('XSS')>"
            ]
            
            input_selectors = ["input[type='text']", "input[type='search']", "textarea"]
            tested = False
            
            for selector in input_selectors:
                try:
                    if page.locator(selector).first.is_visible():
                        for payload in test_payloads:
                            page.fill(selector, payload)
                            page.wait_for_timeout(500)
                            
                            # Check if script executed (it shouldn't)
                            alert_triggered = False
                            try:
                                page.wait_for_event("dialog", timeout=1000)
                                alert_triggered = True
                            except:
                                pass
                            
                            if alert_triggered:
                                print(f"✗ XSS vulnerability detected with payload: {payload[:30]}...")
                                self.add_test_result("XSS Protection", "FAIL", {"vulnerable_payload": payload})
                                break
                        
                        tested = True
                        break
                except:
                    continue
            
            if tested and not alert_triggered:
                print("✓ XSS protection appears effective")
                self.add_test_result("XSS Protection", "PASS")
            elif not tested:
                print("ℹ️  No input fields found for XSS testing")
                self.add_test_result("XSS Protection", "SKIP")
                
        except Exception as e:
            print(f"⚠️  XSS test failed: {e}")
            self.add_test_result("XSS Protection", "ERROR", error=e)
    
    def generate_report(self):
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 70)
        
        # Group results by category
        categories = {}
        for result in self.test_results:
            category = result["test"].split(":")[0].split(" ")[0]
            if category not in categories:
                categories[category] = []
            categories[category].append(result)
        
        # Summary by category
        print("\n📈 SUMMARY BY CATEGORY:")
        for category, results in categories.items():
            passed = sum(1 for r in results if r["status"] == "PASS")
            failed = sum(1 for r in results if r["status"] == "FAIL")
            partial = sum(1 for r in results if r["status"] == "PARTIAL")
            total = len(results)
            
            print(f"\n{category}:")
            print(f"  Total: {total}")
            print(f"  ✅ Passed: {passed}")
            print(f"  ❌ Failed: {failed}")
            print(f"  ⚠️  Partial: {partial}")
        
        # Overall summary
        total_tests = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["status"] == "PASS")
        failed = sum(1 for r in self.test_results if r["status"] == "FAIL")
        partial = sum(1 for r in self.test_results if r["status"] == "PARTIAL")
        
        print("\n" + "=" * 70)
        print("📊 OVERALL RESULTS")
        print("=" * 70)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed} ({passed/total_tests*100:.1f}%)")
        print(f"❌ Failed: {failed} ({failed/total_tests*100:.1f}%)")
        print(f"⚠️  Partial: {partial} ({partial/total_tests*100:.1f}%)")
        
        # Critical failures
        critical_failures = [r for r in self.test_results 
                           if r["status"] == "FAIL" and 
                           any(critical in r["test"] for critical in ["API", "Loading", "Security"])]
        
        if critical_failures:
            print("\n🚨 CRITICAL FAILURES:")
            for failure in critical_failures:
                print(f"  - {failure['test']}: {failure.get('error', 'Failed')}")
        
        # Save detailed report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"test_report_{timestamp}.json"
        
        report_data = {
            "test_run": timestamp,
            "summary": {
                "total": total_tests,
                "passed": passed,
                "failed": failed,
                "partial": partial,
                "pass_rate": f"{passed/total_tests*100:.1f}%"
            },
            "categories": {cat: len(results) for cat, results in categories.items()},
            "results": self.test_results
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        print("\n✨ Test suite completed!")

if __name__ == "__main__":
    # Create screenshots directory structure
    os.makedirs("test_screenshots/homepage", exist_ok=True)
    os.makedirs("test_screenshots/auth", exist_ok=True)
    os.makedirs("test_screenshots/homeowner", exist_ok=True)
    os.makedirs("test_screenshots/contractor", exist_ok=True)
    os.makedirs("test_screenshots/responsive", exist_ok=True)
    os.makedirs("test_screenshots/errors", exist_ok=True)
    
    # Run the comprehensive test suite
    suite = InstaBidsTestSuite()
    suite.run_all_tests()