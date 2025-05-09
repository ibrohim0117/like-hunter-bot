from playwright.sync_api import sync_playwright
import os
import time

SESSION_PATH = "data/sessions/ig_login.json"


def login_and_save_session(username: str, password: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=None)
        page = context.new_page()

        page.goto("https://www.instagram.com/accounts/login/")
        time.sleep(3)

        page.fill("input[name='username']", username)
        page.fill("input[name='password']", password)
        page.click("button[type='submit']")
        time.sleep(5)

        # Check login success
        if "challenge" in page.url:
            raise Exception("Login challenge (2FA?) needed, can't proceed.")

        # Sessionni saqlash
        context.storage_state(path=SESSION_PATH)
        browser.close()
