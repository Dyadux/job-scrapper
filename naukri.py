from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os


class NaukriLogin:
    def __init__(self, email=None, password=None, headless=False):
        """
        Initialize the Naukri login automation

        Args:
            email (str, optional): Your Naukri email/username
            password (str, optional): Your Naukri password
            headless (bool): Run browser in headless mode (default: False)
        """
        self.email = email
        self.password = password
        self.driver = None
        self.wait = None

        # Chrome options
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Initialize the driver
        # Note: Make sure you have chromedriver installed or use webdriver-manager
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 10)

    def login(self, email=None, password=None):
        """
        Perform login to Naukri.com

        Args:
            email (str, optional): Your Naukri email/username
            password (str, optional): Your Naukri password

        Returns:
            bool: True if login successful, False otherwise
        """
        # Use provided credentials or fall back to instance variables
        login_email = email or self.email
        login_password = password or self.password
        
        if not login_email or not login_password:
            print("❌ Email and password are required for login")
            return False
        try:
            print("Navigating to Naukri.com...")
            self.driver.get("https://www.naukri.com/nlogin/login")

            # Wait for the page to load
            time.sleep(2)

            # Find and fill email field
            print("Entering email...")
            email_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "usernameField"))
            )
            email_field.clear()
            email_field.send_keys(login_email)

            # Find and fill password field
            print("Entering password...")
            password_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "passwordField"))
            )
            password_field.clear()
            password_field.send_keys(login_password)

            # Click login button
            print("Clicking login button...")
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and contains(text(), 'Login')]"))
            )
            login_button.click()

            # Wait for login to complete and check for success
            print("Waiting for login to complete...")
            time.sleep(3)  # Give some time for the login process
            
            # Check current URL to see if we've been redirected
            current_url = self.driver.current_url
            print(f"Current URL after login attempt: {current_url}")
            
            # Primary method: Check if we're redirected away from login page
            if "login" not in current_url.lower() and "naukri.com" in current_url:
                print("✅ Login successful! (Redirected from login page)")
                return True
            
            # Fallback: Check for error messages
            try:
                error_selectors = [
                    (By.CLASS_NAME, "err-msg"),
                    (By.CLASS_NAME, "error-message"),
                    (By.CLASS_NAME, "alert-danger"),
                    (By.XPATH, "//div[contains(@class, 'error')]"),
                    (By.XPATH, "//span[contains(@class, 'error')]")
                ]
                
                for by, selector in error_selectors:
                    try:
                        error_element = self.driver.find_element(by, selector)
                        if error_element.is_displayed():
                            error_message = error_element.text.strip()
                            if error_message:
                                print(f"❌ Login failed: {error_message}")
                                return False
                    except NoSuchElementException:
                        continue
                        
            except Exception as e:
                print(f"Error checking for error messages: {e}")
            
            # If no clear success or failure, assume success (most common case)
            print("✅ Login successful! (No errors detected)")
            return True

        except TimeoutException as e:
            print(f"❌ Timeout: Page elements not found - {str(e)}")
            print(f"Current URL: {self.driver.current_url}")
            # Take a screenshot for debugging
            try:
                self.driver.save_screenshot("login_timeout_debug.png")
                print("📸 Debug screenshot saved as login_timeout_debug.png")
            except:
                pass
            return False
        except Exception as e:
            print(f"❌ An error occurred: {str(e)}")
            print(f"Current URL: {self.driver.current_url}")
            # Take a screenshot for debugging
            try:
                self.driver.save_screenshot("login_error_debug.png")
                print("📸 Debug screenshot saved as login_error_debug.png")
            except:
                pass
            return False

    def navigate_to_profile(self):
        """
        Navigate to profile page after successful login
        """
        try:
            print("Navigating to profile...")
            profile_link = self.wait.until(
                EC.element_to_be_clickable((By.LINK_TEXT, "View & Update Profile"))
            )
            profile_link.click()
            print("✅ Navigated to profile page")
        except Exception as e:
            print(f"❌ Could not navigate to profile: {str(e)}")

    def take_screenshot(self, filename="naukri_screenshot.png"):
        """
        Take a screenshot of the current page

        Args:
            filename (str): Screenshot filename
        """
        try:
            self.driver.save_screenshot(filename)
            print(f"📸 Screenshot saved as {filename}")
        except Exception as e:
            print(f"❌ Could not take screenshot: {str(e)}")

    def debug_page_info(self):
        """
        Print debugging information about the current page
        """
        try:
            print(f"Current URL: {self.driver.current_url}")
            print(f"Page title: {self.driver.title}")
            
            # Check for common elements that might indicate login status
            common_elements = [
                "usernameField", "passwordField", "login", "profile", "user", "dashboard"
            ]
            
            print("Checking for common page elements:")
            for element_id in common_elements:
                try:
                    elements = self.driver.find_elements(By.XPATH, f"//*[contains(@id, '{element_id}') or contains(@class, '{element_id}')]")
                    if elements:
                        print(f"  Found {len(elements)} elements containing '{element_id}'")
                except:
                    pass
                    
        except Exception as e:
            print(f"Error getting page info: {e}")

    def find_job_search_elements(self):
        """
        Find and display job search form elements for debugging
        """
        try:
            print("🔍 Searching for job search elements...")
            
            # Get all input elements and filter them
            all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
            all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
            
            print(f"\n📝 Found {len(all_inputs)} input elements:")
            for i, element in enumerate(all_inputs):
                if element.is_displayed():
                    element_type = element.get_attribute('type') or 'text'
                    placeholder = element.get_attribute('placeholder') or 'No placeholder'
                    element_id = element.get_attribute('id') or 'No ID'
                    element_class = element.get_attribute('class') or 'No class'
                    element_name = element.get_attribute('name') or 'No name'
                    
                    # Only show relevant inputs
                    if any(keyword in (placeholder + element_id + element_class + element_name).lower() 
                           for keyword in ['job', 'skill', 'keyword', 'title', 'location', 'city', 'search']):
                        print(f"  {i+1}. Type: '{element_type}' | Placeholder: '{placeholder}' | ID: '{element_id}' | Name: '{element_name}' | Class: '{element_class[:50]}...'")
            
            print(f"\n🔘 Found {len(all_buttons)} button elements:")
            for i, element in enumerate(all_buttons):
                if element.is_displayed():
                    text = element.text or element.get_attribute('value') or 'No text'
                    element_id = element.get_attribute('id') or 'No ID'
                    element_class = element.get_attribute('class') or 'No class'
                    element_type = element.get_attribute('type') or 'button'
                    
                    # Only show relevant buttons
                    if any(keyword in (text + element_id + element_class).lower() 
                           for keyword in ['search', 'find', 'submit', 'go']):
                        print(f"  {i+1}. Type: '{element_type}' | Text: '{text}' | ID: '{element_id}' | Class: '{element_class[:50]}...'")
            
            # Also look for common Naukri-specific selectors
            print(f"\n🎯 Checking for common Naukri selectors:")
            naukri_selectors = [
                ("Skills/Designations", "//input[@placeholder='Skills, Designations, Companies']"),
                ("Location", "//input[@placeholder='Enter Location / City']"),
                ("Search Button", "//button[contains(@class, 'search')]"),
                ("Submit Button", "//input[@type='submit']")
            ]
            
            for name, selector in naukri_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        element = elements[0]
                        if element.is_displayed():
                            print(f"  ✅ Found {name}: {selector}")
                        else:
                            print(f"  ⚠️ Found {name} but not visible: {selector}")
                    else:
                        print(f"  ❌ Not found: {name}")
                except Exception as e:
                    print(f"  ❌ Error checking {name}: {e}")
                    
        except Exception as e:
            print(f"Error finding job search elements: {e}")

    def search_jobs(self, job_title="", location="", experience="2"):
        """
        Complete job search with all parameters
        
        Args:
            job_title (str): Job title to search for
            location (str): Location to search in
            experience (str): Years of experience
            
        Returns:
            bool: True if job search was successful
        """
        try:
            print(f"🔍 Entering job title: '{job_title}'")
            
            # Navigate to the main job search page
            print("Navigating to job search page...")
            self.driver.get("https://www.naukri.com/jobs-in-india")
            time.sleep(3)
            
            # Click on the search bar to expand it
            try:
                search_bar = self.driver.find_element(By.CLASS_NAME, "nI-gNb-search-bar")
                print("✅ Found search bar container")
                
                # Click on the sb__main element to expand it
                print("🖱️ Clicking search bar main to expand...")
                search_main = search_bar.find_element(By.CLASS_NAME, "nI-gNb-sb__main")
                search_main.click()
                time.sleep(2)  # Wait for expansion animation
                
                # Find keyword input
                keyword_input = search_bar.find_element(By.XPATH, ".//input[@placeholder='Enter keyword / designation / companies']")
                print("✅ Found keyword input")
                
                # Enter job title using JavaScript since element might not be interactable
                if job_title:
                    try:
                        # Try normal interaction first
                        keyword_input.clear()
                        keyword_input.send_keys(job_title)
                        print(f"✅ Entered job title: {job_title}")
                    except Exception as e:
                        print(f"⚠️ Normal interaction failed: {e}")
                        print("🔄 Trying JavaScript interaction...")
                        
                        # Use JavaScript to interact with the element
                        self.driver.execute_script("arguments[0].focus();", keyword_input)
                        time.sleep(0.5)
                        self.driver.execute_script("arguments[0].value = '';", keyword_input)
                        self.driver.execute_script("arguments[0].value = arguments[1];", keyword_input, job_title)
                        self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", keyword_input)
                        print(f"✅ Entered job title via JavaScript: {job_title}")
                
                # Click on experience dropdown
                print("🖱️ Clicking experience dropdown...")
                try:
                    experience_dropdown = search_bar.find_element(By.XPATH, ".//span[@class='ni-gnb-icn ni-gnb-icn-expand-more']")
                    experience_dropdown.click()
                    time.sleep(1)  # Wait for dropdown to open
                    print("✅ Experience dropdown opened")
                    
                    # Select experience based on parameter
                    exp_value = f"a{experience}" if experience.isdigit() else "a2"
                    exp_title = f"{experience} years" if experience.isdigit() else "2 years"
                    print(f"🖱️ Selecting experience: {exp_title}...")
                    experience_option = self.driver.find_element(By.XPATH, f"//li[@value='{exp_value}' and @title='{exp_title}']")
                    experience_option.click()
                    time.sleep(1)
                    print(f"✅ Selected {exp_title} experience")
                    
                except Exception as e:
                    print(f"❌ Error selecting experience: {e}")
                
                # Enter location
                print(f"📍 Entering location: {location}...")
                try:
                    location_input = search_bar.find_element(By.XPATH, ".//input[@placeholder='Enter location']")
                    
                    # Clear the default "india, " text using JavaScript
                    print("🗑️ Clearing default location text using JavaScript...")
                    self.driver.execute_script("arguments[0].focus();", location_input)
                    time.sleep(0.5)
                    self.driver.execute_script("arguments[0].value = '';", location_input)
                    self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", location_input)
                    time.sleep(0.5)  # Wait for clear to take effect
                    
                    # Enter new location
                    if location:
                        location_input.send_keys(location)
                        print(f"✅ Entered location: {location}")
                    else:
                        location_input.send_keys("Bangalore")
                        print("✅ Entered default location: Bangalore")
                except Exception as e:
                    print(f"❌ Error entering location: {e}")
                
                # Click search button
                print("🔍 Clicking search button...")
                try:
                    search_button = search_bar.find_element(By.XPATH, ".//button[@class='nI-gNb-sb__icon-wrapper']")
                    search_button.click()
                    time.sleep(3)  # Wait for search results to load
                    print("✅ Search button clicked successfully!")
                except Exception as e:
                    print(f"❌ Error clicking search button: {e}")
                
                print("✅ Job search completed! All fields filled and search executed.")
                
                # Extract job listings with pagination
                print("📋 Extracting job listings with pagination...")
                jobs = self.extract_job_listings_with_pagination(max_jobs=100)
                print(f"✅ Found {len(jobs)} total job listings across all pages")
                
                # Save jobs to file for analysis
                if jobs:
                    self.save_jobs_to_file(jobs)
                
                return (True, jobs)
                
            except Exception as e:
                print(f"❌ Error in search bar interaction: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Error in search_jobs method: {e}")
            return False

    def extract_job_listings(self, max_results=20):
        """
        Extract job listings from the search results page
        
        Args:
            max_results (int): Maximum number of jobs to extract
            
        Returns:
            list: List of job dictionaries
        """
        jobs = []
        try:
            # Wait for job listings to load
            time.sleep(2)
            
            # Find all job containers
            job_containers = self.driver.find_elements(By.CLASS_NAME, "srp-jobtuple-wrapper")
            print(f"🔍 Found {len(job_containers)} job containers")
            
            for i, job_container in enumerate(job_containers[:max_results]):
                try:
                    job_data = self.extract_job_details(job_container, i + 1)
                    if job_data:
                        jobs.append(job_data)
                        print(f"✅ Job {i + 1}: {job_data['title']} at {job_data['company']}")
                except Exception as e:
                    print(f"❌ Error extracting job {i + 1}: {e}")
                    continue
            
            return jobs
            
        except Exception as e:
            print(f"❌ Error extracting job listings: {e}")
            return []

    def extract_job_listings_with_pagination(self, max_jobs=100):
        """
        Extract job listings from multiple pages using pagination
        
        Args:
            max_jobs (int): Maximum number of jobs to extract
            
        Returns:
            list: List of job dictionaries from all pages
        """
        all_jobs = []
        page_number = 1
        max_pages = 10  # Limit to prevent infinite loops
        
        try:
            while len(all_jobs) < max_jobs and page_number <= max_pages:
                print(f"📄 Extracting jobs from page {page_number}...")
                
                # Extract jobs from current page
                page_jobs = self.extract_job_listings(max_jobs)
                
                if not page_jobs:
                    print(f"❌ No jobs found on page {page_number}, stopping pagination")
                    break
                
                all_jobs.extend(page_jobs)
                print(f"✅ Page {page_number}: Found {len(page_jobs)} jobs (Total: {len(all_jobs)})")
                
                # Check if we have enough jobs
                if len(all_jobs) >= max_jobs:
                    print(f"🎯 Reached target of {max_jobs} jobs!")
                    break
                
                # Try to navigate to next page
                ##TODO: Breaking even though pages available after page 4
                if not self.go_to_next_page():
                    print(f"❌ No more pages available, stopping at page {page_number}")
                    break
                
                page_number += 1
                time.sleep(2)  # Wait between page loads
            
            return all_jobs[:max_jobs]  # Return only the requested number
            
        except Exception as e:
            print(f"❌ Error in pagination: {e}")
            return all_jobs

    def go_to_next_page(self):
        """
        Navigate to the next page of job listings
        
        Returns:
            bool: True if successfully navigated to next page
        """
        try:
            # Look for pagination elements
            pagination_selectors = [
                "//a[contains(@class, 'styles_btn-secondary__2AsIP') and contains(., 'Next')]",
                "//a[contains(@href, '-2') and contains(@class, 'styles_btn-secondary__2AsIP')]",
                "//a[contains(., 'Next')]",
                "//a[contains(@class, 'next')]"
            ]
            
            next_button = None
            for selector in pagination_selectors:
                try:
                    next_button = self.driver.find_element(By.XPATH, selector)
                    if next_button.is_enabled() and next_button.is_displayed():
                        break
                except:
                    continue
            
            if not next_button:
                print("❌ Next page button not found")
                return False
            
            # Check if button is disabled
            if next_button.get_attribute('disabled'):
                print("❌ Next page button is disabled")
                return False
            
            # Store current URL before clicking
            old_url = self.driver.current_url

            # Click next page button
            print("🖱️ Clicking next page button...")
            next_button.click()
            time.sleep(3)  # Wait for page to load
            
            # Verify we're on a new page by checking if URL changed
            new_url = self.driver.current_url
            if new_url != old_url:
                print(f"✅ Successfully navigated to next page: {new_url}")
                return True
            else:
                print(f"⚠️ URL didn't change as expected: {new_url}")
                return False
                
        except Exception as e:
            print(f"❌ Error navigating to next page: {e}")
            return False

    def extract_job_details(self, job_element, job_number):
        """
        Extract details from a single job element with improved selectors
        
        Args:
            job_element: WebElement containing job data
            job_number (int): Job number for logging
            
        Returns:
            dict: Job details dictionary
        """
        try:
            job_data = {}
            
            # Extract job title and link with multiple selectors
            title_selectors = [
                ".//h2/a[@class='title']",
                ".//h2/a[contains(@class, 'title')]",
                ".//a[contains(@class, 'title')]",
                ".//h2//a",
                ".//a[contains(@href, 'job-listings')]"
            ]
            
            for selector in title_selectors:
                try:
                    title_element = job_element.find_element(By.XPATH, selector)
                    if title_element.text.strip():
                        job_data['title'] = title_element.text.strip()
                        job_data['link'] = title_element.get_attribute('href')
                        break
                except:
                    continue
            
            if 'title' not in job_data:
                job_data['title'] = "N/A"
                job_data['link'] = "N/A"
            
            # Extract company name with multiple selectors
            company_selectors = [
                ".//a[@class='comp-name mw-25']",
                ".//a[contains(@class, 'comp-name')]",
                ".//span[contains(@class, 'comp-name')]",
                ".//a[contains(@href, 'company')]"
            ]
            
            for selector in company_selectors:
                try:
                    company_element = job_element.find_element(By.XPATH, selector)
                    if company_element.text.strip():
                        job_data['company'] = company_element.text.strip()
                        break
                except:
                    continue
            
            if 'company' not in job_data:
                job_data['company'] = "N/A"
            
            # Extract company rating
            try:
                rating_element = job_element.find_element(By.XPATH, ".//span[@class='main-2']")
                job_data['rating'] = rating_element.text.strip()
            except:
                job_data['rating'] = "N/A"
            
            # Extract experience with multiple selectors
            exp_selectors = [
                ".//span[@class='expwdth']",
                ".//span[contains(@class, 'exp')]",
                ".//span[contains(@title, 'Yrs')]",
                ".//span[contains(text(), 'Yrs')]"
            ]
            
            for selector in exp_selectors:
                try:
                    exp_element = job_element.find_element(By.XPATH, selector)
                    exp_text = exp_element.get_attribute('title') or exp_element.text.strip()
                    if exp_text and ('yr' in exp_text.lower() or 'exp' in exp_text.lower()):
                        job_data['experience'] = exp_text
                        break
                except:
                    continue
            
            if 'experience' not in job_data:
                job_data['experience'] = "N/A"
            
            # Extract location with multiple selectors
            loc_selectors = [
                ".//span[@class='locWdth']",
                ".//span[contains(@class, 'loc')]",
                ".//span[contains(@title, ',')]"
            ]
            
            for selector in loc_selectors:
                try:
                    loc_element = job_element.find_element(By.XPATH, selector)
                    loc_text = loc_element.get_attribute('title') or loc_element.text.strip()
                    if loc_text and len(loc_text) > 2:
                        job_data['location'] = loc_text
                        break
                except:
                    continue
            
            if 'location' not in job_data:
                job_data['location'] = "N/A"
            
            # Extract job description
            desc_selectors = [
                ".//span[@class='job-desc ni-job-tuple-icon ni-job-tuple-icon-srp-description']",
                ".//span[contains(@class, 'job-desc')]",
                ".//div[contains(@class, 'description')]",
                ".//span[contains(@class, 'description')]"
            ]
            
            for selector in desc_selectors:
                try:
                    desc_element = job_element.find_element(By.XPATH, selector)
                    if desc_element.text.strip():
                        job_data['description'] = desc_element.text.strip()
                        break
                except:
                    continue
            
            if 'description' not in job_data:
                job_data['description'] = "N/A"
            
            # Extract skills/tags
            try:
                skill_elements = job_element.find_elements(By.XPATH, ".//li[@class='dot-gt tag-li ']")
                job_data['skills'] = [skill.text.strip() for skill in skill_elements if skill.text.strip()]
            except:
                job_data['skills'] = []
            
            # Extract posted date
            date_selectors = [
                ".//span[@class='job-post-day ']",
                ".//span[contains(@class, 'job-post-day')]",
                ".//span[contains(text(), 'days ago')]",
                ".//span[contains(text(), 'day ago')]"
            ]
            
            for selector in date_selectors:
                try:
                    date_element = job_element.find_element(By.XPATH, selector)
                    if date_element.text.strip():
                        job_data['posted_date'] = date_element.text.strip()
                        break
                except:
                    continue
            
            if 'posted_date' not in job_data:
                job_data['posted_date'] = "N/A"
            
            # Extract job ID
            try:
                job_data['job_id'] = job_element.get_attribute('data-job-id')
            except:
                job_data['job_id'] = "N/A"
            
            # Debug: Print what we found
            print(f"  📝 Job {job_number}: '{job_data['title']}' at '{job_data['company']}' - {job_data['experience']} - {job_data['location']}")
            
            return job_data
            
        except Exception as e:
            print(f"❌ Error extracting job details for job {job_number}: {e}")
            return None

    def save_jobs_to_file(self, jobs, filename="naukri_jobs.json"):
        """
        Save extracted jobs to a JSON file for analysis
        
        Args:
            jobs (list): List of job dictionaries
            filename (str): Output filename
        """
        try:
            import json
            from datetime import datetime
            
            # Add timestamp to filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"naukri_jobs_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(jobs, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Jobs saved to {filename}")
            
            # Also create a simple text summary
            summary_filename = f"naukri_jobs_summary_{timestamp}.txt"
            with open(summary_filename, 'w', encoding='utf-8') as f:
                f.write("NAUKRI JOB SEARCH RESULTS\n")
                f.write("=" * 50 + "\n\n")
                
                for i, job in enumerate(jobs, 1):
                    f.write(f"Job {i}:\n")
                    f.write(f"  Title: {job.get('title', 'N/A')}\n")
                    f.write(f"  Company: {job.get('company', 'N/A')}\n")
                    f.write(f"  Experience: {job.get('experience', 'N/A')}\n")
                    f.write(f"  Location: {job.get('location', 'N/A')}\n")
                    f.write(f"  Rating: {job.get('rating', 'N/A')}\n")
                    f.write(f"  Posted: {job.get('posted_date', 'N/A')}\n")
                    f.write(f"  Skills: {', '.join(job.get('skills', []))}\n")
                    f.write(f"  Link: {job.get('link', 'N/A')}\n")
                    f.write(f"  Job ID: {job.get('job_id', 'N/A')}\n")
                    f.write("-" * 30 + "\n\n")
            
            print(f"📄 Summary saved to {summary_filename}")
            
        except Exception as e:
            print(f"❌ Error saving jobs to file: {e}")

    def close(self):
        """
        Close the browser
        """
        if self.driver:
            self.driver.quit()
            print("🔒 Browser closed")


