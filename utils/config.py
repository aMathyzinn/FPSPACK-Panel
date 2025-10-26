#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Configuração do FPSPACK PANEL
Gerenciamento de configurações e preferências
"""

import os
import json
import shutil
from pathlib import Path
from typing import Any, Dict, Optional
from utils.logger import Logger

APP_FOLDER_NAME = "FPSPACK_PANEL"


def get_appdata_root() -> Path:
    """Retorna o diretório base de dados do usuário para o FPSPACK."""
    if os.name == "nt":
        base = os.environ.get("APPDATA")
        if base:
            return Path(base) / APP_FOLDER_NAME
        return Path.home() / "AppData" / "Roaming" / APP_FOLDER_NAME
    return Path.home() / f".{APP_FOLDER_NAME.lower()}"


APPDATA_ROOT = get_appdata_root()
APPDATA_CONFIG_DIR = APPDATA_ROOT / "config"
DEFAULT_BACKUP_PATH = str(APPDATA_ROOT / "backups")

class Config:
    """Sistema de configuração"""
    
    _instance = None
    _config_data = None
    _config_file = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_config()
        return cls._instance
    
    def _initialize_config(self):
        """Inicializa o sistema de configuração"""
        if self._config_data is not None:
            return
            
        self.logger = Logger()
        
        # Diretório de configuração
        config_dir = APPDATA_CONFIG_DIR
        config_dir.mkdir(parents=True, exist_ok=True)
        self._config_dir = config_dir
        self._config_file = config_dir / "settings.json"

        legacy_file = Path(__file__).parent.parent / "config" / "settings.json"
        if legacy_file.exists() and not self._config_file.exists():
            try:
                shutil.copy2(legacy_file, self._config_file)
                self.logger.info(f"Configuração migrada de {legacy_file} para {self._config_file}")
            except Exception as exc:
                self.logger.warning(f"Falha ao migrar configuração antiga: {exc}")
        
        # Carrega configurações
        self._load_config()
        
        self.logger.info("Sistema de configuração inicializado")
    
    def _load_config(self):
        """Carrega configurações do arquivo"""
        try:
            if self._config_file.exists():
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    self._config_data = json.load(f)
                self.logger.info(f"Configurações carregadas de: {self._config_file}")
            else:
                self._config_data = self._get_default_config()
                self._save_config()
                self.logger.info("Configurações padrão criadas")
                
        except Exception as e:
            self.logger.error(f"Erro ao carregar configurações: {e}")
            self._config_data = self._get_default_config()
    
    def _save_config(self):
        """Salva configurações no arquivo"""
        try:
            self._config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config_data, f, indent=4, ensure_ascii=False)
            self.logger.debug("Configurações salvas")
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar configurações: {e}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Retorna configurações padrão"""
        return {
            "version": "1.0.0",
            "app": {
                "theme": "dark",
                "language": "pt-BR",
                "auto_start": False,
                "minimize_to_tray": True,
                "check_updates": True,
                "show_notifications": True,
                "animation_speed": "normal",
                "transparency": 0.95
            },
            "monitoring": {
                "update_interval": 1000,
                "history_points": 60,
                "show_graphs": True,
                "monitor_temperature": True,
                "monitor_network": True,
                "monitor_processes": True
            },
            "optimization": {
                "auto_ram_cleanup": False,
                "ram_cleanup_interval": 300,
                "ram_threshold": 80,
                "auto_optimize_startup": False,
                "auto_optimize_services": False,
                "backup_services": True,
                "advanced_options": {
                    "aggressive_ram": True,
                    "disable_services": True,
                    "adjust_mtu": False,
                    "tcp_optimization": True,
                    "process_priority": False,
                    "system_cache": True,
                    "visual_effects": False
                },
                "create_restore_point": True,
                "backup_registry": True,
                "safe_mode": True,
                "turbo_mode_timeout": 3600
            },
            "cleanup": {
                "auto_cleanup": False,
                "cleanup_schedule": "daily",
                "cleanup_temp_files": True,
                "cleanup_browser_cache": True,
                "cleanup_system_cache": True,
                "cleanup_logs": True,
                "cleanup_registry": False,
                "empty_recycle_bin": False,
                "days_to_keep_logs": 7,
                "create_backups": True,
                "backup_registry": True,
                "backup_path": DEFAULT_BACKUP_PATH
            },
            "network": {
                "optimize_tcp": True,
                "optimize_dns": True,
                "use_custom_dns": False,
                "primary_dns": "1.1.1.1",
                "secondary_dns": "1.0.0.1",
                "disable_nagle": True,
                "enable_rss": True
            },
            "gaming": {
                "game_mode_enabled": False,
                "auto_detect_games": True,
                "boost_priority": True,
                "disable_windows_game_mode": False,
                "optimize_gpu": True,
                "reduce_input_lag": True
            },
            "power": {
                "create_custom_plan": True,
                "plan_name": "aMathyzin Performance Mode",
                "cpu_min_state": 100,
                "cpu_max_state": 100,
                "disable_sleep": True,
                "disable_hibernation": True,
                "usb_selective_suspend": False
            },
            "security": {
                "create_backups": True,
                "backup_location": "",
                "encrypt_backups": False,
                "verify_signatures": True,
                "safe_mode_only": False
            },
            "advanced": {
                "require_admin": False,
                "create_restore_points": True,
                "verify_signatures": True,
                "debug_mode": False,
                "log_level": "INFO",
                "verbose_logging": False,
                "performance_monitoring": False,
                "worker_threads": 4,
                "memory_cache_mb": 256,
                "enable_telemetry": False,
                "experimental_features": False,
                "developer_mode": False,
                "custom_scripts": False
            },
            "ui": {
                "window_width": 1400,
                "window_height": 900,
                "window_maximized": False,
                "sidebar_width": 250,
                "show_tooltips": True,
                "compact_mode": False,
                "show_system_info": True,
                "graph_style": "line",
                "color_scheme": "blue",
                "theme": "Dark",
                "accent_color": "Azul",
                "animations": True,
                "smooth_scrolling": True,
                "fade_effects": True,
                "chart_update_rate": 1000,
                "chart_history_points": 100
            },
            "notifications": {
                "enabled": True,
                "sound": False,
                "optimization_alerts": True,
                "show_optimization_results": True,
                "show_cleanup_results": True,
                "show_warnings": True,
                "show_errors": True,
                "sound_enabled": False,
                "desktop_notifications": True,
                "tray_notifications": True
            },
            "logging": {
                "level": "INFO",
                "retention_days": 30
            },
            "performance": {
                "max_cpu_usage": 80,
                "max_ram_usage": 85,
                "max_disk_usage": 90,
                "max_temp_cpu": 80,
                "alert_thresholds": True,
                "auto_optimize_on_threshold": False
            },
            "startup": {
                "disable_unnecessary": True,
                "backup_startup_items": True,
                "whitelist": [
                    "Windows Security",
                    "Audio drivers",
                    "Graphics drivers",
                    "Antivirus"
                ],
                "blacklist": [
                    "Spotify",
                    "Discord",
                    "Steam",
                    "Epic Games",
                    "Adobe Updater"
                ]
            },
            "services": {
                "optimize_services": True,
                "backup_service_config": True,
                "safe_services_only": True,
                "services_to_disable": [
                    "SysMain",
                    "Themes",
                    "Fax",
                    "WSearch"
                ],
                "services_to_manual": [
                    "Spooler",
                    "TabletInputService",
                    "WbioSrvc"
                ]
            },
            "registry": {
                "cleanup_registry": False,
                "backup_before_cleanup": True,
                "safe_keys_only": True,
                "create_restore_point": True,
                "verify_changes": True
            },
            "disk": {
                "defragment_hdd": True,
                "optimize_ssd": True,
                "trim_ssd": True,
                "check_disk_health": True,
                "monitor_disk_space": True,
                "cleanup_threshold": 85
            },
            "memory": {
                "empty_working_sets": True,
                "clear_standby_cache": True,
                "optimize_page_file": True,
                "disable_superfetch": True,
                "optimize_prefetch": True
            },
            "cpu": {
                "set_high_priority": True,
                "disable_core_parking": False,
                "optimize_scheduler": True,
                "boost_mode": "aggressive",
                "thermal_throttling": False
            },
            "gpu": {
                "optimize_gpu_scheduling": True,
                "hardware_acceleration": True,
                "gpu_priority": "high",
                "disable_gpu_timeout": True,
                "optimize_vram": True
            },
            "paths": {
                "temp_folders": [],
                "cache_folders": [],
                "log_folders": [],
                "backup_folder": "",
                "custom_cleanup_paths": []
            },
            "exclusions": {
                "processes": [],
                "files": [],
                "folders": [],
                "registry_keys": [],
                "services": []
            },
            "profiles": {
                "current_profile": "balanced",
                "profiles": {
                    "gaming": {
                        "name": "Modo Gaming",
                        "description": "Otimizações focadas em jogos",
                        "settings": {
                            "ram_cleanup": True,
                            "cpu_priority": "realtime",
                            "gpu_optimization": True,
                            "network_optimization": True,
                            "disable_services": True
                        }
                    },
                    "balanced": {
                        "name": "Modo Equilibrado",
                        "description": "Balance entre performance e estabilidade",
                        "settings": {
                            "ram_cleanup": True,
                            "cpu_priority": "high",
                            "gpu_optimization": False,
                            "network_optimization": False,
                            "disable_services": False
                        }
                    },
                    "maximum": {
                        "name": "Máximo Desempenho",
                        "description": "Todas as otimizações ativadas",
                        "settings": {
                            "ram_cleanup": True,
                            "cpu_priority": "realtime",
                            "gpu_optimization": True,
                            "network_optimization": True,
                            "disable_services": True,
                            "disable_visual_effects": True
                        }
                    }
                }
            },
            "schedule": {
                "auto_cleanup_enabled": False,
                "cleanup_time": "02:00",
                "cleanup_days": ["sunday"],
                "auto_optimization_enabled": False,
                "optimization_interval": 60,
                "maintenance_mode": False
            },
            "reporting": {
                "generate_reports": True,
                "report_format": "html",
                "include_graphs": True,
                "report_location": "",
                "auto_export": False,
                "report_frequency": "weekly"
            },
            "updates": {
                "auto_check": True,
                "check_interval": 24,
                "beta_updates": False,
                "auto_download": False,
                "auto_install": False,
                "update_channel": "stable"
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtém valor de configuração"""
        try:
            keys = key.split('.')
            value = self._config_data
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
                    
            return value
            
        except Exception as e:
            self.logger.error(f"Erro ao obter configuração '{key}': {e}")
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """Define valor de configuração"""
        try:
            keys = key.split('.')
            config = self._config_data
            
            # Navega até o penúltimo nível
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # Define o valor
            config[keys[-1]] = value
            
            # Salva configurações
            self._save_config()
            
            self.logger.debug(f"Configuração '{key}' definida para: {value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao definir configuração '{key}': {e}")
            return False
    
    def reset_to_default(self, section: Optional[str] = None) -> bool:
        """Reseta configurações para padrão"""
        try:
            default_config = self._get_default_config()
            
            if section:
                if section in default_config:
                    self._config_data[section] = default_config[section]
                    self.logger.info(f"Seção '{section}' resetada para padrão")
                else:
                    self.logger.warning(f"Seção '{section}' não encontrada")
                    return False
            else:
                self._config_data = default_config
                self.logger.info("Todas as configurações resetadas para padrão")
            
            self._save_config()
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao resetar configurações: {e}")
            return False
    
    def export_config(self, file_path: str) -> bool:
        """Exporta configurações para arquivo"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self._config_data, f, indent=4, ensure_ascii=False)
            
            self.logger.info(f"Configurações exportadas para: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao exportar configurações: {e}")
            return False
    
    def import_config(self, file_path: str) -> bool:
        """Importa configurações de arquivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            # Valida configurações importadas
            if self._validate_config(imported_config):
                self._config_data = imported_config
                self._save_config()
                self.logger.info(f"Configurações importadas de: {file_path}")
                return True
            else:
                self.logger.error("Configurações importadas são inválidas")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao importar configurações: {e}")
            return False
    
    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """Valida estrutura de configuração"""
        try:
            # Validações básicas
            required_sections = ['app', 'monitoring', 'optimization', 'cleanup']
            
            for section in required_sections:
                if section not in config:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def get_profile(self, profile_name: str) -> Optional[Dict[str, Any]]:
        """Obtém perfil de configuração"""
        profiles = self.get('profiles.profiles', {})
        return profiles.get(profile_name)
    
    def set_profile(self, profile_name: str, profile_data: Dict[str, Any]) -> bool:
        """Define perfil de configuração"""
        return self.set(f'profiles.profiles.{profile_name}', profile_data)
    
    def get_current_profile(self) -> str:
        """Obtém perfil atual"""
        return self.get('profiles.current_profile', 'balanced')
    
    def set_current_profile(self, profile_name: str) -> bool:
        """Define perfil atual"""
        return self.set('profiles.current_profile', profile_name)
    
    def is_safe_mode(self) -> bool:
        """Verifica se está em modo seguro"""
        return self.get('optimization.safe_mode', True)
    
    def is_debug_mode(self) -> bool:
        """Verifica se está em modo debug"""
        return self.get('advanced.debug_mode', False)
    
    def get_theme(self) -> str:
        """Obtém tema atual"""
        return self.get('app.theme', 'dark')
    
    def get_language(self) -> str:
        """Obtém idioma atual"""
        return self.get('app.language', 'pt-BR')
    
    def get_update_interval(self) -> int:
        """Obtém intervalo de atualização"""
        return self.get('monitoring.update_interval', 1000)
    
    def should_create_backups(self) -> bool:
        """Verifica se deve criar backups"""
        return self.get('security.create_backups', True)
    
    def should_show_notifications(self) -> bool:
        """Verifica se deve mostrar notificações"""
        return self.get('app.show_notifications', True)
    
    def get_cleanup_settings(self) -> Dict[str, Any]:
        """Obtém configurações de limpeza"""
        return self.get('cleanup', {})
    
    def get_optimization_settings(self) -> Dict[str, Any]:
        """Obtém configurações de otimização"""
        return self.get('optimization', {})
    
    def get_monitoring_settings(self) -> Dict[str, Any]:
        """Obtém configurações de monitoramento"""
        return self.get('monitoring', {})
    
    def reload(self) -> bool:
        """Recarrega configurações do arquivo"""
        try:
            self._load_config()
            self.logger.info("Configurações recarregadas")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao recarregar configurações: {e}")
            return False
    
    @classmethod
    def load(cls):
        """Carrega configurações (método de classe)"""
        return cls()

# Instância global de configuração
config = Config()
