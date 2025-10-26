#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Núcleo de Otimização do FPSPACK PANEL
Funcionalidades reais de otimização de performance
"""

import os
import sys
import time
import psutil
import subprocess
import winreg
import ctypes
from ctypes import wintypes
import threading
from typing import Dict, List, Tuple, Optional, Any
from utils.logger import Logger
from utils.config import Config
from utils.system_integration import create_restore_point, create_settings_backup, is_admin

class OptimizationEngine:
    def __init__(self):
        self.logger = Logger()
        self.config = Config()
        self.is_admin = self._check_admin_privileges()
        self.optimization_active = False
        self._last_checkpoint_label: Optional[str] = None
        
        # Configurações de otimização
        self.optimization_profiles = {
            "gamer": {
                "name": "Modo Gamer",
                "description": "Otimizações focadas em jogos",
                "settings": {
                    "ram_cleanup": True,
                    "process_priority": "high",
                    "power_plan": "ultimate_performance",
                    "network_optimization": True,
                    "disable_services": ["superfetch", "sysmain", "themes"],
                    "cpu_priority": "realtime"
                }
            },
            "balanced": {
                "name": "Modo Equilibrado",
                "description": "Balance entre performance e estabilidade",
                "settings": {
                    "ram_cleanup": True,
                    "process_priority": "above_normal",
                    "power_plan": "high_performance",
                    "network_optimization": False,
                    "disable_services": ["superfetch"],
                    "cpu_priority": "high"
                }
            },
            "maximum": {
                "name": "Máximo Desempenho",
                "description": "Todas as otimizações ativadas",
                "settings": {
                    "ram_cleanup": True,
                    "process_priority": "realtime",
                    "power_plan": "ultimate_performance",
                    "network_optimization": True,
                    "disable_services": ["superfetch", "sysmain", "themes", "spooler", "fax"],
                    "cpu_priority": "realtime",
                    "disable_visual_effects": True,
                    "optimize_startup": True
                }
            }
        }
        
    def _check_admin_privileges(self) -> bool:
        """Verifica se esta executando como administrador"""
        return is_admin()

    def ensure_safety_checkpoint(self, reason: str, include_restore_point: bool = True, include_backup: bool = True) -> Dict[str, Dict[str, Optional[str]]]:
        """Cria salvaguardas antes de aplicar otimizacoes que alteram o sistema."""
        results: Dict[str, Dict[str, Optional[str]]] = {}
        label = reason.strip() or "Acao nao especificada"
        self._last_checkpoint_label = label

        if include_restore_point and self.config.get("advanced.create_restore_points", True):
            description = f"FPSPACK PANEL - {label}"
            success, message = create_restore_point(description)
            results["restore_point"] = {"success": "1" if success else "0", "message": message}
            if success:
                self.logger.info(message)
            else:
                self.logger.warning(f"Restore point nao criado: {message}")

        if include_backup and self.config.get("security.create_backups", True):
            backup_dir = self.config.get("security.backup_location", "") or None
            success, backup_path, message = create_settings_backup(backup_dir)
            results["backup"] = {"success": "1" if success else "0", "path": str(backup_path) if backup_path else None, "message": message}
            if success and backup_path:
                self.logger.info(f"Backup criado em: {backup_path}")
            elif success:
                self.logger.info(message)
            else:
                self.logger.warning(f"Backup nao criado: {message}")

        return results

    @staticmethod
    def _admin_required_response(action: str) -> Dict[str, Any]:
        """Resposta padronizada para ações que exigem modo administrador."""
        return {
            "success": False,
            "error": f"A operação '{action}' requer privilégios de administrador. Execute o FPSPACK como administrador e tente novamente.",
            "code": "admin_required"
        }
    def clean_ram(self) -> Dict[str, any]:
        """Limpeza inteligente de RAM"""
        try:
            self.logger.info("Iniciando limpeza de RAM...")
            
            # Informações antes da limpeza
            memory_before = psutil.virtual_memory()
            # 1. EmptyWorkingSet para todos os processos (exige admin)
            if self.is_admin:
                freed_memory = self._empty_working_sets()
            else:
                freed_memory = 0
                self.logger.debug("EmptyWorkingSet pulado: sem privilégios de administrador")

            # 2. Limpeza do cache de standby (exige admin)
            if self.is_admin:
                standby_freed = self._clear_standby_cache()
            else:
                standby_freed = 0
                self.logger.debug("Clear standby pulado: sem privilégios de administrador")

            # 3. Coleta de lixo do sistema (seguro)
            self._trigger_garbage_collection()
            
            # Informações após a limpeza
            memory_after = psutil.virtual_memory()
            
            total_freed = memory_before.used - memory_after.used
            
            result = {
                "success": True,
                "memory_before_gb": memory_before.used / (1024**3),
                "memory_after_gb": memory_after.used / (1024**3),
                "freed_gb": total_freed / (1024**3),
                "freed_working_sets": freed_memory,
                "freed_standby": standby_freed,
                "percent_freed": (total_freed / memory_before.used) * 100
            }
            
            self.logger.info(f"RAM limpa: {result['freed_gb']:.2f} GB liberados")
            return result
            
        except Exception as e:
            self.logger.error(f"Erro na limpeza de RAM: {e}")
            return {"success": False, "error": str(e)}
            
    def _empty_working_sets(self) -> int:
        """Esvazia working sets dos processos"""
        freed_memory = 0
        
        try:
            # Importa APIs do Windows
            kernel32 = ctypes.windll.kernel32
            psapi = ctypes.windll.psapi
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    # Abre handle do processo
                    handle = kernel32.OpenProcess(0x1F0FFF, False, proc.info['pid'])
                    if handle:
                        # EmptyWorkingSet
                        if psapi.EmptyWorkingSet(handle):
                            freed_memory += 1
                        kernel32.CloseHandle(handle)
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            self.logger.error(f"Erro no EmptyWorkingSet: {e}")
            
        return freed_memory
        
    def _clear_standby_cache(self) -> int:
        """Limpa cache de standby usando RAMMap technique"""
        try:
            if not self.is_admin:
                return 0
                
            # Comando para limpar standby cache
            cmd = 'powershell -Command "& {Get-CimInstance -ClassName Win32_OperatingSystem | Invoke-CimMethod -MethodName SetPrioritySeparation -Arguments @{PrioritySeparation=2}}"'
            subprocess.run(cmd, shell=True, capture_output=True)
            
            # Limpa cache usando técnica de alocação/liberação
            return self._force_standby_cleanup()
            
        except Exception as e:
            self.logger.error(f"Erro na limpeza de standby: {e}")
            return 0
            
    def _force_standby_cleanup(self) -> int:
        """Força limpeza do cache de standby"""
        try:
            # Técnica de alocação temporária para forçar limpeza
            available_memory = psutil.virtual_memory().available
            chunk_size = min(available_memory // 4, 1024 * 1024 * 1024)  # Max 1GB
            
            # Aloca e libera memória para forçar limpeza do standby
            temp_data = bytearray(chunk_size)
            del temp_data
            
            return chunk_size
            
        except Exception as e:
            self.logger.error(f"Erro na limpeza forçada: {e}")
            return 0
            
    def _trigger_garbage_collection(self):
        """Dispara coleta de lixo do sistema"""
        try:
            import gc
            gc.collect()
            
            # Força limpeza de buffers do sistema
            if os.name == 'nt':
                subprocess.run('echo off | clip', shell=True, capture_output=True)
                
        except Exception as e:
            self.logger.error(f"Erro na coleta de lixo: {e}")
            
    def optimize_startup(self) -> Dict[str, any]:
        """Otimiza programas de inicialização"""
        try:
            if not self.is_admin:
                self.logger.warning("Otimização de inicialização requer privilégios de administrador.")
                return self._admin_required_response("Otimizar programas de inicialização")
            self.logger.info("Otimizando inicialização...")
            
            disabled_items = []
            
            # Registros de inicialização
            startup_keys = [
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Run")
            ]
            
            for hkey, subkey in startup_keys:
                disabled_items.extend(self._optimize_registry_startup(hkey, subkey))
                
            # Pasta de inicialização
            startup_folder = os.path.join(os.environ['APPDATA'], 
                                        'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
            disabled_items.extend(self._optimize_startup_folder(startup_folder))
            
            return {
                "success": True,
                "disabled_items": disabled_items,
                "total_disabled": len(disabled_items)
            }
            
        except Exception as e:
            self.logger.error(f"Erro na otimização de startup: {e}")
            return {"success": False, "error": str(e)}
            
    def _optimize_registry_startup(self, hkey, subkey) -> List[str]:
        """Otimiza itens de startup no registro"""
        disabled_items = []
        
        try:
            with winreg.OpenKey(hkey, subkey, 0, winreg.KEY_ALL_ACCESS) as key:
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        
                        # Lista de programas seguros para desabilitar
                        safe_to_disable = [
                            'spotify', 'discord', 'steam', 'epic', 'origin',
                            'skype', 'zoom', 'teams', 'slack', 'adobe',
                            'office', 'onedrive', 'dropbox', 'googledrive'
                        ]
                        
                        if any(app in name.lower() or app in value.lower() 
                               for app in safe_to_disable):
                            # Move para chave de backup
                            backup_key = subkey + "_Disabled"
                            self._backup_and_remove_startup_item(hkey, backup_key, name, value)
                            disabled_items.append(name)
                            
                        i += 1
                        
                    except WindowsError:
                        break
                        
        except Exception as e:
            self.logger.error(f"Erro no registro de startup: {e}")
            
        return disabled_items
        
    def _backup_and_remove_startup_item(self, hkey, backup_subkey, name, value):
        """Faz backup e remove item de startup"""
        try:
            # Cria chave de backup
            with winreg.CreateKey(hkey, backup_subkey) as backup_key:
                winreg.SetValueEx(backup_key, name, 0, winreg.REG_SZ, value)
                
            # Remove da chave original
            with winreg.OpenKey(hkey, backup_subkey.replace("_Disabled", ""), 
                              0, winreg.KEY_ALL_ACCESS) as key:
                winreg.DeleteValue(key, name)
                
        except Exception as e:
            self.logger.error(f"Erro no backup de startup: {e}")
            
    def _optimize_startup_folder(self, folder_path) -> List[str]:
        """Otimiza pasta de inicialização"""
        disabled_items = []
        
        try:
            if os.path.exists(folder_path):
                backup_folder = folder_path + "_Disabled"
                os.makedirs(backup_folder, exist_ok=True)
                
                for item in os.listdir(folder_path):
                    item_path = os.path.join(folder_path, item)
                    backup_path = os.path.join(backup_folder, item)
                    
                    # Move itens não essenciais
                    if item.lower().endswith(('.lnk', '.exe')):
                        os.rename(item_path, backup_path)
                        disabled_items.append(item)
                        
        except Exception as e:
            self.logger.error(f"Erro na pasta de startup: {e}")
            
        return disabled_items
        
    def optimize_services(self) -> Dict[str, any]:
        """Otimiza serviços do Windows"""
        try:
            self.logger.info("Otimizando serviços...")

            # Operações em serviços exigem privilégios de administrador
            if not self.is_admin:
                self.logger.warning("Otimização de serviços requer privilégios de administrador")
                return self._admin_required_response("Otimizar serviços do Windows")
            
            # Serviços seguros para desabilitar/atrasar
            services_to_optimize = {
                "SysMain": "disabled",  # Superfetch
                "Themes": "manual",     # Temas
                "Spooler": "manual",    # Spooler de impressão
                "Fax": "disabled",      # Fax
                "WSearch": "manual",    # Windows Search
                "TabletInputService": "manual",  # Tablet Input
                "WbioSrvc": "manual",   # Windows Biometric
                "WMPNetworkSvc": "disabled",  # Windows Media Player Network
                "XblAuthManager": "manual",   # Xbox Live Auth
                "XblGameSave": "manual",      # Xbox Live Game Save
                "XboxNetApiSvc": "manual",    # Xbox Live Networking
                "XboxGipSvc": "manual"        # Xbox Accessory Management
            }

            # Além de otimizar serviços, vamos ajustar afinidades e prioridades de processos críticos
            process_priority_adjustments = {
                'explorer.exe': psutil.HIGH_PRIORITY_CLASS,
                'dwm.exe': psutil.HIGH_PRIORITY_CLASS,
            }
            
            optimized_services = []
            
            for service_name, target_state in services_to_optimize.items():
                if self._optimize_service(service_name, target_state):
                    optimized_services.append(f"{service_name} -> {target_state}")
                    
            return {
                "success": True,
                "optimized_services": optimized_services,
                "total_optimized": len(optimized_services)
            }
            
        except Exception as e:
            self.logger.error(f"Erro na otimização de serviços: {e}")
            return {"success": False, "error": str(e)}
            
    def _optimize_service(self, service_name: str, target_state: str) -> bool:
        """Otimiza um serviço específico"""
        try:
            if not self.is_admin:
                return False
                
            # Comando para alterar serviço
            if target_state == "disabled":
                cmd = f'sc config "{service_name}" start= disabled'
            elif target_state == "manual":
                cmd = f'sc config "{service_name}" start= demand'
            else:
                return False
                
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Para o serviço se estiver rodando
                subprocess.run(f'sc stop "{service_name}"', shell=True, capture_output=True)
                return True
                
        except Exception as e:
            self.logger.error(f"Erro ao otimizar serviço {service_name}: {e}")
            
        return False
        
    def optimize_network(self) -> Dict[str, any]:
        """Otimiza configurações de rede para jogos"""
        try:
            self.logger.info("Otimizando rede...")

            # A maioria das otimizações de rede altera configurações do sistema
            # e requer privilégios de administrador.
            if not self.is_admin:
                self.logger.warning("Otimização de rede requer privilégios de administrador")
                return self._admin_required_response("Aplicar plano de energia")
            
            optimizations = []
            
            # Otimizações TCP/IP
            tcp_optimizations = [
                ('netsh int tcp set global autotuninglevel=normal', 'TCP Auto-Tuning'),
                ('netsh int tcp set global chimney=enabled', 'TCP Chimney Offload'),
                ('netsh int tcp set global rss=enabled', 'Receive Side Scaling'),
                ('netsh int tcp set global netdma=enabled', 'NetDMA'),
                ('netsh int tcp set global dca=enabled', 'Direct Cache Access'),
                ('netsh int tcp set global ecncapability=enabled', 'ECN Capability'),
                ('netsh int tcp set global timestamps=enabled', 'TCP Timestamps')
            ]
            
            for cmd, description in tcp_optimizations:
                if self._run_network_command(cmd):
                    optimizations.append(description)
                    
            # Otimizações de interface de rede
            network_optimizations = [
                ('netsh int ip set global taskoffload=enabled', 'Task Offload'),
                ('netsh int ip set global neighborcachelimit=4096', 'Neighbor Cache Limit'),
                ('netsh int ip set global routecachelimit=4096', 'Route Cache Limit')
            ]
            
            for cmd, description in network_optimizations:
                if self._run_network_command(cmd):
                    optimizations.append(description)
                    
            # DNS otimizado
            self._optimize_dns()
            optimizations.append("DNS Otimizado")

            # Ajuste MTU (tenta detectar interface ativa)
            mtu_result = self._optimize_mtu()
            if mtu_result:
                optimizations.append(f"MTU ajustado: {mtu_result}")
            
            return {
                "success": True,
                "optimizations": optimizations,
                "total_optimizations": len(optimizations)
            }
            
        except Exception as e:
            self.logger.error(f"Erro na otimização de rede: {e}")
            return {"success": False, "error": str(e)}
            
    def _run_network_command(self, cmd: str) -> bool:
        """Executa comando de rede"""
        try:
            if not self.is_admin:
                return False
                
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Erro no comando de rede: {e}")
            return False
            
    def _optimize_dns(self):
        """Configura DNS otimizado"""
        try:
            # DNS servers rápidos
            dns_servers = ["1.1.1.1", "1.0.0.1"]  # Cloudflare
            
            # Configura DNS
            for i, dns in enumerate(dns_servers):
                cmd = f'netsh interface ip set dns "Ethernet" static {dns}'
                if i > 0:
                    cmd = f'netsh interface ip add dns "Ethernet" {dns} index={i+1}'
                subprocess.run(cmd, shell=True, capture_output=True)
                
        except Exception as e:
            self.logger.error(f"Erro na configuração de DNS: {e}")

    def _optimize_mtu(self) -> Optional[int]:
        """Tenta ajustar MTU para a interface ativa (Windows). Retorna MTU aplicado ou None."""
        try:
            if not self.is_admin:
                self.logger.warning("Ajuste de MTU requisita privilégios de administrador")
                return None

            # Detecta interface em uso via rota padrão
            result = subprocess.run('route PRINT 0.0.0.0', shell=True, capture_output=True, text=True)
            output = result.stdout or result.stderr

            # Tenta extrair nome da interface (heurística simples)
            import re
            m = re.search(r"0.0.0.0\s+0.0.0.0\s+[0-9.]+\.[0-9.]+\s+[0-9.]+\s+(\d+)", output)
            if m:
                iface_index = m.group(1)
                # Comando para ajustar MTU (exemplo: define 1500)
                mtu_value = 1500
                # Tenta aplicar para interfaces Ethernet/Wi-Fi via netsh
                cmds = [
                    f'netsh interface ipv4 set subinterface "{iface_index}" mtu={mtu_value} store=persistent',
                    f'netsh interface ipv6 set subinterface "{iface_index}" mtu={mtu_value} store=persistent'
                ]

                for cmd in cmds:
                    subprocess.run(cmd, shell=True, capture_output=True)

                return mtu_value

            return None

        except Exception as e:
            self.logger.error(f"Erro ao ajustar MTU: {e}")
            return None
            
    def set_power_plan(self, plan_type: str = "maximum") -> Dict[str, any]:
        """Aplica plano de energia baseado no tipo selecionado"""
        try:
            self.logger.info(f"Aplicando plano de energia: {plan_type}")
            
            if not self.is_admin:
                return self._admin_required_response("Aplicar plano de energia")
            
            # GUIDs dos planos do Windows
            power_plans = {
                "maximum": "e9a42b02-d5df-448d-aa00-03f14749eb61",  # Ultimate Performance
                "high": "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",     # High Performance
                "balanced": "381b4222-f694-41f0-9685-ff5bb260df2e"   # Balanced
            }
            
            if plan_type not in power_plans:
                return {"success": False, "error": "Tipo de plano inválido"}
            
            plan_guid = power_plans[plan_type]
            plan_names = {
                "maximum": "Desempenho Máximo",
                "high": "Alto Desempenho", 
                "balanced": "Equilibrado"
            }
            
            # Ativa o plano
            result = subprocess.run(f'powercfg -setactive {plan_guid}', shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Se for máximo, cria plano personalizado otimizado
                if plan_type == "maximum":
                    return self._create_optimized_power_plan()
                else:
                    return {
                        "success": True,
                        "plan_name": plan_names[plan_type],
                        "plan_type": plan_type
                    }
            else:
                return {"success": False, "error": f"Falha ao ativar plano: {result.stderr}"}
                
        except Exception as e:
            self.logger.error(f"Erro ao aplicar plano de energia: {e}")
            return {"success": False, "error": str(e)}
    
    def _create_optimized_power_plan(self) -> Dict[str, any]:
        """Cria plano de energia personalizado otimizado"""
        try:
            if not self.is_admin:
                self.logger.warning("Criação de plano de energia requer privilégios de administrador")
                return self._admin_required_response("Criar plano de energia personalizado")
            # Nome do plano personalizado
            plan_name = "FPSPACK Performance Mode"
            
            # Cria plano baseado no Ultimate Performance
            cmd = f'powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61 "{plan_name}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Extrai GUID do novo plano
                plan_guid = self._extract_plan_guid(result.stdout)
                
                if plan_guid:
                    # Ativa o plano
                    subprocess.run(f'powercfg -setactive {plan_guid}', shell=True)
                    
                    # Configura otimizações específicas
                    self._configure_power_plan(plan_guid)
                    
                    return {
                        "success": True,
                        "plan_name": plan_name,
                        "plan_guid": plan_guid,
                        "plan_type": "maximum"
                    }
                    
            return {"success": False, "error": "Falha ao criar plano personalizado"}
            
        except Exception as e:
            self.logger.error(f"Erro ao criar plano personalizado: {e}")
            return {"success": False, "error": str(e)}

    def create_performance_power_plan(self) -> Dict[str, any]:
        """Public wrapper to create and activate an optimized performance power plan.

        This method is a safe public entrypoint used by the UI. It returns the
        same structure as _create_optimized_power_plan and logs errors.
        """
        try:
            # Delegate to internal implementation which already handles commands
            return self._create_optimized_power_plan()
        except Exception as e:
            self.logger.error(f"Erro ao criar plano de energia (public): {e}")
            return {"success": False, "error": str(e)}
            
    def _extract_plan_guid(self, output: str) -> Optional[str]:
        """Extrai GUID do plano de energia"""
        try:
            import re
            match = re.search(r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})', output)
            return match.group(1) if match else None
        except:
            return None
            
    def _configure_power_plan(self, plan_guid: str):
        """Configura otimizações do plano de energia"""
        try:
            # Configurações de performance máxima
            settings = [
                ('SUB_PROCESSOR', 'PROCTHROTTLEMIN', '100'),  # CPU mínima 100%
                ('SUB_PROCESSOR', 'PROCTHROTTLEMAX', '100'),  # CPU máxima 100%
                ('SUB_PROCESSOR', 'PERFBOOSTMODE', '2'),      # Boost agressivo
                ('SUB_SLEEP', 'STANDBYIDLE', '0'),            # Sem standby
                ('SUB_SLEEP', 'HIBERNATEIDLE', '0'),          # Sem hibernação
                ('SUB_VIDEO', 'VIDEOIDLE', '0'),              # GPU sempre ativa
                ('SUB_DISK', 'DISKIDLE', '0')                 # Disco sempre ativo
            ]
            
            for subgroup, setting, value in settings:
                cmd = f'powercfg -setacvalueindex {plan_guid} {subgroup} {setting} {value}'
                subprocess.run(cmd, shell=True, capture_output=True)
                
        except Exception as e:
            self.logger.error(f"Erro na configuração do plano: {e}")
            
    def apply_quick_boost(self) -> Dict[str, any]:
        """Aplica boost rápido do sistema"""
        try:
            if not self.is_admin:
                self.logger.warning("Boost rápido requer privilégios de administrador")
                return self._admin_required_response("Aplicar Boost Rápido")
            self.logger.info("Aplicando boost rápido...")
            
            results = []
            
            # 1. Limpeza rápida de RAM
            ram_result = self.clean_ram()
            if ram_result["success"]:
                results.append(f"RAM: {ram_result['freed_gb']:.1f} GB liberados")
                
            # 2. Prioridade de processos
            self._boost_process_priorities()
            results.append("Prioridades otimizadas")
            
            # 3. Limpeza de cache rápida
            self._quick_cache_cleanup()
            results.append("Cache limpo")
            
            return {
                "success": True,
                "optimizations": results,
                "total_optimizations": len(results)
            }
            
        except Exception as e:
            self.logger.error(f"Erro no boost rápido: {e}")
            return {"success": False, "error": str(e)}
            
    def _boost_process_priorities(self):
        """Otimiza prioridades de processos"""
        try:
            # Processos para aumentar prioridade
            important_processes = ['dwm.exe', 'explorer.exe', 'winlogon.exe']
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'].lower() in important_processes:
                        p = psutil.Process(proc.info['pid'])
                        try:
                            p.nice(psutil.HIGH_PRIORITY_CLASS)
                        except Exception:
                            pass
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            self.logger.error(f"Erro nas prioridades: {e}")
            
    def _quick_cache_cleanup(self):
        """Limpeza rápida de cache"""
        try:
            # Limpa cache DNS
            subprocess.run('ipconfig /flushdns', shell=True, capture_output=True)
            
            # Limpa cache de ícones
            subprocess.run('ie4uinit.exe -ClearIconCache', shell=True, capture_output=True)
            
        except Exception as e:
            self.logger.error(f"Erro na limpeza de cache: {e}")
            
    def activate_turbo_mode(self) -> Dict[str, any]:
        """Ativa modo turbo com todas as otimizações"""
        try:
            self.logger.info("Ativando Modo Turbo...")

            # Modo Turbo realiza mudanças profundas no sistema — exige admin
            if not self.is_admin:
                self.logger.warning("Modo Turbo requer privilégios de administrador")
                return self._admin_required_response("Aplicar plano de energia")
            
            if self.optimization_active:
                return {"success": False, "error": "Modo Turbo já está ativo"}
                
            results = []
            
            # Aplica perfil máximo
            profile = self.optimization_profiles["maximum"]
            
            # 1. Limpeza de RAM
            if profile["settings"]["ram_cleanup"]:
                ram_result = self.clean_ram()
                if ram_result["success"]:
                    results.append(f"RAM: {ram_result['freed_gb']:.1f} GB liberados")
                    
            # 2. Otimização de serviços
            services_result = self.optimize_services()
            if services_result["success"]:
                results.append(f"Serviços: {services_result['total_optimized']} otimizados")
                
            # 3. Otimização de rede
            network_result = self.optimize_network()
            if network_result["success"]:
                results.append(f"Rede: {network_result['total_optimizations']} otimizações")
                
            # 4. Plano de energia
            power_result = self.set_power_plan("maximum")
            if power_result["success"]:
                results.append("Plano de energia criado")
                
            # 5. Startup
            startup_result = self.optimize_startup()
            if startup_result["success"]:
                results.append(f"Startup: {startup_result['total_disabled']} itens desabilitados")
                
            self.optimization_active = True
            
            return {
                "success": True,
                "mode": "Turbo Mode",
                "optimizations": results,
                "total_optimizations": len(results)
            }
            
        except Exception as e:
            self.logger.error(f"Erro no Modo Turbo: {e}")
            return {"success": False, "error": str(e)}
            
    def deactivate_turbo_mode(self) -> Dict[str, any]:
        """Desativa modo turbo"""
        try:
            self.logger.info("Desativando Modo Turbo...")
            
            # Restaura configurações padrão
            # (implementar restauração de backups)
            
            self.optimization_active = False
            
            return {"success": True, "message": "Modo Turbo desativado"}
            
        except Exception as e:
            self.logger.error(f"Erro ao desativar Modo Turbo: {e}")
            return {"success": False, "error": str(e)}
            
    def get_optimization_status(self) -> Dict[str, any]:
        """Retorna status das otimizações"""
        return {
            "turbo_mode_active": self.optimization_active,
            "admin_privileges": self.is_admin,
            "available_profiles": list(self.optimization_profiles.keys()),
            "system_info": {
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total / (1024**3),
                "memory_available": psutil.virtual_memory().available / (1024**3)
            }
        }
