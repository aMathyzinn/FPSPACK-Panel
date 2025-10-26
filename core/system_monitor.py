#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitor de Sistema do FPSPACK PANEL
Coleta informações em tempo real do sistema
"""

import psutil
import time
import threading
from typing import Dict, List, Optional
from PySide6.QtCore import QObject, Signal, QThread
from utils.logger import Logger

class SystemMonitor(QObject):
    # Sinais para atualização da interface
    system_updated = Signal(dict)

    def __init__(self):
        super().__init__()
        self.logger = Logger()
        self.monitoring = False
        self.update_interval = 1000  # 1 segundo

        # Histórico de dados
        self.cpu_history = []
        self.ram_history = []
        self.disk_history = []
        self.network_history = []
        self.temp_history = []

        # Configurações de monitoramento
        self.max_history_points = 60  # 1 minuto de histórico

        # Worker thread para coletar dados do sistema sem bloquear a UI
        self._worker: Optional[QThread] = None

        # Informações de rede anteriores para calcular velocidade
        self.prev_network_io = None
        self.prev_network_time = None
        
    def start_monitoring(self):
        """Inicia o monitoramento do sistema"""
        if not self.monitoring:
            self.monitoring = True
            # Inicia worker que coleta dados periodicamente fora da thread da UI
            self._worker = MonitorWorker(self, self.update_interval)
            self._worker.data_ready.connect(self.system_updated.emit)
            self._worker.start()
            self.logger.info("Monitoramento do sistema iniciado (worker thread)")
            
    def stop_monitoring(self):
        """Para o monitoramento do sistema"""
        if self.monitoring:
            self.monitoring = False
            # Para o worker
            try:
                if self._worker:
                    self._worker.stop()
                    self._worker = None
            except Exception:
                pass
            self.logger.info("Monitoramento do sistema parado")
            
    def update_system_info(self):
        """Atualiza informações do sistema"""
        try:
            # Coleta informações
            cpu_info = self.get_cpu_info()
            memory_info = self.get_memory_info()
            disk_info = self.get_disk_info()
            network_info = self.get_network_info()
            temp_info = self.get_temperature_info()
            process_info = self.get_process_info()
            
            # Atualiza históricos
            self._update_history(self.cpu_history, cpu_info['percent'])
            self._update_history(self.ram_history, memory_info['percent'])
            self._update_history(self.disk_history, disk_info['percent'])
            self._update_history(self.temp_history, temp_info['cpu_temp'])
            
            # Monta dados completos
            system_data = {
                'cpu': cpu_info,
                'memory': memory_info,
                'disk': disk_info,
                'network': network_info,
                'temperature': temp_info,
                'processes': process_info,
                'history': {
                    'cpu': self.cpu_history.copy(),
                    'ram': self.ram_history.copy(),
                    'disk': self.disk_history.copy(),
                    'temp': self.temp_history.copy()
                },
                'timestamp': time.time()
            }
            
            # Emite sinal com os dados
            self.system_updated.emit(system_data)
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar informações do sistema: {e}")
            
    def get_cpu_info(self) -> Dict[str, any]:
        """Obtém informações da CPU"""
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            cpu_freq = psutil.cpu_freq()
            cpu_count = psutil.cpu_count()
            cpu_count_logical = psutil.cpu_count(logical=True)
            
            # CPU por core
            cpu_per_core = psutil.cpu_percent(interval=None, percpu=True)
            
            return {
                'percent': cpu_percent,
                'frequency_current': cpu_freq.current if cpu_freq else 0,
                'frequency_max': cpu_freq.max if cpu_freq else 0,
                'cores_physical': cpu_count,
                'cores_logical': cpu_count_logical,
                'per_core': cpu_per_core,
                'load_avg': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter informações da CPU: {e}")
            return {'percent': 0, 'frequency_current': 0, 'frequency_max': 0, 
                   'cores_physical': 0, 'cores_logical': 0, 'per_core': [], 'load_avg': [0, 0, 0]}
            
    def get_memory_info(self) -> Dict[str, any]:
        """Obtém informações da memória"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'free': memory.free,
                'percent': memory.percent,
                'total_gb': memory.total / (1024**3),
                'available_gb': memory.available / (1024**3),
                'used_gb': memory.used / (1024**3),
                'free_gb': memory.free / (1024**3),
                'swap_total': swap.total,
                'swap_used': swap.used,
                'swap_percent': swap.percent,
                'swap_total_gb': swap.total / (1024**3),
                'swap_used_gb': swap.used / (1024**3)
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter informações da memória: {e}")
            return {'total': 0, 'available': 0, 'used': 0, 'free': 0, 'percent': 0,
                   'total_gb': 0, 'available_gb': 0, 'used_gb': 0, 'free_gb': 0,
                   'swap_total': 0, 'swap_used': 0, 'swap_percent': 0,
                   'swap_total_gb': 0, 'swap_used_gb': 0}
            
    def get_disk_info(self) -> Dict[str, any]:
        """Obtém informações do disco"""
        try:
            # Disco principal (C:)
            disk_usage = psutil.disk_usage('C:')
            disk_io = psutil.disk_io_counters()
            
            # Informações de todas as partições
            partitions = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    partitions.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': (usage.used / usage.total) * 100,
                        'total_gb': usage.total / (1024**3),
                        'used_gb': usage.used / (1024**3),
                        'free_gb': usage.free / (1024**3)
                    })
                except PermissionError:
                    continue
                    
            return {
                'total': disk_usage.total,
                'used': disk_usage.used,
                'free': disk_usage.free,
                'percent': (disk_usage.used / disk_usage.total) * 100,
                'total_gb': disk_usage.total / (1024**3),
                'used_gb': disk_usage.used / (1024**3),
                'free_gb': disk_usage.free / (1024**3),
                'read_bytes': disk_io.read_bytes if disk_io else 0,
                'write_bytes': disk_io.write_bytes if disk_io else 0,
                'read_count': disk_io.read_count if disk_io else 0,
                'write_count': disk_io.write_count if disk_io else 0,
                'partitions': partitions
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter informações do disco: {e}")
            return {'total': 0, 'used': 0, 'free': 0, 'percent': 0,
                   'total_gb': 0, 'used_gb': 0, 'free_gb': 0,
                   'read_bytes': 0, 'write_bytes': 0, 'read_count': 0, 'write_count': 0,
                   'partitions': []}
            
    def get_network_info(self) -> Dict[str, any]:
        """Obtém informações da rede"""
        try:
            network_io = psutil.net_io_counters()
            current_time = time.time()
            
            # Calcula velocidade se temos dados anteriores
            upload_speed = 0
            download_speed = 0
            
            if self.prev_network_io and self.prev_network_time:
                time_diff = current_time - self.prev_network_time
                if time_diff > 0:
                    upload_speed = (network_io.bytes_sent - self.prev_network_io.bytes_sent) / time_diff
                    download_speed = (network_io.bytes_recv - self.prev_network_io.bytes_recv) / time_diff
                    
            # Atualiza dados anteriores
            self.prev_network_io = network_io
            self.prev_network_time = current_time
            
            # Informações de interfaces
            interfaces = []
            for interface_name, interface_info in psutil.net_if_stats().items():
                interfaces.append({
                    'name': interface_name,
                    'is_up': interface_info.isup,
                    'duplex': interface_info.duplex,
                    'speed': interface_info.speed,
                    'mtu': interface_info.mtu
                })
                
            return {
                'bytes_sent': network_io.bytes_sent,
                'bytes_recv': network_io.bytes_recv,
                'packets_sent': network_io.packets_sent,
                'packets_recv': network_io.packets_recv,
                'upload_speed': upload_speed,
                'download_speed': download_speed,
                'upload_speed_mbps': upload_speed / (1024**2),
                'download_speed_mbps': download_speed / (1024**2),
                'total_sent_gb': network_io.bytes_sent / (1024**3),
                'total_recv_gb': network_io.bytes_recv / (1024**3),
                'interfaces': interfaces
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter informações da rede: {e}")
            return {'bytes_sent': 0, 'bytes_recv': 0, 'packets_sent': 0, 'packets_recv': 0,
                   'upload_speed': 0, 'download_speed': 0, 'upload_speed_mbps': 0, 'download_speed_mbps': 0,
                   'total_sent_gb': 0, 'total_recv_gb': 0, 'interfaces': []}
            
    def get_temperature_info(self) -> Dict[str, any]:
        """Obtém informações de temperatura"""
        try:
            temperatures = {}
            cpu_temp = 0
            
            # Tenta obter temperaturas (nem sempre disponível)
            if hasattr(psutil, 'sensors_temperatures'):
                temps = psutil.sensors_temperatures()
                
                for name, entries in temps.items():
                    for entry in entries:
                        if 'cpu' in name.lower() or 'core' in name.lower():
                            cpu_temp = max(cpu_temp, entry.current)
                        temperatures[f"{name}_{entry.label}"] = {
                            'current': entry.current,
                            'high': entry.high,
                            'critical': entry.critical
                        }
                        
            # Se não conseguiu obter temperatura da CPU, usa valor padrão
            if cpu_temp == 0:
                cpu_temp = 45  # Valor padrão simulado
                
            return {
                'cpu_temp': cpu_temp,
                'all_temperatures': temperatures,
                'has_sensors': len(temperatures) > 0
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter informações de temperatura: {e}")
            return {'cpu_temp': 45, 'all_temperatures': {}, 'has_sensors': False}
            
    def get_process_info(self) -> Dict[str, any]:
        """Obtém informações dos processos"""
        try:
            processes = []
            total_processes = 0
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    total_processes += 1
                    
                    # Adiciona apenas processos com uso significativo
                    if proc.info['cpu_percent'] > 1 or proc.info['memory_percent'] > 1:
                        processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cpu_percent': proc.info['cpu_percent'],
                            'memory_percent': proc.info['memory_percent'],
                            'status': proc.info['status']
                        })
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
            # Ordena por uso de CPU
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            
            return {
                'total_processes': total_processes,
                'top_processes': processes[:10],  # Top 10
                'all_processes': processes
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter informações dos processos: {e}")
            return {'total_processes': 0, 'top_processes': [], 'all_processes': []}
            
    def _update_history(self, history_list: List[float], new_value: float):
        """Atualiza lista de histórico"""
        history_list.append(new_value)
        
        # Mantém apenas os últimos pontos
        if len(history_list) > self.max_history_points:
            history_list.pop(0)
            
    def get_current_info(self) -> Dict[str, any]:
        """Retorna informações atuais do sistema (sem histórico)"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(),
                'ram_used_gb': psutil.virtual_memory().used / (1024**3),
                'ram_percent': psutil.virtual_memory().percent,
                'disk_percent': (psutil.disk_usage('C:').used / psutil.disk_usage('C:').total) * 100,
                'cpu_temp': 45,  # Valor padrão
                'processes_count': len(psutil.pids())
            }
        except Exception as e:
            self.logger.error(f"Erro ao obter informações atuais: {e}")
            return {'cpu_percent': 0, 'ram_used_gb': 0, 'ram_percent': 0, 
                   'disk_percent': 0, 'cpu_temp': 0, 'processes_count': 0}
            
    def get_system_specs(self) -> Dict[str, any]:
        """Retorna especificações do sistema"""
        try:
            import platform
            
            # Informações do sistema
            uname = platform.uname()
            
            # CPU
            cpu_freq = psutil.cpu_freq()
            
            # Memória
            memory = psutil.virtual_memory()
            
            # Disco
            disk = psutil.disk_usage('C:')
            
            return {
                'system': uname.system,
                'node': uname.node,
                'release': uname.release,
                'version': uname.version,
                'machine': uname.machine,
                'processor': uname.processor,
                'cpu_cores_physical': psutil.cpu_count(logical=False),
                'cpu_cores_logical': psutil.cpu_count(logical=True),
                'cpu_max_frequency': cpu_freq.max if cpu_freq else 0,
                'memory_total_gb': memory.total / (1024**3),
                'disk_total_gb': disk.total / (1024**3),
                'boot_time': psutil.boot_time()
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter especificações do sistema: {e}")
            return {}
            
    def set_update_interval(self, interval_ms: int):
        """Define intervalo de atualização"""
        self.update_interval = interval_ms
        if self.monitoring:
            # Se estiver monitorando via worker, reinicie o worker com novo intervalo
            try:
                if self._worker:
                    self._worker.set_interval(interval_ms)
            except Exception:
                pass
            
    def get_network_connections(self) -> List[Dict[str, any]]:
        """Obtém conexões de rede ativas"""
        try:
            connections = []
            
            for conn in psutil.net_connections():
                if conn.status == 'ESTABLISHED':
                    connections.append({
                        'local_address': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "",
                        'remote_address': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "",
                        'status': conn.status,
                        'pid': conn.pid
                    })
                    
            return connections
            
        except Exception as e:
            self.logger.error(f"Erro ao obter conexões de rede: {e}")
            return []


class MonitorWorker(QThread):
    """Thread worker que coleta informações do SystemMonitor em intervalo regular
    Emite sinal `data_ready` com o dicionário de sistema pronto para UI."""

    data_ready = Signal(dict)

    def __init__(self, monitor: SystemMonitor, interval_ms: int = 1000):
        super().__init__()
        self.monitor = monitor
        self._interval = max(100, int(interval_ms)) / 1000.0
        self._running = True

    def run(self):
        while self._running:
            try:
                # Coleta informações com métodos do monitor (que usam psutil)
                cpu = self.monitor.get_cpu_info()
                memory = self.monitor.get_memory_info()
                disk = self.monitor.get_disk_info()
                network = self.monitor.get_network_info()
                temp = self.monitor.get_temperature_info()
                processes = self.monitor.get_process_info()

                # Atualiza históricos locais no monitor (rápido)
                self.monitor._update_history(self.monitor.cpu_history, cpu.get('percent', 0))
                self.monitor._update_history(self.monitor.ram_history, memory.get('percent', 0))
                self.monitor._update_history(self.monitor.disk_history, disk.get('percent', 0))
                self.monitor._update_history(self.monitor.temp_history, temp.get('cpu_temp', 0))

                system_data = {
                    'cpu': cpu,
                    'memory': memory,
                    'disk': disk,
                    'network': network,
                    'temperature': temp,
                    'processes': processes,
                    'history': {
                        'cpu': self.monitor.cpu_history.copy(),
                        'ram': self.monitor.ram_history.copy(),
                        'disk': self.monitor.disk_history.copy(),
                        'temp': self.monitor.temp_history.copy()
                    },
                    'timestamp': time.time()
                }

                # Emite dados para a UI
                self.data_ready.emit(system_data)

            except Exception as e:
                self.monitor.logger.error(f"MonitorWorker erro: {e}")

            # Sleep pelo intervalo (não bloquear a UI porque está em thread separada)
            try:
                time.sleep(self._interval)
            except Exception:
                pass

    def stop(self):
        self._running = False
        self.wait(2000)

    def set_interval(self, interval_ms: int):
        self._interval = max(100, int(interval_ms)) / 1000.0