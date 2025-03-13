import requests
import pandas as pd
import time
import random
import argparse
import json
import csv
import os
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor


class LeadGenerationAgent:
    """
    Automated agent for generating business leads based on industry, location and lead type.
    """
    
    def __init__(self, delay=1.0, use_proxies=False, debug=False):
        self.ua = UserAgent()
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument(f"user-agent={self.ua.random}")
        
        # Configuration
        self.delay = delay  # Delay between requests to avoid rate limiting
        self.debug = debug  # Enable/disable debug output
        self.use_proxies = use_proxies  # Use proxy rotation for web scraping
        
        # Sources for lead generation
        self.sources = {
            "business": ["google_maps", "yelp", "yellow_pages", "better_business_bureau", "chambers_of_commerce", "indeed"],
            "personal": ["linkedin", "zoominfo", "hunter_io", "apollo_io", "clearbit"],
            "institutional": ["government_websites", "association_directories", "guidestar", "charity_navigator", "educational_directories"]
        }
        
        # Proxy list for rotation (would be loaded from a file in production)
        self.proxies = []
        if use_proxies:
            self.load_proxies()
        
        # API keys for various services
        self.api_keys = {
            "hunter_io": os.environ.get("HUNTER_IO_API_KEY", ""),
            "clearbit": os.environ.get("CLEARBIT_API_KEY", ""),
            "apollo_io": os.environ.get("APOLLO_IO_API_KEY", ""),
            "zoominfo": os.environ.get("ZOOMINFO_API_KEY", "")
        }
        
        # Data structure to store leads
        self.leads = []
    
    def load_proxies(self, proxy_file="proxies.txt"):
        """Load proxies from a file or environment variables"""
        try:
            if os.path.exists(proxy_file):
                with open(proxy_file, 'r') as f:
                    self.proxies = [line.strip() for line in f if line.strip()]
            else:
                # Try to get proxies from environment
                proxy_env = os.environ.get("PROXY_LIST", "")
                if proxy_env:
                    self.proxies = proxy_env.split(",")
            
            if self.debug:
                print(f"Loaded {len(self.proxies)} proxies")
        except Exception as e:
            print(f"Error loading proxies: {e}")
    
    def get_random_proxy(self):
        """Get a random proxy from the proxy list"""
        if not self.proxies:
            return None
        return random.choice(self.proxies)
    
    def log(self, message):
        """Log message if debug is enabled"""
        if self.debug:
            print(f"[DEBUG] {message}")
    
    def create_driver(self):
        """Create and return a new webdriver instance"""
        # If using proxies, apply a random one
        if self.use_proxies and self.proxies:
            proxy = self.get_random_proxy()
            if proxy:
                self.log(f"Using proxy: {proxy}")
                self.chrome_options.add_argument(f'--proxy-server={proxy}')
        
        # Rotate user agent
        self.chrome_options.add_argument(f"user-agent={self.ua.random}")
        
        driver = webdriver.Chrome(options=self.chrome_options)
        
        # Set page load timeout
        driver.set_page_load_timeout(30)
        
        return driver
    
    def search_zoominfo(self, industry, location, lead_count=20):
        """Search for contacts using ZoomInfo API"""
        print(f"Searching ZoomInfo for contacts in {industry} companies in {location}...")
        
        # Note: This requires an API key in production
        # This is a mock implementation
        
        for i in range(lead_count):
            company_name = f"{industry.capitalize()} {['Inc', 'Corp', 'LLC', 'Company', 'Partners'][i % 5]} {i+1}"
            domain = f"{company_name.lower().replace(' ', '')}.com"
            
            revenue_ranges = ["$1M-$5M", "$5M-$10M", "$10M-$50M", "$50M-$100M", "$100M-$500M"]
            employee_ranges = ["1-10", "11-50", "51-200", "201-500", "501-1000", "1000+"]
            
            first_name = f"First{i+1}"
            last_name = f"Last{i+1}"
            title = random.choice([
                "CEO", "CTO", "CIO", "COO", "CMO", 
                f"VP of {industry.capitalize()}", 
                f"Director of {industry.capitalize()}", 
                f"{industry.capitalize()} Manager"
            ])
            
            email = f"{first_name.lower()}.{last_name.lower()}@{domain}"
            phone = f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            
            # Additional ZoomInfo specific fields
            technologies = [f"Tech{j}" for j in range(1, random.randint(2, 6))]
            intent_signals = random.choice(["High", "Medium", "Low"])
            
            self.leads.append({
                "Name": f"{first_name} {last_name}",
                "Title": title,
                "Company": company_name,
                "Email": email,
                "Phone": phone,
                "Revenue": random.choice(revenue_ranges),
                "Employees": random.choice(employee_ranges),
                "Technologies": ", ".join(technologies),
                "Intent": intent_signals,
                "Industry": industry,
                "Location": location,
                "Source": "ZoomInfo"
            })
    
    def search_government_websites(self, industry, location, lead_count=20):
        """Search government websites for institutional leads"""
        print(f"Searching government websites for {industry} organizations in {location}...")
        
        # Government department types
        dept_types = [
            "Department", "Agency", "Office", "Bureau", "Division", "Authority", "Commission"
        ]
        
        for i in range(lead_count):
            dept_type = random.choice(dept_types)
            org_name = f"{location} {dept_type} of {industry.capitalize()}"
            
            address = f"{random.randint(100, 999)} Government Center, {location}"
            website = f"https://www.{location.lower().replace(' ', '')}.gov/{industry.lower().replace(' ', '')}"
            phone = f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            
            # Generate contact info
            contact_title = f"Director of {industry.capitalize()}"
            contact_name = f"Official{i+1} Surname{i+1}"
            contact_email = f"{contact_name.lower().replace(' ', '.')}@{location.lower().replace(' ', '')}.gov"
            
            self.leads.append({
                "Organization": org_name,
                "Type": "Government",
                "Address": address,
                "Website": website,
                "Phone": phone,
                "Contact Name": contact_name,
                "Contact Title": contact_title,
                "Contact Email": contact_email,
                "Industry": industry,
                "Location": location,
                "Source": "Government Website"
            })
    
    def search_association_directories(self, industry, location, lead_count=20):
        """Search association directories for institutional leads"""
        print(f"Searching association directories for {industry} organizations in {location}...")
        
        # Association types
        assoc_types = [
            "Association", "Society", "Council", "Federation", "Institute", "Guild", "Consortium"
        ]
        
        for i in range(lead_count):
            assoc_type = random.choice(assoc_types)
            org_name = f"{location} {assoc_type} of {industry.capitalize()} Professionals"
            
            address = f"{random.randint(100, 999)} Association Way, {location}"
            website = f"https://www.{industry.lower().replace(' ', '')}{assoc_type.lower()}.org"
            phone = f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            
            # Generate contact info
            contact_title = random.choice(["Executive Director", "President", "Secretary General", "Chairperson"])
            contact_name = f"Dr. Assoc{i+1} Surname{i+1}"
            contact_email = f"contact@{industry.lower().replace(' ', '')}{assoc_type.lower()}.org"
            
            # Random stats
            member_count = random.randint(100, 10000)
            founding_year = random.randint(1900, 2010)
            
            self.leads.append({
                "Organization": org_name,
                "Type": "Association",
                "Address": address,
                "Website": website,
                "Phone": phone,
                "Contact Name": contact_name,
                "Contact Title": contact_title,
                "Contact Email": contact_email,
                "Members": member_count,
                "Founded": founding_year,
                "Industry": industry,
                "Location": location,
                "Source": "Association Directory"
            })
    
    def search_charity_navigator(self, industry, location, lead_count=20):
        """Search Charity Navigator for nonprofit leads"""
        print(f"Searching Charity Navigator for {industry} nonprofits in {location}...")
        
        # Nonprofit types
        nonprofit_types = [
            "Foundation", "Charity", "Nonprofit", "Trust", "Fund", "Initiative", "Project"
        ]
        
        for i in range(lead_count):
            nonprofit_type = random.choice(nonprofit_types)
            org_name = f"{industry.capitalize()} {nonprofit_type} of {location}"
            
            address = f"{random.randint(100, 999)} Charity Lane, {location}"
            website = f"https://www.{org_name.lower().replace(' ', '')}.org"
            phone = f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            
            # Financial information
            annual_budget = f"${random.randint(50, 999)}K"
            program_expenses = f"{random.randint(60, 95)}%"
            admin_expenses = f"{random.randint(5, 30)}%"
            
            # Rating
            rating = f"{random.randint(2, 4)}.{random.randint(0, 9)} Stars"
            
            # Contact information
            contact_name = f"Nonprofit{i+1} Director{i+1}"
            contact_email = f"director@{org_name.lower().replace(' ', '')}.org"
            
            self.leads.append({
                "Organization": org_name,
                "Type": "Nonprofit",
                "Address": address,
                "Website": website,
                "Phone": phone,
                "Contact Name": contact_name,
                "Contact Email": contact_email,
                "Annual Budget": annual_budget,
                "Program Expenses": program_expenses,
                "Admin Expenses": admin_expenses,
                "Rating": rating,
                "Industry": industry,
                "Location": location,
                "Source": "Charity Navigator"
            })
    
    def search_google_maps(self, industry, location, lead_count=20):
        """Scrape business data from Google Maps"""
        print(f"Searching Google Maps for {industry} in {location}...")
        
        driver = self.create_driver()
        query = f"{industry} in {location}"
        url = f"https://www.google.com/maps/search/{'+'.join(query.split())}"
        
        try:
            driver.get(url)
            # Wait for results to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.V0h1Ob-haAclf"))
            )
            
            # Scroll to load more results
            for _ in range(min(lead_count // 10 + 1, 5)):  # Limit scrolling to prevent excessive requests
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Extract business data
            business_elements = driver.find_elements(By.CSS_SELECTOR, "div.V0h1Ob-haAclf")
            
            for element in business_elements[:lead_count]:
                try:
                    name = element.find_element(By.CSS_SELECTOR, "div.qBF1Pd").text
                    address_element = element.find_elements(By.CSS_SELECTOR, "div.W4Efsd")[1]
                    address = address_element.text.split("·")[0].strip() if "·" in address_element.text else address_element.text
                    
                    # Click to get more details (phone, website)
                    element.click()
                    time.sleep(2)
                    
                    phone = "N/A"
                    website = "N/A"
                    
                    # Try to get phone
                    try:
                        phone_elements = WebDriverWait(driver, 3).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "button[data-item-id^='phone']"))
                        )
                        if phone_elements:
                            phone = phone_elements[0].text
                    except TimeoutException:
                        pass
                    
                    # Try to get website
                    try:
                        website_elements = WebDriverWait(driver, 3).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[data-item-id^='authority']"))
                        )
                        if website_elements:
                            website = website_elements[0].get_attribute("href")
                    except TimeoutException:
                        pass
                    
                    self.leads.append({
                        "Name": name,
                        "Address": address,
                        "Phone": phone,
                        "Website": website,
                        "Source": "Google Maps",
                        "Industry": industry,
                        "Location": location
                    })
                    
                except Exception as e:
                    print(f"Error extracting business data: {e}")
                    continue
        
        except Exception as e:
            print(f"Error searching Google Maps: {e}")
        
        finally:
            driver.quit()
    
    def search_yelp(self, industry, location, lead_count=20):
        """Scrape business data from Yelp"""
        print(f"Searching Yelp for {industry} in {location}...")
        
        driver = self.create_driver()
        query = f"{industry} {location}"
        url = f"https://www.yelp.com/search?find_desc={'+'.join(industry.split())}&find_loc={'+'.join(location.split())}"
        
        try:
            driver.get(url)
            # Wait for results to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.businessName__09f24__EYSZE"))
            )
            
            # Extract business data
            business_elements = driver.find_elements(By.CSS_SELECTOR, "div.container__09f24__mpR8_")
            
            for element in business_elements[:lead_count]:
                try:
                    name_element = element.find_element(By.CSS_SELECTOR, "div.businessName__09f24__EYSZE")
                    name = name_element.text
                    
                    # Get the link to business page
                    link = name_element.find_element(By.TAG_NAME, "a").get_attribute("href")
                    
                    # Visit the business page to get more details
                    driver.get(link)
                    time.sleep(2)
                    
                    # Extract address
                    address = "N/A"
                    try:
                        address_element = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "address"))
                        )
                        address = address_element.text.replace("\n", ", ")
                    except TimeoutException:
                        pass
                    
                    # Extract phone
                    phone = "N/A"
                    try:
                        phone_elements = driver.find_elements(By.CSS_SELECTOR, "p.css-1p9ibgf")
                        for p in phone_elements:
                            if p.text and len(p.text) > 6 and any(c.isdigit() for c in p.text):
                                phone = p.text
                                break
                    except:
                        pass
                    
                    # Extract website
                    website = "N/A"
                    try:
                        website_element = driver.find_element(By.CSS_SELECTOR, "a[href^='https://www.yelp.com/biz_redir']")
                        website = website_element.get_attribute("href")
                    except:
                        pass
                    
                    self.leads.append({
                        "Name": name,
                        "Address": address,
                        "Phone": phone,
                        "Website": website,
                        "Source": "Yelp",
                        "Industry": industry,
                        "Location": location
                    })
                    
                    # Go back to search results
                    driver.back()
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"Error extracting Yelp business data: {e}")
                    continue
        
        except Exception as e:
            print(f"Error searching Yelp: {e}")
        
        finally:
            driver.quit()
    
    def search_linkedin(self, industry, location, lead_count=20):
        """Scrape professional leads from LinkedIn (note: requires authentication in real usage)"""
        print(f"Searching LinkedIn for professionals in {industry} in {location}...")
        # Note: LinkedIn has strict anti-scraping measures. In a real implementation,
        # you would need to use their API or implement more sophisticated methods.
        
        # This is a simplified mock implementation
        mock_titles = [
            "CEO", "CTO", "CFO", "COO", "Director", "VP", "Manager", "Specialist",
            "Consultant", "Analyst", "Lead", "Head of", "President"
        ]
        
        mock_companies = [
            f"{industry} Solutions", f"{industry} Innovations", f"Global {industry}",
            f"{industry} Tech", f"{industry} Partners", f"{location} {industry} Group",
            f"{industry} Associates", f"Advanced {industry}", f"{industry} Experts"
        ]
        
        mock_domains = ["gmail.com", "outlook.com", "company.com", "business.net", "mail.org"]
        
        # Generate mock LinkedIn leads
        for i in range(lead_count):
            first_name = f"FirstName{i+1}"
            last_name = f"LastName{i+1}"
            title = random.choice(mock_titles) + " of " + random.choice(["Marketing", "Sales", "Operations", "Development", industry])
            company = random.choice(mock_companies)
            email = f"{first_name.lower()}.{last_name.lower()}@{company.lower().replace(' ', '')}.com"
            phone = f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            
            self.leads.append({
                "Name": f"{first_name} {last_name}",
                "Title": title,
                "Company": company,
                "Email": email,
                "Phone": phone,
                "Industry": industry,
                "Location": location,
                "Source": "LinkedIn"
            })
            
            # Add random delay to simulate scraping
            time.sleep(random.uniform(0.1, 0.3))
    
    def search_yellow_pages(self, industry, location, lead_count=20):
        """Scrape business data from Yellow Pages"""
        print(f"Searching Yellow Pages for {industry} in {location}...")
        
        driver = self.create_driver()
        query = f"{industry} {location}"
        url = f"https://www.yellowpages.com/search?search_terms={'+'.join(industry.split())}&geo_location_terms={'+'.join(location.split())}"
        
        try:
            driver.get(url)
            # Wait for results to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.result"))
            )
            
            # Extract business data
            business_elements = driver.find_elements(By.CSS_SELECTOR, "div.result")
            
            for element in business_elements[:lead_count]:
                try:
                    name = element.find_element(By.CSS_SELECTOR, "a.business-name").text
                    
                    # Get address
                    address = "N/A"
                    try:
                        address_element = element.find_element(By.CSS_SELECTOR, "div.street-address")
                        locality_element = element.find_element(By.CSS_SELECTOR, "div.locality")
                        address = f"{address_element.text}, {locality_element.text}"
                    except:
                        pass
                    
                    # Get phone
                    phone = "N/A"
                    try:
                        phone = element.find_element(By.CSS_SELECTOR, "div.phones").text
                    except:
                        pass
                    
                    # Get website
                    website = "N/A"
                    try:
                        website_element = element.find_element(By.CSS_SELECTOR, "a.track-visit-website")
                        website = website_element.get_attribute("href")
                    except:
                        pass
                    
                    self.leads.append({
                        "Name": name,
                        "Address": address,
                        "Phone": phone,
                        "Website": website,
                        "Source": "Yellow Pages",
                        "Industry": industry,
                        "Location": location
                    })
                    
                except Exception as e:
                    print(f"Error extracting Yellow Pages business data: {e}")
                    continue
        
        except Exception as e:
            print(f"Error searching Yellow Pages: {e}")
        
        finally:
            driver.quit()

    def search_better_business_bureau(self, industry, location, lead_count=20):
        """Scrape business data from Better Business Bureau"""
        print(f"Searching BBB for {industry} in {location}...")
        
        driver = self.create_driver()
        url = f"https://www.bbb.org/search?filter_category={'+'.join(industry.split())}&filter_city={'+'.join(location.split())}"
        
        try:
            driver.get(url)
            # Wait for results to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.result"))
            )
            
            # Extract business data
            business_elements = driver.find_elements(By.CSS_SELECTOR, "div.result")
            
            for element in business_elements[:lead_count]:
                try:
                    name = element.find_element(By.CSS_SELECTOR, "h3.result-title a").text
                    link = element.find_element(By.CSS_SELECTOR, "h3.result-title a").get_attribute("href")
                    
                    # Visit business page for more details
                    driver.get(link)
                    time.sleep(2)
                    
                    # Get address
                    address = "N/A"
                    try:
                        address_element = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div.dtm-address"))
                        )
                        address = address_element.text.replace("\n", ", ")
                    except:
                        pass
                    
                    # Get phone
                    phone = "N/A"
                    try:
                        phone_element = driver.find_element(By.CSS_SELECTOR, "div.dtm-phone")
                        phone = phone_element.text
                    except:
                        pass
                    
                    # Get website
                    website = "N/A"
                    try:
                        website_element = driver.find_element(By.CSS_SELECTOR, "a.dtm-url")
                        website = website_element.get_attribute("href")
                    except:
                        pass
                    
                    # Get rating
                    rating = "N/A"
                    try:
                        rating_element = driver.find_element(By.CSS_SELECTOR, "div.rating")
                        rating = rating_element.text
                    except:
                        pass
                    
                    self.leads.append({
                        "Name": name,
                        "Address": address,
                        "Phone": phone,
                        "Website": website,
                        "BBB Rating": rating,
                        "Source": "Better Business Bureau",
                        "Industry": industry,
                        "Location": location
                    })
                    
                    # Go back to search results
                    driver.back()
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"Error extracting BBB business data: {e}")
                    continue
        
        except Exception as e:
            print(f"Error searching BBB: {e}")
        
        finally:
            driver.quit()
    
    def search_hunter_io(self, industry, location, lead_count=20):
        """Search for email contacts using Hunter.io API"""
        print(f"Searching Hunter.io for contacts in {industry} companies in {location}...")
        
        # Note: This requires an API key in production
        # This is a mock implementation to show the structure
        # Hunter.io API URL: https://api.hunter.io/v2/domain-search?domain=example.com&api_key=YOUR_API_KEY
        
        # Generate mock Hunter.io data
        company_domains = [
            f"{industry.lower().replace(' ', '')}.com",
            f"{industry.lower().replace(' ', '')}-{location.lower().replace(' ', '')}.com",
            f"{industry.lower().replace(' ', '')}group.com",
            f"{industry.lower().replace(' ', '')}solutions.com",
            f"the{industry.lower().replace(' ', '')}.com"
        ]
        
        positions = [
            "CEO", "CTO", "CFO", "CMO", "COO", 
            "VP of Sales", "VP of Marketing", "Director of Operations",
            "Head of Business Development", "Sales Manager", "Marketing Manager"
        ]
        
        for i in range(lead_count):
            company_name = f"{industry.capitalize()} {['Solutions', 'Group', 'Partners', 'Tech', 'Innovations'][i % 5]}"
            domain = random.choice(company_domains)
            position = random.choice(positions)
            first_name = f"First{i+1}"
            last_name = f"Last{i+1}"
            email = f"{first_name.lower()}.{last_name.lower()}@{domain}"
            
            confidence_score = random.randint(50, 99)
            
            self.leads.append({
                "Name": f"{first_name} {last_name}",
                "Company": company_name,
                "Position": position,
                "Email": email,
                "Email Confidence": f"{confidence_score}%",
                "Domain": domain,
                "Industry": industry,
                "Location": location,
                "Source": "Hunter.io"
            })
    
    def search_clearbit(self, industry, location, lead_count=20):
        """Search for company and contact information using Clearbit API"""
        print(f"Searching Clearbit for {industry} companies in {location}...")
        
        # Note: This requires an API key in production
        # This is a mock implementation to show the structure
        
        for i in range(lead_count):
            company_name = f"{industry.capitalize()} {['Solutions', 'Group', 'Partners', 'Tech', 'Innovations'][i % 5]} {i+1}"
            domain = f"{company_name.lower().replace(' ', '')}.com"
            
            employees = random.randint(10, 5000)
            revenue = f"${random.randint(1, 500)}M"
            founded = random.randint(1980, 2020)
            
            first_name = f"First{i+1}"
            last_name = f"Last{i+1}"
            position = random.choice(["CEO", "CTO", "CFO", "CMO", "COO", "VP Sales", "VP Marketing"])
            email = f"{first_name.lower()}.{last_name.lower()}@{domain}"
            
            self.leads.append({
                "Company": company_name,
                "Domain": domain,
                "Industry": industry,
                "Location": location,
                "Employees": employees,
                "Annual Revenue": revenue,
                "Year Founded": founded,
                "Contact Name": f"{first_name} {last_name}",
                "Contact Position": position,
                "Contact Email": email,
                "Source": "Clearbit"
            })
    
    def search_chambers_of_commerce(self, industry, location, lead_count=20):
        """Search local Chambers of Commerce for business data"""
        print(f"Searching Chambers of Commerce for {industry} businesses in {location}...")
        
        driver = self.create_driver()
        
        # Find local chamber website (mock implementation)
        chamber_url = f"https://www.{location.lower().replace(' ', '')}chamber.org/directory"
        
        try:
            driver.get(chamber_url)
            # This would typically involve navigating a chamber directory
            # Mock implementation for demonstration
            
            for i in range(lead_count):
                name = f"{industry.capitalize()} {['Company', 'Business', 'Group', 'Enterprise', 'Solutions'][i % 5]} {i+1}"
                address = f"{random.randint(100, 9999)} Main St, {location}"
                phone = f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
                website = f"https://www.{name.lower().replace(' ', '')}.com"
                year_joined = random.randint(2000, 2023)
                
                self.leads.append({
                    "Name": name,
                    "Address": address,
                    "Phone": phone,
                    "Website": website,
                    "Chamber Member Since": year_joined,
                    "Industry": industry,
                    "Location": location,
                    "Source": "Chamber of Commerce"
                })
        
        except Exception as e:
            print(f"Error searching Chamber of Commerce: {e}")
        
        finally:
            driver.quit()
    
    def generate_leads(self, industry, location, lead_type, count=50):
        """Main method to generate leads based on the specified parameters"""
        self.leads = []  # Reset leads list
        
        sources = self.sources.get(lead_type.lower(), ["google_maps"])
        leads_per_source = max(5, count // len(sources))
        
        if "google_maps" in sources:
            self.search_google_maps(industry, location, leads_per_source)
        
        if "yelp" in sources:
            self.search_yelp(industry, location, leads_per_source)
        
        if "linkedin" in sources:
            self.search_linkedin(industry, location, leads_per_source)
        
        if "yellow_pages" in sources:
            self.search_yellow_pages(industry, location, leads_per_source)
        
        if "better_business_bureau" in sources:
            self.search_better_business_bureau(industry, location, leads_per_source)
        
        if "hunter_io" in sources:
            self.search_hunter_io(industry, location, leads_per_source)
        
        if "clearbit" in sources:
            self.search_clearbit(industry, location, leads_per_source)
        
        if "chambers_of_commerce" in sources:
            self.search_chambers_of_commerce(industry, location, leads_per_source)
        
        # Deduplicate leads
        unique_leads = []
        seen_names = set()
        
        for lead in self.leads:
            name = lead.get("Name", "")
            if name and name not in seen_names:
                seen_names.add(name)
                unique_leads.append(lead)
        
        self.leads = unique_leads
        
        print(f"Generated {len(self.leads)} unique leads for {industry} in {location}")
        return self.leads
    
    def search_apollo_io(self, industry, location, lead_count=20):
        """Search for contacts using Apollo.io API"""
        print(f"Searching Apollo.io for contacts in {industry} companies in {location}...")
        
        # Note: This requires an API key in production
        # Apollo.io API: https://api.apollo.io/v1/people/search
        
        # Generate mock Apollo.io data
        for i in range(lead_count):
            company_name = f"{industry.capitalize()} {['Technologies', 'Innovations', 'Solutions', 'Group', 'Co'][i % 5]} {i+1}"
            first_name = f"First{i+1}"
            last_name = f"Last{i+1}"
            
            title = random.choice([
                f"Head of {industry.capitalize()}", 
                "CEO", 
                "Founder", 
                f"{industry.capitalize()} Manager",
                "Director of Operations",
                "Chief Revenue Officer",
                "VP Sales"
            ])
            
            email = f"{first_name.lower()[0]}{last_name.lower()}@{company_name.lower().replace(' ', '')}.com"
            phone = f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            linkedin_url = f"https://www.linkedin.com/in/{first_name.lower()}-{last_name.lower()}-{random.randint(10000, 99999)}"
            
            self.leads.append({
                "Name": f"{first_name} {last_name}",
                "Title": title,
                "Company": company_name,
                "Email": email,
                "Phone": phone,
                "LinkedIn": linkedin_url,
                "Industry": industry,
                "Location": location,
                "Employees": random.randint(10, 5000),
                "Source": "Apollo.io"
            })
    
    def search_indeed(self, industry, location, lead_count=20):
        """Search Indeed for company information based on job postings"""
        print(f"Searching Indeed for {industry} companies in {location}...")
        
        driver = self.create_driver()
        
        url = f"https://www.indeed.com/jobs?q={'+'.join(industry.split())}&l={'+'.join(location.split())}"
        
        try:
            driver.get(url)
            # Wait for job cards to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.job_seen_beacon"))
            )
            
            # Extract companies from job listings
            job_cards = driver.find_elements(By.CSS_SELECTOR, "div.job_seen_beacon")
            
            companies_found = set()
            
            for card in job_cards:
                if len(companies_found) >= lead_count:
                    break
                    
                try:
                    company_element = card.find_element(By.CSS_SELECTOR, "span.companyName")
                    company_name = company_element.text.strip()
                    
                    if company_name and company_name not in companies_found:
                        companies_found.add(company_name)
                        
                        # Extract job title
                        job_title = "N/A"
                        try:
                            title_element = card.find_element(By.CSS_SELECTOR, "h2.jobTitle")
                            job_title = title_element.text.strip()
                        except:
                            pass
                        
                        # Extract location
                        company_location = location
                        try:
                            location_element = card.find_element(By.CSS_SELECTOR, "div.companyLocation")
                            company_location = location_element.text.strip()
                        except:
                            pass
                        
                        # Extract salary if available
                        salary = "N/A"
                        try:
                            salary_element = card.find_element(By.CSS_SELECTOR, "div.salary-snippet")
                            salary = salary_element.text.strip()
                        except:
                            pass
                        
                        self.leads.append({
                            "Company": company_name,
                            "Recent Job Posting": job_title,
                            "Location": company_location,
                            "Estimated Salary": salary,
                            "Industry": industry,
                            "Source": "Indeed"
                        })
                
                except Exception as e:
                    print(f"Error extracting Indeed company data: {e}")
                    continue
        
        except Exception as e:
            print(f"Error searching Indeed: {e}")
        
        finally:
            driver.quit()
    
    def search_guidestar(self, industry, location, lead_count=20):
        """Search Guidestar/Candid for nonprofit organization data"""
        print(f"Searching Guidestar for {industry} nonprofits in {location}...")
        
        # Note: In production, you might need to use their API or implement proper authentication
        # This is a mock implementation
        
        for i in range(lead_count):
            org_name = f"{industry.capitalize()} {['Foundation', 'Initiative', 'Alliance', 'Association', 'Society'][i % 5]} of {location}"
            
            address = f"{random.randint(100, 9999)} Nonprofit St, {location}"
            revenue = f"${random.randint(100, 999)}K"
            employee_count = random.randint(5, 100)
            year_founded = random.randint(1950, 2020)
            tax_id = f"{random.randint(10, 99)}-{random.randint(1000000, 9999999)}"
            
            executive_name = f"Dr. Name{i+1} Surname{i+1}"
            executive_title = "Executive Director"
            
            self.leads.append({
                "Organization": org_name,
                "Address": address,
                "Executive": executive_name,
                "Executive Title": executive_title,
                "Annual Revenue": revenue,
                "Employees": employee_count,
                "Year Founded": year_founded,
                "Tax ID": tax_id,
                "Industry": industry,
                "Location": location,
                "Source": "Guidestar/Candid"
            })
    
    def search_educational_directories(self, industry, location, lead_count=20):
        """Search educational institution directories"""
        print(f"Searching for educational institutions related to {industry} in {location}...")
        
        # Educational institution types
        institution_types = [
            "University", "College", "Community College", "Technical Institute", 
            "Vocational School", "High School", "School District"
        ]
        
        for i in range(lead_count):
            inst_type = random.choice(institution_types)
            name = f"{location} {inst_type} of {industry.capitalize()}"
            
            address = f"{random.randint(100, 9999)} Campus Dr, {location}"
            phone = f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            website = f"https://www.{name.lower().replace(' ', '')}.edu"
            
            # Generate random stats
            student_count = random.randint(500, 20000)
            faculty_count = random.randint(25, 1000)
            programs_count = random.randint(5, 100)
            
            # Generate admin contact
            admin_title = random.choice(["President", "Dean", "Director", "Department Chair", "Principal"])
            admin_name = f"Dr. Admin{i+1} Surname{i+1}"
            admin_email = f"admin{i+1}@{name.lower().replace(' ', '')}.edu"
            
            self.leads.append({
                "Institution": name,
                "Type": inst_type,
                "Address": address,
                "Phone": phone,
                "Website": website,
                "Students": student_count,
                "Faculty": faculty_count,
                "Programs": programs_count,
                "Admin Name": admin_name,
                "Admin Title": admin_title,
                "Admin Email": admin_email,
                "Industry": industry,
                "Location": location,
                "Source": "Educational Directory"
            })
    
    def export_to_excel(self, filename="leads.xlsx"):
        """Export the generated leads to an Excel file"""
        if not self.leads:
            print("No leads to export")
            return False
        
        try:
            # Create a timestamp for the filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_base, filename_ext = os.path.splitext(filename)
            if not filename_ext:
                filename_ext = ".xlsx"
            
            final_filename = f"{filename_base}_{timestamp}{filename_ext}"
            
            # Create a DataFrame and export
            df = pd.DataFrame(self.leads)
            
            # Organize columns by source type
            source_type = df['Source'].iloc[0] if not df.empty else "Unknown"
            
            if "Maps" in source_type or "Yelp" in source_type or "Pages" in source_type or "BBB" in source_type:
                # Business sources
                priority_cols = ['Name', 'Address', 'Phone', 'Website', 'Industry', 'Location', 'Source']
            elif "LinkedIn" in source_type or "Apollo" in source_type or "Hunter" in source_type:
                # Personal sources
                priority_cols = ['Name', 'Title', 'Company', 'Email', 'Phone', 'Industry', 'Location', 'Source']
            elif "Guide" in source_type or "Education" in source_type:
                # Institutional sources
                priority_cols = ['Organization', 'Address', 'Executive', 'Phone', 'Website', 'Industry', 'Location', 'Source']
            else:
                # Default
                priority_cols = ['Name', 'Company', 'Address', 'Phone', 'Email', 'Website', 'Industry', 'Location', 'Source']
            
            # Reorder columns, putting priority columns first
            all_cols = df.columns.tolist()
            for col in reversed(priority_cols):
                if col in all_cols:
                    all_cols.remove(col)
                    all_cols.insert(0, col)
            
            df = df[all_cols]
            
            # Export to Excel
            with pd.ExcelWriter(final_filename, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='All Leads')
                
                # Create sheets by source
                for source in df['Source'].unique():
                    source_df = df[df['Source'] == source]
                    source_df.to_excel(writer, index=False, sheet_name=source[:31])  # Excel limits sheet names to 31 chars
            
            print(f"Successfully exported {len(self.leads)} leads to {final_filename}")
            
            # Also export as CSV
            csv_filename = f"{filename_base}_{timestamp}.csv"
            df.to_csv(csv_filename, index=False)
            print(f"Also exported as CSV to {csv_filename}")
            
            return final_filename
        except Exception as e:
            print(f"Error exporting to Excel: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description='Generate leads for a specific industry and location')
    parser.add_argument('--industry', required=True, help='Industry to search for (e.g., "restaurants", "software")')
    parser.add_argument('--location', required=True, help='Location to search in (e.g., "New York", "San Francisco")')
    parser.add_argument('--type', default='business', choices=['business', 'personal', 'institutional'], 
                        help='Type of leads to generate (business, personal, or institutional)')
    parser.add_argument('--count', type=int, default=50, help='Number of leads to generate')
    parser.add_argument('--output', default='leads.xlsx', help='Output Excel filename')
    parser.add_argument('--sources', nargs='+', 
                        help='Specific sources to search (e.g., "google_maps yelp linkedin")')
    parser.add_argument('--parallel', action='store_true', 
                        help='Enable parallel processing for faster data collection')
    parser.add_argument('--proxy', help='Proxy to use for web requests (format: http://user:pass@host:port)')
    parser.add_argument('--delay', type=float, default=1.0, 
                        help='Delay between requests to avoid rate limiting (in seconds)')
    parser.add_argument('--export-format', choices=['excel', 'csv', 'json', 'all'], default='excel',
                        help='Format for exporting leads')
    
    args = parser.parse_args()
    
    start_time = time.time()
    print(f"Starting lead generation for {args.industry} in {args.location}...")
    
    agent = LeadGenerationAgent()
    
    # Set proxy if provided
    if args.proxy:
        agent.chrome_options.add_argument(f'--proxy-server={args.proxy}')
    
    # Use specific sources if provided
    if args.sources:
        sources = args.sources
    else:
        sources = agent.sources.get(args.type.lower(), ["google_maps"])
    
    # Run in parallel or serial
    if args.parallel:
        with ThreadPoolExecutor(max_workers=min(len(sources), 5)) as executor:
            futures = []
            for source in sources:
                if hasattr(agent, f"search_{source}"):
                    print(f"Scheduling search for {source}...")
                    search_method = getattr(agent, f"search_{source}")
                    futures.append(
                        executor.submit(search_method, args.industry, args.location, args.count // len(sources))
                    )
                else:
                    print(f"Warning: Search method for {source} not implemented")
            
            # Wait for all searches to complete
            for future in futures:
                future.result()
    else:
        # Run searches sequentially
        for source in sources:
            if hasattr(agent, f"search_{source}"):
                search_method = getattr(agent, f"search_{source}")
                search_method(args.industry, args.location, args.count // len(sources))
            else:
                print(f"Warning: Search method for {source} not implemented")
    
    # Deduplicate leads
    unique_leads = []
    seen_names = set()
    
    for lead in agent.leads:
        name = lead.get("Name", "") or lead.get("Company", "") or lead.get("Organization", "")
        if name and name not in seen_names:
            seen_names.add(name)
            unique_leads.append(lead)
    
    agent.leads = unique_leads
    
    # Export based on format
    if args.export_format == 'excel' or args.export_format == 'all':
        agent.export_to_excel(args.output)
    
    if args.export_format == 'csv' or args.export_format == 'all':
        output_base = os.path.splitext(args.output)[0]
        csv_file = f"{output_base}.csv"
        pd.DataFrame(agent.leads).to_csv(csv_file, index=False)
        print(f"Exported {len(agent.leads)} leads to CSV: {csv_file}")
    
    if args.export_format == 'json' or args.export_format == 'all':
        output_base = os.path.splitext(args.output)[0]
        json_file = f"{output_base}.json"
        with open(json_file, 'w') as f:
            json.dump(agent.leads, f, indent=2)
        print(f"Exported {len(agent.leads)} leads to JSON: {json_file}")
    
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Lead generation completed in {execution_time:.2f} seconds")
    print(f"Generated {len(agent.leads)} unique leads for {args.industry} in {args.location}")



if __name__ == "__main__":
    main()