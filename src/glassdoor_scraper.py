"""
Glassdoor Scraper Function
"""

from time import sleep
from datetime import date, datetime
import re
import json
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


RE_ESTIMATE_TYPE = r'(Employer|Glassdoor)'
RE_SALARY_RANGE = r'\$[\d]{0,4}[\.]?[\d]{1,4}?[K|M]?[\s]?[-]?[\s]?(\$[\d]{0,4}[\.]?[\d]{1,4}?[K|M]?)?'
RE_SINGLE_SALARY = r'\$[\d]*[.]?[KM]?[\d]*'
RE_AVG_BASE_SAL = r'[\d]*([,.][\d]*)+'

NO_COMP_VALUES = ['Unknown', 'Unknown / Non-Applicable']


class DriverTypeNotSupported(Exception):
    """
    Handling exception when the selenium web driver type is currently not supported
    Args:
        Exception (_type_): _description_
    """


class DriverUnsuccessful(Exception):
    """
    Handling exception when the selenium web driver type is unsuccessful
        Exception (_type_): _description_
    """


class GlassdoorScraper:
    """
    Glassdoor scraper class implementation
    """

    def __init__(self) -> None:
        self.driver = None
        self.scraped_dataset = None

    def initiate_selenium_driver(self, executable_path: str = None, driver_type: str = 'Chrome',
                                 headless_mode: bool = False) -> None:
        """
        Initiate selenium web driver instance
        Args:
            executable_path (str, optional): path to the location of the web driver executable. Defaults to None.
            driver_type (str, optional): web driver type Chrome Web Driver or Gecko Driver. Defaults to 'Chrome'.
            headless_mode (bool, optional): Toggle On/Off headless mode. Defaults to False.

        Raises:
            DriverTypeNotSupportedException: The requested driver type is not currently supported
        """
        if driver_type.title() == 'Chrome':
            options = webdriver.ChromeOptions()
            if headless_mode:
                options.add_argument("headless")
            if executable_path:
                self.driver = webdriver.Chrome(executable_path=executable_path, options=options)
            else:
                self.driver = webdriver.Chrome(options=options)
        else:
            raise DriverTypeNotSupported('Only Chrome driver is currently supported.')

    def go_to_glassdoor(self, keyword: str) -> None:
        """
        Navigate to the requested job listing search page in Glassdoor.com
        Args:
            keyword (_type_): requested job eg: data science, data engineering, etc.
        """

        self.driver.get(f"https://www.glassdoor.com/Job/{keyword.lower().replace(' ', '-')}-jobs-SRCH_KO0,14.htm?clickSource=searchBox")


    def exit_salary_estimate_popup(self) -> None:
        """
        Check whether the salary estimate popup box is displayed and close it
        """
        try:
            if 'Salary' in self.driver.find_element(By.XPATH, ".//div[@class='modal_title']").text:
                self.driver.find_element(By.XPATH, ".//span[@alt='Close' and contains(@class, \
                                         'modal_closeIcon')]").click()
                sleep(2)
        except NoSuchElementException:
            pass

    def exit_login_popup(self) -> None:
        """
        Check whether login popup box is displayed and close it
        """
        try:
            self.driver.find_element(By.XPATH, '//*[@id="JAModal"]/div/div[2]/span').click()
        except NoSuchElementException:
            pass

    @staticmethod
    def generate_company_information_xpath(keyword: str=None) -> str:
        """
        Based on the keyword specified generate a static XPATH to access company information

        Args:
            keyword (str, optional): Element identifier text. Defaults to None.

        Returns:
            str: custom XPATH 
        """
        return f"//div[@id='EmpBasicInfo']/descendant::*[contains(text(),'{keyword}')]/following::*"

    def get_jobs_data(self, keyword: str=None, num_jobs: int=0, verbose: bool=False) -> None:
        """
        Navigate to Glassdoor website and scrape the specified number of jobs if available
        Args:
            keyword (str, optional): job to be scraped. Defaults to None.
            num_jobs (int, optional): number of jobs to be scraped. Defaults to 0.
            verbose (bool, optional): display the job information. Defaults to False.
        """
        scraped_jobs = []

        # Raises an exception if the job is not specified
        if not keyword:
            raise ValueError(" Keyword argument is not specified! Please specify the job to be scraped.")

        # Go to the specific job's listing page in Glassdoor
        self.go_to_glassdoor(keyword=keyword)

        # Ensure that you aren't scraping jobs more than what you need
        while len(scraped_jobs) < num_jobs:

            sleep(2)

            # Grab all the jobs in page
            job_listings = self.driver.find_elements(By.XPATH, ".//*[@data-test='jobListing']")

            # Loop through each of the job in the listing
            for job in job_listings:

                print(f"\n\nProgress: {len(scraped_jobs)} / {num_jobs}")

                # Terminate when enough number of jobs have been parsed
                if len(scraped_jobs) >= num_jobs:
                    break

                # Exit glassdoor salary estimate popup
                self.exit_salary_estimate_popup()

                # Exit login
                self.exit_login_popup()

                # Click on the job listing to access the description and other useful information
                job.click()
                sleep(3)

                # Exit glassdoor salary estimate popup
                self.exit_salary_estimate_popup()

                # Exit login
                self.exit_login_popup()

                collected_successfully = False

                while not collected_successfully:
                    try:

                        # Get the company name
                        company_name = self.driver.find_element(By.XPATH, "//*[@data-test='hero-header-module']\
                                                                //*[@data-test='employerName']//self::div").text
                        company_name = company_name.split('\n')[0]

                        # Get the job title
                        job_title = self.driver.find_element(By.XPATH, "//*[@data-test='hero-header-module']//*[@data-test='jobTitle']").text

                        # Get the job location
                        location = self.driver.find_element(By.XPATH, "//*[@data-test='hero-header-module']//*[@data-test='location']").text

                        # Get the salary information
                        try:
                            salary_info = self.driver.find_element(By.XPATH, "//*[@data-test='hero-header-module']//*[@data-test='detailSalary']").text
                            # Get the estimate type
                            if re.search(RE_ESTIMATE_TYPE, salary_info):
                                estimate_type = re.search(RE_ESTIMATE_TYPE, salary_info).group(0)
                            else:
                                estimate_type = None

                            # Get the salary range
                            if re.search(RE_SALARY_RANGE, salary_info):
                                salary_range = re.search(RE_SALARY_RANGE, salary_info).group(0)

                                if '-' in salary_range:
                                    salary_ranges = salary_range.split('-')
                                    lower_salary_estimate = salary_ranges[0].replace('$', '').replace('K', '000')
                                    higher_salary_estimate = salary_ranges[1].replace('$', '').replace('K', '000')

                                elif re.search(RE_SINGLE_SALARY, salary_info):
                                    single_salary_value = re.search(RE_SINGLE_SALARY, salary_info).group(0)
                                    lower_salary_estimate = single_salary_value.replace('$', '').replace('K', '000')
                                    higher_salary_estimate = single_salary_value.replace('$', '').replace('K', '000')
                                else:
                                    lower_salary_estimate, higher_salary_estimate = -1, -1
                            else:
                                lower_salary_estimate, higher_salary_estimate = -1, -1
                        except NoSuchElementException:
                            estimate_type, lower_salary_estimate, higher_salary_estimate = None, -1, -1

                        # Get company rating
                        try:
                            rating = self.driver.find_element(By.XPATH, "//*[@data-test='detailRating']").text
                        except NoSuchElementException:
                            rating = -1

                        # Get the average base salary
                        try:
                            avg_base_salary_est = self.driver.find_element(By.XPATH, "//div[contains(@class, 'salaryTab')]//following::div[contains(text(), '$')]").text

                            # Parse the base salary value
                            if re.search(RE_AVG_BASE_SAL, avg_base_salary_est):
                                avg_base_salary_value = re.search(RE_AVG_BASE_SAL, avg_base_salary_est).group(0)
                            else:
                                avg_base_salary_value = -1

                            # parse avg base salary estimate type
                            if re.search(r'(hr|yr)', avg_base_salary_est):
                                avg_base_salary_est_type = re.search(r'(hr|yr)', avg_base_salary_est).group(0)
                                if avg_base_salary_est_type == 'hr':
                                    is_avg_base_salary_hourly = 1
                                    is_avg_base_salary_yearly = 0
                                elif avg_base_salary_est_type == 'yr':
                                    is_avg_base_salary_hourly = 0
                                    is_avg_base_salary_yearly = 1
                            else:
                                is_avg_base_salary_hourly = 0
                                is_avg_base_salary_yearly = 0

                        except NoSuchElementException:
                            avg_base_salary_value, is_avg_base_salary_yearly, is_avg_base_salary_hourly = -1, 0, 0
                        
                        # Get the job description
                        try:
                            job_description = self.driver.find_element(By.XPATH, "//*[contains(@class,'jobDescriptionContent')]").text
                        except NoSuchElementException:
                            job_description = None

                        # Get the year the company was founded
                        try:
                            yr_founded = self.driver.find_element(By.XPATH, self.generate_company_information_xpath(keyword='Founded')).text
                            if yr_founded in NO_COMP_VALUES:
                                yr_founded = None
                                yr_active = None
                            else:
                                yr_active = date.today().year - int(yr_founded)

                        except NoSuchElementException:
                            yr_founded = -1
                            yr_active = -1

                        # Get the industry information
                        try:
                            industry = self.driver.find_element(By.XPATH, self.generate_company_information_xpath(keyword='Industry')).text
                            if industry in NO_COMP_VALUES:
                                industry = None
                        except NoSuchElementException:
                            industry = None

                        # Get the sector information
                        try:
                            sector = self.driver.find_element(By.XPATH, self.generate_company_information_xpath(keyword='Sector')).text
                            if sector in NO_COMP_VALUES:
                                sector = None
                        except NoSuchElementException:
                            sector = None

                        # Get the company type information
                        try:
                            company_type = self.driver.find_element(By.XPATH, self.generate_company_information_xpath(keyword='Type')).text
                            if company_type in NO_COMP_VALUES:
                                company_type = None
                        except NoSuchElementException:
                            company_type = None

                        # Get the company revenue information
                        try:
                            revenue = self.driver.find_element(By.XPATH, self.generate_company_information_xpath(keyword='Revenue')).text
                            if revenue in NO_COMP_VALUES:
                                revenue = None
                        except NoSuchElementException:
                            revenue = None

                        # Get the company headquarters information
                        try:
                            headquarters = self.driver.find_element(By.XPATH, self.generate_company_information_xpath(keyword='Headquarters')).text
                            if headquarters in NO_COMP_VALUES:
                                headquarters = None
                        except NoSuchElementException:
                            headquarters = None

                        # Get the company size information
                        try:
                            size = self.driver.find_element(By.XPATH, self.generate_company_information_xpath(keyword='Size')).text
                            if size in NO_COMP_VALUES:
                                size = None
                        except NoSuchElementException:
                            size = None

                        collected_successfully = True
                    
                    # Sleep and retry if the web driver crashed 
                    except DriverUnsuccessful:
                        sleep(5)

                if verbose:
                    print(f"Job Title: {job_title}")
                    print(f"Salary Estimate: {lower_salary_estimate} - {higher_salary_estimate}")
                    print(f"Salary Estimate Type: {estimate_type}")
                    print(f"Company: {company_name}")
                    print(f"Location: {location}")
                    print(f"Company Rating: {rating}")
                    print(f"Avg Base Salary: {avg_base_salary_value}")
                    print(f"is Avg Base Salary per Hour: {is_avg_base_salary_hourly}")
                    print(f"is Avg Base Salary per Year: {is_avg_base_salary_yearly}")
                    print(f"Year Founded: {yr_founded}")
                    print(f"Years Active: {yr_active}")
                    print(f"Industry: {industry}")
                    print(f"Sector: {sector}")
                    print(f"Company Type: {company_type}")
                    print(f"Revenue: {revenue}")
                    print(f"Headquarters: {headquarters}")
                    print(f"Size: {size}")
                    print(f"Job Description: {job_description}")

                scraped_jobs.append(
                    {
                        "Job Title": job_title,
                        "Salary Range Estimate": f"{lower_salary_estimate} - {higher_salary_estimate}",
                        "Salary Estimate Type": estimate_type,
                        "Company": company_name,
                        "Location": location,
                        "Company Rating": rating,
                        "Avg Base Salary": avg_base_salary_value,
                        "is Avg Base Salary per Hour": is_avg_base_salary_hourly,
                        "is Avg Base Salary per Year": is_avg_base_salary_yearly,
                        "Year Founded": yr_founded,
                        "Years Active": yr_active,
                        "Industry": industry,
                        "Sector": sector,
                        "Company Type": company_type,
                        "Revenue": revenue,
                        "Headquarters": headquarters,
                        "Size": size,
                        "Job Description": job_description
                    }
                )

            # Click Next Page for More Jobs
            try:
                if len(scraped_jobs) < num_jobs:
                    self.driver.find_element(By.XPATH, "//button[(@data-test='pagination-next') and (contains(@class, 'nextButton'))]").click()
                    sleep(10)
            except NoSuchElementException:
                print(f"No more jobs to scrape! Only {len(scraped_jobs)} jobs were available out of the required {num_jobs} jobs.")

            # Store the scraped jobs to the scraped dataset variable
            self.scraped_dataset = scraped_jobs

    def dump_scraped_data_to_json(self, filename: str=str(datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))) -> None:
        """
        Writes the scraped jobs to a JSON file
        Args:
            filename (str, optional): Filename to store the scraped data. Defaults to str(datetime.now().strftime('%Y-%m-%dT%H:%M:%S')).
        """
        with open(f"{filename}.json", "w", encoding="utf-8") as json_file:
            json.dump(self.scraped_dataset, json_file, ensure_ascii=False, indent=4)
