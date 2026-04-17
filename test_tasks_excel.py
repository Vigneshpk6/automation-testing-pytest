"""
tests/test_tasks_excel.py
Task, Filter, UI, and Delete tests — all data-driven from Excel.
Only rows marked run=Y are executed; run=N rows are silently skipped.
"""
import os
import pytest
from playwright.sync_api import Page, expect
from pages.task_page import TaskPage, LoginPage
from utils.excel_reader import get_reader, TaskRow, FilterRow, UICheckRow, DeleteRow

_reader = get_reader()

# ── Collect only enabled rows at import time ───────────────────────────────
_task_rows   = _reader.task_rows()          # run=Y only
_filter_rows = _reader.filter_rows()
_ui_rows     = _reader.ui_check_rows()
_delete_rows = _reader.delete_rows()


# ════════════════════════════════════════════════════════════════════════════
#  TaskData — add & complete
# ════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize(
    "row", _task_rows,
    ids=[r.test_case for r in _task_rows],
)
def test_add_task_from_excel(logged_in: TaskPage, row: TaskRow):
    """Add each run=Y task; verify name and priority tag appear."""
    logged_in.add_task(row.task_name, priority=row.priority)

    visible = logged_in.get_visible_tasks()
    assert row.task_name in visible, \
        f"[{row.test_case}] Task '{row.task_name}' not found in list"

    priority_shown = logged_in.get_task_priority(0)
    assert priority_shown == row.priority, \
        f"[{row.test_case}] Priority '{row.priority}' expected, got '{priority_shown}'"


@pytest.mark.parametrize(
    "row",
    _reader.tasks_to_complete(),   # subset: should_complete=Y AND run=Y
    ids=[r.test_case for r in _reader.tasks_to_complete()],
)
def test_complete_task_from_excel(logged_in: TaskPage, row: TaskRow):
    """Add then complete tasks flagged should_complete=Y in Excel."""
    logged_in.add_task(row.task_name, priority=row.priority)
    logged_in.complete_task(0)
    assert logged_in.is_task_completed(0), \
        f"[{row.test_case}] Task should be marked completed"


def test_all_enabled_tasks_added_sequentially(logged_in: TaskPage):
    """Add all run=Y tasks from Excel in order; verify total count and names."""
    tasks = _reader.task_rows()
    for t in tasks:
        logged_in.add_task(t.task_name, priority=t.priority)

    assert logged_in.get_task_count_badge() == len(tasks)
    visible = logged_in.get_visible_tasks()
    for t in tasks:
        assert t.task_name in visible, f"Missing: '{t.task_name}'"


def test_task_data_run_column_summary():
    """Report how many task rows are enabled vs skipped."""
    all_rows = _reader.task_rows(enabled_only=False)
    enabled  = _reader.task_rows()
    skipped  = [r for r in all_rows if r.run.upper() != "Y"]
    print(f"\nTaskData: {len(all_rows)} total | "
          f"✅ {len(enabled)} run=Y | ⏭  {len(skipped)} run=N skipped")
    for r in skipped:
        print(f"   ⏭  SKIPPED: {r.test_case} ({r.task_name})")
    assert len(enabled) > 0


# ════════════════════════════════════════════════════════════════════════════
#  FilterScenarios
# ════════════════════════════════════════════════════════════════════════════

def _seed_filter_state(tp: TaskPage):
    """Add 3 tasks, complete the first — matches FilterScenarios setup."""
    tp.add_task("Alpha Task", priority="high")
    tp.add_task("Beta Task",  priority="medium")
    tp.add_task("Gamma Task", priority="low")
    tp.complete_task(0)


@pytest.mark.parametrize(
    "row", _filter_rows,
    ids=[r.filter_name for r in _filter_rows],
)
def test_filter_from_excel(logged_in: TaskPage, row: FilterRow):
    """Each run=Y filter scenario: seed tasks, apply filter, assert counts."""
    _seed_filter_state(logged_in)
    logged_in.set_filter(row.filter_name)

    visible = len(logged_in.get_visible_tasks())
    assert visible == row.expected_visible, (
        f"Filter '{row.filter_name}': expected {row.expected_visible} visible, "
        f"got {visible}. Note: {row.notes}"
    )


# ════════════════════════════════════════════════════════════════════════════
#  UIChecks
# ════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize(
    "row", _ui_rows,
    ids=[r.check_name for r in _ui_rows],
)
def test_ui_check_from_excel(open_app: Page, row: UICheckRow):
    """Each run=Y UI check: verify selector visibility and text."""
    if row.selector == "title":
        expect(open_app).to_have_title(row.expected_text)
        return

    locator = open_app.locator(row.selector)
    if row.should_be_visible:
        expect(locator).to_be_visible()
    if row.expected_text:
        expect(locator).to_contain_text(row.expected_text)


def test_ui_checks_run_column_summary():
    all_rows = _reader.ui_check_rows(enabled_only=False)
    enabled  = _reader.ui_check_rows()
    skipped  = [r for r in all_rows if r.run.upper() != "Y"]
    print(f"\nUIChecks: {len(all_rows)} total | "
          f"✅ {len(enabled)} run=Y | ⏭  {len(skipped)} run=N skipped")
    for r in skipped:
        print(f"   ⏭  SKIPPED: {r.check_name}")


# ════════════════════════════════════════════════════════════════════════════
#  DeleteScenarios
# ════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize(
    "row", _delete_rows,
    ids=[r.test_case for r in _delete_rows],
)
def test_delete_from_excel(logged_in: TaskPage, row: DeleteRow):
    """Each run=Y delete scenario: add task, delete it, check count."""
    logged_in.add_task(row.task_name, priority="medium")

    # If the scenario seeds 2 tasks (expected_count_after=1), add a second one
    if row.expected_count_after == 1:
        logged_in.add_task(row.task_name + " #2", priority="low")

    logged_in.delete_task(0)

    actual = logged_in.get_task_count_badge()
    assert actual == row.expected_count_after, (
        f"[{row.test_case}] Expected {row.expected_count_after} tasks after delete, got {actual}"
    )
    if row.expected_count_after == 0:
        assert logged_in.is_empty_state_visible(), \
            f"[{row.test_case}] Empty state should be visible"


def test_delete_run_column_summary():
    all_rows = _reader.delete_rows(enabled_only=False)
    enabled  = _reader.delete_rows()
    skipped  = [r for r in all_rows if r.run.upper() != "Y"]
    print(f"\nDeleteScenarios: {len(all_rows)} total | "
          f"✅ {len(enabled)} run=Y | ⏭  {len(skipped)} run=N skipped")
    for r in skipped:
        print(f"   ⏭  SKIPPED: {r.test_case}")


# ════════════════════════════════════════════════════════════════════════════
#  Full Excel summary
# ════════════════════════════════════════════════════════════════════════════

def test_excel_full_summary():
    """Prints the complete run=Y / run=N breakdown for all sheets."""
    print(f"\n{_reader.summary()}")
    assert True
