from selenium import webdriver
from selenium.webdriver.support.ui import Select
import os
import time

""" Function Definitions:
"""

# Creates a new web driver (with a specified download destination/directory for each module code).
# There is also some extra setup to make sure that the PDF files are downloaded properly
# instead of opening the Chrome PDF viewer.
def create_web_driver_capabilities(download_directory):
    chrome_profile = webdriver.ChromeOptions()
    chrome_options = {"download.default_directory": download_directory,
                      "download.prompt_for_download": False,
                      "download.directory_upgrade": True,
                      "plugins.plugins_disabled": ["Chrome PDF Viewer"],
                      "plugins.always_open_pdf_externally": True
                      }
    chrome_profile.add_experimental_option("prefs", chrome_options)
    capabilities = chrome_profile.to_capabilities()
    return capabilities


# Logs into UCC with the given login details, if necessary.
def ucc_login(driver, student_number, password):
    if r"Login to UCC Library" in driver.page_source:
        username = student_number + "@umail.ucc.ie"
        driver.find_element_by_id("username").send_keys(username)
        driver.find_element_by_id("password").send_keys(password)
        driver.find_element_by_name("_eventId_proceed").click()


# Accesses the UCC Book of Modules to extract list of all module codes.
def get_valid_module_extensions(student_number, password):
    book_of_modules_link = r"https://www.ucc.ie/admin/registrar/modules/"
    module_extensions = []

    # Open the UCC Book of Modules URL.
    modules_driver = webdriver.Chrome(chrome_driver_directory)
    modules_driver.get(book_of_modules_link)
    ucc_login(modules_driver, student_number, password)

    # Select the dropdown menu containing list of module codes
    modules_select = Select(modules_driver.find_element_by_id("users"))

    # Populate the module_codes array with the available list of module codes
    for i in range(1, len(modules_select.options)):
        raw_string = modules_select.options[i].text
        module_extension = raw_string[0:2]
        module_extensions.append(module_extension)
    return module_extensions


# Counts the number of rows/papers found.
def get_table_row_count(driver, table_xpath):
    return len(main_driver.find_elements_by_xpath(table_xpath + "/tr"))


# Checks if files are still being downloaded.
def downloads_done(directory, number_of_papers):
    if len(os.listdir(directory)) != number_of_papers:
        time.sleep(1)
        downloads_done(directory, number_of_papers)


# Prints log for user to see how many papers were downloaded for each module code.
def print_log(number_of_papers, module):
    print(f"-I- Downloaded {number_of_papers} papers for {module}")


""" User Specifications:
"""

module_codes = ["AM4062", "MA4058", "MF4052", "ST3300", "ST4060", "MF4090", "ST4068"]
hard_limit = 5  # Maximum number of papers to be downloaded, starting from the most recent

# Chrome webdriver directory
chrome_driver_directory = r"C:\Users\nvolf\Anaconda3\chromedriver76.exe"


""" Main Implementation:
"""

# Added this function just for fun and practice. This isn't necessary for downloading the papers.
# valid_module_extensions = get_valid_module_extensions(student_number, password)


for module in module_codes:
    # Open the main/parent URL for accessing papers by subject and logging in if necessary.
    module_directory = download_directory + f"\{module}"
    capabilities = create_web_driver_capabilities(module_directory)
    main_driver = webdriver.Chrome(executable_path=chrome_driver_directory, desired_capabilities=capabilities)
    exam_papers_link = r"https://www-ucc-ie.ucc.idm.oclc.org/exampapers/"
    main_driver.get(exam_papers_link)
    ucc_login(main_driver, student_number, password)

    # Search for the given module code.
    main_driver.find_element_by_xpath("//input[@placeholder='Module or Subject']").send_keys(module)
    main_driver.find_element_by_xpath("//input[@value='Search for Exam papers']").click()

    # Find table and count the number of papers available for download.
    table_xpath = r"//*[@id='mainPadder']/table/tbody/tr/td/table/tbody"
    number_of_rows = get_table_row_count(main_driver, table_xpath)
    number_of_papers = number_of_rows if hard_limit == 0 else min(number_of_rows, hard_limit)

    # If there are no search results for the given module code:
    if number_of_papers == 0:
        os.mkdir(module_directory + " (empty)")
    else:
        # Begin iterating through the table of papers and downloading each paper.
        for i in range(1, number_of_papers+1):
            main_driver.find_element_by_xpath(f"//*[@id='mainPadder']/table/tbody/tr/td/table/tbody/tr[{i}]/td[4]/a").click()

        # Wait until downloads have finished before moving on.
        downloads_done(module_directory, number_of_papers)

    print_log(number_of_papers, module)
    main_driver.close()
