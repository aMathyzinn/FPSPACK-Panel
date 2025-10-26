#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerenciador de Threads do FPSPACK PANEL
Sistema centralizado de gerenciamento de threads para otimização de performance
"""

import threading
import queue
import time
from concurrent.futures import ThreadPoolExecutor, Future, wait
from typing import Dict, List, Callable, Any, Optional
from PySide6.QtCore import QObject, Signal, QTimer, QThread
from utils.logger import Logger

class TaskResult:
    """Resultado de uma tarefa executada"""
    def __init__(self, task_id: str, success: bool, result: Any = None, error: str = None):
        self.task_id = task_id
        self.success = success
        self.result = result
        self.error = error
        self.timestamp = time.time()

class WorkerThread(QThread):
    """Thread worker otimizada para tarefas específicas"""
    progress_updated = Signal(str, int)  # task_id, progress
    status_updated = Signal(str, str)    # task_id, status
    task_completed = Signal(object)      # TaskResult
    
    def __init__(self, task_id: str, func: Callable, *args, **kwargs):
        super().__init__()
        self.task_id = task_id
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.logger = Logger()
        self._is_cancelled = False
        
    def run(self):
        """Executa a tarefa"""
        try:
            self.status_updated.emit(self.task_id, "Iniciando...")
            
            # Executa a função com callback de progresso
            if 'progress_callback' not in self.kwargs:
                self.kwargs['progress_callback'] = self._progress_callback
            if 'status_callback' not in self.kwargs:
                self.kwargs['status_callback'] = self._status_callback
                
            result = self.func(*self.args, **self.kwargs)
            
            if not self._is_cancelled:
                self.task_completed.emit(TaskResult(self.task_id, True, result))
                self.status_updated.emit(self.task_id, "Concluído")
                
        except Exception as e:
            self.logger.error(f"Erro na tarefa {self.task_id}: {e}")
            self.task_completed.emit(TaskResult(self.task_id, False, None, str(e)))
            self.status_updated.emit(self.task_id, f"Erro: {str(e)}")
            
    def _progress_callback(self, progress: int):
        """Callback de progresso"""
        if not self._is_cancelled:
            self.progress_updated.emit(self.task_id, progress)
            
    def _status_callback(self, status: str):
        """Callback de status"""
        if not self._is_cancelled:
            self.status_updated.emit(self.task_id, status)
            
    def cancel(self):
        """Cancela a tarefa"""
        self._is_cancelled = True
        self.status_updated.emit(self.task_id, "Cancelado")

class ThreadManager(QObject):
    """Gerenciador centralizado de threads"""
    
    # Sinais
    task_started = Signal(str)           # task_id
    task_progress = Signal(str, int)     # task_id, progress
    task_status = Signal(str, str)       # task_id, status
    task_completed = Signal(object)      # TaskResult
    
    def __init__(self, max_workers: int = 4):
        super().__init__()
        self.logger = Logger()
        self.max_workers = max_workers
        
        # ThreadPool para tarefas CPU-intensivas
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="FPSPack")
        
        # Threads ativas
        self.active_threads: Dict[str, WorkerThread] = {}
        self.active_futures: Dict[str, Future] = {}
        
        # Contador de tarefas
        self._task_counter = 0
        self._lock = threading.Lock()
        
        # Timer para limpeza
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self._cleanup_finished_tasks)
        self.cleanup_timer.start(5000)  # Limpeza a cada 5 segundos
        
        self.logger.info(f"ThreadManager inicializado com {max_workers} workers")
        
    def submit_task(self, func: Callable, *args, task_name: str = None, use_qthread: bool = False, **kwargs) -> str:
        """
        Submete uma tarefa para execução
        
        Args:
            func: Função a ser executada
            *args: Argumentos da função
            task_name: Nome da tarefa (opcional)
            use_qthread: Se True, usa QThread ao invés do ThreadPool
            **kwargs: Argumentos nomeados da função
            
        Returns:
            task_id: ID único da tarefa
        """
        with self._lock:
            self._task_counter += 1
            task_id = f"task_{self._task_counter}_{int(time.time())}"
            
        if task_name:
            task_id = f"{task_name}_{task_id}"
            
        try:
            if use_qthread:
                # Usa QThread para tarefas que precisam de sinais Qt
                worker = WorkerThread(task_id, func, *args, **kwargs)
                worker.progress_updated.connect(lambda tid, p: self.task_progress.emit(tid, p))
                worker.status_updated.connect(lambda tid, s: self.task_status.emit(tid, s))
                worker.task_completed.connect(self._on_task_completed)
                worker.finished.connect(lambda: self._cleanup_thread(task_id))

                self.active_threads[task_id] = worker
                worker.start()

            else:
                # Usa ThreadPool para tarefas simples
                future = self.thread_pool.submit(self._execute_task, task_id, func, *args, **kwargs)
                self.active_futures[task_id] = future
                
            self.task_started.emit(task_id)
            self.logger.debug(f"Tarefa {task_id} submetida")
            
            return task_id
            
        except Exception as e:
            self.logger.error(f"Erro ao submeter tarefa {task_id}: {e}")
            raise
            
    def _execute_task(self, task_id: str, func: Callable, *args, **kwargs) -> Any:
        """Executa uma tarefa no ThreadPool"""
        try:
            self.task_status.emit(task_id, "Executando...")
            
            # Adiciona callbacks se não existirem
            if 'progress_callback' not in kwargs:
                kwargs['progress_callback'] = lambda p: self.task_progress.emit(task_id, p)
            if 'status_callback' not in kwargs:
                kwargs['status_callback'] = lambda s: self.task_status.emit(task_id, s)
                
            result = func(*args, **kwargs)
            
            # Emite resultado
            task_result = TaskResult(task_id, True, result)
            self.task_completed.emit(task_result)
            self.task_status.emit(task_id, "Concluído")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erro na execução da tarefa {task_id}: {e}")
            task_result = TaskResult(task_id, False, None, str(e))
            self.task_completed.emit(task_result)
            self.task_status.emit(task_id, f"Erro: {str(e)}")
            raise
            
    def _on_task_completed(self, result: TaskResult):
        """Callback quando uma tarefa QThread é concluída"""
        self.task_completed.emit(result)
        
    def _cleanup_thread(self, task_id: str):
        """Remove thread finalizada"""
        if task_id in self.active_threads:
            del self.active_threads[task_id]
            
    def _cleanup_finished_tasks(self):
        """Limpa tarefas finalizadas do ThreadPool"""
        finished_tasks = []
        
        for task_id, future in self.active_futures.items():
            if future.done():
                finished_tasks.append(task_id)
                
        for task_id in finished_tasks:
            del self.active_futures[task_id]
            
        if finished_tasks:
            self.logger.debug(f"Limpeza: {len(finished_tasks)} tarefas removidas")
            
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancela uma tarefa
        
        Args:
            task_id: ID da tarefa
            
        Returns:
            bool: True se cancelada com sucesso
        """
        try:
            # Tenta cancelar QThread
            if task_id in self.active_threads:
                thread = self.active_threads[task_id]
                thread.cancel()
                thread.quit()
                thread.wait(3000)  # Espera até 3 segundos
                return True
                
            # Tenta cancelar Future
            if task_id in self.active_futures:
                future = self.active_futures[task_id]
                cancelled = future.cancel()
                if cancelled:
                    del self.active_futures[task_id]
                return cancelled
                
            return False
            
        except Exception as e:
            self.logger.error(f"Erro ao cancelar tarefa {task_id}: {e}")
            return False
            
    def cancel_all_tasks(self):
        """Cancela todas as tarefas ativas"""
        self.logger.info("Cancelando todas as tarefas...")
        
        # Cancela QThreads
        for task_id in list(self.active_threads.keys()):
            self.cancel_task(task_id)
            
        # Cancela Futures
        for task_id in list(self.active_futures.keys()):
            self.cancel_task(task_id)
            
    def get_active_tasks(self) -> List[str]:
        """Retorna lista de tarefas ativas"""
        return list(self.active_threads.keys()) + list(self.active_futures.keys())
        
    def get_task_count(self) -> Dict[str, int]:
        """Retorna contagem de tarefas"""
        return {
            'qthreads': len(self.active_threads),
            'futures': len(self.active_futures),
            'total': len(self.active_threads) + len(self.active_futures)
        }
        
    def shutdown(self, wait: bool = True, timeout: Optional[float] = 10.0):
        """
        Finaliza o gerenciador de threads
        
        Args:
            wait: Se deve esperar as tarefas terminarem
            timeout: Tempo limite para espera
        """
        self.logger.info("Finalizando ThreadManager...")
        
        # Para o timer de limpeza
        self.cleanup_timer.stop()
        
        # Cancela todas as tarefas
        self.cancel_all_tasks()
        
        # Aguarda futures se solicitado
        if wait and timeout is not None and self.active_futures:
            remaining = list(self.active_futures.values())
            done, not_done = wait(remaining, timeout=timeout)
            if not_done:
                self.logger.warning(f"{len(not_done)} tarefas não finalizaram dentro do timeout; cancelando...")
                for future in not_done:
                    future.cancel()

        # Finaliza ThreadPool (timeout não suportado diretamente)
        self.thread_pool.shutdown(wait=wait)
        
        self.logger.info("ThreadManager finalizado")

# Instância global do gerenciador
_thread_manager: Optional[ThreadManager] = None

def get_thread_manager() -> ThreadManager:
    """Retorna a instância global do ThreadManager"""
    global _thread_manager
    if _thread_manager is None:
        _thread_manager = ThreadManager()
    return _thread_manager

def shutdown_thread_manager():
    """Finaliza o ThreadManager global"""
    global _thread_manager
    if _thread_manager is not None:
        _thread_manager.shutdown()
        _thread_manager = None
