from playwright.sync_api import sync_playwright
from bot.config import IG_USERNAME, IG_PASSWORD
from scraping.login import SESSION_PATH, login_and_save_session
import os
import time

def get_top_comment(post_url: str):
    if not os.path.exists(SESSION_PATH):
        login_and_save_session(IG_USERNAME, IG_PASSWORD)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=SESSION_PATH)
        page = context.new_page()

        page.goto(post_url)
        time.sleep(5)

        for _ in range(5):
            try:
                page.click("text=View all comments")
                time.sleep(2)
            except:
                break

        comments = page.query_selector_all("ul.XQXOT > ul > div > li")
        top_comment = None
        max_likes = -1

        for comment in comments:
            try:
                text = comment.inner_text()
                parts = text.split('\n')
                comment_text = parts[1] if len(parts) > 1 else "No text"
                like_text = parts[-1]
                if 'like' in like_text:
                    likes = int(like_text.split(' ')[0])
                    if likes > max_likes:
                        max_likes = likes
                        top_comment = comment_text
            except:
                continue

        browser.close()
        return top_comment, max_likes
