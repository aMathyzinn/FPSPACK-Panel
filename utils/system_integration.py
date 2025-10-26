#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integrações com o Windows para o FPSPACK PANEL.

Centraliza operações sensíveis ao sistema como:
- Registrar/desregistrar inicialização com o Windows;
- Requisitar elevação UAC quando necessário;
- Criar pontos de restauração;
- Gerar backups de configuração antes de otimizações/limpezas;
- Ajustar modo debug (nível de log e variáveis de ambiente).
"""

from __future__ import annotations

import ctypes
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from utils.config import get_appdata_root

if os.name == "nt":
    import winreg  # type: ignore
else:  # pragma: no cover - Non Windows fallback
    winreg = None  # type: ignore

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_STARTUP_VALUE = "FPSPACKPanel"


def is_windows() -> bool:
    """Retorna True se estiver em um ambiente Windows."""
    return os.name == "nt"


def is_admin() -> bool:
    """Verifica privilégios de administrador."""
    if not is_windows():
        return os.geteuid() == 0 if hasattr(os, "geteuid") else False

    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def get_launch_command() -> str:
    """
    Retorna o comando usado para iniciar o painel.
    Reaproveitamos o executável embutido quando disponível (PyInstaller).
    """
    if getattr(sys, "frozen", False):
        return str(Path(sys.executable).resolve())

    python_exe = Path(sys.executable).resolve()
    script = Path(sys.argv[0]).resolve()
    return f'"{python_exe}" "{script}"'


def configure_startup(enable: bool, app_name: str = APP_STARTUP_VALUE, command: Optional[str] = None) -> bool:
    """
    Habilita ou remove o registro para iniciar junto com o Windows.

    Args:
        enable: Define se o valor deve ser criado ou removido.
        app_name: Nome usado na chave de Run.
        command: Comando customizado; quando None usa o executável atual.
    """
    if not is_windows():
        return False

    if winreg is None:  # pragma: no cover - safety guard
        return False

    command = command or get_launch_command()

    try:
        access = winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, access) as key:
            if enable:
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, command)
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                except FileNotFoundError:
                    pass
        return True
    except PermissionError:
        return False
    except Exception:
        return False


def relaunch_as_admin(extra_args: Optional[list[str]] = None) -> bool:
    """
    Reexecuta o painel com privilégios administrativos via ShellExecute.
    Retorna True quando o pedido foi enviado (processo atual deve encerrar).
    """
    if not is_windows():
        return False

    try:
        params = " ".join(extra_args or sys.argv[1:])

        executable = Path(sys.executable).resolve()
        if not getattr(sys, "frozen", False):
            script = Path(sys.argv[0]).resolve()
            params = f'"{script}" {params}'.strip()

        ret = ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            str(executable),
            params,
            None,
            1,
        )
        return ret > 32
    except Exception:
        return False


def ensure_admin(require_admin: bool, logger=None) -> bool:
    """
    Garante execução com privilégios administrativos quando solicitado.

    Retorna:
        True se um pedido de elevação foi disparado (caller deve encerrar).
        False quando nenhuma ação adicional é necessária.
    """
    if not require_admin:
        return False

    if is_admin():
        if logger:
            logger.debug("Aplicação já está em modo administrador.")
        return False

    if logger:
        logger.info("Solicitando elevação UAC conforme configuração.")

    launched = relaunch_as_admin()

    if not launched and logger:
        logger.error("Não foi possível solicitar privilégios administrativos.")

    return launched


def create_restore_point(description: str) -> Tuple[bool, str]:
    """
    Cria um ponto de restauração do sistema usando PowerShell.

    Retorna (sucesso, mensagem).
    """
    if not is_windows() or winreg is None:
        return False, "Pontos de restauração são suportados apenas no Windows."

    if not is_admin():
        return False, "É necessário executar como administrador para criar pontos de restauração."

    sanitized = description.replace('"', "'")[:200]
    command = (
        "Checkpoint-Computer -Description \"{desc}\" -RestorePointType \"MODIFY_SETTINGS\""
    ).format(desc=sanitized)

    try:
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode == 0:
            return True, "Ponto de restauração criado com sucesso."

        stderr = result.stderr.strip() or result.stdout.strip()
        return False, stderr or "Falha ao criar ponto de restauração."

    except subprocess.TimeoutExpired:
        return False, "Timeout ao criar ponto de restauração."
    except FileNotFoundError:
        return False, "PowerShell não está disponível no sistema."
    except Exception as exc:
        return False, f"Erro inesperado ao criar ponto de restauração: {exc}"


def get_default_backup_dir() -> Path:
    """Retorna diretório padrão de backups no AppData."""
    base = get_appdata_root() / "backups"
    base.mkdir(parents=True, exist_ok=True)
    return base


def create_settings_backup(target_dir: Optional[str] = None) -> Tuple[bool, Optional[Path], str]:
    """
    Cria backup do arquivo de configuração principal (settings.json).

    Retorna (sucesso, caminho_backup, mensagem).
    """
    config_file = Path(__file__).resolve().parent.parent / "config" / "settings.json"
    if not config_file.exists():
        return False, None, "Arquivo de configuração não encontrado."

    try:
        target = Path(target_dir) if target_dir else get_default_backup_dir()
        target.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = target / f"settings_backup_{timestamp}.json"
        shutil.copy2(config_file, backup_file)

        return True, backup_file, "Backup de configuração criado."
    except Exception as exc:
        return False, None, f"Erro ao criar backup de configuração: {exc}"


def apply_debug_mode(enabled: bool, logger=None):
    """
    Ajusta nível de log e variáveis de ambiente para modo debug.
    """
    if enabled:
        os.environ["QT_LOGGING_RULES"] = "*.debug=true"
        if logger:
            logger.set_level("DEBUG")
            logger.info("Modo debug habilitado.")
    else:
        os.environ.pop("QT_LOGGING_RULES", None)
        if logger:
            logger.set_level("INFO")
            logger.info("Modo debug desabilitado.")
