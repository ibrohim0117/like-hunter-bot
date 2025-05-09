import os
import time
from playwright.sync_api import sync_playwright
from bot.config import IG_USERNAME, IG_PASSWORD
from scraping.login import SESSION_PATH, login_and_save_session


def get_top_comment(post_url: str):
    if not os.path.exists(SESSION_PATH):
        os.makedirs(os.path.dirname(SESSION_PATH), exist_ok=True)
        login_and_save_session(IG_USERNAME, IG_PASSWORD)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=SESSION_PATH)
        page = context.new_page()

        page.goto(post_url)

        page.wait_for_load_state('domcontentloaded', timeout=60000)

        time.sleep(5)

        for _ in range(5):
            try:
                page.click("text=View all comments")
                time.sleep(1)
            except:
                break

        try:
            page.wait_for_selector('span[dir="auto"]', timeout=10000)
            spans = page.query_selector_all('span[dir="auto"]')
            comment_texts = [s.inner_text() for s in spans]

            # Filter out author names and pick repeated comments
            from collections import Counter
            counted = Counter(comment_texts)
            counted = {k: v for k, v in counted.items() if len(k) > 3}  # 3 harfdan uzunroq
            if counted:
                top_comment = max(counted.items(), key=lambda x: x[1])
                return top_comment[0], top_comment[1]
            else:
                return None, -1
        except Exception as e:
            print("❌ Exception:", e)
            return None, -1
        finally:
            browser.close()


if __name__ == "__main__":
    url = 'https://www.instagram.com/reel/DJHd5o-M9Tg/?utm_source=ig_web_copy_link'
    result = get_top_comment(url)
    print("🏆 Top Comment:", result)
