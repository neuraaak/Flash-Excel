import base64
import ctypes
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from shutil import which
from types import SimpleNamespace

import pytest

from flash_excel.paths import DEFAULT_OUTPUT_DIR
from flash_excel.ui.api import FlashExcelAPI
from flash_excel.ui.scheduling import build_schedule_command, build_task_xml


def _split_windows_command(command):
    shell = ctypes.windll.shell32
    shell.CommandLineToArgvW.argtypes = [ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_int)]
    shell.CommandLineToArgvW.restype = ctypes.POINTER(ctypes.c_wchar_p)
    count = ctypes.c_int()
    argv = shell.CommandLineToArgvW(command, ctypes.byref(count))
    try:
        return [argv[index] for index in range(count.value)]
    finally:
        ctypes.windll.kernel32.LocalFree(ctypes.cast(argv, ctypes.c_void_p))


@pytest.mark.skipif(sys.platform != "win32", reason="Exercises Windows cmd quoting")
@pytest.mark.parametrize("frozen", [False, True])
def test_command_survives_cmd_and_nested_windows_quoting(monkeypatch, tmp_path, frozen):
    interpreter = sys.executable
    monkeypatch.setattr(sys, "frozen", frozen, raising=False)
    monkeypatch.setattr(
        sys, "executable", r"C:\Program Files\Flash Excel\flash-excel.exe"
    )
    project = tmp_path / "Project with spaces"
    monkeypatch.setattr("flash_excel.ui.scheduling.PROJECT_ROOT", project)
    preset = r"C:\Team presets\Finance & sales.toml"
    files = [r"C:\Input folder\report 1.xlsx", r"\\server\shared team\report 2.csv"]
    output = {
        "folder": "C:\\Output folder\\",
        "format": "csv",
        "pattern": "{name} & clean^copy",
    }

    result = build_schedule_command(preset, files, output)

    # Replace schtasks with an argv recorder: exercise the actual cmd parser
    # without registering any task or launching the generated action.
    recorder = tmp_path / "record argv.py"
    recorder.write_text(
        "import json, sys; print(json.dumps(sys.argv[1:]))", encoding="utf-8"
    )
    harmless = (
        subprocess.list2cmdline([interpreter, str(recorder)])
        + result["command"][len("schtasks") :]
    )
    comspec = os.environ.get("COMSPEC", "cmd.exe")
    completed = subprocess.run(
        f'"{comspec}" /d /v:off /s /c "{harmless}"',
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    arguments = json.loads(completed.stdout)
    assert arguments[:3] == [
        "/create",
        "/tn",
        r"\Flash-Excel\flash-excel Finance & sales",
    ]
    assert arguments[-5:] == ["/sc", "DAILY", "/st", "08:00", "/IT"]
    action = _split_windows_command(arguments[arguments.index("/tr") + 1])
    expected = [sys.executable]
    if not frozen:
        expected.append(str(project / "main.py"))
    expected.extend(
        [
            "--preset",
            preset,
            "--input",
            *files,
            "--output",
            str(Path(output["folder"])),
            "--format",
            "csv",
            "--pattern",
            output["pattern"],
        ]
    )
    assert action == expected
    assert result["development"] is not frozen
    assert result["executable"] == sys.executable
    assert "/f" not in arguments


def test_command_anchors_default_and_relative_output(monkeypatch):
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", r"C:\FlashExcel\app.exe")
    for folder in ("", "reports"):
        result = build_schedule_command(
            "preset.toml", ["input.csv"], {"folder": folder}
        )
        expected = DEFAULT_OUTPUT_DIR / folder
        # list2cmdline escapes the folder inside the nested /tr argument.
        assert str(expected).replace('"', '\\"') in result["command"]


@pytest.mark.parametrize(
    "preset,files,output",
    [
        ("", ["input.csv"], {}),
        ("preset.toml", [], {}),
        ("preset.toml", ["input.csv"], {"format": "unknown"}),
        ("preset.toml", ["C:/%USERPROFILE%/input.csv"], {}),
        ("preset.toml", ["input.csv"], {"pattern": "bad!name"}),
        ("preset.toml", ["input.csv"], {"pattern": 'bad"name'}),
        ("preset.toml", ["input.csv"], {"pattern": "bad\nname"}),
    ],
)
def test_schedule_returns_bridge_errors(preset, files, output):
    result = FlashExcelAPI().get_schedule_command(preset, files, output)
    assert result["ok"] is False
    assert result["error"]


def test_schedule_bridge_returns_command_without_starting_a_task(monkeypatch):
    calls = []
    monkeypatch.setattr("subprocess.Popen", lambda *args, **_kwargs: calls.append(args))

    result = FlashExcelAPI().get_schedule_command("preset.toml", ["input.csv"], {})

    assert result["ok"] is True
    assert result["data"]["command"].startswith("schtasks /create")
    assert calls == []


def test_task_requires_confirmation_before_starting_any_process(monkeypatch):
    calls = []
    monkeypatch.setattr(
        "subprocess.run", lambda *args, **kwargs: calls.append((args, kwargs))
    )

    result = FlashExcelAPI().create_scheduled_task(
        "preset.toml", ["input.csv"], {}, "Test", "09:30"
    )

    assert result["ok"] is False
    assert "confirmation" in result["error"]
    assert calls == []


@pytest.mark.skipif(sys.platform != "win32", reason="Windows task creation")
@pytest.mark.parametrize("returncode", [0, 1])
def test_task_imports_xml_and_reports_windows_errors(monkeypatch, returncode):
    calls = []

    def run(args, **kwargs):
        xml_path = Path(args[args.index("/xml") + 1])
        task = ET.fromstring(xml_path.read_bytes())  # noqa: S314 - Application-generated XML.
        ns = {"t": "http://schemas.microsoft.com/windows/2004/02/mit/task"}
        assert (
            task.findtext("t:Actions/t:Exec/t:Command", namespaces=ns) == sys.executable
        )
        assert task.findtext(
            "t:Triggers/t:CalendarTrigger/t:StartBoundary", namespaces=ns
        ).endswith("T09:30:00")
        assert (
            task.findtext("t:Principals/t:Principal/t:LogonType", namespaces=ns)
            == "InteractiveToken"
        )
        calls.append((args, kwargs))
        return SimpleNamespace(
            returncode=returncode,
            stdout="",
            stderr="Access denied" if returncode else "",
        )

    monkeypatch.setattr("subprocess.run", run)

    result = FlashExcelAPI().create_scheduled_task(
        "preset.toml", ["input.csv"], {}, "My task", "09:30", True
    )

    args, options = calls[0]
    assert Path(args[0]).name.lower() == "schtasks.exe"
    assert args[1:4] == ["/create", "/tn", r"\Flash-Excel\My task"]
    assert "/tr" not in args
    assert not Path(args[args.index("/xml") + 1]).exists()
    assert "/F" not in [arg.upper() for arg in args]
    assert not options.get("shell")
    assert options["stdin"] == subprocess.DEVNULL
    assert options["creationflags"] == subprocess.CREATE_NO_WINDOW
    if returncode:
        assert result == {"ok": False, "error": "Access denied"}
    else:
        assert result["data"] == {"task_name": "My task", "start_time": "09:30"}


@pytest.mark.skipif(sys.platform != "win32", reason="Windows task creation")
def test_long_task_action_is_imported_without_the_tr_length_limit(monkeypatch):
    files = [
        f"C:/Team reports/{'Monthly exports ' * 8}/source {n}.xlsx" for n in range(3)
    ]
    captured = []

    def run(args, **_kwargs):
        ns = {"t": "http://schemas.microsoft.com/windows/2004/02/mit/task"}
        root = ET.fromstring(Path(args[args.index("/xml") + 1]).read_bytes())  # noqa: S314 - Application-generated XML.
        arguments = root.findtext("t:Actions/t:Exec/t:Arguments", namespaces=ns)
        assert len(arguments) > 261
        parsed = _split_windows_command("program.exe " + arguments)[1:]
        for path in files:
            assert str(Path(path).resolve()) in parsed
        assert parsed[-2:] == ["--pattern", "{name} & export"]
        captured.append(args)
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr("subprocess.run", run)

    result = FlashExcelAPI().create_scheduled_task(
        "preset.toml", files, {"pattern": "{name} & export"}, "Long task", "11:25", True
    )

    assert result["ok"] is True
    assert len(captured) == 1
    assert "/tr" not in captured[0]


@pytest.mark.skipif(
    sys.platform != "win32", reason="Validates a Windows task definition"
)
def test_long_xml_is_accepted_by_windows_task_definition():
    execution = build_schedule_command(
        "preset.toml",
        [f"C:/Reports/{'Monthly exports ' * 10}/file.xlsx"],
        {},
        "Long task",
        "09:30",
    )
    xml = build_task_xml(execution).decode("utf-16").replace("'", "''")
    # NewTask creates an in-memory definition; never register it with Windows.
    script = (
        "$ErrorActionPreference='Stop';"
        "$service=New-Object -ComObject Schedule.Service; $service.Connect();"
        "$task=$service.NewTask(0);"
        f"$task.XmlText='{xml}';"
        "Write-Output $task.Actions.Item(1).Arguments.Length"
    )
    encoded = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
    powershell = which("powershell.exe")
    assert powershell is not None
    result = subprocess.run(
        [powershell, "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded],
        capture_output=True,
        text=True,
        errors="replace",
        check=False,
        timeout=20,
    )
    assert result.returncode == 0, result.stderr
    assert int(result.stdout.strip()) > 261


@pytest.mark.parametrize(
    "name,time",
    [("../Other", "08:00"), ("Test", "25:00"), ("", "08:00"), ("Test", "8:00")],
)
def test_invalid_task_settings_never_start_a_process(monkeypatch, name, time):
    calls = []
    monkeypatch.setattr(
        "subprocess.run", lambda *args, **kwargs: calls.append((args, kwargs))
    )
    result = FlashExcelAPI().create_scheduled_task(
        "preset.toml", ["input.csv"], {}, name, time, True
    )
    assert result["ok"] is False
    assert not calls


def test_launcher_save_dialog_writes_wrapper_without_running_it(monkeypatch, tmp_path):
    dest = tmp_path / "Manual run.cmd"
    dialog = []

    def save_dialog(*args, **kwargs):
        dialog.append((args, kwargs))
        return [str(dest)]

    monkeypatch.setattr(
        "flash_excel.ui.api.webview.active_window",
        lambda: SimpleNamespace(create_file_dialog=save_dialog),
    )
    calls = []
    monkeypatch.setattr(
        "subprocess.Popen", lambda *args, **kwargs: calls.append((args, kwargs))
    )

    result = FlashExcelAPI().create_execution_launcher(
        "preset.toml", ["input.csv"], {}, "Manual run"
    )

    assert result == {"ok": True, "data": {"dest": str(dest)}}
    assert b"--preset" in dest.read_bytes()
    assert b"pause\r\n" in dest.read_bytes()
    assert dialog[0][1]["save_filename"] == "Manual run.cmd"
    assert not calls


def test_launcher_cancel_does_not_write_files(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "flash_excel.ui.api.webview.active_window",
        lambda: SimpleNamespace(create_file_dialog=lambda *_args, **_kwargs: None),
    )
    result = FlashExcelAPI().create_execution_launcher(
        "preset.toml", ["input.csv"], {}, "Manual run"
    )
    assert result == {"ok": True, "data": {"cancelled": True}}
    assert not list(tmp_path.iterdir())


@pytest.mark.skipif(sys.platform != "win32", reason="Executes a Windows batch launcher")
def test_launcher_preserves_arguments_and_exit_code(monkeypatch, tmp_path):
    project = tmp_path / "équipe & project"
    project.mkdir()
    recorder = project / "main.py"
    recorder.write_text(
        "import json, sys\nfrom pathlib import Path\n"
        "Path(__file__).with_suffix('.json').write_text(json.dumps(sys.argv[1:]))\n"
        "raise SystemExit(7)\n",
        encoding="utf-8",
    )
    monkeypatch.setattr("flash_excel.ui.scheduling.PROJECT_ROOT", project)
    monkeypatch.setattr(sys, "frozen", False, raising=False)
    preset = tmp_path / "Finance & sales.toml"
    files = [str(tmp_path / "report 1.csv"), str(tmp_path / "report 2.csv")]
    execution = build_schedule_command(
        str(preset), files, {"pattern": "{name} & copy^tail"}, "Manual test", "10:45"
    )
    launcher = tmp_path / "Manual test.cmd"
    launcher.write_bytes(execution["launcher"].encode("utf-8"))
    comspec = os.environ.get("COMSPEC", "cmd.exe")

    result = subprocess.run(
        f'"{comspec}" /d /s /c ""{launcher}""',
        input="",
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        timeout=15,
    )

    assert result.returncode == 7, result.stderr
    arguments = json.loads(recorder.with_suffix(".json").read_text())
    assert arguments[:5] == ["--preset", str(preset), "--input", *files]
    assert arguments[-2:] == ["--pattern", "{name} & copy^tail"]
