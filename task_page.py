"""
pages/task_page.py  —  Page Object Models for TaskFlow
"""
from __future__ import annotations
from playwright.sync_api import Page, expect


class LoginPage:
    def __init__(self, page: Page):
        self.page           = page
        self.username_input = page.locator("#username")
        self.password_input = page.locator("#password")
        self.login_btn      = page.locator("#login-btn")
        self.error_msg      = page.locator("#login-error")
        self.overlay        = page.locator("#login-overlay")

    def login(self, username: str, password: str) -> None:
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_btn.click()

    def login_with_enter(self, username: str, password: str) -> None:
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.password_input.press("Enter")

    def get_error(self) -> str:
        return self.error_msg.inner_text()

    def is_visible(self) -> bool:
        return self.overlay.is_visible()

    def wait_for_hidden(self) -> None:
        self.overlay.wait_for(state="hidden", timeout=5000)


class TaskPage:
    def __init__(self, page: Page):
        self.page            = page
        self.task_input      = page.locator("#task-input")
        self.priority_select = page.locator("#priority-select")
        self.add_btn         = page.locator("#add-btn")
        self.task_list       = page.locator("#task-list")
        self.task_count      = page.locator("#task-count")
        self.empty_state     = page.locator("#empty-state")
        self.toast           = page.locator("#toast")

    def add_task(self, text: str, priority: str = "medium") -> None:
        self.task_input.fill(text)
        self.priority_select.select_option(priority)
        self.add_btn.click()

    def add_task_with_enter(self, text: str, priority: str = "medium") -> None:
        self.task_input.fill(text)
        self.priority_select.select_option(priority)
        self.task_input.press("Enter")

    def complete_task(self, index: int = 0) -> None:
        self.page.locator(".task-check").nth(index).click()

    def delete_task(self, index: int = 0) -> None:
        self.page.locator(".delete-btn").nth(index).click()

    def set_filter(self, name: str) -> None:
        self.page.locator(f".filter-btn[data-filter='{name}']").click()

    def get_task_count_badge(self) -> int:
        return int(self.task_count.inner_text())

    def get_visible_tasks(self) -> list[str]:
        return self.task_list.locator(".task-text").all_inner_texts()

    def get_task_priority(self, index: int = 0) -> str:
        return self.task_list.locator(".priority-tag").nth(index).inner_text()

    def is_task_completed(self, index: int = 0) -> bool:
        cls = self.task_list.locator(".task-item").nth(index).get_attribute("class") or ""
        return "completed" in cls

    def is_empty_state_visible(self) -> bool:
        return self.empty_state.is_visible()

    def wait_for_toast(self, timeout: int = 3000) -> None:
        expect(self.toast).to_be_visible(timeout=timeout)

    def filter_btn(self, name: str):
        return self.page.locator(f".filter-btn[data-filter='{name}']")
