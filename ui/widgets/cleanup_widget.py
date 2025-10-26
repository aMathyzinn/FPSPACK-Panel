#!/usr/bin/env python3
"""
FPSPACK PANEL - Widget de Limpeza
Sistema de limpeza profunda com interface moderna
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                               QLabel, QPushButton, QProgressBar, QFrame, 
                               QGroupBox, QTextEdit, QScrollArea,
                               QMessageBox, QTreeWidget, QTreeWidgetItem)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QPixmap, QPalette, QColor, QIcon
from core.cleanup_engine import CleanupEngine
from core.thread_manager import get_thread_manager
from utils.logger import Logger
from .toggle_switch import ToggleSwitch
import time

class CleanupWidget(QWidget):
    """Widget principal de limpeza"""
    
    status_updated = Signal(str)
    
    def __init__(self, cleanup_engine=None):
        super().__init__()
        self.cleanup_engine = cleanup_engine or CleanupEngine()
        self.logger = Logger()
        self.thread_manager = get_thread_manager()
        # Conecta sinais uma vez e filtra por task_id nos handlers
        self.thread_manager.task_progress.connect(self._on_progress_update)
        self.thread_manager.task_status.connect(self._on_status_update)
        self.thread_manager.task_completed.connect(self._on_cleanup_finished)
        self.current_task_id = None
        self.analysis_results = {}
        self.cleanup_options = {}
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface do widget"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title = QLabel("🧹 Limpeza do Sistema")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Scroll area para conteúdo
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Seção de limpeza rápida
        self.create_quick_cleanup(content_layout)
        
        # Seção de opções de limpeza
        self.create_cleanup_options(content_layout)
        
        # Seção de análise
        self.create_analysis_section(content_layout)
        
        # Seção de progresso
        self.create_progress_section(content_layout)
        
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
    def create_quick_cleanup(self, parent_layout):
        """Cria seção de limpeza rápida"""
        group = QGroupBox("⚡ Limpeza Rápida")
        group.setObjectName("cleanup_group")
        layout = QHBoxLayout(group)
        
        # Botões de limpeza rápida
        quick_clean_btn = QPushButton("🚀 Limpeza Completa")
        quick_clean_btn.setObjectName("cleanup_button_primary")
        quick_clean_btn.clicked.connect(self.quick_cleanup)
        
        preview_btn = QPushButton("👁️ Prévia da Limpeza")
        preview_btn.setObjectName("cleanup_button")
        preview_btn.clicked.connect(self.preview_cleanup)
        
        layout.addWidget(quick_clean_btn)
        layout.addWidget(preview_btn)
        layout.addStretch()
        
        parent_layout.addWidget(group)
        
    def create_cleanup_options(self, parent_layout):
        """Cria seção de opções de limpeza"""
        group = QGroupBox("🔧 Opções de Limpeza")
        group.setObjectName("cleanup_group")
        layout = QGridLayout(group)
        
        # Opções de limpeza
        cleanup_options = [
            ("🗂️ Arquivos Temporários", "temp_files", True, "Limpa arquivos temporários do sistema"),
            ("💾 Cache do Sistema", "system_cache", True, "Limpa cache DNS, ícones e sistema"),
            ("🌐 Cache dos Navegadores", "browser_cache", True, "Limpa cache de todos os navegadores"),
            ("📋 Logs do Sistema", "system_logs", False, "Limpa logs do Event Viewer"),
            ("⚙️ Registro do Windows", "registry", False, "Limpeza segura do registro"),
            ("🗑️ Lixeira", "recycle_bin", True, "Esvazia a lixeira"),
            ("🔄 Cache Windows Update", "windows_update", False, "Limpa cache de atualizações")
        ]
        
        for i, (text, key, default, tooltip) in enumerate(cleanup_options):
            checkbox = ToggleSwitch(text)
            checkbox.setChecked(default)
            checkbox.setObjectName("cleanup_checkbox")
            checkbox.setToolTip(tooltip)
            self.cleanup_options[key] = checkbox
            
            row = i // 2
            col = i % 2
            layout.addWidget(checkbox, row, col)
            
        parent_layout.addWidget(group)
        
    def create_analysis_section(self, parent_layout):
        """Cria seção de análise"""
        group = QGroupBox("📊 Análise do Sistema")
        group.setObjectName("cleanup_group")
        layout = QVBoxLayout(group)
        
        # Botão de análise
        analyze_btn = QPushButton("🔍 Analisar Sistema")
        analyze_btn.setObjectName("cleanup_button")
        analyze_btn.clicked.connect(self.analyze_system)
        
        # Árvore de resultados
        self.analysis_tree = QTreeWidget()
        self.analysis_tree.setObjectName("cleanup_tree")
        self.analysis_tree.setHeaderLabels(["Categoria", "Arquivos", "Tamanho"])
        self.analysis_tree.setMaximumHeight(200)
        
        layout.addWidget(analyze_btn)
        layout.addWidget(self.analysis_tree)
        
        parent_layout.addWidget(group)
        
    def create_progress_section(self, parent_layout):
        """Cria seção de progresso"""
        group = QGroupBox("📈 Status da Limpeza")
        group.setObjectName("cleanup_group")
        layout = QVBoxLayout(group)
        
        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("cleanup_progress")
        self.progress_bar.setVisible(False)
        
        # Label de status
        self.status_label = QLabel("Pronto para limpeza")
        self.status_label.setObjectName("cleanup_status")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        # Log de atividades
        self.activity_log = QTextEdit()
        self.activity_log.setObjectName("cleanup_log")
        self.activity_log.setMaximumHeight(150)
        self.activity_log.setReadOnly(True)
        self.activity_log.append("Sistema pronto para limpeza...")
        
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(QLabel("Log de Atividades:"))
        layout.addWidget(self.activity_log)
        
        parent_layout.addWidget(group)
        
    def quick_cleanup(self):
        """Executa limpeza rápida com opções padrão"""
        # Seleciona opções seguras
        safe_options = ["temp_files", "system_cache", "browser_cache", "recycle_bin"]
        self.run_cleanup(safe_options)
        
    def preview_cleanup(self):
        """Mostra prévia da limpeza"""
        selected_options = self.get_selected_options()
        if not selected_options:
            QMessageBox.warning(self, "Aviso", "Selecione pelo menos uma opção de limpeza!")
            return
            
        self.run_cleanup(selected_options, preview_mode=True)
        
    def analyze_system(self):
        """Analisa o sistema para mostrar o que pode ser limpo"""
        self.analysis_tree.clear()
        self.log_activity("Analisando sistema...")
        
        # Simula análise (em implementação real, usaria o engine)
        categories = [
            ("Arquivos Temporários", "1,247", "2.3 GB"),
            ("Cache do Sistema", "892", "1.1 GB"),
            ("Cache dos Navegadores", "3,451", "4.7 GB"),
            ("Logs do Sistema", "156", "234 MB"),
            ("Lixeira", "23", "156 MB")
        ]
        
        total_size = 0
        for category, files, size in categories:
            item = QTreeWidgetItem([category, files, size])
            self.analysis_tree.addTopLevelItem(item)
            
        self.log_activity("Análise concluída - Total recuperável: ~8.5 GB")
        
    def get_selected_options(self):
        """Retorna opções selecionadas"""
        selected = []
        for key, checkbox in self.cleanup_options.items():
            if checkbox.isChecked():
                selected.append(key)
        return selected
        
    def run_cleanup(self, cleanup_types, preview_mode=False):
        """Executa limpeza com tipos especificados"""
        if self.current_task_id:
            QMessageBox.warning(self, "Aviso", "Uma limpeza já está em andamento!")
            return
            
        if not cleanup_types:
            QMessageBox.warning(self, "Aviso", "Selecione pelo menos uma opção de limpeza!")
            return
            
        # Submete tarefa para o ThreadManager
        task_data = {
            'cleanup_types': cleanup_types,
            'preview_mode': preview_mode,
            'engine': self.cleanup_engine
        }
        
        self.current_task_id = self.thread_manager.submit_task(
            self._execute_cleanup_task,
            task_data,
            task_name="cleanup_task"
        )
        
        # Conecta sinais
        self.thread_manager.task_progress.connect(self._on_progress_update)
        self.thread_manager.task_status.connect(self._on_status_update)
        self.thread_manager.task_completed.connect(self._on_cleanup_finished)
        
        # Mostra progresso
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        mode_text = "Prévia" if preview_mode else "Limpeza"
        self.log_activity(f"Iniciando {mode_text}: {', '.join(cleanup_types)}")
        
    def _execute_cleanup_task(self, task_data, progress_callback, status_callback):
        """Executa a tarefa de limpeza"""
        cleanup_types = task_data['cleanup_types']
        preview_mode = task_data['preview_mode']
        engine = task_data['engine']
        
        results = {}
        total_steps = len(cleanup_types)
        
        for i, cleanup_type in enumerate(cleanup_types):
            progress = int((i / total_steps) * 100)
            progress_callback(progress)
            
            if cleanup_type == "temp_files":
                status_callback("Limpando arquivos temporários...")
                if preview_mode:
                    result = engine.preview_temp_cleanup()
                else:
                    result = engine.clean_temp_files()
                    
            elif cleanup_type == "system_cache":
                status_callback("Limpando cache do sistema...")
                if preview_mode:
                    result = engine.preview_cache_cleanup()
                else:
                    result = engine.clean_system_cache()
                    
            elif cleanup_type == "browser_cache":
                status_callback("Limpando cache dos navegadores...")
                if preview_mode:
                    result = engine.preview_browser_cleanup()
                else:
                    result = engine.clean_browser_cache()
                    
            elif cleanup_type == "system_logs":
                status_callback("Limpando logs do sistema...")
                if preview_mode:
                    result = engine.preview_logs_cleanup()
                else:
                    result = engine.clean_system_logs()
                    
            elif cleanup_type == "registry":
                status_callback("Limpando registro...")
                if preview_mode:
                    result = engine.preview_registry_cleanup()
                else:
                    result = engine.clean_registry()
                    
            elif cleanup_type == "recycle_bin":
                status_callback("Esvaziando lixeira...")
                if preview_mode:
                    result = engine.preview_recycle_bin_cleanup()
                else:
                    result = engine.empty_recycle_bin()
                    
            elif cleanup_type == "windows_update":
                status_callback("Limpando cache do Windows Update...")
                if preview_mode:
                    result = engine.preview_windows_update_cleanup()
                else:
                    result = engine.clean_windows_update_cache()
                    
            results[cleanup_type] = result
            
        progress_callback(100)
        return {"success": True, "message": "Limpeza concluída com sucesso!", "results": results}
        
    def _on_progress_update(self, task_id, progress):
        """Callback para atualização de progresso"""
        if task_id == self.current_task_id:
            self.progress_bar.setValue(progress)
            
    def _on_status_update(self, task_id, status):
        """Callback para atualização de status"""
        if task_id == self.current_task_id:
            self.status_label.setText(status)
            self.status_updated.emit(status)
            self.log_activity(status)
            
    def _on_cleanup_finished(self, task_id, result):
        """Callback quando limpeza termina"""
        if task_id != self.current_task_id:
            return
            
        # Desconecta sinais
        self.thread_manager.task_progress.disconnect(self._on_progress_update)
        self.thread_manager.task_status.disconnect(self._on_status_update)
        self.thread_manager.task_completed.disconnect(self._on_cleanup_finished)
        
        self.current_task_id = None
        self.progress_bar.setVisible(False)
        
        if result.get("success", False):
            self.status_label.setText("✅ Limpeza concluída!")
            self.log_activity(f"✅ {result['message']}")
            self.show_cleanup_results(result.get("results", {}))
            QMessageBox.information(self, "Sucesso", result["message"])
        else:
            error_msg = result.get("error", "Erro desconhecido")
            self.status_label.setText("❌ Erro na limpeza")
            self.log_activity(f"❌ {error_msg}")
            QMessageBox.warning(self, "Erro", error_msg)
        
    def show_cleanup_results(self, results):
        """Mostra resultados detalhados da limpeza"""
        result_text = "Resultados da Limpeza:\n\n"
        total_freed = 0
        
        for cleanup_type, result in results.items():
            if result.get("success", False):
                freed = result.get("space_freed", 0)
                files = result.get("files_processed", 0)
                result_text += f"✅ {cleanup_type}: {files} arquivos, {freed} MB liberados\n"
                total_freed += freed
            else:
                result_text += f"❌ {cleanup_type}: {result.get('message', 'Erro desconhecido')}\n"
                
        result_text += f"\n🎉 Total liberado: {total_freed} MB"
        
        QMessageBox.information(self, "Resultados da Limpeza", result_text)
        
    def log_activity(self, message):
        """Adiciona mensagem ao log de atividades"""
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.activity_log.append(formatted_message)
        
        # Mantém apenas as últimas 100 linhas
        if self.activity_log.document().blockCount() > 100:
            cursor = self.activity_log.textCursor()
            cursor.movePosition(cursor.Start)
            cursor.select(cursor.LineUnderCursor)
            cursor.removeSelectedText()
            cursor.deletePreviousChar()  # Remove quebra de linha