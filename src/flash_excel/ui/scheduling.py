"""Build shared execution settings for Windows tasks and manual launchers."""

from __future__ import annotations

import getpass
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from subprocess import list2cmdline

from flash_excel.paths import DEFAULT_OUTPUT_DIR, PROJECT_ROOT


def build_schedule_command(
    preset_path: str,
    file_paths: list[str],
    output_config: dict,
    task_name: str | None = None,
    start_time: str = "08:00",
) -> dict:
    """Build a daily task and a manual launcher from the same execution settings."""
    if not preset_path or not file_paths:
        raise ValueError("Select a preset and at least one input file")
    task_name = (
        task_name.strip()
        if task_name is not None
        else f"flash-excel {Path(preset_path).stem}"
    )
    if (
        not task_name
        or len(task_name) > 200
        or any(char in task_name for char in '\\/:*?"<>|%!')
        or any(ord(char) < 32 for char in task_name)
        or task_name.endswith((".", " "))
    ):
        raise ValueError(
            "Enter a name of 1–200 characters without reserved filename characters"
        )
    if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", start_time):
        raise ValueError("Start time must use HH:mm (00:00–23:59)")
    output_format = output_config.get("format", "keep")
    if output_format not in {"keep", "csv", "xlsx", "parquet"}:
        raise ValueError("Unsupported output format")
    folder = Path(output_config.get("folder") or DEFAULT_OUTPUT_DIR)
    if not folder.is_absolute():
        folder = DEFAULT_OUTPUT_DIR / folder
    development = not getattr(sys, "frozen", False)
    args = [sys.executable]
    if development:
        args.append(str(PROJECT_ROOT / "main.py"))
    args.extend(
        [
            "--preset",
            str(Path(preset_path).resolve()),
            "--input",
            *[str(Path(path).resolve()) for path in file_paths],
            "--output",
            str(folder),
            "--format",
            output_format,
            "--pattern",
            output_config.get("pattern") or "{name}_clean",
        ]
    )
    # Percent expansion and delayed expansion can alter even quoted arguments.
    if any(any(char in arg for char in '%!"\r\n') for arg in args):
        raise ValueError("Scheduling commands cannot contain %, !, quotes or newlines")
    action = list2cmdline(args)
    task_path = f"\\Flash-Excel\\{task_name}"
    task_args = [
        "schtasks",
        "/create",
        "/tn",
        task_path,
        "/tr",
        action,
        "/sc",
        "DAILY",
        "/st",
        start_time,
        "/IT",
    ]
    launcher = (
        "@echo off\r\nsetlocal DisableDelayedExpansion\r\nchcp 65001 >nul\r\n"
        + _escape_cmd(action)
        + '\r\nset "flash_excel_exit=%ERRORLEVEL%"\r\npause\r\nexit /b %flash_excel_exit%\r\n'
    )
    return {
        "command": _escape_cmd(list2cmdline(task_args)),
        "executable": sys.executable,
        "development": development,
        "task_name": task_name,
        "task_path": task_path,
        "start_time": start_time,
        "task_args": task_args,
        "execution_args": args,
        "command_too_long": len(action) > 261,
        "launcher": launcher,
    }


def build_task_xml(execution: dict) -> bytes:
    """Serialize the task action without schtasks /tr's 261-character limit."""
    task = ET.Element(
        "Task",
        {
            "version": "1.2",
            "xmlns": "http://schemas.microsoft.com/windows/2004/02/mit/task",
        },
    )
    triggers = ET.SubElement(task, "Triggers")
    daily = ET.SubElement(triggers, "CalendarTrigger")
    today = datetime.now().date().isoformat()
    ET.SubElement(daily, "StartBoundary").text = f"{today}T{execution['start_time']}:00"
    ET.SubElement(daily, "Enabled").text = "true"
    ET.SubElement(ET.SubElement(daily, "ScheduleByDay"), "DaysInterval").text = "1"
    principal = ET.SubElement(
        ET.SubElement(task, "Principals"), "Principal", {"id": "Author"}
    )
    user = getpass.getuser()
    domain = os.environ.get("USERDOMAIN")
    if domain and "\\" not in user:
        user = f"{domain}\\{user}"
    ET.SubElement(principal, "UserId").text = user
    ET.SubElement(principal, "LogonType").text = "InteractiveToken"
    ET.SubElement(principal, "RunLevel").text = "LeastPrivilege"
    settings = ET.SubElement(task, "Settings")
    ET.SubElement(settings, "MultipleInstancesPolicy").text = "IgnoreNew"
    ET.SubElement(settings, "DisallowStartIfOnBatteries").text = "false"
    ET.SubElement(settings, "StopIfGoingOnBatteries").text = "false"
    action = ET.SubElement(
        ET.SubElement(task, "Actions", {"Context": "Author"}), "Exec"
    )
    args = execution["execution_args"]
    ET.SubElement(action, "Command").text = args[0]
    ET.SubElement(action, "Arguments").text = list2cmdline(args[1:])
    return ET.tostring(task, encoding="utf-16", xml_declaration=True)


def _escape_cmd(command: str) -> str:
    """Protect shell operators while preserving Windows argument quoting."""
    # cmd.exe treats quotes independently of the backslash escaping used by
    # Windows argv parsers, so protect shell operators outside its quotes.
    escaped = []
    quoted = False
    for char in command:
        if char == '"':
            quoted = not quoted
        elif not quoted and char in "^&|<>":
            escaped.append("^")
        escaped.append(char)
    return "".join(escaped)
