#!/usr/bin/env python3
"""
FPSPACK PANEL - Widget de Configurações
Sistema de configurações com interface moderna
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                               QLabel, QPushButton, QFrame, QGroupBox,                                QSlider, QComboBox, QSpinBox,
                               QScrollArea, QMessageBox, QFileDialog,
                               QTabWidget, QLineEdit, QApplication)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap, QPalette, QColor, QIcon
from utils.config import Config, DEFAULT_BACKUP_PATH
from utils.logger import Logger
from utils.system_integration import configure_startup, ensure_admin, is_admin, apply_debug_mode
from .toggle_switch import ToggleSwitch

class SettingsWidget(QWidget):
    """Widget principal de configurações"""
    
    settings_changed = Signal()
    
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.logger = Logger()
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """Configura a interface do widget"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title = QLabel("⚙️ Configurações")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Tabs de configurações
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("settings_tabs")
        self.tab_widget.setAttribute(Qt.WA_StyledBackground)
        self.tab_widget.setAutoFillBackground(True)
        self.tab_widget.setTabPosition(QTabWidget.North)
        _tb = self.tab_widget.tabBar()
        _tb.setObjectName("settings_tabbar")
        _tb.setExpanding(False)
        
        # Abas
        self.create_general_tab()
        self.create_optimization_tab()
        self.create_cleanup_tab()
        self.create_interface_tab()
        self.create_advanced_tab()
        
        layout.addWidget(self.tab_widget)
        
        # Botões de ação
        self.create_action_buttons(layout)
        
    def create_general_tab(self):
        """Cria aba de configurações gerais"""
        tab = QWidget()
        tab.setObjectName("settings_tab")
        tab.setAttribute(Qt.WA_StyledBackground)
        tab.setAutoFillBackground(True)
        layout = QVBoxLayout(tab)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setObjectName("settings_scroll")
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setWidgetResizable(True)
        content = QWidget()
        content.setObjectName("settings_content")
        content.setAttribute(Qt.WA_StyledBackground)
        content.setAutoFillBackground(True)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(12)
        
        # Configurações de inicialização
        startup_group = QGroupBox("🚀 Inicialização")
        startup_layout = QVBoxLayout(startup_group)
        
        self.auto_start_check = ToggleSwitch("Iniciar com o Windows")
        self.minimize_to_tray_check = ToggleSwitch("Minimizar para bandeja do sistema")
        self.check_updates_check = ToggleSwitch("Verificar atualizações automaticamente")
        
        startup_layout.addWidget(self.auto_start_check)
        startup_layout.addWidget(self.minimize_to_tray_check)
        startup_layout.addWidget(self.check_updates_check)
        
        # Configurações de notificações
        notifications_group = QGroupBox("🔔 Notificações")
        notifications_layout = QVBoxLayout(notifications_group)
        
        self.show_notifications_check = ToggleSwitch("Mostrar notificações")
        self.sound_notifications_check = ToggleSwitch("Sons de notificação")
        self.optimization_alerts_check = ToggleSwitch("Alertas de otimização")
        
        notifications_layout.addWidget(self.show_notifications_check)
        notifications_layout.addWidget(self.sound_notifications_check)
        notifications_layout.addWidget(self.optimization_alerts_check)
        
        # Configurações de logs
        logging_group = QGroupBox("📋 Logs")
        logging_layout = QGridLayout(logging_group)
        
        logging_layout.addWidget(QLabel("Nível de log:"), 0, 0)
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        logging_layout.addWidget(self.log_level_combo, 0, 1)
        
        logging_layout.addWidget(QLabel("Manter logs por (dias):"), 1, 0)
        self.log_retention_spin = QSpinBox()
        self.log_retention_spin.setRange(1, 365)
        self.log_retention_spin.setValue(30)
        logging_layout.addWidget(self.log_retention_spin, 1, 1)
        
        content_layout.addWidget(startup_group)
        content_layout.addWidget(notifications_group)
        content_layout.addWidget(logging_group)
        content_layout.addStretch()
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(tab, "Geral")
        
    def create_optimization_tab(self):
        """Cria aba de configurações de otimização"""
        tab = QWidget()
        tab.setObjectName("settings_tab")
        tab.setAttribute(Qt.WA_StyledBackground)
        tab.setAutoFillBackground(True)
        layout = QVBoxLayout(tab)
        
        scroll = QScrollArea()
        scroll.setObjectName("settings_scroll")
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setWidgetResizable(True)
        content = QWidget()
        content.setObjectName("settings_content")
        content.setAttribute(Qt.WA_StyledBackground)
        content.setAutoFillBackground(True)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(12)
        
        # Configurações de RAM
        ram_group = QGroupBox("💾 Memória RAM")
        ram_layout = QGridLayout(ram_group)
        
        ram_layout.addWidget(QLabel("Limpeza automática de RAM:"), 0, 0)
        self.auto_ram_clean_check = ToggleSwitch("Ativar")
        ram_layout.addWidget(self.auto_ram_clean_check, 0, 1)
        
        ram_layout.addWidget(QLabel("Intervalo (minutos):"), 1, 0)
        self.ram_clean_interval_spin = QSpinBox()
        self.ram_clean_interval_spin.setRange(5, 120)
        self.ram_clean_interval_spin.setValue(30)
        ram_layout.addWidget(self.ram_clean_interval_spin, 1, 1)
        
        ram_layout.addWidget(QLabel("Limite de uso (%):"), 2, 0)
        self.ram_threshold_slider = QSlider(Qt.Horizontal)
        self.ram_threshold_slider.setRange(50, 95)
        self.ram_threshold_slider.setValue(80)
        self.ram_threshold_label = QLabel("80%")
        self.ram_threshold_slider.valueChanged.connect(
            lambda v: self.ram_threshold_label.setText(f"{v}%")
        )
        ram_layout.addWidget(self.ram_threshold_slider, 2, 1)
        ram_layout.addWidget(self.ram_threshold_label, 2, 2)
        
        # Configurações de serviços
        services_group = QGroupBox("⚙️ Serviços")
        services_layout = QVBoxLayout(services_group)
        
        self.safe_mode_check = ToggleSwitch("Modo seguro (não desabilita serviços críticos)")
        self.backup_services_check = ToggleSwitch("Fazer backup das configurações de serviços")
        self.auto_optimize_services_check = ToggleSwitch("Otimizar serviços automaticamente")
        
        services_layout.addWidget(self.safe_mode_check)
        services_layout.addWidget(self.backup_services_check)
        services_layout.addWidget(self.auto_optimize_services_check)
        
        # Configurações de rede
        network_group = QGroupBox("🌐 Rede")
        network_layout = QVBoxLayout(network_group)
        
        self.optimize_tcp_check = ToggleSwitch("Otimizar configurações TCP/IP")
        self.dns_optimization_check = ToggleSwitch("Otimizar DNS")
        self.qos_optimization_check = ToggleSwitch("Otimizar QoS para jogos")
        
        network_layout.addWidget(self.optimize_tcp_check)
        network_layout.addWidget(self.dns_optimization_check)
        network_layout.addWidget(self.qos_optimization_check)
        
        content_layout.addWidget(ram_group)
        content_layout.addWidget(services_group)
        content_layout.addWidget(network_group)
        content_layout.addStretch()
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(tab, "Otimização")
        
    def create_cleanup_tab(self):
        """Cria aba de configurações de limpeza"""
        tab = QWidget()
        tab.setObjectName("settings_tab")
        tab.setAttribute(Qt.WA_StyledBackground)
        tab.setAutoFillBackground(True)
        layout = QVBoxLayout(tab)
        
        scroll = QScrollArea()
        scroll.setObjectName("settings_scroll")
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setWidgetResizable(True)
        content = QWidget()
        content.setObjectName("settings_content")
        content.setAttribute(Qt.WA_StyledBackground)
        content.setAutoFillBackground(True)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(12)
        
        # Configurações de limpeza automática
        auto_cleanup_group = QGroupBox("🧹 Limpeza Automática")
        auto_cleanup_layout = QGridLayout(auto_cleanup_group)
        
        auto_cleanup_layout.addWidget(QLabel("Limpeza automática:"), 0, 0)
        self.auto_cleanup_check = ToggleSwitch("Ativar")
        auto_cleanup_layout.addWidget(self.auto_cleanup_check, 0, 1)
        
        auto_cleanup_layout.addWidget(QLabel("Frequência:"), 1, 0)
        self.cleanup_frequency_combo = QComboBox()
        self.cleanup_frequency_combo.addItems(["Diário", "Semanal", "Mensal"])
        auto_cleanup_layout.addWidget(self.cleanup_frequency_combo, 1, 1)
        
        # Configurações de backup
        backup_group = QGroupBox("💾 Backup")
        backup_layout = QVBoxLayout(backup_group)
        
        self.create_backups_check = ToggleSwitch("Criar backups antes da limpeza")
        self.backup_registry_check = ToggleSwitch("Backup do registro")
        
        backup_layout.addWidget(self.create_backups_check)
        backup_layout.addWidget(self.backup_registry_check)
        
        # Pasta de backup
        backup_path_layout = QHBoxLayout()
        backup_path_layout.addWidget(QLabel("Pasta de backup:"))
        self.backup_path_edit = QLineEdit()
        self.backup_path_edit.setPlaceholderText(DEFAULT_BACKUP_PATH)
        backup_path_btn = QPushButton("Procurar...")
        backup_path_btn.clicked.connect(self.select_backup_folder)
        
        backup_path_layout.addWidget(self.backup_path_edit)
        backup_path_layout.addWidget(backup_path_btn)
        backup_layout.addLayout(backup_path_layout)
        
        # Configurações de exclusões
        exclusions_group = QGroupBox("🚫 Exclusões")
        exclusions_layout = QVBoxLayout(exclusions_group)
        
        self.exclude_important_check = ToggleSwitch("Excluir arquivos importantes automaticamente")
        self.exclude_recent_check = ToggleSwitch("Excluir arquivos modificados recentemente")
        
        exclusions_layout.addWidget(self.exclude_important_check)
        exclusions_layout.addWidget(self.exclude_recent_check)
        
        content_layout.addWidget(auto_cleanup_group)
        content_layout.addWidget(backup_group)
        content_layout.addWidget(exclusions_group)
        content_layout.addStretch()
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(tab, "Limpeza")
        
    def create_interface_tab(self):
        """Cria aba de configurações de interface"""
        tab = QWidget()
        tab.setObjectName("settings_tab")
        tab.setAttribute(Qt.WA_StyledBackground)
        tab.setAutoFillBackground(True)
        layout = QVBoxLayout(tab)
        
        scroll = QScrollArea()
        scroll.setObjectName("settings_scroll")
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setWidgetResizable(True)
        content = QWidget()
        content.setObjectName("settings_content")
        content.setAttribute(Qt.WA_StyledBackground)
        content.setAutoFillBackground(True)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(12)
        
        # Configurações de tema
        theme_group = QGroupBox("🎨 Aparência")
        theme_layout = QGridLayout(theme_group)
        
        theme_layout.addWidget(QLabel("Tema:"), 0, 0)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark"])
        self.theme_combo.setCurrentIndex(0)
        self.theme_combo.setEnabled(False)
        theme_layout.addWidget(self.theme_combo, 0, 1)
        
        theme_layout.addWidget(QLabel("Cor de destaque:"), 1, 0)
        self.accent_color_combo = QComboBox()
        self.accent_color_combo.addItems(["Azul", "Roxo", "Verde", "Vermelho", "Laranja"])
        theme_layout.addWidget(self.accent_color_combo, 1, 1)
        
        # Configurações de animações
        animations_group = QGroupBox("✨ Animações")
        animations_layout = QVBoxLayout(animations_group)
        
        self.enable_animations_check = ToggleSwitch("Ativar animações")
        self.smooth_scrolling_check = ToggleSwitch("Rolagem suave")
        self.fade_effects_check = ToggleSwitch("Efeitos de fade")
        
        animations_layout.addWidget(self.enable_animations_check)
        animations_layout.addWidget(self.smooth_scrolling_check)
        animations_layout.addWidget(self.fade_effects_check)
        
        # Configurações de gráficos
        charts_group = QGroupBox("📊 Gráficos")
        charts_layout = QGridLayout(charts_group)
        
        charts_layout.addWidget(QLabel("Taxa de atualização (ms):"), 0, 0)
        self.chart_update_spin = QSpinBox()
        self.chart_update_spin.setRange(100, 5000)
        self.chart_update_spin.setValue(1000)
        charts_layout.addWidget(self.chart_update_spin, 0, 1)
        
        charts_layout.addWidget(QLabel("Histórico (pontos):"), 1, 0)
        self.chart_history_spin = QSpinBox()
        self.chart_history_spin.setRange(50, 1000)
        self.chart_history_spin.setValue(100)
        charts_layout.addWidget(self.chart_history_spin, 1, 1)
        
        content_layout.addWidget(theme_group)
        content_layout.addWidget(animations_group)
        content_layout.addWidget(charts_group)
        content_layout.addStretch()
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(tab, "Interface")
        
    def create_advanced_tab(self):
        """Cria aba de configurações avançadas"""
        tab = QWidget()
        tab.setObjectName("settings_tab")
        tab.setAttribute(Qt.WA_StyledBackground)
        tab.setAutoFillBackground(True)
        layout = QVBoxLayout(tab)
        
        scroll = QScrollArea()
        scroll.setObjectName("settings_scroll")
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setWidgetResizable(True)
        content = QWidget()
        content.setObjectName("settings_content")
        content.setAttribute(Qt.WA_StyledBackground)
        content.setAutoFillBackground(True)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(12)
        
        # Configurações de segurança
        security_group = QGroupBox("🛡️ Segurança")
        security_layout = QVBoxLayout(security_group)
        
        self.require_admin_check = ToggleSwitch("Sempre executar como administrador")
        self.create_restore_points_check = ToggleSwitch("Criar pontos de restauração")
        self.verify_signatures_check = ToggleSwitch("Verificar assinaturas digitais")
        
        security_layout.addWidget(self.require_admin_check)
        security_layout.addWidget(self.create_restore_points_check)
        security_layout.addWidget(self.verify_signatures_check)
        
        # Configurações de performance
        performance_group = QGroupBox("⚡ Performance")
        performance_layout = QGridLayout(performance_group)
        
        performance_layout.addWidget(QLabel("Threads de trabalho:"), 0, 0)
        self.worker_threads_spin = QSpinBox()
        self.worker_threads_spin.setRange(1, 16)
        self.worker_threads_spin.setValue(4)
        performance_layout.addWidget(self.worker_threads_spin, 0, 1)
        
        performance_layout.addWidget(QLabel("Cache de memória (MB):"), 1, 0)
        self.memory_cache_spin = QSpinBox()
        self.memory_cache_spin.setRange(64, 1024)
        self.memory_cache_spin.setValue(256)
        performance_layout.addWidget(self.memory_cache_spin, 1, 1)
        
        # Configurações de debug
        debug_group = QGroupBox("🐛 Debug")
        debug_layout = QVBoxLayout(debug_group)
        
        self.debug_mode_check = ToggleSwitch("Modo debug")
        self.verbose_logging_check = ToggleSwitch("Log detalhado")
        self.performance_monitoring_check = ToggleSwitch("Monitoramento de performance")
        
        debug_layout.addWidget(self.debug_mode_check)
        debug_layout.addWidget(self.verbose_logging_check)
        debug_layout.addWidget(self.performance_monitoring_check)
        
        content_layout.addWidget(security_group)
        content_layout.addWidget(performance_group)
        content_layout.addWidget(debug_group)
        content_layout.addStretch()
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(tab, "Avançado")
        
    def create_action_buttons(self, parent_layout):
        """Cria botões de ação"""
        buttons_layout = QHBoxLayout()
        
        # Botões
        save_btn = QPushButton("💾 Salvar")
        save_btn.setObjectName("settings_button_primary")
        save_btn.clicked.connect(self.save_settings)
        
        reset_btn = QPushButton("🔄 Restaurar Padrões")
        reset_btn.setObjectName("settings_button")
        reset_btn.clicked.connect(self.reset_settings)
        
        export_btn = QPushButton("📤 Exportar")
        export_btn.setObjectName("settings_button")
        export_btn.clicked.connect(self.export_settings)
        
        import_btn = QPushButton("📥 Importar")
        import_btn.setObjectName("settings_button")
        import_btn.clicked.connect(self.import_settings)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(reset_btn)
        buttons_layout.addWidget(export_btn)
        buttons_layout.addWidget(import_btn)
        buttons_layout.addStretch()
        
        parent_layout.addLayout(buttons_layout)
        
    def load_settings(self):
        """Carrega configurações salvas"""
        try:
            # Aba Geral
            self.auto_start_check.setChecked(self.config.get("app.auto_start", False))
            self.minimize_to_tray_check.setChecked(self.config.get("app.minimize_to_tray", True))
            self.check_updates_check.setChecked(self.config.get("app.check_updates", True))
            
            self.show_notifications_check.setChecked(self.config.get("notifications.enabled", True))
            self.sound_notifications_check.setChecked(self.config.get("notifications.sound", False))
            self.optimization_alerts_check.setChecked(self.config.get("notifications.optimization_alerts", True))
            
            self.log_level_combo.setCurrentText(self.config.get("logging.level", "INFO"))
            self.log_retention_spin.setValue(self.config.get("logging.retention_days", 30))
            
            # Aba Otimização
            self.auto_ram_clean_check.setChecked(self.config.get("optimization.auto_ram_cleanup", False))
            self.ram_clean_interval_spin.setValue(self.config.get("optimization.ram_cleanup_interval", 30))
            self.ram_threshold_slider.setValue(self.config.get("optimization.ram_threshold", 80))
            
            self.safe_mode_check.setChecked(self.config.get("optimization.safe_mode", True))
            self.backup_services_check.setChecked(self.config.get("optimization.backup_services", True))
            self.auto_optimize_services_check.setChecked(self.config.get("optimization.auto_optimize_services", False))
            
            # Aba Limpeza
            self.auto_cleanup_check.setChecked(self.config.get("cleanup.auto_cleanup", False))
            schedule_value = self.config.get("cleanup.cleanup_schedule", "weekly")
            schedule_index = {"daily": 0, "weekly": 1, "monthly": 2}.get(schedule_value, 1)
            self.cleanup_frequency_combo.setCurrentIndex(schedule_index)
            
            self.create_backups_check.setChecked(self.config.get("cleanup.create_backups", True))
            self.backup_registry_check.setChecked(self.config.get("cleanup.backup_registry", True))
            self.backup_path_edit.setText(self.config.get("cleanup.backup_path", DEFAULT_BACKUP_PATH))
            
            # Aba Interface
            self.theme_combo.setCurrentText("Dark")
            self.accent_color_combo.setCurrentText(self.config.get("ui.accent_color", "Azul"))
            
            self.enable_animations_check.setChecked(self.config.get("ui.animations", True))
            self.smooth_scrolling_check.setChecked(self.config.get("ui.smooth_scrolling", True))
            self.fade_effects_check.setChecked(self.config.get("ui.fade_effects", True))
            
            self.chart_update_spin.setValue(self.config.get("ui.chart_update_rate", 1000))
            self.chart_history_spin.setValue(self.config.get("ui.chart_history_points", 100))
            
            # Aba Avançado
            self.require_admin_check.setChecked(self.config.get("advanced.require_admin", False))
            self.create_restore_points_check.setChecked(self.config.get("advanced.create_restore_points", True))
            self.verify_signatures_check.setChecked(self.config.get("advanced.verify_signatures", True))
            
            self.worker_threads_spin.setValue(self.config.get("advanced.worker_threads", 4))
            self.memory_cache_spin.setValue(self.config.get("advanced.memory_cache_mb", 256))
            
            self.debug_mode_check.setChecked(self.config.get("advanced.debug_mode", False))
            self.verbose_logging_check.setChecked(self.config.get("advanced.verbose_logging", False))
            self.performance_monitoring_check.setChecked(self.config.get("advanced.performance_monitoring", False))
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar configurações: {str(e)}")
            
    def save_settings(self):
        """Salva configurações"""
        try:
            previous_auto_start = self.config.get("app.auto_start", False)
            previous_require_admin = self.config.get("advanced.require_admin", False)
            previous_debug = self.config.get("advanced.debug_mode", False)

            # Aba Geral
            auto_start_enabled = self.auto_start_check.isChecked()
            self.config.set("app.auto_start", auto_start_enabled)
            self.config.set("app.minimize_to_tray", self.minimize_to_tray_check.isChecked())
            self.config.set("app.check_updates", self.check_updates_check.isChecked())

            self.config.set("notifications.enabled", self.show_notifications_check.isChecked())
            self.config.set("notifications.sound", self.sound_notifications_check.isChecked())
            self.config.set("notifications.optimization_alerts", self.optimization_alerts_check.isChecked())

            self.config.set("logging.level", self.log_level_combo.currentText())
            self.config.set("logging.retention_days", self.log_retention_spin.value())

            # Aba Otimização
            self.config.set("optimization.auto_ram_cleanup", self.auto_ram_clean_check.isChecked())
            self.config.set("optimization.ram_cleanup_interval", self.ram_clean_interval_spin.value())
            self.config.set("optimization.ram_threshold", self.ram_threshold_slider.value())
            self.config.set("optimization.safe_mode", self.safe_mode_check.isChecked())
            self.config.set("optimization.backup_services", self.backup_services_check.isChecked())
            self.config.set("optimization.auto_optimize_services", self.auto_optimize_services_check.isChecked())

            # Aba Limpeza
            schedule_choice = {0: "daily", 1: "weekly", 2: "monthly"}.get(self.cleanup_frequency_combo.currentIndex(), "weekly")
            self.config.set("cleanup.auto_cleanup", self.auto_cleanup_check.isChecked())
            self.config.set("cleanup.cleanup_schedule", schedule_choice)
            self.config.set("cleanup.create_backups", self.create_backups_check.isChecked())
            self.config.set("cleanup.backup_registry", self.backup_registry_check.isChecked())
            backup_path = self.backup_path_edit.text().strip() or DEFAULT_BACKUP_PATH
            self.backup_path_edit.setText(backup_path)
            self.config.set("cleanup.backup_path", backup_path)

            # Aba Interface
            theme_choice = "Dark"
            self.theme_combo.setCurrentText("Dark")
            self.config.set("ui.theme", theme_choice)
            self.config.set("ui.accent_color", self.accent_color_combo.currentText())
            self.config.set("ui.animations", self.enable_animations_check.isChecked())
            self.config.set("ui.smooth_scrolling", self.smooth_scrolling_check.isChecked())
            self.config.set("ui.fade_effects", self.fade_effects_check.isChecked())
            self.config.set("ui.chart_update_rate", self.chart_update_spin.value())
            self.config.set("ui.chart_history_points", self.chart_history_spin.value())

            # Aba Avançado
            require_admin_value = self.require_admin_check.isChecked()
            self.config.set("advanced.require_admin", require_admin_value)
            self.config.set("advanced.create_restore_points", self.create_restore_points_check.isChecked())
            self.config.set("advanced.verify_signatures", self.verify_signatures_check.isChecked())
            self.config.set("advanced.worker_threads", self.worker_threads_spin.value())
            self.config.set("advanced.memory_cache_mb", self.memory_cache_spin.value())
            debug_mode_value = self.debug_mode_check.isChecked()
            self.config.set("advanced.debug_mode", debug_mode_value)
            self.config.set("advanced.verbose_logging", self.verbose_logging_check.isChecked())
            self.config.set("advanced.performance_monitoring", self.performance_monitoring_check.isChecked())

            # Integrações adicionais
            if auto_start_enabled != previous_auto_start:
                if not configure_startup(auto_start_enabled):
                    QMessageBox.warning(self, "Aviso", "Não foi possível atualizar a inicialização com o Windows.")
                    self.config.set("app.auto_start", previous_auto_start)
                    self.auto_start_check.setChecked(previous_auto_start)

            if require_admin_value and not previous_require_admin and not is_admin():
                if ensure_admin(True, self.logger):
                    QMessageBox.information(self, "Reinicialização necessária", "O aplicativo será reaberto com privilégios administrativos.")
                    app = QApplication.instance()
                    if app is not None:
                        app.quit()
                    return
                else:
                    QMessageBox.warning(self, "Aviso", "Não foi possível solicitar privilégios administrativos.")
            if debug_mode_value != previous_debug:
                apply_debug_mode(debug_mode_value, self.logger)

            QMessageBox.information(self, "Sucesso", "Configurações salvas com sucesso!")
            self.settings_changed.emit()

        except Exception as e:
            self.logger.error(f"Erro ao salvar configurações: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Erro ao salvar configurações: {str(e)}")

    def reset_settings(self):
        """Restaura configurações padrão"""
        reply = QMessageBox.question(
            self, "Confirmar", 
            "Tem certeza que deseja restaurar as configurações padrão?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Reseta todas as configurações para os valores de fábrica.
                self.config.reset_to_default()
                self.load_settings()
                QMessageBox.information(self, "Sucesso", "Configurações restauradas para o padrão!")
                self.settings_changed.emit()
            except Exception as e:
                self.logger.error(f"Erro ao restaurar configurações: {str(e)}")
                QMessageBox.critical(self, "Erro", f"Erro ao restaurar configurações: {str(e)}")
                
    def export_settings(self):
        """Exporta configurações para arquivo"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exportar Configurações", 
            "fpspack_config.json", 
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                self.config.export_config(file_path)
                QMessageBox.information(self, "Sucesso", "Configurações exportadas com sucesso!")
            except Exception as e:
                self.logger.error(f"Erro ao exportar configurações: {str(e)}")
                QMessageBox.critical(self, "Erro", f"Erro ao exportar configurações: {str(e)}")
                
    def import_settings(self):
        """Importa configurações de arquivo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Importar Configurações", 
            "", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                self.config.import_config(file_path)
                self.load_settings()
                QMessageBox.information(self, "Sucesso", "Configurações importadas com sucesso!")
                self.settings_changed.emit()
            except Exception as e:
                self.logger.error(f"Erro ao importar configurações: {str(e)}")
                QMessageBox.critical(self, "Erro", f"Erro ao importar configurações: {str(e)}")
                
    def select_backup_folder(self):
        """Seleciona pasta de backup"""
        folder = QFileDialog.getExistingDirectory(
            self, "Selecionar Pasta de Backup", 
            self.backup_path_edit.text()
        )
        
        if folder:
            self.backup_path_edit.setText(folder)
