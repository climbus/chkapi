from rest_checker.app import RestChecker
from rich.console import Console
from io import StringIO
import pytest
import asyncio
import pyautogui


def create_app():
    console = Console(file=StringIO())
    app = RestChecker(console=console)
    return app, console


async def press_ctrl_c():
    pyautogui.hotkey("ctrl", "c")


async def press(key):
    pyautogui.press(key)


@pytest.mark.asyncio
async def test_app_quits_on_ctr_c():
    app, _ = create_app()

    await asyncio.gather(app.process_messages(), press_ctrl_c())
    assert True


@pytest.mark.asyncio
async def test_app_quits_on_q():
    app, _ = create_app()

    await asyncio.gather(app.process_messages(), press("q"))
    assert True
