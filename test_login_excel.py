"""
tests/test_login_excel.py
Login tests — data-driven from LoginData sheet.
Only rows marked run=Y in Excel are parametrized and executed.
"""
import pytest
from playwright.sync_api import Page, expect
from pages.task_page import LoginPage
from utils.excel_reader import get_reader, LoginRow

_reader = get_reader()

# Build parametrize lists at collection time (only run=Y rows)
_valid_logins   = _reader.valid_logins()
_invalid_logins = _reader.invalid_logins()


@pytest.mark.parametrize(
    "row",
    _valid_logins,
    ids=[r.test_case for r in _valid_logins],
)
def test_valid_login(open_app: Page, row: LoginRow):
    """run=Y success rows: login must dismiss overlay."""
    lp = LoginPage(open_app)
    lp.login(row.username, row.password)
    expect(open_app.locator("#login-overlay")).to_be_hidden(timeout=5000)


@pytest.mark.parametrize(
    "row",
    _invalid_logins,
    ids=[r.test_case for r in _invalid_logins],
)
def test_invalid_login(open_app: Page, row: LoginRow):
    """run=Y failure rows: overlay must stay, error must appear."""
    lp = LoginPage(open_app)
    lp.login(row.username, row.password)
    assert lp.is_visible(),            f"Overlay should stay visible — {row.test_case}"
    assert lp.get_error().strip() != "", f"Error message expected — {row.test_case}"


def test_excel_login_summary():
    """Prints a summary of run=Y vs run=N rows (always passes)."""
    all_rows = _reader.login_rows(enabled_only=False)
    enabled  = _reader.login_rows(enabled_only=True)
    skipped  = [r for r in all_rows if r.run.upper() != "Y"]
    print(f"\nLoginData: {len(all_rows)} total | "
          f"✅ {len(enabled)} run=Y | ⏭  {len(skipped)} run=N skipped")
    for r in skipped:
        print(f"   ⏭  SKIPPED: {r.test_case}")
    assert len(enabled) > 0, "No login rows marked run=Y in Excel!"
