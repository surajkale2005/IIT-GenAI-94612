from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time


URL = "https://www.sunbeaminfo.in/internship"


options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get(URL)
wait = WebDriverWait(driver, 10)

print(f"Page Title: {driver.title}\n")


for panel in ["#collapseOne", "#collapseTwo", "#collapseSix"]:
    try:
        elem = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"a[href='{panel}']")))
        elem.click()
        time.sleep(1)  # wait for JS to render content
    except:
        print(f"Panel {panel} not found!")

print("\n Internship \n")
try:
    overview = driver.find_element(By.CSS_SELECTOR, "#collapseOne .panel-body").text
    print(overview)
except:
    print("Overview not found!")


print("\n Available Internship Technologies \n")
try:
    tech_list = driver.find_elements(By.CSS_SELECTOR, "#collapseTwo li")
    for tech in tech_list:
        text = tech.text.strip()
        if text:
            print("-", text)
except:
    print("Technologies not found!")


print("\n Internship Batches \n")
try:
    table = driver.find_element(By.CSS_SELECTOR, "#collapseSix table")
    rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # skip header
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) >= 7:
            print(f"{cols[0].text} | {cols[1].text} | {cols[2].text} | {cols[3].text} | {cols[4].text} | {cols[5].text} | {cols[6].text}")
except:
    print("Batches table not found!")

driver.quit()
