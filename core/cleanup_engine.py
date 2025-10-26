#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Limpeza e Manutenção do FPSPACK PANEL
Limpeza profunda de cache, registro e otimização de disco
"""

import os
import sys
import shutil
import tempfile
import winreg
import subprocess
import glob
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from utils.logger import Logger
from utils.config import Config

class CleanupEngine:
    def __init__(self):
        self.logger = Logger()
        self.config = Config()
        self.temp_folders = []
        self.cache_folders = []
        self.log_folders = []
        self.browser_cache_folders = []
        
        self._initialize_cleanup_paths()
        
    def _initialize_cleanup_paths(self):
        """Inicializa caminhos para limpeza"""
        try:
            # Pastas temporárias
            self.temp_folders = [
                os.environ.get('TEMP', ''),
                os.environ.get('TMP', ''),
                os.path.join(os.environ.get('WINDIR', ''), 'Temp'),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Temp'),
                os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'Temp')
            ]
            
            # Cache do sistema
            self.cache_folders = [
                os.path.join(os.environ.get('WINDIR', ''), 'Prefetch'),
                os.path.join(os.environ.get('WINDIR', ''), 'SoftwareDistribution', 'Download'),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Windows', 'INetCache'),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Windows', 'WebCache'),
                os.path.join(os.environ.get('APPDATA', ''), 'Microsoft', 'Windows', 'Recent'),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'IconCache.db')
            ]
            
            # Logs do sistema
            self.log_folders = [
                os.path.join(os.environ.get('WINDIR', ''), 'Logs'),
                os.path.join(os.environ.get('WINDIR', ''), 'Debug'),
                os.path.join(os.environ.get('WINDIR', ''), 'Minidump'),
                os.path.join(os.environ.get('WINDIR', ''), 'memory.dmp'),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'CrashDumps')
            ]
            
            # Cache de navegadores
            user_profile = os.environ.get('USERPROFILE', '')
            local_appdata = os.environ.get('LOCALAPPDATA', '')
            appdata = os.environ.get('APPDATA', '')
            
            self.browser_cache_folders = [
                # Chrome
                os.path.join(local_appdata, 'Google', 'Chrome', 'User Data', 'Default', 'Cache'),
                os.path.join(local_appdata, 'Google', 'Chrome', 'User Data', 'Default', 'Code Cache'),
                os.path.join(local_appdata, 'Google', 'Chrome', 'User Data', 'Default', 'GPUCache'),
                
                # Firefox
                os.path.join(appdata, 'Mozilla', 'Firefox', 'Profiles'),
                os.path.join(local_appdata, 'Mozilla', 'Firefox', 'Profiles'),
                
                # Edge
                os.path.join(local_appdata, 'Microsoft', 'Edge', 'User Data', 'Default', 'Cache'),
                os.path.join(local_appdata, 'Microsoft', 'Edge', 'User Data', 'Default', 'Code Cache'),
                
                # Opera
                os.path.join(appdata, 'Opera Software', 'Opera Stable', 'Cache'),
                
                # Brave
                os.path.join(local_appdata, 'BraveSoftware', 'Brave-Browser', 'User Data', 'Default', 'Cache')
            ]
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar caminhos de limpeza: {e}")
            
    def full_system_cleanup(self) -> Dict[str, any]:
        """Executa limpeza completa do sistema"""
        try:
            self.logger.info("Iniciando limpeza completa do sistema...")
            
            # Execute only safe, non-destructive cleaning steps by default.
            # More aggressive steps (registry, windows update) remain available
            # but will only run when explicitly requested by the UI with admin consent.
            results = {
                "temp_files": self.clean_temp_files(),
                "system_cache": self.clean_system_cache(),
                "browser_cache": self.clean_browser_cache(),
                "logs": self.clean_system_logs(),
                "recycle_bin": self.empty_recycle_bin()
            }
            
            # Calcula totais
            total_files_cleaned = sum(r.get("files_cleaned", 0) for r in results.values() if isinstance(r, dict))
            total_space_freed = sum(r.get("space_freed_mb", 0) for r in results.values() if isinstance(r, dict))
            
            return {
                "success": True,
                "results": results,
                "summary": {
                    "total_files_cleaned": total_files_cleaned,
                    "total_space_freed_mb": total_space_freed,
                    "total_space_freed_gb": total_space_freed / 1024
                }
            }
            
        except Exception as e:
            self.logger.error(f"Erro na limpeza completa: {e}")
            return {"success": False, "error": str(e)}
            
    def clean_temp_files(self) -> Dict[str, any]:
        """Limpa arquivos temporários"""
        try:
            self.logger.info("Limpando arquivos temporários...")
            
            files_cleaned = 0
            space_freed = 0
            errors = []
            
            for temp_folder in self.temp_folders:
                if temp_folder and os.path.exists(temp_folder):
                    folder_result = self._clean_folder(temp_folder, recursive=True)
                    files_cleaned += folder_result["files_cleaned"]
                    space_freed += folder_result["space_freed"]
                    errors.extend(folder_result["errors"])
                    
            return {
                "success": True,
                "files_cleaned": files_cleaned,
                "space_freed_mb": space_freed / (1024 * 1024),
                "errors": errors
            }
            
        except Exception as e:
            self.logger.error(f"Erro na limpeza de arquivos temporários: {e}")
            return {"success": False, "error": str(e)}
            
    def clean_system_cache(self) -> Dict[str, any]:
        """Limpa cache do sistema"""
        try:
            self.logger.info("Limpando cache do sistema...")
            
            files_cleaned = 0
            space_freed = 0
            errors = []
            
            for cache_folder in self.cache_folders:
                if cache_folder and os.path.exists(cache_folder):
                    if os.path.isfile(cache_folder):
                        # É um arquivo específico
                        try:
                            size = os.path.getsize(cache_folder)
                            os.remove(cache_folder)
                            files_cleaned += 1
                            space_freed += size
                        except Exception as e:
                            errors.append(f"Erro ao remover {cache_folder}: {e}")
                    else:
                        # É uma pasta
                        folder_result = self._clean_folder(cache_folder, recursive=True)
                        files_cleaned += folder_result["files_cleaned"]
                        space_freed += folder_result["space_freed"]
                        errors.extend(folder_result["errors"])
                        
            # Limpeza específica do DNS
            self._flush_dns_cache()
            
            # Limpeza do cache de ícones
            self._clear_icon_cache()
            
            return {
                "success": True,
                "files_cleaned": files_cleaned,
                "space_freed_mb": space_freed / (1024 * 1024),
                "errors": errors
            }
            
        except Exception as e:
            self.logger.error(f"Erro na limpeza de cache do sistema: {e}")
            return {"success": False, "error": str(e)}
            
    def clean_browser_cache(self) -> Dict[str, any]:
        """Limpa cache dos navegadores"""
        try:
            self.logger.info("Limpando cache dos navegadores...")
            
            files_cleaned = 0
            space_freed = 0
            errors = []
            browsers_cleaned = []
            
            for cache_folder in self.browser_cache_folders:
                if cache_folder and os.path.exists(cache_folder):
                    # Identifica o navegador
                    browser_name = self._identify_browser(cache_folder)
                    
                    if os.path.isdir(cache_folder):
                        folder_result = self._clean_folder(cache_folder, recursive=True)
                        if folder_result["files_cleaned"] > 0:
                            browsers_cleaned.append(browser_name)
                        files_cleaned += folder_result["files_cleaned"]
                        space_freed += folder_result["space_freed"]
                        errors.extend(folder_result["errors"])
                        
            # Limpeza específica do Firefox
            self._clean_firefox_cache()
            
            return {
                "success": True,
                "files_cleaned": files_cleaned,
                "space_freed_mb": space_freed / (1024 * 1024),
                "browsers_cleaned": list(set(browsers_cleaned)),
                "errors": errors
            }
            
        except Exception as e:
            self.logger.error(f"Erro na limpeza de cache dos navegadores: {e}")
            return {"success": False, "error": str(e)}
            
    def clean_system_logs(self) -> Dict[str, any]:
        """Limpa logs do sistema"""
        try:
            self.logger.info("Limpando logs do sistema...")
            
            files_cleaned = 0
            space_freed = 0
            errors = []
            
            for log_folder in self.log_folders:
                if log_folder and os.path.exists(log_folder):
                    if os.path.isfile(log_folder):
                        # É um arquivo específico (como memory.dmp)
                        try:
                            size = os.path.getsize(log_folder)
                            os.remove(log_folder)
                            files_cleaned += 1
                            space_freed += size
                        except Exception as e:
                            errors.append(f"Erro ao remover {log_folder}: {e}")
                    else:
                        # É uma pasta
                        folder_result = self._clean_folder(log_folder, recursive=True, 
                                                         extensions=['.log', '.dmp', '.tmp'])
                        files_cleaned += folder_result["files_cleaned"]
                        space_freed += folder_result["space_freed"]
                        errors.extend(folder_result["errors"])
                        
            # Limpeza de logs do Event Viewer
            self._clear_event_logs()
            
            return {
                "success": True,
                "files_cleaned": files_cleaned,
                "space_freed_mb": space_freed / (1024 * 1024),
                "errors": errors
            }
            
        except Exception as e:
            self.logger.error(f"Erro na limpeza de logs: {e}")
            return {"success": False, "error": str(e)}
            
    def clean_registry(self) -> Dict[str, any]:
        """Limpa registro do Windows (seguro)"""
        try:
            self.logger.info("Limpando registro do Windows...")
            
            keys_cleaned = 0
            errors = []
            
            # Chaves seguras para limpeza
            safe_cleanup_keys = [
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs"),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU"),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\TypedPaths"),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Applets\Regedit\Favorites"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\SharedDLLs")
            ]
            
            for hkey, subkey in safe_cleanup_keys:
                try:
                    keys_cleaned += self._clean_registry_key(hkey, subkey)
                except Exception as e:
                    errors.append(f"Erro na chave {subkey}: {e}")
                    
            # Limpeza de entradas órfãs
            keys_cleaned += self._clean_orphaned_registry_entries()
            
            return {
                "success": True,
                "keys_cleaned": keys_cleaned,
                "errors": errors
            }
            
        except Exception as e:
            self.logger.error(f"Erro na limpeza do registro: {e}")
            return {"success": False, "error": str(e)}
            
    def empty_recycle_bin(self) -> Dict[str, any]:
        """Esvazia lixeira"""
        try:
            self.logger.info("Esvaziando lixeira...")
            
            # Calcula tamanho antes
            recycle_bin_size = self._get_recycle_bin_size()
            
            # Esvazia lixeira usando PowerShell
            cmd = 'powershell -Command "Clear-RecycleBin -Force"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "space_freed_mb": recycle_bin_size / (1024 * 1024),
                    "message": "Lixeira esvaziada com sucesso"
                }
            else:
                return {
                    "success": False,
                    "error": f"Erro ao esvaziar lixeira: {result.stderr}"
                }
                
        except Exception as e:
            self.logger.error(f"Erro ao esvaziar lixeira: {e}")
            return {"success": False, "error": str(e)}
            
    def clean_windows_update_cache(self) -> Dict[str, any]:
        """Limpa cache do Windows Update"""
        try:
            self.logger.info("Limpando cache do Windows Update...")
            
            # Para o serviço Windows Update
            subprocess.run('net stop wuauserv', shell=True, capture_output=True)
            subprocess.run('net stop cryptSvc', shell=True, capture_output=True)
            subprocess.run('net stop bits', shell=True, capture_output=True)
            subprocess.run('net stop msiserver', shell=True, capture_output=True)
            
            files_cleaned = 0
            space_freed = 0
            
            # Limpa pastas do Windows Update
            update_folders = [
                os.path.join(os.environ.get('WINDIR', ''), 'SoftwareDistribution'),
                os.path.join(os.environ.get('WINDIR', ''), 'System32', 'catroot2')
            ]
            
            for folder in update_folders:
                if os.path.exists(folder):
                    # Renomeia pasta para backup
                    backup_folder = folder + '.bak'
                    if os.path.exists(backup_folder):
                        shutil.rmtree(backup_folder, ignore_errors=True)
                    
                    try:
                        os.rename(folder, backup_folder)
                        folder_size = self._get_folder_size(backup_folder)
                        space_freed += folder_size
                        files_cleaned += 1
                    except Exception as e:
                        self.logger.error(f"Erro ao limpar {folder}: {e}")
                        
            # Reinicia serviços
            subprocess.run('net start wuauserv', shell=True, capture_output=True)
            subprocess.run('net start cryptSvc', shell=True, capture_output=True)
            subprocess.run('net start bits', shell=True, capture_output=True)
            subprocess.run('net start msiserver', shell=True, capture_output=True)
            
            return {
                "success": True,
                "files_cleaned": files_cleaned,
                "space_freed_mb": space_freed / (1024 * 1024)
            }
            
        except Exception as e:
            self.logger.error(f"Erro na limpeza do Windows Update: {e}")
            return {"success": False, "error": str(e)}
            
    def _clean_folder(self, folder_path: str, recursive: bool = False, 
                     extensions: List[str] = None) -> Dict[str, any]:
        """Limpa uma pasta específica"""
        files_cleaned = 0
        space_freed = 0
        errors = []
        
        try:
            if not os.path.exists(folder_path):
                return {"files_cleaned": 0, "space_freed": 0, "errors": []}
                
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Verifica extensões se especificadas
                    if extensions:
                        if not any(file.lower().endswith(ext) for ext in extensions):
                            continue
                            
                    try:
                        # Verifica se o arquivo não está em uso
                        if self._is_file_in_use(file_path):
                            continue
                            
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        files_cleaned += 1
                        space_freed += file_size
                        
                    except Exception as e:
                        errors.append(f"Erro ao remover {file_path}: {e}")
                        
                # Remove pastas vazias se recursivo
                if recursive:
                    for dir_name in dirs:
                        dir_path = os.path.join(root, dir_name)
                        try:
                            if not os.listdir(dir_path):  # Pasta vazia
                                os.rmdir(dir_path)
                        except:
                            pass
                            
        except Exception as e:
            errors.append(f"Erro ao acessar pasta {folder_path}: {e}")
            
        return {
            "files_cleaned": files_cleaned,
            "space_freed": space_freed,
            "errors": errors
        }
        
    def _is_file_in_use(self, file_path: str) -> bool:
        """Verifica se um arquivo está em uso"""
        try:
            with open(file_path, 'r+b'):
                return False
        except IOError:
            return True
            
    def _identify_browser(self, cache_path: str) -> str:
        """Identifica o navegador pelo caminho do cache"""
        cache_path_lower = cache_path.lower()
        
        if 'chrome' in cache_path_lower:
            return 'Google Chrome'
        elif 'firefox' in cache_path_lower:
            return 'Mozilla Firefox'
        elif 'edge' in cache_path_lower:
            return 'Microsoft Edge'
        elif 'opera' in cache_path_lower:
            return 'Opera'
        elif 'brave' in cache_path_lower:
            return 'Brave'
        else:
            return 'Navegador Desconhecido'
            
    def _clean_firefox_cache(self):
        """Limpeza específica do Firefox"""
        try:
            profiles_path = os.path.join(os.environ.get('APPDATA', ''), 'Mozilla', 'Firefox', 'Profiles')
            
            if os.path.exists(profiles_path):
                for profile in os.listdir(profiles_path):
                    profile_path = os.path.join(profiles_path, profile)
                    if os.path.isdir(profile_path):
                        # Cache folders específicos do Firefox
                        cache_folders = ['cache2', 'startupCache', 'OfflineCache']
                        
                        for cache_folder in cache_folders:
                            cache_path = os.path.join(profile_path, cache_folder)
                            if os.path.exists(cache_path):
                                self._clean_folder(cache_path, recursive=True)
                                
        except Exception as e:
            self.logger.error(f"Erro na limpeza do Firefox: {e}")
            
    def _flush_dns_cache(self):
        """Limpa cache DNS"""
        try:
            subprocess.run('ipconfig /flushdns', shell=True, capture_output=True)
        except Exception as e:
            self.logger.error(f"Erro ao limpar cache DNS: {e}")
            
    def _clear_icon_cache(self):
        """Limpa cache de ícones"""
        try:
            subprocess.run('ie4uinit.exe -ClearIconCache', shell=True, capture_output=True)
        except Exception as e:
            self.logger.error(f"Erro ao limpar cache de ícones: {e}")
            
    def _clear_event_logs(self):
        """Limpa logs do Event Viewer"""
        try:
            # Lista de logs seguros para limpar
            safe_logs = ['Application', 'System', 'Security', 'Setup']
            
            for log_name in safe_logs:
                cmd = f'wevtutil cl {log_name}'
                subprocess.run(cmd, shell=True, capture_output=True)
                
        except Exception as e:
            self.logger.error(f"Erro ao limpar Event Logs: {e}")
            
    def _clean_registry_key(self, hkey, subkey: str) -> int:
        """Limpa uma chave específica do registro"""
        keys_cleaned = 0
        
        try:
            with winreg.OpenKey(hkey, subkey, 0, winreg.KEY_ALL_ACCESS) as key:
                # Lista todos os valores
                i = 0
                values_to_delete = []
                
                while True:
                    try:
                        value_name, _, _ = winreg.EnumValue(key, i)
                        values_to_delete.append(value_name)
                        i += 1
                    except WindowsError:
                        break
                        
                # Remove valores
                for value_name in values_to_delete:
                    try:
                        winreg.DeleteValue(key, value_name)
                        keys_cleaned += 1
                    except Exception as e:
                        self.logger.error(f"Erro ao remover valor {value_name}: {e}")
                        
        except Exception as e:
            self.logger.error(f"Erro ao acessar chave {subkey}: {e}")
            
        return keys_cleaned
        
    def _clean_orphaned_registry_entries(self) -> int:
        """Limpa entradas órfãs do registro"""
        # Implementação básica - pode ser expandida
        return 0
        
    def _get_recycle_bin_size(self) -> int:
        """Obtém tamanho da lixeira"""
        try:
            # Caminho da lixeira
            recycle_bin_path = r'C:\$Recycle.Bin'
            
            if os.path.exists(recycle_bin_path):
                return self._get_folder_size(recycle_bin_path)
            else:
                return 0
                
        except Exception as e:
            self.logger.error(f"Erro ao obter tamanho da lixeira: {e}")
            return 0
            
    def _get_folder_size(self, folder_path: str) -> int:
        """Calcula tamanho total de uma pasta"""
        total_size = 0
        
        try:
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(file_path)
                    except (OSError, IOError):
                        continue
                        
        except Exception as e:
            self.logger.error(f"Erro ao calcular tamanho da pasta {folder_path}: {e}")
            
        return total_size
        
    def get_cleanup_preview(self) -> Dict[str, any]:
        """Obtém preview do que será limpo"""
        try:
            preview = {
                "temp_files": self._preview_temp_files(),
                "system_cache": self._preview_system_cache(),
                "browser_cache": self._preview_browser_cache(),
                "logs": self._preview_system_logs(),
                "recycle_bin": self._preview_recycle_bin()
            }
            
            # Calcula totais
            total_files = sum(p.get("file_count", 0) for p in preview.values())
            total_size = sum(p.get("size_mb", 0) for p in preview.values())
            
            return {
                "success": True,
                "preview": preview,
                "summary": {
                    "total_files": total_files,
                    "total_size_mb": total_size,
                    "total_size_gb": total_size / 1024
                }
            }
            
        except Exception as e:
            self.logger.error(f"Erro no preview de limpeza: {e}")
            return {"success": False, "error": str(e)}
            
    def _preview_temp_files(self) -> Dict[str, any]:
        """Preview de arquivos temporários"""
        file_count = 0
        total_size = 0
        
        for temp_folder in self.temp_folders:
            if temp_folder and os.path.exists(temp_folder):
                folder_info = self._get_folder_info(temp_folder)
                file_count += folder_info["file_count"]
                total_size += folder_info["size"]
                
        return {
            "file_count": file_count,
            "size_mb": total_size / (1024 * 1024)
        }
        
    def _preview_system_cache(self) -> Dict[str, any]:
        """Preview de cache do sistema"""
        file_count = 0
        total_size = 0
        
        for cache_folder in self.cache_folders:
            if cache_folder and os.path.exists(cache_folder):
                if os.path.isfile(cache_folder):
                    file_count += 1
                    total_size += os.path.getsize(cache_folder)
                else:
                    folder_info = self._get_folder_info(cache_folder)
                    file_count += folder_info["file_count"]
                    total_size += folder_info["size"]
                    
        return {
            "file_count": file_count,
            "size_mb": total_size / (1024 * 1024)
        }
        
    def _preview_browser_cache(self) -> Dict[str, any]:
        """Preview de cache dos navegadores"""
        file_count = 0
        total_size = 0
        browsers = []
        
        for cache_folder in self.browser_cache_folders:
            if cache_folder and os.path.exists(cache_folder):
                browser_name = self._identify_browser(cache_folder)
                if browser_name not in browsers:
                    browsers.append(browser_name)
                    
                folder_info = self._get_folder_info(cache_folder)
                file_count += folder_info["file_count"]
                total_size += folder_info["size"]
                
        return {
            "file_count": file_count,
            "size_mb": total_size / (1024 * 1024),
            "browsers": browsers
        }
        
    def _preview_system_logs(self) -> Dict[str, any]:
        """Preview de logs do sistema"""
        file_count = 0
        total_size = 0
        
        for log_folder in self.log_folders:
            if log_folder and os.path.exists(log_folder):
                if os.path.isfile(log_folder):
                    file_count += 1
                    total_size += os.path.getsize(log_folder)
                else:
                    folder_info = self._get_folder_info(log_folder, extensions=['.log', '.dmp', '.tmp'])
                    file_count += folder_info["file_count"]
                    total_size += folder_info["size"]
                    
        return {
            "file_count": file_count,
            "size_mb": total_size / (1024 * 1024)
        }
        
    def _preview_recycle_bin(self) -> Dict[str, any]:
        """Preview da lixeira"""
        size = self._get_recycle_bin_size()
        
        return {
            "file_count": 1 if size > 0 else 0,
            "size_mb": size / (1024 * 1024)
        }
        
    def _get_folder_info(self, folder_path: str, extensions: List[str] = None) -> Dict[str, any]:
        """Obtém informações de uma pasta"""
        file_count = 0
        total_size = 0
        
        try:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if extensions:
                        if not any(file.lower().endswith(ext) for ext in extensions):
                            continue
                            
                    file_path = os.path.join(root, file)
                    try:
                        total_size += os.path.getsize(file_path)
                        file_count += 1
                    except (OSError, IOError):
                        continue
                        
        except Exception as e:
            self.logger.error(f"Erro ao obter informações da pasta {folder_path}: {e}")
            
        return {
            "file_count": file_count,
            "size": total_size
        }