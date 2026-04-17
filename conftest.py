"""
conftest.py  —  Shared pytest-playwright fixtures for TaskFlow tests.
Excel test data is loaded once per session; only run=Y rows are used.
"""
import os
import pytest
from pathlib import Path
from playwright.sync_api import Page
from pages.task_page import LoginPage, TaskPage
from utils.excel_reader import ExcelReader, get_reader

# ── App path ───────────────────────────────────────────────────────────────
APP_PATH = Path(__file__).parent / "app.html"
APP_URL  = APP_PATH.as_uri()


def pytest_addoption(parser):
    parser.addoption("--app-url", default=APP_URL,
                     help="URL of the app under test")


@pytest.fixture(scope="session")
def app_url(pytestconfig) -> str:
    return pytestconfig.getoption("--app-url")


# ── Excel reader — loaded ONCE for the whole session ──────────────────────
@pytest.fixture(scope="session")
def excel() -> ExcelReader:
    """Session-scoped Excel reader. Only run=Y rows are returned."""
    reader = get_reader()
    print(f"\n{reader.summary()}\n")
    return reader


# ── Browser / context ──────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, tmp_path_factory):
    return {
        **browser_context_args,
        "viewport":         {"width": 1280, "height": 800},
        "record_video_dir": str(tmp_path_factory.mktemp("videos")),
    }


# ── Page fixtures ──────────────────────────────────────────────────────────
@pytest.fixture
def open_app(page: Page, app_url: str) -> Page:
    page.goto(app_url)
    return page


@pytest.fixture
def login_page(open_app: Page) -> LoginPage:
    return LoginPage(open_app)


@pytest.fixture
def logged_in(page: Page, app_url: str) -> TaskPage:
    page.goto(app_url)
    lp = LoginPage(page)
    lp.login("admin", "admin123")
    lp.wait_for_hidden()
    return TaskPage(page)


@pytest.fixture
def logged_in_with_tasks(logged_in: TaskPage) -> TaskPage:
    """Seeds 3 tasks (matching FilterScenarios sheet setup)."""
    logged_in.add_task("Alpha Task",  priority="high")
    logged_in.add_task("Beta Task",   priority="medium")
    logged_in.add_task("Gamma Task",  priority="low")
    return logged_in


# ── Screenshot on failure ──────────────────────────────────────────────────
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report  = outcome.get_result()
    if report.when == "call" and report.failed:
        page: Page = item.funcargs.get("page")
        if page:
            os.makedirs("screenshots", exist_ok=True)
            safe = item.name.replace("/", "_").replace("::", "__")
            page.screenshot(path=f"screenshots/FAIL_{safe}.png", full_page=True)
            print(f"\n📸  Saved: screenshots/FAIL_{safe}.png")

