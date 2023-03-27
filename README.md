# Glassdoor Scraper

**Glassdoor Scraper** provides a Selenium based web scraper for Glassdoor website. This tool currently supports only scraping job listings.

### Features

1. User must specify the job of interest (eg: data scientist) and the minimum number of jobs to scrape (eg: 100)
2. User can also provide the job location of preference (eg: dallas), but its not a required field
3. User can specify whether duplicate job entries should be skipped
4. Scraper will scrape from multiple pages (if available) till the requested number of jobs have been scraped
5. Dumps the scraped listings to a JSON file
6. Prints the job progress status

### How to Use?
1. Setup Selenium and install web drivers
2. Install the requirements in the *requirements.txt*
    > pip3 install -r requirements.txt
3. In a python file, import the scraper class
    > from glassdoor_scraper import GlassdoorScraper
4. Instantiate the class object and execute the job
    > demo_job = GlassdoorScraper()
    > """ Initiate the Selenium WebDriver """
    > demo_job.initiate_selenium_driver()
    > """ Execute the scraping - scrape at least 1000 data scientist jobs """
    > demo_job.get_jobs_data(keyword="data scientist", num_jobs=1000)
    > """ Execute the scraping (with location) - scrape at least 1000 data scientist jobs """
    > demo_job.get_jobs_data(keyword="data scientist", location="dallas", num_jobs=1000)
    > """ Execute the scraping (scrape with duplicate jobs) - scrape at least 1000 data scientist jobs """
    > demo_job.get_jobs_data(keyword="data scientist", remove_duplicates=False, num_jobs=1000)
    > """ Dump the scraped data to a JSON file - Stores in the current working directory"""
    > demo_job.dump_scraped_data_to_json(filename="demo_data_scientist_jobs.json")

### Sample Scraped Data
>{
        "Job Title": "Data Research Scientist",
        "Salary Range Estimate": "96000  -  132000",
        "Salary Estimate Type": "Glassdoor",
        "Company": "Demo Company",
        "Location": "Philadelphia, PA",
        "Company Rating": "3.7",
        "Avg Base Salary": "112617",
        "is Avg Base Salary per Hour": 0,
        "is Avg Base Salary per Year": 1,
        "Year Founded": "1975",
        "Years Active": 48,
        "Industry": "Computer Hardware Development",
        "Sector": "Information Technology",
        "Company Type": "Company - Private",
        "Revenue": "\$5 to \$25 million (USD)",
        "Headquarters": null,
        "Size": "10000+ Employees",
        "Job Description": "Supports and performs the development and programming of machine learning integrated software algorithms to structure, analyze, and leverage data in a production environment.\nCore Responsibilities\nLeverages data pipeline designs and supports the development of data pipelines to support model development. Proficient with software tools that develop data pipelines in a distributed computing environment (PySprak, GlueETL).\nSupports integration of model pipelines in a production environment. Develops understanding of SDLC for model production.\nReviews pipeline designs, makes data model design changes as needed. Documents and reviews design changes with data science teams."
    }


### Things to Note
1. The code has been currently tested only with Chromedriver on a Google Chrome browser
2. The maximum number of jobs I tried to scrape without duplicates was 1000 data scientist jobs (117 unique jobs over 1000 listings :D)
3. Headless mode is broken :( - will passively work on fixing it

### Credits
I developed this tool loosely based on [Vinny Sakarya's Scraper](https://github.com/arapfaik/scraping-glassdoor-selenium) which was referenced by YouTuber **Ken Jee** in his [Data Science Project from Scratch](https://www.youtube.com/watch?v=MpF9HENQjDo&list=PL2zq7klxX5ASFejJj80ob9ZAnBHdz5O1t) series.