from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import re
from datetime import datetime

def clean_date(date_match):
    raw_date = date_match.group()
    raw_date = re.sub(r',\s*,+', ',', raw_date)
    raw_date = re.sub(r',(\d{4})', r', \1', raw_date)
    return raw_date

def extract_info(text):
    info = {"keyword": None, "date": None, "time": None, "levels": None}

    # --- Filter relevant posts ---
    if not re.search(r'(suspend|advisory|classes|school|PAGASA)', text, re.IGNORECASE):
        return info  # ignore non-relevant posts
    
    print('hi')
    # --- Keyword detection ---
    if re.search(r'\bsuspend(ed|sion)?\b', text, re.IGNORECASE):
        info["keyword"] = "suspension"
    elif re.search(r'advisory', text, re.IGNORECASE):
        info["keyword"] = "advisory"

    # --- Date extraction ---
    date_match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s*,?\s*\d{4}', text)
    if date_match:
        raw_date = clean_date(date_match)  
        try:
            dt = datetime.strptime(raw_date, "%B %d, %Y")
            info["date"] = dt.strftime("%Y-%m-%d")
        except:
            pass

    # --- Time extraction ---
    time_match = re.search(
        r'(\d{1,2}(:\d{2})?\s?(AM|PM|MN)?)(\s*(-|to)\s*(\d{1,2}(:\d{2})?\s?(AM|PM|MN)?))?|afternoon|morning|evening|noon|midnight',
        text,
        re.IGNORECASE
    )
    if time_match:
        raw_time = time_match.group().strip().lower()
        if raw_time in ["afternoon", "morning", "evening"]:
            info["time"] = raw_time
        elif raw_time in ["noon"]:
            info["time"] = "12:00 PM"
        elif raw_time in ["midnight", "mn"]:
            info["time"] = "12:00 AM"
        else:
            info["time"] = raw_time.upper()

    re

    # --- Levels extraction ---
    if re.search(r'all levels', text, re.IGNORECASE):
        info["levels"] = "all levels"
    elif re.search(r'face-to-face classes', text, re.IGNORECASE):
        info["levels"] = "face-to-face classes"
    elif re.search(r'public and private schools?', text, re.IGNORECASE):
        info["levels"] = "public and private schools"

    return info

def scrape_facebook_page(url):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)

    posts = driver.find_elements(By.CSS_SELECTOR, "div[data-ad-preview='message']")

    results = []
    for i, post in enumerate(posts, start=1):
        text = post.text.strip()
        if not text:
            continue

        # Extract info
        info = extract_info(text)

        # Try to find the post link (anchor tag inside the post container)
        try:
            link_element = post.find_element(By.XPATH, ".//ancestor::div[@role='article']//a[contains(@href,'/posts/')]")
            post_link = link_element.get_attribute("href")
        except:
            post_link = None

        results.append((i, text, info, post_link))

    driver.quit()
    return results


if __name__ == "__main__":
    page_url = "https://www.facebook.com/zambocitygovt" # example pages https://www.facebook.com/share/p/1CLCowBoUF/ https://www.facebook.com/zambocitygovt/posts/pfbid0NQbMrJfAEZanVferGuZAUuV1f7Q79AE2KL2FoQgG1PiowwLkzrK8McJLuAmPwm3Vl https://www.facebook.com/zambocitygovt/posts/pfbid0Dqn7CVW9pKZCBexcdGqjzEBLoDKGrr7NLpxEHKWeiMyc7guTRn3ckHdpgSVkke2Dl?rdid=NQ8Z9I1sxBmzUqvM#
    scraped_posts = scrape_facebook_page(page_url)

    for i, text, info, link in scraped_posts:
        print(f"\nPost {i}:\n{text}\nExtracted Info: {info}\nLink: {link}")