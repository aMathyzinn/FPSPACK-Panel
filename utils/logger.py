#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Logging do FPSPACK PANEL
Logging colorido e estruturado
"""

import os
import sys
import logging
import colorlog
from datetime import datetime
from pathlib import Path
from typing import Optional

class Logger:
    """Sistema de logging personalizado"""
    
    _instance = None
    _logger = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance
    
    def _initialize_logger(self):
        """Inicializa o sistema de logging"""
        if self._logger is not None:
            return
            
        # Cria diretório de logs
        log_dir = Path(__file__).parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # Nome do arquivo de log
        log_file = log_dir / f"fpspack_panel_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Configura logger principal
        self._logger = logging.getLogger("FPSPACK_PANEL")
        self._logger.setLevel(logging.DEBUG)
        
        # Remove handlers existentes
        for handler in self._logger.handlers[:]:
            self._logger.removeHandler(handler)
        
        # Handler para console (colorido)
        console_handler = colorlog.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        console_format = colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s | %(levelname)-8s | %(name)s | %(message)s%(reset)s',
            datefmt='%H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        console_handler.setFormatter(console_format)
        
        # Handler para arquivo
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        file_format = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        
        # Adiciona handlers
        self._logger.addHandler(console_handler)
        self._logger.addHandler(file_handler)
        
        # Log inicial
        self._logger.info("Sistema de logging inicializado")
        self._logger.info(f"Arquivo de log: {log_file}")
    
    def debug(self, message: str, extra: Optional[dict] = None):
        """Log de debug"""
        self._logger.debug(message, extra=extra)
    
    def info(self, message: str, extra: Optional[dict] = None):
        """Log de informação"""
        self._logger.info(message, extra=extra)
    
    def warning(self, message: str, extra: Optional[dict] = None):
        """Log de aviso"""
        self._logger.warning(message, extra=extra)
    
    def error(self, message: str, extra: Optional[dict] = None):
        """Log de erro"""
        self._logger.error(message, extra=extra)
    
    def critical(self, message: str, extra: Optional[dict] = None):
        """Log crítico"""
        self._logger.critical(message, extra=extra)
    
    def exception(self, message: str, extra: Optional[dict] = None):
        """Log de exceção com traceback"""
        self._logger.exception(message, extra=extra)
    
    def log_system_info(self):
        """Log informações do sistema"""
        import platform
        import psutil
        
        self.info("=== INFORMAÇÕES DO SISTEMA ===")
        self.info(f"Sistema: {platform.system()} {platform.release()}")
        self.info(f"Arquitetura: {platform.architecture()[0]}")
        self.info(f"Processador: {platform.processor()}")
        self.info(f"CPU Cores: {psutil.cpu_count()} ({psutil.cpu_count(logical=False)} físicos)")
        self.info(f"Memória Total: {psutil.virtual_memory().total / (1024**3):.1f} GB")
        self.info(f"Python: {platform.python_version()}")
        self.info("================================")
    
    def log_performance(self, operation: str, duration: float, details: Optional[dict] = None):
        """Log de performance"""
        message = f"PERFORMANCE | {operation} | {duration:.3f}s"
        if details:
            message += f" | {details}"
        self.info(message)
    
    def log_optimization(self, optimization_type: str, result: dict):
        """Log de otimização"""
        if result.get("success", False):
            self.info(f"OTIMIZAÇÃO | {optimization_type} | SUCESSO | {result}")
        else:
            self.error(f"OTIMIZAÇÃO | {optimization_type} | FALHA | {result}")
    
    def log_cleanup(self, cleanup_type: str, files_cleaned: int, space_freed_mb: float):
        """Log de limpeza"""
        self.info(f"LIMPEZA | {cleanup_type} | {files_cleaned} arquivos | {space_freed_mb:.1f} MB liberados")
    
    def log_user_action(self, action: str, details: Optional[str] = None):
        """Log de ação do usuário"""
        message = f"USUÁRIO | {action}"
        if details:
            message += f" | {details}"
        self.info(message)
    
    def log_error_with_context(self, error: Exception, context: str):
        """Log de erro com contexto"""
        self.error(f"ERRO | {context} | {type(error).__name__}: {str(error)}")
        self.exception("Detalhes do erro:")
    
    def set_level(self, level: str):
        """Define nível de logging"""
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        
        if level.upper() in level_map:
            self._logger.setLevel(level_map[level.upper()])
            self.info(f"Nível de logging alterado para: {level.upper()}")
        else:
            self.warning(f"Nível de logging inválido: {level}")
    
    def get_log_files(self) -> list:
        """Retorna lista de arquivos de log"""
        log_dir = Path(__file__).parent.parent / "logs"
        if log_dir.exists():
            return [f for f in log_dir.glob("*.log")]
        return []
    
    def clean_old_logs(self, days_to_keep: int = 7):
        """Remove logs antigos"""
        try:
            log_dir = Path(__file__).parent.parent / "logs"
            if not log_dir.exists():
                return
            
            from datetime import datetime, timedelta
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            removed_count = 0
            for log_file in log_dir.glob("*.log"):
                file_date = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_date < cutoff_date:
                    log_file.unlink()
                    removed_count += 1
            
            if removed_count > 0:
                self.info(f"Removidos {removed_count} arquivos de log antigos")
                
        except Exception as e:
            self.error(f"Erro ao limpar logs antigos: {e}")
    
    def export_logs(self, output_file: str, level: str = "INFO"):
        """Exporta logs para arquivo"""
        try:
            level_map = {
                'DEBUG': logging.DEBUG,
                'INFO': logging.INFO,
                'WARNING': logging.WARNING,
                'ERROR': logging.ERROR,
                'CRITICAL': logging.CRITICAL
            }
            
            min_level = level_map.get(level.upper(), logging.INFO)
            
            log_dir = Path(__file__).parent.parent / "logs"
            output_path = Path(output_file)
            
            with open(output_path, 'w', encoding='utf-8') as output:
                output.write(f"FPSPACK PANEL - Logs Exportados\n")
                output.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                output.write(f"Nível Mínimo: {level}\n")
                output.write("=" * 80 + "\n\n")
                
                for log_file in sorted(log_dir.glob("*.log")):
                    output.write(f"Arquivo: {log_file.name}\n")
                    output.write("-" * 40 + "\n")
                    
                    with open(log_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            # Filtra por nível (implementação básica)
                            if any(lvl in line for lvl in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']):
                                output.write(line)
                    
                    output.write("\n")
            
            self.info(f"Logs exportados para: {output_path}")
            return True
            
        except Exception as e:
            self.error(f"Erro ao exportar logs: {e}")
            return False
    
    def get_recent_logs(self, count: int = 100) -> list:
        """Retorna logs recentes"""
        try:
            log_dir = Path(__file__).parent.parent / "logs"
            recent_logs = []
            
            # Pega o arquivo de log mais recente
            log_files = sorted(log_dir.glob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True)
            
            if log_files:
                with open(log_files[0], 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    recent_logs = lines[-count:] if len(lines) > count else lines
            
            return recent_logs
            
        except Exception as e:
            self.error(f"Erro ao obter logs recentes: {e}")
            return []
    
    def log_startup(self):
        """Log de inicialização do aplicativo"""
        self.info("=" * 60)
        self.info("FPSPACK PANEL - INICIANDO")
        self.info("=" * 60)
        self.log_system_info()
        self.info("Aplicativo iniciado com sucesso")
    
    def log_shutdown(self):
        """Log de encerramento do aplicativo"""
        self.info("FPSPACK PANEL - ENCERRANDO")
        self.info("Aplicativo encerrado com sucesso")
        self.info("=" * 60)

# Instância global do logger
logger = Logger()