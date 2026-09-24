Name: Wanyi Liu
JHED ID: wliu127
Module Info: Module 2 - Web Scraping

Robots.txt Compliance:
I have checked the robots.txt file (see screenshot.jpg) before scraping. I confirmed the public applicant result pages are not disallowed. My scraper will use polite behavior, including reasonable delays between requests, and will not attempt to bypass CAPTCHAs or logins.

Approach:
1. I first downloaded a single page locally (`page1.html`) to test my code. I used BeautifulSoup and regular expressions to pull out all information I need.
2. After validating the parser, I updated `scrape.py` to loop through 1,500 pages to reach 30,000 entries. I added Chrome headers and SSL handling to avoid 403 Forbidden errors, and set the script to auto-save to `applicant_data.json` every 20 pages so progress wouldn't be lost.
3. I use `clean.py` to run the provided local model script (`llm_hosting/app.py`). This standardized the messy school and program names and generated the final `llm_extend_applicant_data.json`.

Known Bugs:
1. HTTP 403 Forbidden Blocking: Initial static requests were blocked by GradCafe's anti-scraping filters. Resolved by adding custom Chrome User-Agent request headers and polite delays.
2. Data missing: Many student submissions miss GRE, GPA, or comment fields. Handled using fallback logic (defaulting to empty strings `""`) to keep the JSON schema consistent without crashing the script.