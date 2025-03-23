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
        # (A) Title
        try:
            title_elem = card.find_element(By.CLASS_NAME, 'line-clamp-3')
            title_text = title_elem.text
        except:
            title_text = "N/A"

        # (C) Volume
        try:
            volume_elem = card.find_element(
                By.CSS_SELECTOR,
                '[aria-label="Total series volume"] .lining-nums.tabular-nums'
            )
            volume_text = volume_elem.text
        except:
            volume_text = "N/A"

        # (D) Find label/percent spans
        spans = card.find_elements(By.CSS_SELECTOR, 'span.transition-colors.duration-300')

        # Pair them
        labels_and_percents = []
        temp_label = None

        for s in spans:
            txt = s.text.strip()
            if txt.endswith('%'):
                # It's a percentage
                if temp_label:
                    labels_and_percents.append((temp_label, txt))
                    temp_label = None
                else:
                    labels_and_percents.append(("UNKNOWN", txt))
            else:
                temp_label = txt  # It's a label

        # (E) Format into one row for each card (assuming up to 2 outcomes)
        # If there's exactly 2 pairs, we match them to Option1/Option2
        # If there's fewer/more, we handle gracefully
        pair_count = len(labels_and_percents)
        if pair_count == 2:
            row = {
                "Title": title_text,
                "Option1Label": labels_and_percents[0][0],
                "Option1Percent": labels_and_percents[0][1],
                "Option2Label": labels_and_percents[1][0],
                "Option2Percent": labels_and_percents[1][1],
                "Volume": volume_text,
            }
        elif pair_count == 1:
            # Only one outcome
            row = {
                "Title": title_text,
                "Option1Label": labels_and_percents[0][0],
                "Option1Percent": labels_and_percents[0][1],
                "Option2Label": "N/A",
                "Option2Percent": "N/A",
                "Volume": volume_text,
            }
        elif pair_count >= 3:
            # More than 2 outcomes; handle first 2, or store them all
            # Here we just store first 2 for simplicity
            row = {
                "Title": title_text,
                "Option1Label": labels_and_percents[0][0],
                "Option1Percent": labels_and_percents[0][1],
                "Option2Label": labels_and_percents[1][0],
                "Option2Percent": labels_and_percents[1][1],
                "Volume": volume_text,
            }
        else:
            # No outcomes found
            row = {
                "Title": title_text,
                "Option1Label": "N/A",
                "Option1Percent": "N/A",
                "Option2Label": "N/A",
                "Option2Percent": "N/A",
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
