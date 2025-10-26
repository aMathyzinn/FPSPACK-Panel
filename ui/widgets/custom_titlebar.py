#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Custom Title Bar para FPSPACK PANEL
Barra de título personalizada com controles de janela
"""

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, 
                               QLabel, QFrame, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QFont, QPixmap, QIcon, QPainter, QLinearGradient, QBrush
import qtawesome as qta

class CustomTitleBar(QWidget):
    """Barra de título customizada"""
    
    # Sinais para controle da janela
    minimize_clicked = Signal()
    maximize_clicked = Signal()
    close_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.drag_position = QPoint()
        self.is_maximized = False
        
        # Garante que o widget pinte seu próprio fundo quando o pai usa WA_TranslucentBackground
        self.setAttribute(Qt.WA_StyledBackground)
        self.setAutoFillBackground(True)
        
        self.setup_ui()
        self.setup_style()
        
    def setup_ui(self):
        """Configura a interface da titlebar"""
        self.setFixedHeight(40)
        self.setObjectName("custom_titlebar")
        
        # Layout principal
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 5, 0)
        layout.setSpacing(10)
        
        # Logo e título
        self.create_title_section(layout)
        
        # Espaçador
        layout.addStretch()
        
        # Controles da janela
        self.create_window_controls(layout)
        
    def create_title_section(self, parent_layout):
        """Cria seção do título"""
        title_layout = QHBoxLayout()
        title_layout.setSpacing(10)
        
        # Logo/Ícone usando Phosphor
        logo_label = QLabel()
        logo_label.setObjectName("titlebar_logo")
        logo_label.setFixedSize(24, 24)
        # Usa o ícone da aplicação (QApplication.windowIcon) quando disponível;
        # fallback para ícone de foguete do qtawesome caso não haja ícone definido.
        try:
            from PySide6.QtWidgets import QApplication
            app_icon = QApplication.instance().windowIcon()
            if app_icon and not app_icon.isNull():
                logo_pix = app_icon.pixmap(20, 20)
                logo_label.setPixmap(logo_pix)
            else:
                raise Exception("no icon")
        except Exception:
            rocket_icon = qta.icon('ph.rocket-fill', color='#00D4FF')
            logo_label.setPixmap(rocket_icon.pixmap(20, 20))
        title_layout.addWidget(logo_label)
        
        # Título
        title_label = QLabel("FPSPACK PANEL")
        title_label.setObjectName("titlebar_title")
        title_layout.addWidget(title_label)
        
        parent_layout.addLayout(title_layout)
        
    def create_window_controls(self, parent_layout):
        """Cria controles da janela"""
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(0)
        
        # Botão minimizar com ícone Phosphor
        self.minimize_btn = QPushButton()
        self.minimize_btn.setObjectName("titlebar_minimize")
        self.minimize_btn.setFixedSize(45, 30)
        minimize_icon = qta.icon('ph.minus-bold', color='#F0F6FC')
        self.minimize_btn.setIcon(minimize_icon)
        self.minimize_btn.clicked.connect(self.minimize_clicked.emit)
        controls_layout.addWidget(self.minimize_btn)
        
        # Botão maximizar/restaurar com ícone Phosphor
        self.maximize_btn = QPushButton()
        self.maximize_btn.setObjectName("titlebar_maximize")
        self.maximize_btn.setFixedSize(45, 30)
        maximize_icon = qta.icon('ph.square-bold', color='#F0F6FC')
        self.maximize_btn.setIcon(maximize_icon)
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        controls_layout.addWidget(self.maximize_btn)
        
        # Botão fechar com ícone Phosphor
        self.close_btn = QPushButton()
        self.close_btn.setObjectName("titlebar_close")
        self.close_btn.setFixedSize(45, 30)
        close_icon = qta.icon('ph.x-bold', color='#F0F6FC')
        self.close_btn.setIcon(close_icon)
        self.close_btn.clicked.connect(self.close_clicked.emit)
        controls_layout.addWidget(self.close_btn)
        
        parent_layout.addLayout(controls_layout)
        
    def toggle_maximize(self):
        """Alterna entre maximizar e restaurar"""
        self.is_maximized = not self.is_maximized
        if self.is_maximized:
            # Ícone para restaurar janela
            restore_icon = qta.icon('ph.copy-bold', color='#F0F6FC')
            self.maximize_btn.setIcon(restore_icon)
        else:
            # Ícone para maximizar janela
            maximize_icon = qta.icon('ph.square-bold', color='#F0F6FC')
            self.maximize_btn.setIcon(maximize_icon)
        self.maximize_clicked.emit()
        
    def setup_style(self):
        """Configura o estilo da titlebar"""
        self.setStyleSheet("""
            QWidget#custom_titlebar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #21262D, stop:1 #161B22);
                border: 1px solid #30363D;
                border-radius: 12px;
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
            }
            
            QLabel#titlebar_logo {
                font-size: 16px;
                color: #00D4FF;
            }
            
            QLabel#titlebar_title {
                font-size: 14px;
                font-weight: bold;
                color: #F0F6FC;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QPushButton#titlebar_minimize,
            QPushButton#titlebar_maximize {
                background: transparent;
                border: none;
                color: #F0F6FC;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
            }
            
            QPushButton#titlebar_minimize:hover,
            QPushButton#titlebar_maximize:hover {
                background: rgba(48, 54, 61, 0.8);
                border-radius: 8px;
            }
            
            QPushButton#titlebar_close {
                background: transparent;
                border: none;
                color: #F0F6FC;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
            }
            
            QPushButton#titlebar_close:hover {
                background: #DA3633;
                color: white;
                border-radius: 8px;
            }
        """)
        
    def mousePressEvent(self, event):
        """Inicia o arraste da janela"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.parent_window.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        """Move a janela durante o arraste"""
        if event.buttons() == Qt.LeftButton and self.drag_position:
            self.parent_window.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
            
    def mouseDoubleClickEvent(self, event):
        """Maximiza/restaura janela com duplo clique"""
        if event.button() == Qt.LeftButton:
            self.toggle_maximize()
            event.accept()