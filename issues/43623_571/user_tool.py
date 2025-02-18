import sys, os

base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, base_path)

from playwright.sync_api import Page, sync_playwright, expect, ViewportSize
from utils.trace_cleaner import trace_cleaner

def login_user(page: Page, user_email: str):

    page.goto("https://dev.new.expensify.com:8082/")


    page.get_by_test_id("username").fill(user_email)
    page.get_by_role("button", name="Continue").click()


    page.get_by_role("button", name="Join").click()

    return user_email


def onboarding_user(page: Page, first_name="Test", last_name="Test"):
    expect(page.get_by_text("What do you want to do today?")).to_be_visible(
        timeout=30000
    )


    activity_text = "Track and budget expenses"
    page.get_by_label(activity_text).first.click()


    page.get_by_role("textbox", name="First name").fill(first_name)
    page.get_by_role("textbox", name="Last name").fill(last_name)
    page.get_by_role("button", name="Continue").last.click()


def invite_member(page: Page, email: str):
    page.get_by_label("Members").click()
    page.get_by_role("button", name="Invite member").click()
    page.get_by_test_id("selection-list-text-input").fill(email)
    page.locator('button[aria-label="Test Test"]').first.click()
    page.get_by_role("button", name="Next").click()
    with page.expect_request(
        lambda response: "api/AddMembersToWorkspace" in response.url
    ) as first:
        page.get_by_test_id("WorkspaceInviteMessagePage").get_by_role(
            "button", name="Invite"
        ).click()
    first.value.response().finished()


def create_workspace_with_precondition(page: Page, member_email: str):

    page.get_by_label("Start chat (Floating action)").click()
    page.get_by_label("New workspace").click()

    page.get_by_label("Categories").click()
    page.get_by_label("Select all").click()
    page.get_by_role("button", name="selected").click()
    page.get_by_label("Disable categories").click()

    invite_member(page, member_email)


def track_expense(page: Page):
    page.get_by_label("Start chat (Floating action)").click()
    page.get_by_label("Track expense").first.click()
    page.get_by_role("button", name="Got it").click()
    page.get_by_label("Manual").click()
    page.get_by_placeholder("0").fill("88")
    page.locator("#numPadContainerView").get_by_role("button", name="Next").click()
    page.get_by_role("button", name="Track expense").first.click()


def test_categorize():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            channel="chrome",
            headless=True,
            args=[
                "--ignore-certificate-errors",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
            ],
            proxy={"server": "http://localhost:8080"},
            slow_mo=1000,
        )
        context_args = {}
        context_args["timezone_id"] = "Asia/Karachi"
        admin_user_context = browser.new_context(
            viewport=ViewportSize(width=1280, height=620), **context_args
        )
        member_user_context = browser.new_context(
            viewport=ViewportSize(width=1280, height=620), **context_args
        )
        admin_user_page = admin_user_context.new_page()
        member_user_page = member_user_context.new_page()


        admin_user_context.tracing.start(screenshots=True, snapshots=True)
        member_user_context.tracing.start(screenshots=True, snapshots=True)

        try:

            admin_email = "t56826807+1733403564@gmail.com"
            login_user(admin_user_page, admin_email)
            onboarding_user(admin_user_page)


            member_email = "t56826807+1733403573@gmail.com"
            login_user(member_user_page, member_email)
            onboarding_user(member_user_page)


            create_workspace_with_precondition(admin_user_page, member_email)


            track_expense(member_user_page)


            member_user_page.get_by_role("button", name="Categorize it").first.click()
            member_user_page.wait_for_timeout(3000)


            expect(
                member_user_page.get_by_test_id("selection-list").get_by_label("Test Test")
            ).not_to_be_visible()
        finally:

            admin_user_context.tracing.stop(path="/app/expensify/user_tool/output_browser1.zip")
            trace_cleaner("/app/expensify/user_tool/output_browser1.zip")
            member_user_context.tracing.stop(path="/app/expensify/user_tool/output_browser2.zip")
            trace_cleaner("/app/expensify/user_tool/output_browser2.zip")

            member_user_page.close()
            admin_user_page.close()
            browser.close()
