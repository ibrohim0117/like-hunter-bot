import os
import time
from playwright.sync_api import sync_playwright
from bot.config import IG_USERNAME, IG_PASSWORD
from scraping.login import SESSION_PATH, login_and_save_session

def parse_likes(text):
    if not text:
        return 0
    text = text.lower().replace(" likes", "").replace(" like", "").strip()
    try:
        return int(text)
    except:
        return 0

def get_all_comments_with_likes(post_url: str):
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

        # Ko‘proq kommentlarni yuklash
        for _ in range(10):
            try:
                page.click("text=View all comments")
                time.sleep(1)
            except:
                break

        result_list = []

        try:
            page.wait_for_selector('ul', timeout=10000)
            comment_items = page.query_selector_all("ul > div > li")

            for item in comment_items:
                try:
                    text_span = item.query_selector('span[dir="auto"]')
                    text = text_span.inner_text() if text_span else ""

                    like_button = item.query_selector('button')
                    like_text = like_button.inner_text() if like_button else "0"
                    likes = parse_likes(like_text)

                    if len(text) > 2:
                        result_list.append({text: likes})
                except:
                    continue

            return result_list

        except Exception as e:
            print("❌ Exception:", e)
            return []

        finally:
            browser.close()

# Test qilish uchun:
if __name__ == "__main__":
    url = 'https://www.instagram.com/reel/DJHd5o-M9Tg/?utm_source=ig_web_copy_link'
    result = get_all_comments_with_likes(url)
    print("💬 All Comments with Likes:", result)
