import urllib3
from bs4 import BeautifulSoup
import json
import time
import urllib.parse
import re
import os
import urllib.request
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
def _build_urls(n):
    base = "https://www.thegradcafe.com/survey/index.php"
    url_list = []
    for i in range(1, n + 1):
        query = urllib.parse.urlencode({'p': i})
        link = f"{base}?{query}"
        url_list.append(link)
    return url_list



def _parse_html(html_text):
    f = open("page1.html", "r", encoding="utf-8")
    html = f.read()
    f.close()
    soup = BeautifulSoup(html, "html.parser")
    results = []
    rows = soup.find_all("tr")
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 5:
            university = cols[0].text.strip()
            program = cols[1].text.strip()
            date_added = cols[2].text.strip()
            status = cols[3].text.strip()
            link_tag = cols[4].find("a")
            if link_tag and "href" in link_tag.attrs:
                url = "https://www.thegradcafe.com" + link_tag["href"]
            else:
                url = ""
            next_row = row.find_next_sibling("tr")
            detail_text = next_row.text if next_row else ""
            combined_text = row.text + " " + detail_text   
            
            
            degree = ""
            if re.search(r'PhD|Doctorate', combined_text, re.IGNORECASE):
                degree = "PhD"
            elif re.search(r'Master|MFA|MS|MA', combined_text, re.IGNORECASE):
                degree = "Masters"
                
            us_intl = ""
            if re.search(r'International', combined_text, re.IGNORECASE):
                us_intl = "International"
            elif re.search(r'American|US', combined_text, re.IGNORECASE):
                us_intl = "American"
                
            term = ""
            term_match = re.search(r'(Fall|Spring|Summer|Winter)\s+20\d{2}', combined_text, re.IGNORECASE)
            if term_match:
                term = term_match.group(0).strip()
                
            gpa = ""
            gpa_match = re.search(r'GPA\s*:?\s*([0-9]\.[0-9]+)', combined_text, re.IGNORECASE)
            if gpa_match:
                gpa = gpa_match.group(0).strip()
                
            gre = ""
            gre_match = re.search(r'GRE\s*:?\s*(\d{3})', combined_text, re.IGNORECASE) 
            if gre_match:
                    gre = gre_match.group(0).strip()
            comments = ""
            if next_row:
                raw_comment = next_row.text.strip()
                clean_comment = re.sub(r'(GPA\s*:?\s*[0-9]\.[0-9]+|Spring\s*20\d{2}|Fall\s*20\d{2}|International|American)', '', raw_comment, flags=re.IGNORECASE).strip()
                if len(clean_comment) > 0:
                    comments = clean_comment
            
            data = {
                "program": program,              
                "university": university,           
                "comments": comments,             
                "date_added": date_added,           
                "url": url,                  
                "status": status,               
                "term": term,                 
                "US/International": us_intl,     
                "Degree": degree,               
                "GPA": gpa,                  
                "GRE": gre                   
            }
            results.append(data)
    return results

def save_data(data,filename):
    f = open(filename, "w", encoding="utf-8")
    json_string = json.dumps(data, indent=4)
    f.write(json_string)
    f.close()
    print("Data saved to:", filename)
def load_data(filename):
    f = open(filename, "r", encoding="utf-8")
    json_string = f.read()
    data = json.loads(json_string)
    f.close()
    return data

def scrape_data():
    try:
        all_results = load_data("applicant_data.json")
        print(f"Loaded {len(all_results)} existing entries.")
    except Exception:
        all_results = []

    page_num = 1501
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    while len(all_results) < 30000:
        link = f"https://www.thegradcafe.com/survey/index.php?p={page_num}"
        print(f"Scraping extra page {page_num}... Current total: {len(all_results)}")
        try:
            req = urllib.request.Request(link, headers=headers)
            response = urllib.request.urlopen(req)
            html_text = response.read().decode("utf-8")
            
            page_data = _parse_html(html_text)
            if not page_data:
                break
            all_results.extend(page_data)
            page_num += 1
            time.sleep(0.3)
        except Exception as e:
            print(f"Error on page {page_num}: {e}")
            break
   
    save_data(all_results, "applicant_data.json")
    return all_results

if __name__ == "__main__":
    scrape_data()
