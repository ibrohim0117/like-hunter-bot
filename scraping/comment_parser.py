from playwright.sync_api import sync_playwright
from typing import List, Dict
import os
import time
from scraping.login import SESSION_PATH, login_and_save_session
from bot.config import IG_USERNAME, IG_PASSWORD


def get_all_comments_with_likes(post_url: str) -> List[Dict[str, str]]:
    # Agar sessiya mavjud bo'lmasa, login qilamiz
    if not os.path.exists(SESSION_PATH):
        os.makedirs(os.path.dirname(SESSION_PATH), exist_ok=True)
        login_and_save_session(IG_USERNAME, IG_PASSWORD)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=SESSION_PATH)
        page = context.new_page()

        page.goto(post_url, wait_until="domcontentloaded")
        time.sleep(5)  # Sahifa to'liq yuklanishi uchun biroz kutish

        # Skriptingni boshlashdan oldin sahifani skrollash
        page.evaluate('window.scrollTo(0, document.body.scrollHeight)')  # Sahifani pastga qarab skrrollash
        time.sleep(3)  # 3 soniya kutish

        # Yana bir bor sahifani pastga qarab skrollash (agar ko‘proq kommentlar yuklanishi uchun)
        page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        time.sleep(3)

        # Kommentlar elementlarini kutish
        try:
            page.wait_for_selector('ul > div > li', timeout=30000)  # 30 soniya
            comments = page.query_selector_all('ul > div > li')

            comment_data = []
            for comment in comments:
                text_element = comment.query_selector('span[dir="auto"]')
                like_element = comment.query_selector('span[aria-label*="like"]')

                if text_element and like_element:
                    text = text_element.inner_text()
                    likes = like_element.inner_text()

                    # Kommentning like sonini int ga aylantirish
                    like_count = int(likes.replace(' likes', '').replace(',', '') if likes else 0)

                    comment_data.append({'comment_text': text, 'comment_like_count': like_count})

            return comment_data

        except Exception as e:
            print(f"❌ Error while fetching comments: {e}")
            return []

        finally:
            browser.close()


# Test
if __name__ == "__main__":
    url = 'https://www.instagram.com/reel/DJlPyFnI6QT/?utm_source=ig_web_copy_link'
    comments_data = get_all_comments_with_likes(url)

    if comments_data:
        print("Comments:")
        for comment in comments_data:
            print(comment)
    else:
        print("No comments found.")
