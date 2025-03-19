from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd

def scrape_kalshi_events():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  
    service = Service("/Users/caelenfry/Downloads/chromedriver-mac-arm64/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get("https://kalshi.com/events")
    time.sleep(5)

  
    cards = driver.find_elements(By.CSS_SELECTOR, 'div.flex.flex-col.justify-between.w-full')
    all_data = []

    for card in cards:

        try:
            title_elem = card.find_element(By.CLASS_NAME, 'line-clamp-3')
            title_text = title_elem.text
        except:
            title_text = "N/A"

  
        try:
            bet_elem = card.find_element(By.CSS_SELECTOR, 'span.lining-nums.tabular-nums')
            bet_text = bet_elem.text
        except:
            bet_text = "N/A"


        spans = card.find_elements(By.CSS_SELECTOR, 'span.transition-colors.duration-300')


        try:
            volume_elem = card.find_element(By.CSS_SELECTOR,'[aria-label="Total series volume"] .lining-nums.tabular-nums')
            volume_text = volume_elem.text
        except:
            volume_text = "N/A"

    
        labels_and_percents = []
        temp_label = None

        for s in spans:
            txt = s.text.strip()
            if txt.endswith('%'):
       
                if temp_label:
                    labels_and_percents.append((temp_label, txt))
                    temp_label = None
                else:
                    labels_and_percents.append(("UNKNOWN", txt))
            else:
        
                temp_label = txt


        for (label, pct) in labels_and_percents:
            row = {
                "Title": title_text,
                "Bet Text": bet_text,
                "Outcome Label": label,
                "Outcome Percent": pct,
                "Volume": volume_text,
            }
            all_data.append(row)

    driver.quit()
    return all_data

if __name__ == "__main__":
    data = scrape_kalshi_events()
    df = pd.DataFrame(data)
    df.to_csv("kalshi_data.csv", index=False)
    print(df)
    print("Data saved to kalshi_data.csv")
