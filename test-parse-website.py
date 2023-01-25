from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
import backoff

options = webdriver.FirefoxOptions()
options.set_preference("browser.download.folderList", 2)
options.set_preference("browser.download.dir", "/tmp/du-insights")
options.set_preference("browser.download.useDownloadDir", True)
options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
options.set_preference("pdfjs.disabled", True)

# NOTE: deploy to cloud run
driver = webdriver.Firefox(options=options, service=Service(GeckoDriverManager().install()))

# Maximum ERC Case number (Brute Force Method):
# 1. Starting from 1, visit every page and iterate until table returns no result.
# 2. When we get table no result, get current iteration - 1 as max_erc_case_number
# 3. Use it as variable/reference for the scraping logic.

max_erc_case_number = 5
for i in range(1, max_erc_case_number, 1):
    # TODO: find maximum ERC case for year given (2022, 2023) programmatically.
    driver.get(f'https://www.erc.gov.ph/Search/2022-00{i}') # 1, 2, 3
    driver.implicitly_wait(30)

    content = driver.page_source
    soup = BeautifulSoup(content, 'html.parser')

    # TODO: implement backoff/retrying strategy feature.
    # @backoff.on_exception(backoff.expo, (OperationalError, Exception, TransactionRollbackError), max_time=60,
    #                       max_tries=8)
    # OR SEARCH: Retrying Strategy python selenium
    if '502' in soup.title:
        print('Trying to refresh website..')
        driver.refresh()
        driver.implicitly_wait(30)

        content = driver.page_source
        soup = BeautifulSoup(content, 'html.parser')


    for body in soup.find_all('table', {'class': 'table table-hover table-bordered table-condensed table-striped'}):
        for row in body.find_all('td'):
            if row.find('a') is not None:
                # NOTE: Only download in where redirect leads to a PDF file
                if 'Files' in row.find('a').get('href'):
                    # TODO: Get latest file per current month (or get the latest file)
                    driver.find_element(By.XPATH, f"""//a[@href='{row.find('a').get('href')}']""").click()

