# PlaywrightTest 🎭

A data-driven UI test automation framework built with **Playwright + pytest** (Python).  
All test inputs are managed through a single Excel file — no hardcoded test data in the code.

---

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Setup & Installation](#setup--installation)
- [Generating Test Data](#generating-test-data)
- [Running Tests](#running-tests)
- [Test Coverage](#test-coverage)
- [Key Design Patterns](#key-design-patterns)
- [Screenshots & Videos](#screenshots--videos)
- [Configuration](#configuration)

---

## Overview

PlaywrightTest automates browser-based testing of a task management web app (`app.html`) using a clean, layered architecture:

- **Excel-driven parametrization** — test cases, inputs, and expected results live in `test_data.xlsx`
- **Page Object Model (POM)** — browser interactions are abstracted into reusable page classes
- **Auto failure capture** — screenshots are saved automatically on any test failure
- **Run toggle** — every row in Excel has a `run` column (`Y`/`N`) to enable or disable test cases without deleting them

---

## Project Structure

```
playwritetest/
├── app.html                    # Web app under test (TaskFlow)
├── test_data.xlsx              # All test data (auto-generated)
├── generate_excel.py           # Script to create/regenerate test_data.xlsx
├── conftest.py                 # Shared pytest fixtures and failure hooks
├── pytest.ini                  # Pytest configuration
├── requirements.txt            # Python dependencies
│
├── pages/
│   └── task_page.py            # Page Object Models (LoginPage, TaskPage)
│
├── utils/
│   └── excel_reader.py         # Reads and parses test_data.xlsx into dataclasses
│
├── tests/
│   ├── test_login_excel.py     # Login test cases
│   └── test_tasks_excel.py     # Task, filter, UI, and delete test cases
│
└── screenshots/                # Failure screenshots (auto-created)
```

---

## Tech Stack

| Tool | Purpose |
|---|---|
| [Playwright for Python](https://playwright.dev/python/) | Browser automation |
| [pytest](https://pytest.org/) | Test runner and parametrization |
| [openpyxl](https://openpyxl.readthedocs.io/) | Excel file creation and styling |
| [pandas](https://pandas.pydata.org/) | Excel file parsing |

---

## Setup & Installation

**Prerequisites:** Python 3.8+, Node.js (optional, for Playwright CLI)

```bash
# 1. Clone the repository
git clone https://github.com/your-username/playwritetest.git
cd playwritetest

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install Playwright browsers
playwright install chromium
```

---

## Generating Test Data

Before running tests for the first time, generate the Excel test data file:

```bash
python generate_excel.py
```

This creates `test_data.xlsx` with 5 sheets pre-populated with sample test cases:

| Sheet | Contents |
|---|---|
| `LoginData` | Valid and invalid login credentials |
| `TaskData` | Task names and priorities to add |
| `FilterScenarios` | All / Active / Completed filter checks |
| `UIChecks` | Element visibility and text assertions |
| `DeleteScenarios` | Task deletion and count verification |

Each row has a `run` column. Set it to `Y` to enable a test case, `N` to skip it.

---

## Running Tests

```bash
# Run all tests
pytest

# Run only login tests
pytest tests/test_login_excel.py

# Run only task tests
pytest tests/test_tasks_excel.py

# Run headless (no browser window)
pytest --headed=false

# Run against a different URL
pytest --app-url="http://localhost:3000/app.html"
```

---

## Test Coverage

### Login Tests (`test_login_excel.py`)

- Valid credentials → overlay disappears, dashboard loads
- Invalid credentials → overlay stays visible, error message shown

### Task Tests (`test_tasks_excel.py`)

- Add tasks with different priorities (Low / Medium / High)
- Mark tasks as completed
- Add multiple tasks sequentially and verify count badge

### Filter Tests

- All / Active / Completed filter buttons show correct task subsets

### UI Checks

- Page title, element visibility, and expected text content

### Delete Tests

- Delete a task and verify the count updates
- Delete last task and verify the empty state is shown

---

## Key Design Patterns

### Page Object Model

Browser interactions are isolated in `pages/task_page.py`. Tests never use raw CSS selectors — they call descriptive methods like `task_page.add_task("Buy milk", "High")` or `task_page.set_filter("completed")`.

### Excel-Driven Parametrization

Tests are parametrized at collection time from Excel rows. Every enabled (`run=Y`) row becomes a separate named test case visible in pytest output.

### Singleton Excel Reader

`utils/excel_reader.py` uses `@lru_cache` to ensure the Excel file is read only once per session, regardless of how many test files import it.

### Auto Screenshot on Failure

`conftest.py` installs a `pytest_runtest_makereport` hook that captures a full-page screenshot whenever a test fails and saves it to `screenshots/FAIL_<testname>.png`.

---

## Screenshots & Videos

- **Screenshots** — saved to `screenshots/` on test failure
- **Videos** — retained in the pytest Playwright output folder on failure (configured via `pytest.ini`)

---

## Configuration

All Playwright and pytest options are set in `pytest.ini`:

```ini
addopts =
    --browser chromium
    --headed
    --slowmo 300
    --screenshot only-on-failure
    --video retain-on-failure
    -v -s
testpaths = tests
```

| Option | Description |
|---|---|
| `--headed` | Run with visible browser window |
| `--slowmo 300` | 300ms delay between actions (useful for demos) |
| `--screenshot only-on-failure` | Capture screenshot on test failure |
| `--video retain-on-failure` | Keep video recording only when test fails |

To run in CI/CD (headless, faster), override with:

```bash
pytest --headed=false --slowmo=0
```

---

## License

MIT
