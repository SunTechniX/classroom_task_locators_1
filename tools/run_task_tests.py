#!/usr/bin/env python3
import json
import sys
import os
import base64
from importlib.util import spec_from_file_location, module_from_spec

# Импортируем playwright только при необходимости
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("❌ Playwright не установлен. Выполните: pip install playwright && playwright install")
    sys.exit(1)

def validate_task_01(locator):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://demoqa.com/text-box", timeout=10000)
        el = page.locator(locator)
        assert el.count() == 1, "Локатор должен находить ровно один элемент"
        el.fill("Test User")
        assert el.input_value() == "Test User"
        browser.close()
    return True

def validate_task_02(locator):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://demoqa.com/text-box", timeout=10000)
        el = page.locator(locator)
        assert el.count() == 1
        el.click()
        assert page.locator(".output").is_visible(), "Блок .output не появился после клика"
        browser.close()
    return True

def validate_task_03(locator):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://www.urn.su/ui/basic_test/#intro", timeout=10000)
        el = page.locator(locator)
        assert el.count() == 1
        with page.expect_navigation():
            el.click()
        assert "8 марта в Италии в 2026 году" in page.title()
        browser.close()
    return True

def validate_task_04(locator):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://www.urn.su/ui/basic_test/#intro", timeout=10000)
        el = page.locator(locator)
        assert el.count() == 1
        el.check()
        assert el.is_checked()
        browser.close()
    return True

def validate_task_05(locator):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://users.bugred.ru/user/login/index", timeout=10000)
        el = page.locator(locator)
        assert el.count() == 1
        el.fill("student@example.com")
        assert el.input_value() == "student@example.com"
        browser.close()
    return True

VALIDATORS = {
    "task_01": ("FULL_NAME_INPUT", validate_task_01),
    "task_02": ("SUBMIT_BUTTON", validate_task_02),
    "task_03": ("MIDDLE_ITALY_LINK", validate_task_03),
    "task_04": ("CERSEI_CHECKBOX", validate_task_04),
    "task_05": ("LOGIN_FIELD", validate_task_05),
}

def main():
    if len(sys.argv) != 2:
        print("Usage: run_task_tests.py <task_id>")
        sys.exit(1)

    task_id = sys.argv[1]
    config_path = ".github/tasks.json"
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    task = next((t for t in config["tasks"] if t["id"] == task_id), None)
    if not task:
        print(f"Task {task_id} not found")
        sys.exit(1)

    file_path = task["file"]
    max_score = task["max_score"]

    if not os.path.exists(file_path):
        result = {"score": 0, "max_score": max_score, "tests": [{"name": "Файл отсутствует", "status": "fail", "score": 0, "max_score": max_score, "output": "Файл не найден"}]}
        print(f"::set-output name=result::{base64.b64encode(json.dumps(result, ensure_ascii=False).encode()).decode()}")
        return

    # Проверка синтаксиса
    try:
        spec = spec_from_file_location(task_id, file_path)
        mod = module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception as e:
        result = {"score": 0, "max_score": max_score, "tests": [{"name": "Синтаксическая ошибка", "status": "fail", "score": 0, "max_score": max_score, "output": str(e)}]}
        print(f"::set-output name=result::{base64.b64encode(json.dumps(result, ensure_ascii=False).encode()).decode()}")
        return

    var_name, validator = VALIDATORS[task_id]
    try:
        locator = getattr(mod, var_name)
        validator(locator)
        test_result = {"name": f"Проверка {var_name}", "status": "pass", "score": max_score, "max_score": max_score, "output": "OK"}
        total_score = max_score
    except Exception as e:
        test_result = {"name": f"Проверка {var_name}", "status": "fail", "score": 0, "max_score": max_score, "output": str(e)}
        total_score = 0

    result = {"score": total_score, "max_score": max_score, "tests": [test_result]}
    encoded = base64.b64encode(json.dumps(result, ensure_ascii=False).encode("utf-8")).decode("utf-8")
    print(f"::set-output name=result::{encoded}")

if __name__ == "__main__":
    main()