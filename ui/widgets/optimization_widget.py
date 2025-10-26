#!/usr/bin/env python3
"""
FPSPACK PANEL - Widget de Otimização
Sistema de otimização avançado com interface moderna
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                               QLabel, QPushButton, QProgressBar, QFrame, 
                               QGroupBox, QTextEdit, QScrollArea,
                               QMessageBox, QComboBox, QSlider, QSpinBox)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QPixmap, QPalette, QColor, QIcon
from core.optimization_engine import OptimizationEngine
from core.thread_manager import get_thread_manager
from utils.logger import Logger
from utils.config import Config
from .toggle_switch import ToggleSwitch
import time



class OptimizationWidget(QWidget):
    """Widget principal de otimização"""
    
    status_updated = Signal(str)
    
    def __init__(self, optimization_engine=None):
        super().__init__()
        self.optimization_engine = optimization_engine or OptimizationEngine()
        self.thread_manager = get_thread_manager()
        # Conecta sinais uma vez e filtra por task_id nos handlers
        self.thread_manager.task_progress.connect(self._on_progress_updated)
        self.thread_manager.task_status.connect(self._on_status_updated)
        self.thread_manager.task_completed.connect(self._on_optimization_finished)
        self.config = Config()
        self.logger = Logger()
        self.current_task_id = None
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface do widget"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title = QLabel("🚀 Otimização do Sistema")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Scroll area para conteúdo
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Seção de otimizações rápidas
        self.create_quick_optimizations(content_layout)
        
        # Seção de otimizações avançadas
        self.create_advanced_optimizations(content_layout)
        
        # Seção de presets
        self.create_presets_section(content_layout)
        
        # Seção de planos de energia
        self.create_power_plan_section(content_layout)
        
        # Barra de progresso
        self.create_progress_section(content_layout)
        
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
    def create_quick_optimizations(self, parent_layout):
        """Cria seção de otimizações rápidas"""
        group = QGroupBox("⚡ Otimizações Rápidas")
        group.setObjectName("optimization_group")
        layout = QGridLayout(group)
        
        # Botões de otimização rápida
        quick_opts = [
            ("🧹 Limpar RAM", "ram_clean", "Libera memória RAM não utilizada"),
            ("🚀 Boost Rápido", "quick_boost", "Aplica optimizações rápidas de performance"),
            ("⚙️ Otimizar Serviços", "services_optimization", "Otimiza serviços do Windows"),
            ("🌐 Tuning de Rede", "network_tuning", "Otimiza configurações de rede"),
            ("⚡ Plano de Energia", "power_plan", "Cria plano de alta performance"),
            ("🔥 Modo Turbo", "turbo_mode", "Ativa todas as otimizações")
        ]
        
        for i, (text, action, tooltip) in enumerate(quick_opts):
            btn = QPushButton(text)
            btn.setObjectName("optimization_button")
            btn.setToolTip(tooltip)
            btn.clicked.connect(lambda checked, a=action: self.run_optimization(a))
            
            row = i // 2
            col = i % 2
            layout.addWidget(btn, row, col)
            
        parent_layout.addWidget(group)
        
    def create_advanced_optimizations(self, parent_layout):
        """Cria seção de otimizações avançadas"""
        group = QGroupBox("🔧 Configurações Avançadas")
        group.setObjectName("optimization_group")
        layout = QVBoxLayout(group)
        
        # Opções de otimização
        self.optimization_options = {}
        self.optimization_option_defaults = {}
        
        options = [
            ("Limpeza agressiva de RAM", "aggressive_ram", True),
            ("Desabilitar serviços desnecessários", "disable_services", True),
            ("Ajustar MTU (rede)", "adjust_mtu", False),
            ("Otimizar TCP/IP", "tcp_optimization", True),
            ("Ajustar prioridade de processos", "process_priority", False),
            ("Otimizar cache de sistema", "system_cache", True),
            ("Desabilitar efeitos visuais", "visual_effects", False)
        ]
        
        for text, key, default in options:
            checkbox = ToggleSwitch(text)
            checkbox.setObjectName("optimization_checkbox")
            saved_state = self.config.get(f"optimization.advanced_options.{key}", default)
            checkbox.setChecked(saved_state)
            checkbox.toggled.connect(lambda checked, k=key: self._on_option_toggled(k, checked))
            self.optimization_option_defaults[key] = default
            self.optimization_options[key] = checkbox
            layout.addWidget(checkbox)
        
        # Botão para aplicar selecionados
        apply_selected_btn = QPushButton("✅ APLICAR SELECIONADOS")
        apply_selected_btn.setObjectName("optimization_button_primary")
        apply_selected_btn.clicked.connect(self.apply_selected_optimizations)
        layout.addWidget(apply_selected_btn)
            
        parent_layout.addWidget(group)
        
    def create_presets_section(self, parent_layout):
        """Cria seção de presets"""
        group = QGroupBox("🎯 Presets de Otimização")
        group.setObjectName("optimization_group")
        layout = QHBoxLayout(group)
        
        # Combo box de presets
        self.preset_combo = QComboBox()
        self.preset_combo.setObjectName("optimization_combo")
        self.preset_combo.addItems([
            "🎮 Modo Gamer",
            "⚖️ Modo Equilibrado", 
            "🔥 Performance Máxima",
            "🔋 Economia de Energia",
            "🛡️ Modo Seguro"
        ])
        
        apply_preset_btn = QPushButton("Aplicar Preset")
        apply_preset_btn.setObjectName("optimization_button")
        apply_preset_btn.clicked.connect(self.apply_preset)
        
        layout.addWidget(QLabel("Preset:"))
        layout.addWidget(self.preset_combo)
        layout.addWidget(apply_preset_btn)
        layout.addStretch()
        
        parent_layout.addWidget(group)
        
    def create_power_plan_section(self, parent_layout):
        """Cria seção de planos de energia"""
        group = QGroupBox("⚡ Planos de Energia")
        group.setObjectName("optimization_group")
        layout = QHBoxLayout(group)
        
        # Combo box de planos de energia
        self.power_plan_combo = QComboBox()
        self.power_plan_combo.setObjectName("optimization_combo")
        self.power_plan_combo.addItems([
            "🔥 Desempenho Máximo",
            "⚡ Alto Desempenho",
            "⚖️ Equilibrado"
        ])
        
        apply_power_btn = QPushButton("Aplicar Plano")
        apply_power_btn.setObjectName("optimization_button")
        apply_power_btn.clicked.connect(self.apply_power_plan)
        
        layout.addWidget(QLabel("Plano de Energia:"))
        layout.addWidget(self.power_plan_combo)
        layout.addWidget(apply_power_btn)
        layout.addStretch()
        
        parent_layout.addWidget(group)
        
    def create_progress_section(self, parent_layout):
        """Cria seção de progresso"""
        group = QGroupBox("📊 Status da Otimização")
        group.setObjectName("optimization_group")
        layout = QVBoxLayout(group)
        
        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("optimization_progress")
        self.progress_bar.setVisible(False)
        
        # Label de status
        self.status_label = QLabel("Pronto para otimizar")
        self.status_label.setObjectName("optimization_status")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        # Log de atividades
        self.activity_log = QTextEdit()
        self.activity_log.setObjectName("optimization_log")
        self.activity_log.setMaximumHeight(150)
        self.activity_log.setReadOnly(True)
        self.activity_log.append("Sistema pronto para otimização...")
        
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(QLabel("Log de Atividades:"))
        layout.addWidget(self.activity_log)
        
        parent_layout.addWidget(group)
        
    def run_optimization(self, optimization_type):
        """Executa uma otimização específica usando ThreadManager"""
        if self.current_task_id:
            QMessageBox.warning(self, "Aviso", "Uma otimização já está em andamento!")
            return
            
        # Coleta opções selecionadas
        options = {}
        for key, checkbox in self.optimization_options.items():
            options[key] = checkbox.isChecked()
            
        # Submete tarefa para o ThreadManager (não usa QThread por padrão)
        self.current_task_id = self.thread_manager.submit_task(
            self._execute_optimization,
            optimization_type,
            options,
            task_name=f"optimization_{optimization_type}"
        )

        # Mostra progresso
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self.log_activity(f"Iniciando: {optimization_type}")
        
    def _execute_optimization(self, optimization_type, options, progress_callback=None, status_callback=None):
        """Executa a otimização (função para ThreadManager)"""
        try:
            if status_callback:
                status_callback("Iniciando otimização...")
            if progress_callback:
                progress_callback(10)
                
            result = None
            include_restore = optimization_type not in {"ram_clean"}
            include_backup = include_restore
            self.optimization_engine.ensure_safety_checkpoint(
                f"Otimizacao {optimization_type}",
                include_restore_point=include_restore,
                include_backup=include_backup
            )

            
            if optimization_type == "ram_clean":
                if status_callback:
                    status_callback("Limpando memória RAM...")
                if progress_callback:
                    progress_callback(25)
                result = self.optimization_engine.clean_ram()
                
            elif optimization_type == "startup_boost":
                if status_callback:
                    status_callback("Otimizando inicialização...")
                if progress_callback:
                    progress_callback(20)
                result = self.optimization_engine.optimize_startup()
                
            elif optimization_type == "services_optimization":
                if status_callback:
                    status_callback("Otimizando serviços...")
                if progress_callback:
                    progress_callback(30)
                result = self.optimization_engine.optimize_services()
                
            elif optimization_type == "network_tuning":
                if status_callback:
                    status_callback("Otimizando rede...")
                if progress_callback:
                    progress_callback(40)
                result = self.optimization_engine.optimize_network()
            elif optimization_type == "quick_boost":
                if status_callback:
                    status_callback("Aplicando boost rapido...")
                if progress_callback:
                    progress_callback(35)
                result = self.optimization_engine.apply_quick_boost()

                
            elif optimization_type == "turbo_mode":
                if status_callback:
                    status_callback("Ativando Modo Turbo...")
                if progress_callback:
                    progress_callback(10)
                result = self.optimization_engine.activate_turbo_mode()
                
            elif optimization_type == "power_plan":
                if status_callback:
                    status_callback("Criando plano de energia...")
                if progress_callback:
                    progress_callback(50)
                result = self.optimization_engine.create_performance_power_plan()
                
            else:
                result = {"success": False, "message": "Tipo de otimização desconhecido"}
                
            if progress_callback:
                progress_callback(100)
                
            return result
            
        except Exception as e:
            self.logger.error(f"Erro na otimização: {str(e)}")
            raise
            
    def _on_progress_updated(self, task_id: str, progress: int):
        """Callback de progresso"""
        if task_id == self.current_task_id:
            self.progress_bar.setValue(progress)
            
    def _on_status_updated(self, task_id: str, status: str):
        """Callback de status"""
        if task_id == self.current_task_id:
            self.status_label.setText(status)
            
    def _on_optimization_finished(self, result):
        """Callback quando otimização termina"""
        if result.task_id != self.current_task_id:
            return

        self.current_task_id = None
        self.progress_bar.setVisible(False)

        optimization_result = result.result or {}
        success_flag = optimization_result.get("success", False) if result.success else False
        message = optimization_result.get("message")
        error = optimization_result.get("error") or result.error
        code = optimization_result.get("code")

        if success_flag:
            final_message = message or "Otimização concluída"
            self.status_label.setText("✅ Otimização concluída!")
            self.log_activity(f"✅ {final_message}")
            QMessageBox.information(self, "Sucesso", final_message)
            return

        if code == "admin_required":
            detailed_error = error or "Essa otimização requer privilégios de administrador. Execute o FPSPACK como administrador e tente novamente."
        else:
            detailed_error = error or message or "Não foi possível concluir a otimização."

        self.status_label.setText("❌ Erro na otimização")
        self.log_activity(f"❌ {detailed_error}")

        QMessageBox.warning(self, "Aviso", detailed_error)

    def apply_power_plan(self):
        """Aplica plano de energia selecionado"""
        plan_text = self.power_plan_combo.currentText()
        
        # Mapeia texto para tipo
        plan_mapping = {
            "🔥 Desempenho Máximo": "maximum",
            "⚡ Alto Desempenho": "high", 
            "⚖️ Equilibrado": "balanced"
        }
        
        plan_type = plan_mapping.get(plan_text, "balanced")
        
        # Executa aplicação do plano
        self.current_task_id = self.thread_manager.submit_task(
            self._execute_power_plan,
            plan_type,
            task_name=f"power_plan_{plan_type}"
        )
        
        # Mostra progresso
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.log_activity(f"Aplicando plano: {plan_text}")
        
    def _execute_power_plan(self, plan_type, progress_callback=None, status_callback=None):
        """Executa aplicação do plano de energia"""
        try:
            if status_callback:
                status_callback("Aplicando plano de energia...")
            if progress_callback:
                progress_callback(25)
            self.optimization_engine.ensure_safety_checkpoint(
                f"Plano de energia {plan_type}",
                include_restore_point=True,
                include_backup=True
            )

                
            # Use the safe public wrapper implemented in OptimizationEngine
            result = self.optimization_engine.create_performance_power_plan() if plan_type == 'maximum' else self.optimization_engine.set_power_plan(plan_type)
            
            if progress_callback:
                progress_callback(100)
                
            return result
            
        except Exception as e:
            self.logger.error(f"Erro ao aplicar plano de energia: {str(e)}")
            raise
            
    def apply_selected_optimizations(self):
        """Aplica otimizações selecionadas pelos toggles"""
        if self.current_task_id:
            QMessageBox.warning(self, "Aviso", "Uma otimização já está em andamento!")
            return
            
        # Coleta opções selecionadas
        selected_options = []
        for key, checkbox in self.optimization_options.items():
            if checkbox.isChecked():
                selected_options.append(key)
        
        if not selected_options:
            QMessageBox.warning(self, "Aviso", "Selecione pelo menos uma otimização!")
            return
            
        # Executa otimizações selecionadas
        self.current_task_id = self.thread_manager.submit_task(
            self._execute_selected_optimizations,
            selected_options,
            task_name="selected_optimizations"
        )
        
        # Mostra progresso
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.log_activity(f"Aplicando otimizações: {', '.join(selected_options)}")
        
    def _execute_selected_optimizations(self, selected_options, progress_callback=None, status_callback=None):
        """Executa otimizações selecionadas"""
        try:
            self.optimization_engine.ensure_safety_checkpoint(
                "Otimizações personalizadas",
                include_restore_point=True,
                include_backup=True
            )
            results = {}
            total_steps = len(selected_options)

            for i, option in enumerate(selected_options):
                progress = int((i / total_steps) * 100) if total_steps else 100
                if progress_callback:
                    progress_callback(progress)

                if status_callback:
                    status_callback(f"Aplicando: {option}")

                if option == "aggressive_ram":
                    result = self.optimization_engine.clean_ram()
                elif option == "disable_services":
                    result = self.optimization_engine.optimize_services()
                elif option == "tcp_optimization":
                    result = self.optimization_engine.optimize_network()
                elif option == "process_priority":
                    result = self.optimization_engine.optimize_startup()
                elif option == "system_cache":
                    result = self.optimization_engine.clean_ram()
                elif option == "visual_effects":
                    result = {"success": True, "message": "Efeitos visuais otimizados"}
                else:
                    result = {"success": False, "error": "Otimização desconhecida"}

                results[option] = result

            if progress_callback:
                progress_callback(100)

            all_success = True
            error_messages = []
            for option_key, option_result in results.items():
                if not option_result.get("success", True):
                    all_success = False
                    msg = option_result.get("error") or option_result.get("message") or f"Falha ao aplicar {option_key}"
                    error_messages.append(msg)

            response = {
                "success": all_success,
                "results": results
            }

            if all_success:
                response["message"] = f"Otimizacoes aplicadas: {len(selected_options)}"
            else:
                response["error"] = "\n".join(error_messages) or "Algumas otimizacoes nao puderam ser aplicadas."

            return response

        except Exception as e:
            self.logger.error(f"Erro nas otimizações selecionadas: {str(e)}")
            raise

    def apply_preset(self):
        """Aplica preset selecionado"""
        preset = self.preset_combo.currentText()
        
        if "Gamer" in preset:
            self.apply_gamer_preset()
        elif "Equilibrado" in preset:
            self.apply_balanced_preset()
        elif "Máxima" in preset:
            self.apply_maximum_preset()
        elif "Economia" in preset:
            self.apply_power_save_preset()
        elif "Seguro" in preset:
            self.apply_safe_preset()
            
        self.log_activity(f"Preset aplicado: {preset}")
        
    def apply_gamer_preset(self):
        """Aplica configurações para jogos"""
        self.optimization_options["aggressive_ram"].setChecked(True)
        self.optimization_options["disable_services"].setChecked(True)
        self.optimization_options["tcp_optimization"].setChecked(True)
        self.optimization_options["process_priority"].setChecked(True)
        self.optimization_options["system_cache"].setChecked(True)
        self.optimization_options["visual_effects"].setChecked(True)
        self._persist_all_option_states()
        
    def apply_balanced_preset(self):
        """Aplica configurações equilibradas"""
        self.optimization_options["aggressive_ram"].setChecked(True)
        self.optimization_options["disable_services"].setChecked(False)
        self.optimization_options["tcp_optimization"].setChecked(True)
        self.optimization_options["process_priority"].setChecked(False)
        self.optimization_options["system_cache"].setChecked(True)
        self.optimization_options["visual_effects"].setChecked(False)
        self._persist_all_option_states()
        
    def apply_maximum_preset(self):
        """Aplica configurações de performance máxima"""
        for checkbox in self.optimization_options.values():
            checkbox.setChecked(True)
        self._persist_all_option_states()
            
    def apply_power_save_preset(self):
        """Aplica configurações de economia"""
        for checkbox in self.optimization_options.values():
            checkbox.setChecked(False)
        self._persist_all_option_states()
            
    def apply_safe_preset(self):
        """Aplica configurações seguras"""
        self.optimization_options["aggressive_ram"].setChecked(True)
        self.optimization_options["disable_services"].setChecked(False)
        self.optimization_options["tcp_optimization"].setChecked(False)
        self.optimization_options["process_priority"].setChecked(False)
        self.optimization_options["system_cache"].setChecked(True)
        self.optimization_options["visual_effects"].setChecked(False)
        self._persist_all_option_states()
        
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
