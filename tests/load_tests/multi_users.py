from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

CHROME_EXECUTABLE_PATH = "/usr/bin/chromedriver"
DST_URL = "https://dst-staging.climatedata.ca/building-dst/decision-support-tool"

def is_homepage(page_source):
    return "WELCOME TO CLIMATEDATA.CA’s INTERACTIVE CLIMATE DATA DECISION SUPPORT TOOL" in page_source

def simultaneous_connections(connections_number=50):
    print(f"Testing {connections_number} simultaneous connections.")
    options = Options()
    options.headless = True
    drivers = []

    for i in range(connections_number):
        if i % 10 == 0:
            print(f"Opening connection number {i+1}...")

        driver = webdriver.Chrome(executable_path=CHROME_EXECUTABLE_PATH, options=options)
        driver.get(DST_URL)

        # Waits for the page to load
        WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//button[text()='Next']")))

        # Will not be homepage if the connection is shared
        if not is_homepage(driver.page_source):
            return False

        # Loads the 2nd DST page
        driver.find_element(By.XPATH, "//button[text()='Next']").click()
        WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//button[text()='Previous']")))

        drivers.append(driver)

    # Close connections
    for driver in drivers:
        driver.quit()

    return True

def test_simultaneous_connections():
    assert(simultaneous_connections())