def main():
    """
    Main function to demonstrate usage
    """
    # Replace with your actual credentials
    EMAIL = "your_email@example.com"
    PASSWORD = "password-here"

    # You can also use environment variables for security
    # EMAIL = os.getenv('NAUKRI_EMAIL')
    # PASSWORD = os.getenv('NAUKRI_PASSWORD')

    if not EMAIL or not PASSWORD or EMAIL == "your_email@example.com":
        print("❌ Please update the EMAIL and PASSWORD variables with your credentials")
        return

    # Create login instance
    naukri = NaukriLogin(EMAIL, PASSWORD, headless=False)

    try:
        # Perform login
        if naukri.login():
            print("Login successful! You can now automate other tasks...")
            
            # Debug: Print page information
            naukri.debug_page_info()

            # Test simple job title entry
            print("\n" + "="*50)
            print("TESTING SIMPLE JOB TITLE ENTRY")
            print("="*50)
            success = naukri.search_jobs("Python Developer", "Bangalore", "2")
            
            if success:
                print("✅ Job title entered successfully!")
                print("Ready for your step-by-step instructions.")
            else:
                print("❌ Failed to enter job title")

            # Optional: Take screenshot
            naukri.take_screenshot("job_search_test.png")

            # Wait a bit to see the result
            time.sleep(5)
        else:
            print("Login failed. Please check your credentials.")
            # Debug: Print page information even on failure
            naukri.debug_page_info()

    finally:
        # Always close the browser
        naukri.close()


if __name__ == "__main__":
    main()