import logging
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class BookingBotMyFitness:
    def __init__(self, email, password, headless=False, target_class="Hot Pilates Sculpt"):
        self.email = email
        self.password = password
        self.target_class = target_class
        self.headless = headless
        self.driver = None
        self.base_url = "https://www.myfitness.lv"
        self.club = "galerija-centrs"
        self.club_url = f"{self.base_url}/club/{self.club}/nodarbibu-saraksts/"
        self.logged_in = False
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("booking_bot.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("MyFitnessBot")
    
    def setup_browser(self):
        """Initialize and configure the browser. Navigate to base URL."""
        options = webdriver.FirefoxOptions()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')

        self.driver = webdriver.Firefox(options=options)
        self.driver.maximize_window()
        self.logger.info("Browser setup complete")

        self.driver.get(self.base_url) # Navigate to the website

        try: # Accept cookies
            cookie_button = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[@id='CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll']")))
            cookie_button.click()
            self.logger.info("Cookie popup accepted")
        except TimeoutException:
            self.logger.info("No cookie popup detected")

    def close_add(self):
        try: # Check if any other dialog popup is present and close it
            close_button = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[@class='c-dialog__close']")))
            close_button.click()
            self.logger.info("Dialog popup closed")
        except TimeoutException:
            self.logger.info("No dialog popup detected")

    def login(self):
        """Log into the MyFitness website."""
        if self.logged_in:
            self.logger.info("Already logged in")
            return
            
        self.logger.info("Logging in to MyFitness...")
        
        try:
            # Wait for the login link and click it
            login_link = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.XPATH, "//a[@class='link link-login']")))
            login_link.click()

            # Enter credentials
            username_field = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.XPATH, "//input[@id='login-field-username']")))
            password_field = self.driver.find_element(By.XPATH, "//input[@id='login-field-password']")
            
            username_field.send_keys(self.email)
            password_field.send_keys(self.password)
            
            # Click the login button
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']/span[contains(text(), 'Ieiet')]")
            login_button.click()
            
            # Wait for login to complete by checking the URL change
            WebDriverWait(self.driver, 60).until(EC.url_to_be("https://www.myfitness.lv/biedra-zona/sakums/"))
            
            self.logged_in = True
            self.logger.info("Login successful")
            
        except Exception as e:
            self.logger.error(f"Login failed: {str(e)}")
            raise
    
    def navigate_to_schedule(self):
        """Navigate to the class schedule page."""
        self.logger.info("Navigating to schedule page...")
        self.driver.get(self.club_url)
        
        # Wait for the timetable to load
        WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH, "//table[@class='timetable-table']")))

        self.logger.info("Schedule page loaded")
    
    def get_current_week(self):
        """Get the current week identifier from the page."""
        week_element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[@data-week and not (contains(@class, 'hidden'))]")))
        return week_element.get_attribute("data-week")
    
    def go_to_next_week(self):
        """Navigate to the next week's schedule."""
        self.logger.info("Navigating to next week's schedule...")
        try:
            next_week_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='week-nav-item next-week']")))
            next_week_button.click()
            
            # Wait for <div class="loader notice success" style="display: none;">Lūdzu uzgaidi</div> to change back to display: none
            WebDriverWait(self.driver, 15).until(EC.invisibility_of_element_located((By.XPATH, "//div[@class='loader notice success']")))

            self.logger.info("Next week's schedule loaded")
            
        except Exception as e:
            self.logger.error(f"Failed to navigate to next week: {str(e)}")
            raise
    
    def find_target_classes(self):
        """Find all Hot Pilates Sculpt classes available for booking."""
        self.logger.info(f"Looking for {self.target_class} classes...")
        
        # Wait for all class elements to load
        WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'timetable-table-wrap')]")))
        
        # Find all classes that are not hidden.
        classes = self.driver.find_elements(By.XPATH, "//table[@class='timetable-table']"
                                                      "//div[contains(@class, 'training-class-item bron-open')"
                                                      "and not(contains(@class, 'hidden'))]")
        
        self.logger.info(f"Found {len(classes)} classes in total")
        
        target_classes = []

        # Check each class to see if it's our target class
        for class_element in classes:
            try:
                # Get the booking link inside this class element
                booking_link_element = class_element.find_element(By.XPATH, ".//a[contains(@class, 'link-bron-training')]")
                booking_link = booking_link_element.get_attribute("href")
                
                # Get the title information
                title_element = class_element.find_element(By.XPATH, ".//span[@class='title']")
                title_text = title_element.text.strip()
                
                if self.target_class in title_text:
                    target_classes.append({
                        "element": booking_link_element,
                        "booking_link": booking_link,
                        "title": title_text
                    })
                    
            except Exception as e:
                self.logger.warning(f"Error checking class: {str(e)}")
                continue
        
        self.logger.info(f"Found {len(target_classes)} {self.target_class} classes")
        return target_classes
    
    def book_classes(self, classes):
        """Book all found classes."""
        if not classes:
            self.logger.warning("No classes found to book")
            return
        
        successful_bookings = 0
        
        for class_info in classes:
            try:
                print(f"Attempting to book {class_info['title']}")

                # Extract class_id from the provided booking link
                match = re.search(r'class_id=(\d+)', class_info['booking_link'])
                if not match:
                    print(f"Error: Could not extract class_id from {class_info['booking_link']}")
                    continue

                class_id = match.group(1)

                # Construct the correct registration URL
                booking_link = f"https://www.myfitness.lv/club/galerija-centrs/nodarbibu-saraksts/?class_id={class_id}&class_action=register"

                # Navigate directly to the correct registration link
                self.driver.get(booking_link)

                # Wait for booking confirmation modal to appear
                WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH, "//div[@class='m-modal comment-modal' and @style='display: block;']")))

                print(f"Successfully booked {class_info['title']}")
                successful_bookings += 1

            except TimeoutException:
                print(f"Booking failed for {class_info['title']}: Confirmation modal not found")
            except Exception as e:
                print(f"Error booking class {class_info['title']}: {str(e)}")

        print(f"Booking complete. Successfully booked {successful_bookings} out of {len(classes)} classes")
    
    def run(self):
        """Run the entire booking process."""
        try:
            self.logger.info("Starting MyFitness booking bot")
            self.setup_browser()
            self.close_add()

            self.login()

            self.navigate_to_schedule()
            self.close_add()
            self.go_to_next_week()
            
            classes = self.find_target_classes()
            self.book_classes(classes)
            
            self.logger.info("Booking process completed")
            
        except Exception as e:
            self.logger.error(f"Bot encountered an error: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()
                self.logger.info("Browser closed")
