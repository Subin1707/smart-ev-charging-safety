"""Shared execution primitives for generated verification artifacts."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence


def resolve_tool(name: str) -> str | None:
    installed = shutil.which(name)
    if installed:
        return installed
    if name == "cbmc":
        bundled = Path(__file__).resolve().parents[2] / "tools/cbmc/extracted/cbmc/bin/cbmc.exe"
        if sys.platform == "win32" and bundled.is_file():
            return str(bundled)
    return None


def tool_available(name: str) -> bool:
    return resolve_tool(name) is not None


def run_command(command: Sequence[str], cwd: str | Path | None = None, timeout: int = 30) -> dict[str, Any]:
    command = list(command)
    try:
        process = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        return {"status": "UNAVAILABLE", "return_code": None, "stdout": "", "stderr": f"Tool not found: {command[0]}"}
    except subprocess.TimeoutExpired as error:
        output = error.stdout or ""
        return {"command": command, "status": "TIMEOUT", "return_code": None, "stdout": output.decode(errors="replace") if isinstance(output, bytes) else output, "stderr": "Execution timeout"}
    except OSError as error:
        return {"status": "EXECUTION_ERROR", "return_code": None, "stdout": "", "stderr": str(error)}
    return {
        "command": command,
        "status": "PASS" if process.returncode == 0 else "FAIL",
        "return_code": process.returncode,
        "stdout": process.stdout,
        "stderr": process.stderr,
    }


def run_gcc_syntax(source_files: Sequence[str | Path], cwd: str | Path | None = None) -> dict[str, Any]:
    if not tool_available("gcc"):
        return {"tool": "gcc", "status": "UNAVAILABLE"}
    result = run_command(["gcc", "-std=c17", "-fsyntax-only", "-D__CPROVER_assume(x)=((void)0)", *map(str, source_files)], cwd)
    result["tool"] = "gcc"
    result["status"] = "PASS" if result["status"] == "PASS" else "BUILD_ERROR"
    return result


def run_cppcheck(source_files: Sequence[str | Path], cwd: str | Path | None = None) -> dict[str, Any]:
    if not tool_available("cppcheck"):
        return {"tool": "cppcheck", "status": "UNAVAILABLE"}
    result = run_command([shutil.which("cppcheck") or "cppcheck", "--enable=warning,style,performance,portability", "--error-exitcode=1", *map(str, source_files)], cwd)
    result["tool"] = "cppcheck"
    return result


def run_cbmc(source_files: Sequence[str | Path], cwd: str | Path | None = None, timeout: int = 60,
             include_dirs: Sequence[str | Path] = (), unwind: int | None = None) -> dict[str, Any]:
    if not tool_available("cbmc"):
        return {"tool": "cbmc", "status": "UNAVAILABLE"}
    includes = [arg for directory in include_dirs for arg in ("-I", str(directory))]
    inputs = list(map(str, source_files))
    preprocessing = []
    if sys.platform == "win32":
        # GCC must see its own MinGW platform macros before CBMC parses the C.
        directory = Path(cwd or Path.cwd()) / "generated/preprocessed" / Path(inputs[0]).stem
        directory.mkdir(parents=True, exist_ok=True)
        inputs = []
        for index, source in enumerate(source_files):
            output = directory / f"{index}_{Path(source).stem}.i"
            step = run_command(["gcc", "-E", "-D__CPROVER__", *includes, str(source), "-o", str(output)], cwd)
            preprocessing.append(step)
            if step["status"] != "PASS":
                return {**step, "tool": "cbmc", "status": "BUILD_ERROR", "preprocessing": preprocessing}
            inputs.append(str(output))
    bounds = ["--unwind", str(unwind), "--unwinding-assertions"] if unwind else []
    result = run_command([resolve_tool("cbmc"), "--gcc", *includes, *inputs, "--drop-unused-functions", "--bounds-check", "--pointer-check", "--signed-overflow-check", *bounds, "--trace"], cwd, timeout)
    result["preprocessing"] = preprocessing
    if result.get("return_code") not in (None, 0, 10):
        result["status"] = "BUILD_ERROR"
    result["tool"] = "cbmc"
    return result


def run_z3(script: str | Path, cwd: str | Path | None = None) -> dict[str, Any]:
    result = run_command([sys.executable, str(script)], cwd)
    output = (result.get("stdout", "") + result.get("stderr", "")).lower()
    if result["status"] == "PASS" and "sat" in output and "unsat" not in output:
        result["status"] = "FAIL"
        result["counterexample"] = result.get("stdout", "")
    elif result["status"] == "PASS" and "unsat" in output:
        result["status"] = "PASS"
    result["tool"] = "z3"
    return result


def run_pytest(test_files: Sequence[str | Path], cwd: str | Path | None = None, basetemp: str | Path | None = None) -> dict[str, Any]:
    command = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *map(str, test_files)]
    if basetemp:
        command.extend(["--basetemp", str(basetemp)])
    result = run_command(command, cwd)
    result["tool"] = "pytest"
    return result


def build_sanitizer(source_files: Sequence[str | Path], output: str | Path, sanitizer: str, cwd: str | Path | None = None) -> dict[str, Any]:
    if not tool_available("gcc"):
        return {"tool": sanitizer, "status": "UNAVAILABLE"}
    result = run_command(["gcc", "-g", f"-fsanitize={sanitizer}", *map(str, source_files), "-o", str(output)], cwd)
    result["tool"] = sanitizer
    result["status"] = "PASS" if result["status"] == "PASS" else "BUILD_ERROR"
    return result


def run_sanitizer(binary: str | Path, sanitizer: str, cwd: str | Path | None = None) -> dict[str, Any]:
    result = run_command([str(binary)], cwd)
    output = result.get("stdout", "") + result.get("stderr", "")
    result["tool"] = sanitizer
    if sanitizer == "asan" and "AddressSanitizer" in output:
        result["status"] = "FAIL"
        result["counterexample"] = output
    if sanitizer == "ubsan" and "runtime error:" in output:
        result["status"] = "FAIL"
        result["counterexample"] = output
    return result


def run_fuzz(binary: str | Path, max_time_seconds: int = 10, cwd: str | Path | None = None) -> dict[str, Any]:
    result = run_command([str(binary), f"-max_total_time={max_time_seconds}"], cwd, max_time_seconds + 5)
    result["tool"] = "fuzz"
    return result
