
import os
import pickle
import random
import time
import tkinter as tkr

import pyperclip
from requests.exceptions import ConnectionError
from requests.exceptions import SSLError, ReadTimeout
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from urllib3.exceptions import MaxRetryError, NewConnectionError
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.proxy import Proxy
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

###########################################################################################################################################################

chrome_options = Options()
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-translate")
chrome_options.add_argument("--disable-client-side-phishing-detection")
chrome_options.add_argument("--disable-default-apps")
chrome_options.add_argument("--disable-hang-monitor")
chrome_options.add_argument("--disable-prompt-on-repost")
chrome_options.add_argument("--disable-renderer-backgrounding")
chrome_options.add_argument('--disable-logging')

###########################################################################################################################################################

class InstagramAutomationBot:

    instagram_url = "https://www.instagram.com/accounts/login/?"
    instagram_home_url = "https://www.instagram.com/"
    
    ###########################################################################################################################################################
    
    def __init__(self, username: str, password: str, proxy: str):
        self.username = username
        self.password = password
        
        self.proxy = Proxy({
            'proxyType': 'MANUAL',
            'httpProxy': proxy,
            'ftpProxy': proxy,
            'sslProxy': proxy,
            'noProxy': ''
        })
        
        print("Creating Chrome Driver...")
        self.driver = self.create_selenium_webdriver()

    ###########################################################################################################################################################

    def close_browser(self):
        self.driver.close()
        self.driver.quit()
        self.driver = None
        return True

    ###########################################################################################################################################################
    
    def create_selenium_webdriver(self):
        # creating Chrome web driver object
        capabilities = DesiredCapabilities.CHROME
        self.proxy.add_to_capabilities(capabilities)
        
        driver = webdriver.Chrome(
            ChromeDriverManager().install(),
            options=chrome_options,
            desired_capabilities=capabilities
        )
        #driver = webdriver.Chrome(desired_capabilities=capabilities)
        
        driver.maximize_window()
        print("Chrome Driver created.")
        
        # load the saved cookies if any
        cookies_file = os.path.join(os.getcwd(), 'cookies', self.username + "_cookies.pkl")
        if os.path.exists(cookies_file):
            driver.get("https://www.instagram.com/")
            try:
                # wait the ready state to be complete
                WebDriverWait(driver=driver, timeout=random.randint(30, 45)).until(
                    lambda x: x.execute_script("return document.readyState === 'complete'")
                )
            except TimeoutException:
                pass

            time.sleep(random.randint(1, 2))
            # delete the current cookies
            driver.delete_all_cookies()
            time.sleep(random.randint(1, 2))

            cookies = pickle.load(open(cookies_file, "rb"))
            for cookie in cookies:
                driver.add_cookie(cookie)

            time.sleep(random.randint(2, 5))

            print("Cookies loaded.")
            driver.get("https://www.instagram.com/")

            try:
                # wait the ready state to be complete
                WebDriverWait(driver=driver, timeout=random.randint(30, 45)).until(
                    lambda x: x.execute_script("return document.readyState === 'complete'")
                )
            except TimeoutException:
                pass

            time.sleep(random.randint(2, 5))

        return driver
    
    ###########################################################################################################################################################

    def login(self):
        # check if the user is already logged in using cookies or not
        # check if login is successful
        try:
            # check for the home button to be visible to confirm login
            WebDriverWait(driver=self.driver, timeout=random.randint(5, 10)).until(
                EC.visibility_of_element_located((By.XPATH, "//*[@aria-label='Home']"))
            )
            print("Instagram login successful using cookies.")
            return True, "Instagram login successful using cookies."
        except TimeoutException:
            print("Instagram login failed using cookies.")
            print("Logging in using username and password...")

        print("Opening Instagram login page...")
        # open instagram
        try:
            self.driver.get(self.instagram_url)
        except (ConnectionError, MaxRetryError, NewConnectionError, SSLError, ReadTimeout) as e:
            print("Connection Error: ", e)
            return False, "Connection Error"

        try:
            # wait the ready state to be complete
            WebDriverWait(driver=self.driver, timeout=random.randint(30, 45)).until(
                lambda x: x.execute_script("return document.readyState === 'complete'")
            )
        except TimeoutException:
            print("TimeoutException: Page load timeout")
            return False, "TimeoutException: Page load timeout"

        # login to instagram
        try:
            WebDriverWait(driver=self.driver, timeout=random.randint(30, 45)).until(
                EC.visibility_of_element_located((By.XPATH, "//input[@name='username']"))
            )
        except TimeoutException:
            print("TimeoutException: Login failed.")
            tkr.messagebox.showerror("Error", "Login failed. Please try again.")
            return False, "TimeoutException: Login failed."

        # send username with delay
        for char in self.username:
            self.driver.find_element(By.XPATH, "//input[@name='username']").send_keys(char)
            time.sleep(random.uniform(0.4, 0.8))

        time.sleep(random.randint(1, 2))

        # send password with delay
        for char in self.password:
            self.driver.find_element(By.XPATH, "//input[@name='password']").send_keys(char)
            time.sleep(random.uniform(0.4, 0.8))

        time.sleep(random.randint(1, 2))

        # click login button
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()

        time.sleep(random.randint(4, 5))

        try:
            WebDriverWait(driver=self.driver, timeout=random.randint(4, 6)).until(
                EC.visibility_of_element_located((By.XPATH, "//p[@data-testid='login-error-message']"))
            )

            error_message = self.driver.find_element(By.XPATH, "//p[@data-testid='login-error-message']").text

            if error_message.lower().__contains__("There was a problem logging you into Instagram.".lower()):
                print("There was a problem logging you into Instagram. Please try again soon.")
                tkr.messagebox.showerror("Error",
                                         "There was a problem logging you into Instagram. Please try again soon.")
                return False, "Problem in logging into Instagram. PTA!"
            elif error_message.lower().__contains__("Sorry, your password was incorrect.".lower()):
                print("Sorry, your password was incorrect. Please double-check your password.")
                tkr.messagebox.showerror("Error",
                                         "Sorry, your password was incorrect. Please double-check your password.")
                return False, "Sorry, your password was incorrect."
            elif error_message.lower().__contains__("The username you entered doesn't belong to an account.".lower()):
                print("The username you entered doesn't belong to an account. "
                      "Please check your username and try again.")
                tkr.messagebox.showerror("Error",
                                         "The username you entered doesn't belong to an account. "
                                         "Please check your username and try again.")
                return False, "Sorry, your username was incorrect."
            else:
                print("Login failed.")
                tkr.messagebox.showerror("Error", "Login failed. Please try again.")
                return False, "Login failed. PTA!"
        except TimeoutException:
            pass

        try:
            # wait the ready state to be complete
            WebDriverWait(driver=self.driver, timeout=random.randint(30, 45)).until(
                lambda x: x.execute_script("return document.readyState === 'complete'")
            )
        except TimeoutException:
            print("TimeoutException: Page load timeout")
            return False, "TimeoutException: Page load timeout"

        time.sleep(random.randint(2, 4))

        # checking for the unusual login activity popup
        try:
            self.driver.find_element(By.XPATH, "//h2[contains(text(), 'We Detected An Unusual Login Attempt')]")

            # click on ok button of tkinter message box to continue the process of login to instagram account
            resp = tkr.messagebox.askokcancel("Unusual Login Attempt",
                                              "There is security barrier by Instagram Authorities.\n"
                                              "From here you have to manually verify your login by receiving "
                                              "code on your mobile or email.\n"
                                              "After receiving the code, and approval, you can continue the process.\n"
                                              "Do you want to continue?")
            if resp:
                time.sleep(random.randint(2, 4))
                try:
                    # wait the ready state to be complete
                    WebDriverWait(driver=self.driver, timeout=random.randint(30, 45)).until(
                        lambda x: x.execute_script("return document.readyState === 'complete'")
                    )
                except TimeoutException:
                    print("TimeoutException: Page load timeout")
                    return False, "TimeoutException: Page load timeout"
            else:
                return False, "Unusual Login Attempt! Need User Attention!"
        except NoSuchElementException:
            pass

        # click not now button for the save login info popup.
        print("Checking for the save login info popup.")
        try:
            WebDriverWait(driver=self.driver, timeout=random.randint(2, 5)).until(
                EC.visibility_of_element_located((By.XPATH, "//button[text()='Not Now']"))
            )
            self.driver.find_element(By.XPATH, "//button[text()='Not Now']").click()
            time.sleep(random.randint(1, 2))
            # wait the ready state to be complete
            WebDriverWait(driver=self.driver, timeout=random.randint(30, 45)).until(
                lambda x: x.execute_script("return document.readyState === 'complete'")
            )
        except TimeoutException:
            print("TimeoutException: Save login info popup not found.")

        # click not now button for the turn on notifications popup.
        print("Checking for the turn on notifications popup.")
        try:
            WebDriverWait(driver=self.driver, timeout=random.randint(2, 4)).until(
                EC.visibility_of_element_located((By.XPATH, "//button[text()='Not Now']"))
            )
            self.driver.find_element(By.XPATH, "//button[text()='Not Now']").click()
            time.sleep(random.randint(1, 2))
            # wait the ready state to be complete
            WebDriverWait(driver=self.driver, timeout=random.randint(30, 45)).until(
                lambda x: x.execute_script("return document.readyState === 'complete'")
            )
        except TimeoutException:
            print("TimeoutException: Turn on notifications popup not found.")

        try:
            self.driver.find_element(By.XPATH, '//span[@aria-label="Dismiss"]').click()
            time.sleep(0.5)
        except NoSuchElementException:
            print("No dismiss button found.")
            pass

        # check if login is successful
        try:
            # check for the home button to be visible to confirm login
            WebDriverWait(driver=self.driver, timeout=random.randint(45, 60)).until(
                EC.visibility_of_element_located((By.XPATH, "//*[text()='Home']"))
            )
            print("Login successful.")
        except TimeoutException:
            print("TimeoutException: Login failed.")
            tkr.messagebox.showerror("Error", "Login failed. Please try again.")
            return False, "Login failed. PTA!"

        print("Login successful.")

        # save session cookies to file for future use of the same session to avoid login again and again
        cookies_name = self.username + "_cookies.pkl"
        if not os.path.exists(os.path.join(os.getcwd(), 'cookies', cookies_name)):
            # with open(cookies_name, 'wb') as filehandler:
            #     pickle.dump(self.driver.get_cookies(), filehandler)
            pickle.dump(self.driver.get_cookies(), open(os.path.join(os.getcwd(), 'cookies', cookies_name), "wb"))
            print("Session cookies saved in 'cookies' folder to file: " + cookies_name)

        # return True if login is successful
        return True, "Login successful."

    ###########################################################################################################################################################

    def follow_user_and_send_dm(self, user, message):
        """
        Follow the user and send the message.
        :param user: user to follow
        :param message: message to send
        :return: True, "Followed the user and sent the message."
        """
        print("Bot is going to follow the user: '{}' to send message: ".format(user))

        # open the user's profile
        self.driver.get("https://www.instagram.com/" + user + "/")
        # wait for the page to load
        try:
            WebDriverWait(driver=self.driver, timeout=random.randint(30, 45)).until(
                lambda x: x.execute_script("return document.readyState === 'complete'")
            )
        except TimeoutException:
            print("TimeoutException: Page not loaded.")
            return False, "TimeoutException: Page not loaded."

        is_private = False
        is_followed = False

        time.sleep(random.randint(3, 5))

        # wait for the follow button to be visible
        try:
            WebDriverWait(driver=self.driver, timeout=random.randint(5, 8)).until(
                EC.visibility_of_element_located((
                    By.XPATH,
                    "//a[contains(@href, '/followers')]/parent::li/parent::ul/parent::section/div[1]"
                    "//button/div/div[text()='Follow']")
                )
            )
        except TimeoutException:
            try:
                try:
                    self.driver.find_element(
                        By.XPATH,
                        "//div[contains(text(), 'follower') or contains(text(), 'Follower')]/span/ancestor::ul"
                        "/parent::section/div[1]//button//div[text()='Follow' or text()='follow' ]"
                        "/ancestor::button"
                    )
                except NoSuchElementException:
                    try:
                        self.driver.find_element(By.XPATH, "//*[text()='Following']") # check if following
                        print("User: " + user + " is already followed. Removing from list")
                        return False, "User: " + user + " is already followed"
                            
                    except:
                        # try if user is requested
                        try:
                            self.driver.find_element(By.XPATH, "//*[text()='Requested']") # check if requested
                            print("User: " + user + " has a request already sent. Removing from list")
                            return False, "User: " + user + " has a request sent."
                        except:
                            print("TimeoutException: Follow button not found.")
                            return False, "TimeoutException-1: Follow button not found."
                        # print("TimeoutException: Follow button not found.")
                        # return False, "TimeoutException-1: Follow button not found."
            except NoSuchElementException:
                print("TimeoutException-2: Follow button not found.")
                return False, "TimeoutException-2: Follow button not found."

        # # check if the user is private
        # try:
        #     #self.driver.find_element(By.XPATH, "//h2[text()='This Account is Private']")
        #     # check if requested button to determine if its private
        #     self.driver.find_element(By.XPATH, "//*[text()='Requested']")
        #     is_private = True
        #     print("user is private")
        # except NoSuchElementException:
        #     pass

        try:
            # get the follow button
            follow_button = self.driver.find_element(
                By.XPATH,
                "//a[contains(@href, '/followers')]/parent::li/parent::ul/parent::section/div[1]"
                "//button/div/div[text()='Follow' or text()='follow']"
            )
            # click on the follow button
            follow_button.click()
            time.sleep(random.randint(8, 15))

            restriction_count = 0
            while True:
                # check restrict activity popup
                try:
                    self.driver.find_element(By.XPATH, "//div[@role='dialog']//h3/following-sibling::div")
                    restriction_count += 1
                except NoSuchElementException:
                    break

                if restriction_count > 3:
                    print("Restrict activity popup found. Bot is not allowed to follow the user due to "
                          "Instagram's restrictions.")
                    print("Instagram is restricting the activities. Please try again after few hours.")
                    print("Skipping current account...")

                    return None, "Instagram is restricting the activities."

                try:
                    self.driver.find_element(By.XPATH, "//div[@role='dialog']//button[text()='OK']").click()
                    time.sleep(random.randint(2, 4))
                except:
                    pass

                print("Bot is going to sleep for 1 to 2 minutes.")
                time.sleep(random.randint(60, 120))
                print("Bot is going to wake up now.")
                self.driver.refresh()
                # wait for the page to load
                try:
                    WebDriverWait(driver=self.driver, timeout=random.randint(30, 45)).until(
                        lambda x: x.execute_script("return document.readyState === 'complete'")
                    )
                except TimeoutException:
                    print("TimeoutException-3: Page not loaded.")
                    continue

                print("Bot is going to follow the user again.")
                time.sleep(random.randint(8, 15))
                # wait for the follow button to be visible
                try:
                    # get the follow button
                    follow_button = self.driver.find_element(
                        By.XPATH,
                        "//a[contains(@href, '/followers')]/parent::li/parent::ul/parent::section/div[1]"
                        "//button/div/div[text()='Follow' or text()='follow']"
                    )
                    # click on the follow button
                    follow_button.click()
                    time.sleep(random.randint(8, 15))
                except:
                    print("TimeoutException-4: Follow button not found.")
                    break

            print("Followed the user: " + user)
            is_followed = True
            time.sleep(random.randint(25, 40))
        except NoSuchElementException:
            try:
                follow_button = self.driver.find_element(
                    By.XPATH,
                    "//div[contains(text(), 'follower') or contains(text(), 'Follower')]/span/ancestor::ul"
                    "/parent::section/div[1]//button//div[text()='Follow' or text()='follow' ]"
                    "/ancestor::button"
                )
                follow_button.click()
                time.sleep(random.randint(8, 15))

                restriction_count = 0
                while True:
                    # check restrict activity popup
                    try:
                        self.driver.find_element(By.XPATH, "//div[@role='dialog']//h3/following-sibling::div")
                        restriction_count += 1
                    except NoSuchElementException:
                        break

                    if restriction_count > 3:
                        print("Restrict activity popup found. Bot is not allowed to follow the user due to "
                              "Instagram's restrictions.")
                        print("Instagram is restricting the activities. Please try again after few hours.")
                        print("Exiting the program...")

                        return None, "Instagram is restricting the activities."
                    try:
                        self.driver.find_element(By.XPATH, "//div[@role='dialog']//button[text()='OK']").click()
                        time.sleep(random.randint(2, 4))
                    except Exception:
                        pass

                    print("Bot is going to sleep for 1 to 2 minutes.")
                    time.sleep(random.randint(60, 120))
                    print("Bot is going to wake up now.")
                    self.driver.refresh()
                    # wait for the page to load
                    try:
                        WebDriverWait(driver=self.driver, timeout=random.randint(30, 45)).until(
                            lambda x: x.execute_script("return document.readyState === 'complete'")
                        )
                    except TimeoutException:
                        print("TimeoutException-5: Page not loaded.")
                        continue

                    print("Bot is going to follow the user again.")
                    time.sleep(random.randint(8, 15))
                    # wait for the follow button to be visible
                    try:
                        # get the follow button
                        follow_button = self.driver.find_element(
                            By.XPATH,
                            "//a[contains(@href, '/followers')]/parent::li/parent::ul/parent::section/div[1]"
                            "//button/div/div[text()='Follow' or text()='follow']"
                        )
                        # click on the follow button
                        follow_button.click()
                        time.sleep(random.randint(8, 15))
                    except:
                        print("TimeoutException-6: Follow button not found.")
                        break

                print("Followed the user: " + user)
                is_followed = True
            except NoSuchElementException:
                print("NoSuchElementException-7: Follow button not found.")
                return False, "NoSuchElementException-7: Follow button not found."
        
        ##########################################################################################
        # check if the user is private
        try:
            #self.driver.find_element(By.XPATH, "//h2[text()='This Account is Private']")
            # check if requested button to determine if its private
            self.driver.find_element(By.XPATH, "//*[text()='Requested']")
            is_private = True
            print("user is private")
        except NoSuchElementException:
            pass
        ##########################################################################################

        if is_followed:
            if is_private:
                print("Not able to send message to the user: " + user + " because the user is private.")
                with open(f"{self.username}.txt", 'a') as f:
                    f.write(user)
                    f.write("\n")
                # remove from scraped list
                return False, "User is private. Not able to send message."
            else:
                # send message to the user if the user is not private
                # click on Message button
                try:
                    WebDriverWait(driver=self.driver, timeout=random.randint(30, 45)).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[text()='Message']"))
                    )

                    message_button = self.driver.find_element(By.XPATH, "//div[text()='Message']")
                    message_button.click()
                    time.sleep(random.randint(5, 8))

                    try:
                        # wait the ready state to be complete
                        WebDriverWait(driver=self.driver, timeout=random.randint(30, 45)).until(
                            lambda x: x.execute_script("return document.readyState === 'complete'")
                        )
                    except TimeoutException:
                        print("Page load timeout for user profile page.")
                        return False, "Page load timeout for user profile page."
                except TimeoutException:
                    print("TimeoutException-11: Page load timeout")
                    return False, "TimeoutException-11: Page load timeout"

                time.sleep(random.randint(2, 4))

                # send the message
                try:
                    WebDriverWait(driver=self.driver, timeout=random.randint(30, 45)).until(
                        EC.element_to_be_clickable((By.XPATH, "//textarea[@placeholder='Message...']"))
                    )

                    message_textarea = self.driver.find_element(By.XPATH, "//textarea[@placeholder='Message...']")
                    ###################################################################################################
                    # copy the comment text to clipboard
                    pyperclip.copy(message)
                    time.sleep(0.5)

                    # type the . to trigger the comment button
                    ActionChains(self.driver).move_to_element(message_textarea).perform()
                    time.sleep(0.5)
                    ActionChains(self.driver).click(message_textarea).perform()
                    time.sleep(0.5)
                    message_textarea.send_keys(".")
                    time.sleep(0.3)

                    # paste the comment text from clipboard
                    message_textarea.send_keys(Keys.CONTROL, 'v')
                    time.sleep(random.randint(4, 7))
                    ###################################################################################################
                except TimeoutException:
                    print("TimeoutException: Page load timeout")
                    return False, "TimeoutException-22: Page load timeout"

                time.sleep(random.randint(2, 4))

                # click on Send button
                try:
                    WebDriverWait(driver=self.driver, timeout=random.randint(30, 45)).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[text()='Send']"))
                    )

                    send_button = self.driver.find_element(By.XPATH, "//button[text()='Send']")
                    send_button.click()
                    time.sleep(random.randint(5, 8))
                except TimeoutException:
                    print("TimeoutException: Page load timeout")
                    return False, "TimeoutException-33: Page load timeout"

                time.sleep(random.randint(2, 4))

                #print("DM sent to the user: " + user)
                time.sleep(random.randint(10, 20))

                return True, "DM sent to the user: " + user
            
    ###########################################################################################################################################################

    def send_dm_message_who_followed_me(self, message, break_time):
        try:
            self.driver.get(self.instagram_home_url)
        except TimeoutException:
            print("Page load timeout for home page.")
            return False, "Page load timeout for home page."

        time.sleep(random.randint(3, 5))

        try:
            # wait the ready state to be complete
            WebDriverWait(driver=self.driver, timeout=random.randint(30, 45)).until(
                lambda x: x.execute_script("return document.readyState === 'complete'")
            )
        except TimeoutException:
            print("Page load timeout for home page.")
            return False, "Page load timeout for home page."

        # click on Notification button
        try:
            WebDriverWait(driver=self.driver, timeout=random.randint(30, 45)).until(
                EC.element_to_be_clickable((By.XPATH, "//*[@aria-label='Notifications']/ancestor::a"))
            )

            activity_button = self.driver.find_element(By.XPATH, "//*[@aria-label='Notifications']/ancestor::a")
            activity_button.click()
            time.sleep(random.randint(5, 8))
        except TimeoutException:
            print("TimeoutException: Page load timeout")
            return False, "TimeoutException: Page load timeout!"

        time.sleep(random.randint(2, 4))

        # select all the follow buttons on activity feed
        follow_back_containers = self.driver.find_elements(
            By.XPATH,
            "//div[text()='Following']/ancestor::button/parent::div/parent::div/div[2]/span"
            "/div[contains(text(), 'started following you.')]/parent::span"
        )
        if len(follow_back_containers) == 0:
            print("No new follow back found.")
            return True, "No new follow back found."

        users_to_send_dm = []
        for container in follow_back_containers:
            follow_back_time = container.find_element(By.XPATH, "./following-sibling::time").text

            if follow_back_time.__contains__('m'):
                follow_back_time = follow_back_time.replace('m', '')
                follow_back_time = int(follow_back_time)

                # check if the follow back time is less than the break time
                if follow_back_time <= break_time + 5:
                    users_to_send_dm.append(container.find_element(By.XPATH, "./a").get_attribute("href"))
            elif follow_back_time.__contains__('s'):
                users_to_send_dm.append(container.find_element(By.XPATH, "./a").get_attribute("href"))

        print("Users to send DM: " + str(users_to_send_dm))

        if len(users_to_send_dm) == 0:
            print("No new follow back found.")
            return True, "No new follow back found."

        # send DM to the users
        for user in users_to_send_dm:
            try:
                self.driver.get(user)
            except TimeoutException:
                print("Page load timeout for user profile page.")
                continue

            time.sleep(random.randint(3, 5))

            try:
                # wait the ready state to be complete
                WebDriverWait(driver=self.driver, timeout=random.randint(30, 45)).until(
                    lambda x: x.execute_script("return document.readyState === 'complete'")
                )
            except TimeoutException:
                print("Page load timeout for user profile page.")
                continue

            # click on Message button
            try:
                WebDriverWait(driver=self.driver, timeout=random.randint(30, 45)).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[text()='Message']/ancestor::button"))
                )

                message_button = self.driver.find_element(By.XPATH, "//div[text()='Message']/ancestor::button")
                message_button.click()
                time.sleep(random.randint(5, 8))

                try:
                    # wait the ready state to be complete
                    WebDriverWait(driver=self.driver, timeout=random.randint(30, 45)).until(
                        lambda x: x.execute_script("return document.readyState === 'complete'")
                    )
                except TimeoutException:
                    print("Page load timeout for user profile page.")
                    continue
            except TimeoutException:
                print("TimeoutException: Page load timeout")
                continue

            time.sleep(random.randint(2, 4))

            # send the message
            try:
                WebDriverWait(driver=self.driver, timeout=random.randint(30, 45)).until(
                    EC.element_to_be_clickable((By.XPATH, "//textarea[@placeholder='Message...']"))
                )

                message_textarea = self.driver.find_element(By.XPATH, "//textarea[@placeholder='Message...']")
                #######################################################################################################
                # copy the comment text to clipboard
                pyperclip.copy(message)
                time.sleep(0.5)

                # type the . to trigger the comment button
                ActionChains(self.driver).move_to_element(message_textarea).perform()
                time.sleep(0.5)
                ActionChains(self.driver).click(message_textarea).perform()
                time.sleep(0.5)
                message_textarea.send_keys(".")
                time.sleep(0.3)

                # paste the comment text from clipboard
                message_textarea.send_keys(Keys.CONTROL, 'v')
                time.sleep(random.randint(4, 7))
                #######################################################################################################
            except TimeoutException:
                print("TimeoutException: Page load timeout")
                continue

            time.sleep(random.randint(2, 4))

            # click on Send button
            try:
                WebDriverWait(driver=self.driver, timeout=random.randint(30, 45)).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[text()='Send']"))
                )

                send_button = self.driver.find_element(By.XPATH, "//button[text()='Send']")
                send_button.click()
                time.sleep(random.randint(5, 8))
            except TimeoutException:
                print("TimeoutException: Page load timeout")
                continue

            time.sleep(random.randint(2, 4))

            print("DM sent to the user: " + user)
            time.sleep(random.randint(10, 20))

        return True, "DM sent to the users."

###########################################################################################################################################################