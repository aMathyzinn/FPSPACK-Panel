#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Janela Principal do FPSPACK PANEL
Interface moderna com tema dark e animações
"""

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QGridLayout, QPushButton, QLabel, QProgressBar,
                               QTabWidget, QFrame, QScrollArea, QGroupBox,
                               QSlider, QComboBox, QCheckBox, QTextEdit,
                               QSystemTrayIcon, QMenu, QMessageBox)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Signal, QEvent
from PySide6.QtGui import QFont, QPixmap, QPalette, QColor, QIcon, QLinearGradient
from ui.widgets.dashboard_widget import DashboardWidget
from ui.widgets.optimization_widget import OptimizationWidget
from ui.widgets.cleanup_widget import CleanupWidget
from ui.widgets.settings_widget import SettingsWidget
from ui.widgets.about_widget import AboutWidget
from ui.widgets.custom_titlebar import CustomTitleBar
from ui.styles.dark_theme import DarkTheme
from utils.config import Config
from core.optimization_engine import OptimizationEngine
from core.cleanup_engine import CleanupEngine
from utils.animations import AnimationManager

class MainWindow(QMainWindow):
    def __init__(self, system_monitor):
        super().__init__()
        self.system_monitor = system_monitor
        self.optimization_engine = OptimizationEngine()
        self.cleanup_engine = CleanupEngine()
        self.animation_manager = AnimationManager()
        self.config = Config()
        
        # Configurar janela sem frame padrão
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.setup_ui()
        self.setup_connections()
        self.setup_system_tray()
        self.apply_theme()

    def show_shutdown_overlay(self):
        """Exibe animação enquanto os processos de encerramento são finalizados."""
        if getattr(self, "_shutdown_overlay", None):
            return

        from PySide6.QtWidgets import QApplication

        overlay = QWidget(self)
        overlay.setObjectName("shutdown_overlay")
        overlay.setAttribute(Qt.WA_StyledBackground, True)
        overlay.setStyleSheet("""
            QWidget#shutdown_overlay {
                background: rgba(13, 17, 23, 220);
            }
            QFrame#shutdown_container {
                background: rgba(33, 38, 45, 235);
                border: 1px solid rgba(0, 212, 255, 0.35);
                border-radius: 14px;
            }
            QLabel#shutdown_label {
                color: #F0F6FC;
                font-size: 15px;
                font-weight: 600;
            }
        """)
        overlay.setGeometry(self.rect())

        layout = QVBoxLayout(overlay)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)

        container = QFrame()
        container.setObjectName("shutdown_container")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(28, 24, 28, 28)
        container_layout.setSpacing(16)

        label = QLabel("Finalizando processos...")
        label.setObjectName("shutdown_label")
        label.setAlignment(Qt.AlignCenter)

        progress = QProgressBar()
        progress.setObjectName("shutdown_progress")
        progress.setRange(0, 0)
        progress.setTextVisible(False)
        progress.setFixedWidth(240)

        container_layout.addWidget(label)
        container_layout.addWidget(progress, alignment=Qt.AlignCenter)
        layout.addWidget(container)

        overlay.show()
        overlay.raise_()
        QApplication.processEvents()
        self._shutdown_overlay = overlay

    def setup_ui(self):
        """Configura a interface principal"""
        self.setWindowTitle("FPSPACK PANEL v1.0 - Sistema de Otimização Avançado")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Widget central
        central_widget = QWidget()
        # Garante pintura do fundo mesmo com WA_TranslucentBackground na janela
        central_widget.setAttribute(Qt.WA_StyledBackground)
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Titlebar customizada
        self.titlebar = CustomTitleBar(self)
        self.titlebar.minimize_clicked.connect(self.showMinimized)
        self.titlebar.maximize_clicked.connect(self.toggle_maximize)
        self.titlebar.close_clicked.connect(self.close)
        main_layout.addWidget(self.titlebar)
        
        # Container para o conteúdo principal
        content_container = QWidget()
        content_layout = QHBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Sidebar
        self.create_sidebar(content_layout)
        
        # Área de conteúdo principal
        self.create_content_area(content_layout)
        
        main_layout.addWidget(content_container)
        
    def create_sidebar(self, parent_layout):
        """Cria a barra lateral de navegação"""
        sidebar = QFrame()
        sidebar.setFixedWidth(250)
        sidebar.setObjectName("sidebar")
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 30, 20, 30)
        sidebar_layout.setSpacing(15)
        
        # Logo/Título
        title_label = QLabel("FPSPACK")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(title_label)
        
        subtitle_label = QLabel("PANEL")
        subtitle_label.setObjectName("subtitle")
        subtitle_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(subtitle_label)
        
        sidebar_layout.addSpacing(30)
        
        # Botões de navegação
        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "🏠 Dashboard", True),
            ("optimization", "⚡ Otimização", False),
            ("cleanup", "🧹 Limpeza", False),
            ("settings", "⚙️ Configurações", False),
            ("about", "ℹ️ Sobre", False)
        ]
        
        for key, text, is_active in nav_items:
            btn = QPushButton(text)
            btn.setObjectName("nav_button")
            btn.setCheckable(True)
            btn.setChecked(is_active)
            btn.clicked.connect(lambda checked, k=key: self.switch_tab(k))
            self.nav_buttons[key] = btn
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        
        # Botão de modo turbo
        turbo_btn = QPushButton("🚀 MODO TURBO")
        turbo_btn.setObjectName("turbo_button")
        turbo_btn.clicked.connect(self.activate_turbo_mode)
        sidebar_layout.addWidget(turbo_btn)
        
        parent_layout.addWidget(sidebar)
        
    def create_content_area(self, parent_layout):
        """Cria a área de conteúdo principal"""
        content_frame = QFrame()
        content_frame.setObjectName("content_frame")
        
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(30, 30, 30, 30)
        
        # Header com informações do sistema
        self.create_header(content_layout)
        
        # Stack de widgets para diferentes abas
        self.content_stack = QWidget()
        self.stack_layout = QVBoxLayout(self.content_stack)
        self.stack_layout.setContentsMargins(0, 0, 0, 0)
        
        # Widgets das abas
        settings_widget = SettingsWidget()
        settings_widget.settings_changed.connect(self.on_settings_changed)
        self.widgets = {
            "dashboard": DashboardWidget(self.system_monitor),
            "optimization": OptimizationWidget(self.optimization_engine),
            "cleanup": CleanupWidget(self.cleanup_engine),
            "settings": settings_widget,
            "about": AboutWidget()
        }
        self.settings_widget = settings_widget
        
        # Adiciona widgets ao stack (inicialmente apenas dashboard visível)
        for key, widget in self.widgets.items():
            widget.setVisible(key == "dashboard")
            self.stack_layout.addWidget(widget)
        
        content_layout.addWidget(self.content_stack)
        parent_layout.addWidget(content_frame)
        
    def create_header(self, parent_layout):
        """Cria o cabeçalho com informações do sistema"""
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(80)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        # Informações do sistema
        system_info = QHBoxLayout()
        
        # CPU
        cpu_frame = self.create_info_frame("CPU", "0%")
        self.cpu_label = cpu_frame.findChild(QLabel, "value")
        system_info.addWidget(cpu_frame)
        
        # RAM
        ram_frame = self.create_info_frame("RAM", "0 GB")
        self.ram_label = ram_frame.findChild(QLabel, "value")
        system_info.addWidget(ram_frame)
        
        # Disco
        disk_frame = self.create_info_frame("DISCO", "0%")
        self.disk_label = disk_frame.findChild(QLabel, "value")
        system_info.addWidget(disk_frame)
        
        # Temperatura
        temp_frame = self.create_info_frame("TEMP", "0°C")
        self.temp_label = temp_frame.findChild(QLabel, "value")
        system_info.addWidget(temp_frame)
        
        header_layout.addLayout(system_info)
        header_layout.addStretch()
        
        # Botões de ação rápida
        quick_actions = QHBoxLayout()
        
        ram_clean_btn = QPushButton("🧠 Limpar RAM")
        ram_clean_btn.setObjectName("quick_action")
        ram_clean_btn.clicked.connect(self.quick_ram_clean)
        quick_actions.addWidget(ram_clean_btn)
        
        boost_btn = QPushButton("⚡ Boost")
        boost_btn.setObjectName("quick_action")
        boost_btn.clicked.connect(self.quick_boost)
        quick_actions.addWidget(boost_btn)
        
        header_layout.addLayout(quick_actions)
        parent_layout.addWidget(header)
        
    def create_info_frame(self, title, value):
        """Cria um frame de informação do sistema"""
        frame = QFrame()
        frame.setObjectName("info_frame")
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(2)
        
        title_label = QLabel(title)
        title_label.setObjectName("info_title")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setObjectName("value")
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)
        
        return frame
        
    def setup_connections(self):
        """Configura as conexões de sinais"""
        # Timer para atualizar informações do sistema
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_system_info)
        self.update_timer.start(1000)  # Atualiza a cada segundo
        
        # Conexões dos widgets
        for widget in self.widgets.values():
            if hasattr(widget, 'status_updated'):
                widget.status_updated.connect(self.show_status_message)
                
    def setup_system_tray(self):
        """Configura o ícone na bandeja do sistema"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            
            # Criar ícone simples usando QIcon
            icon = self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon)
            self.tray_icon.setIcon(icon)
            self.tray_icon.setToolTip("FPSPACK Panel - Sistema de Otimização")
            
            # Menu do tray
            tray_menu = QMenu()
            
            show_action = tray_menu.addAction("Mostrar")
            show_action.triggered.connect(self.show)
            
            tray_menu.addSeparator()
            
            ram_action = tray_menu.addAction("Limpar RAM")
            ram_action.triggered.connect(self.quick_ram_clean)
            
            boost_action = tray_menu.addAction("Modo Turbo")
            boost_action.triggered.connect(self.activate_turbo_mode)
            
            tray_menu.addSeparator()
            
            quit_action = tray_menu.addAction("Sair")
            # Garante que 'Sair' encerre totalmente o app e remova o ícone da bandeja
            quit_action.triggered.connect(self._tray_quit)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
            
    def apply_theme(self):
        """Mantém o tema dark padrão e aplica apenas cores de destaque."""
        accent_choice = (self.config.get("ui.accent_color", "Azul") or "Azul").lower()

        accent_palette = {
            "azul": ("#00D4FF", "#8B5CF6"),
            "roxo": ("#8B5CF6", "#C084FC"),
            "verde": ("#00FF88", "#43FFAF"),
            "vermelho": ("#FF4757", "#FF6B81"),
            "laranja": ("#FFA726", "#FFC371"),
        }
        primary, secondary = accent_palette.get(accent_choice, accent_palette["azul"])

        base_stylesheet = DarkTheme.get_stylesheet()
        stylesheet = base_stylesheet.replace("#00D4FF", primary).replace("#8B5CF6", secondary)

        pr, pg, pb = self._hex_to_rgb(primary)
        sr, sg, sb = self._hex_to_rgb(secondary)
        for prefix in ("rgba(0,212,255", "rgba(0, 212, 255"):
            stylesheet = stylesheet.replace(prefix, f"rgba({pr},{pg},{pb}")
        for prefix in ("rgba(139,92,246", "rgba(139, 92, 246"):
            stylesheet = stylesheet.replace(prefix, f"rgba({sr},{sg},{sb}")

        self.setStyleSheet(stylesheet)

    @staticmethod
    def _hex_to_rgb(hex_color: str):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    def on_settings_changed(self):
        """Reaplica personalizações ao atualizar configurações."""
        try:
            self.config.reload()
        except Exception:
            pass
        self.apply_theme()

    def switch_tab(self, tab_key):
        """Troca entre as abas"""
        # Atualiza botões de navegação
        for key, btn in self.nav_buttons.items():
            btn.setChecked(key == tab_key)
            
        # Mostra/esconde widgets
        for key, widget in self.widgets.items():
            widget.setVisible(key == tab_key)
            
        # Animação de transição
        self.animation_manager.fade_in(self.widgets[tab_key])
        
    def toggle_maximize(self):
        """Alterna entre maximizar e restaurar janela"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
        
    def update_system_info(self):
        """Atualiza as informações do sistema no header"""
        if self.system_monitor:
            info = self.system_monitor.get_current_info()
            
            self.cpu_label.setText(f"{info['cpu_percent']:.1f}%")
            self.ram_label.setText(f"{info['ram_used_gb']:.1f} GB")
            self.disk_label.setText(f"{info['disk_percent']:.1f}%")
            self.temp_label.setText(f"{info['cpu_temp']:.0f}°C")
            
    def quick_ram_clean(self):
        """Limpeza rápida de RAM"""
        self.show_status_message("🧠 Limpando RAM...", 2000)
        self.optimization_engine.clean_ram()
        self.show_status_message("✅ RAM limpa com sucesso!", 3000)
        
    def quick_boost(self):
        """Boost rápido do sistema"""
        self.show_status_message("⚡ Aplicando boost...", 2000)
        self.optimization_engine.ensure_safety_checkpoint(
            "Boost rapido",
            include_restore_point=True,
            include_backup=True
        )
        self.optimization_engine.apply_quick_boost()
        self.show_status_message("🚀 Boost aplicado com sucesso!", 3000)
        
    def activate_turbo_mode(self):
        """Ativa o modo turbo"""
        reply = QMessageBox.question(
            self, 
            "Modo Turbo", 
            "O Modo Turbo aplicará otimizações avançadas.\nDeseja continuar?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.show_status_message("🚀 Ativando Modo Turbo...", 3000)
            self.optimization_engine.ensure_safety_checkpoint(
                "Modo turbo",
                include_restore_point=True,
                include_backup=True
            )
            self.optimization_engine.activate_turbo_mode()
            self.show_status_message("⚡ Modo Turbo ativado!", 5000)
            
    def show_status_message(self, message, duration=3000):
        """Mostra mensagem de status"""
        if hasattr(self, 'statusBar'):
            self.statusBar().showMessage(message, duration)
            
    def closeEvent(self, event):
        """Evento de fechamento da janela"""
        # Se houver ícone na bandeja visível, ao clicar no botão fechar
        # queremos encerrar a aplicação completamente, não apenas esconder.
        # Chamamos quit() para garantir que o loop de eventos finalize e
        # o sinal aboutToQuit execute a limpeza registrada em main.FPSPackPanel.
        if hasattr(self, 'tray_icon') and self.tray_icon and self.tray_icon.isVisible():
            try:
                # Esconder ícone do sistema antes de sair
                self.tray_icon.hide()
            except Exception:
                pass
        # Exibe animação de encerramento para evitar congelamento aparente
        self.show_shutdown_overlay()
        self.setEnabled(False)
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()
        # Aceita o evento e força encerramento da aplicação
        event.accept()
        try:
            QApplication.quit()
        except Exception:
            # Fallback para encerrar processo
            import sys
            sys.exit(0)

    def changeEvent(self, event):
        """Detecta mudança de estado da janela (minimizado/restaurado)"""
        if event.type() == QEvent.WindowStateChange:
            if self.isMinimized():
                if self.system_monitor:
                    self.system_monitor.stop_monitoring()
            elif self.isVisible():
                if self.system_monitor:
                    self.system_monitor.start_monitoring()
        super().changeEvent(event)

    def focusInEvent(self, event):
        """Retoma monitoramento ao focar (janela recebeu foco)"""
        if self.system_monitor:
            self.system_monitor.start_monitoring()
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        """Pausa monitoramento ao perder foco (janela perdeu foco)"""
        if self.system_monitor:
            self.system_monitor.stop_monitoring()
        super().focusOutEvent(event)

    def _tray_quit(self):
        """Handler para ação 'Sair' no menu da bandeja: remove o ícone e encerra o app."""
        try:
            if hasattr(self, 'tray_icon') and self.tray_icon:
                self.tray_icon.hide()
        except Exception:
            pass

        try:
            from PySide6.QtWidgets import QApplication
            QApplication.quit()
        except Exception:
            import sys
            sys.exit(0)
