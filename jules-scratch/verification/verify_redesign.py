import time
from playwright.sync_api import sync_playwright, Page, expect

def verify_redesign(page: Page):
    time.sleep(5) # Wait for server to start
    # 1. Navigate to the receiver page
    page.goto("http://127.0.0.1:8000/receiver")

    # 2. Enter room name and username
    page.get_by_label("Room Name").fill("test-room")
    page.get_by_label("Display Name").fill("jules")
    page.get_by_role("button", name="Connect to Room").click()

    # Wait for the page to load
    expect(page).to_have_title("Room: test-room - FileBridge")

    # Wait for socket to connect
    time.sleep(2)

    # 3. Send a message
    page.get_by_placeholder("Type your message or drag files here...").fill("Hello, this is a test message!")
    page.get_by_title("Send Message").click()

    # Wait for the message to appear
    expect(page.get_by_text("Hello, this is a test message!").first).to_be_visible()

    # 4. Take a screenshot of the chat page
    page.screenshot(path="jules-scratch/verification/chat_page.png")

    # 5. Click the hamburger menu to open the user panel
    # The hamburger menu is only visible on smaller screens.
    # I will resize the viewport to a mobile size.
    page.set_viewport_size({"width": 767, "height": 800})
    page.locator(".hamburger-menu").click()

    # Wait for the panel to be active and animation to complete
    page.wait_for_timeout(1000)

    # 6. Take another screenshot
    page.screenshot(path="jules-scratch/verification/chat_page_mobile_panel.png")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    verify_redesign(page)
    browser.close()
