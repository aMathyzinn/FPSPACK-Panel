#!/usr/bin/env python3
"""
FPSPACK PANEL - Widget Sobre
Informações sobre o aplicativo
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QTextEdit, QScrollArea)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap, QPalette, QColor, QIcon
import sys
import platform
from pathlib import Path

class AboutWidget(QWidget):
    """Widget de informações sobre o aplicativo"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface do widget"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)

        # Seções principais
        self.create_header(content_layout)
        self.create_app_info(content_layout)
        self.create_system_info(content_layout)
        self.create_credits(content_layout)
        self.create_license(content_layout)

        content_layout.addStretch()

        scroll.setWidget(content)
        layout.addWidget(scroll)

    def create_header(self, parent_layout):
        """Cria cabeçalho com logo e título"""
        header_layout = QVBoxLayout()

        logo_label = QLabel()
        logo_label.setText("FPSPACK PANEL V4.0")
        logo_label.setObjectName("logo_text")
        logo_label.setAlignment(Qt.AlignCenter)

        title = QLabel("FPSPACK PANEL")
        title.setObjectName("about_title")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Sistema Avançado de Otimização para Windows")
        subtitle.setObjectName("about_subtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        header_layout.addWidget(logo_label)
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)

        parent_layout.addLayout(header_layout)

    def create_app_info(self, parent_layout):
        """Cria seção de informações do aplicativo"""
        info_frame = QFrame()
        info_frame.setObjectName("info_frame")
        info_layout = QVBoxLayout(info_frame)

        section_title = QLabel("📱 Informações do Aplicativo")
        section_title.setObjectName("section_title")
        info_layout.addWidget(section_title)

        app_info = [
            ("Versão:", "4.0.0", None),
            ("Data de lançamento:", "Outubro 2025", None),
            ("Desenvolvedor:", "aMathyzin (Matheus Damodara)", None),
            ("Site oficial:", "https://amathyzin.com.br", "https://amathyzin.com.br"),
            ("YouTube:", "https://youtube.com/@amathyzin", "https://youtube.com/@amathyzin"),
            ("Discord:", "https://discord.gg/XBajMu5dcr", "https://discord.gg/XBajMu5dcr"),
            ("Linguagem:", "Python 3.13", None),
            ("Framework GUI:", "PySide6", None),
            ("Licença:", "MIT License (Open Source)", None),
            ("Arquitetura:", platform.machine(), None),
            ("Plataforma:", f"{platform.system()} {platform.release()}", None)
        ]

        for label, value, link in app_info:
            info_row = QHBoxLayout()
            label_widget = QLabel(label)
            label_widget.setObjectName("info_label")
            if link:
                value_widget = QLabel(f'<a href="{link}">{value}</a>')
                value_widget.setTextFormat(Qt.RichText)
                value_widget.setTextInteractionFlags(Qt.TextBrowserInteraction)
                value_widget.setOpenExternalLinks(True)
            else:
                value_widget = QLabel(value)
            value_widget.setObjectName("info_value")

            info_row.addWidget(label_widget)
            info_row.addWidget(value_widget)
            info_row.addStretch()

            info_layout.addLayout(info_row)

        parent_layout.addWidget(info_frame)

    def create_system_info(self, parent_layout):
        """Cria seção de informações do sistema"""
        system_frame = QFrame()
        system_frame.setObjectName("info_frame")
        system_layout = QVBoxLayout(system_frame)
        
        # Título da seção
        section_title = QLabel("💻 Informações do Sistema")
        section_title.setObjectName("section_title")
        system_layout.addWidget(section_title)
        
        # Informações do sistema
        try:
            import psutil
            
            # Informações básicas
            system_info = [
                ("Sistema Operacional:", f"{platform.system()} {platform.release()}"),
                ("Versão:", platform.version()),
                ("Processador:", platform.processor()),
                ("Arquitetura:", platform.architecture()[0]),
                ("Nome do Computador:", platform.node()),
                ("Usuário:", platform.node()),
                ("Python:", f"{sys.version.split()[0]}"),
                ("Memória Total:", f"{psutil.virtual_memory().total // (1024**3)} GB"),
                ("Cores CPU:", str(psutil.cpu_count())),
                ("Cores Físicos:", str(psutil.cpu_count(logical=False)))
            ]
            
        except ImportError:
            system_info = [
                ("Sistema Operacional:", f"{platform.system()} {platform.release()}"),
                ("Versão:", platform.version()),
                ("Processador:", platform.processor()),
                ("Arquitetura:", platform.architecture()[0]),
                ("Nome do Computador:", platform.node()),
                ("Python:", f"{sys.version.split()[0]}")
            ]
        
        for label, value in system_info:
            info_row = QHBoxLayout()
            label_widget = QLabel(label)
            label_widget.setObjectName("info_label")
            value_widget = QLabel(value)
            value_widget.setObjectName("info_value")
            
            info_row.addWidget(label_widget)
            info_row.addWidget(value_widget)
            info_row.addStretch()
            
            system_layout.addLayout(info_row)
            
        parent_layout.addWidget(system_frame)
        
    def create_credits(self, parent_layout):
        """Cria seção de créditos"""
        credits_frame = QFrame()
        credits_frame.setObjectName("info_frame")
        credits_layout = QVBoxLayout(credits_frame)
        
        # Título da seção
        section_title = QLabel("👥 Créditos")
        section_title.setObjectName("section_title")
        credits_layout.addWidget(section_title)
        
        # Texto de créditos
        credits_text = QTextEdit()
        credits_text.setObjectName("credits_text")
        credits_text.setReadOnly(True)
        credits_text.setMaximumHeight(200)
        
        credits_content = """
<b>Desenvolvimento:</b><br>
- aMathyzin (Matheus Damodara) - Idealização e desenvolvimento principal<br>
- Comunidade FPSPACK - Feedback contínuo e testes<br><br>

<b>Bibliotecas e Frameworks:</b><br>
- PySide6 - Interface gráfica moderna<br>
- psutil - Monitoramento do sistema<br>
- matplotlib - Gráficos e visualizações<br>
- pandas - Processamento de dados<br>
- colorlog - Sistema de logs colorido<br><br>

<b>Agradecimentos Especiais:</b><br>
- Comunidade Python<br>
- Qt Project<br>
- Todos os apoiadores e testadores da comunidade FPSPACK
        """
        
        credits_text.setHtml(credits_content)
        credits_layout.addWidget(credits_text)
        
        parent_layout.addWidget(credits_frame)
        
    def create_license(self, parent_layout):
        """Cria seção de licença"""
        license_frame = QFrame()
        license_frame.setObjectName("info_frame")
        license_layout = QVBoxLayout(license_frame)
        
        # Título da seção
        section_title = QLabel("📄 Licença")
        section_title.setObjectName("section_title")
        license_layout.addWidget(section_title)
        
        # Texto da licença
        license_text = QTextEdit()
        license_text.setObjectName("license_text")
        license_text.setReadOnly(True)
        license_text.setMaximumHeight(150)
        
        license_content = """
<b>MIT License</b><br><br>

Copyright (c) 2024 aMathyzin<br><br>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:<br><br>

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
        """
        
        license_text.setHtml(license_content)
        license_layout.addWidget(license_text)
        
        # Botões
        buttons_layout = QHBoxLayout()
        
        website_btn = QPushButton("🌐 Site Oficial")
        website_btn.setObjectName("about_button")
        website_btn.clicked.connect(self.open_website)

        youtube_btn = QPushButton("▶️ YouTube")
        youtube_btn.setObjectName("about_button")
        youtube_btn.clicked.connect(self.open_youtube)

        discord_btn = QPushButton("💬 Discord")
        discord_btn.setObjectName("about_button")
        discord_btn.clicked.connect(self.open_discord)

        buttons_layout.addWidget(website_btn)
        buttons_layout.addWidget(youtube_btn)
        buttons_layout.addWidget(discord_btn)
        buttons_layout.addStretch()
        
        license_layout.addLayout(buttons_layout)
        parent_layout.addWidget(license_frame)
        
    def open_website(self):
        """Abre o site oficial"""
        import webbrowser
        webbrowser.open("https://amathyzin.com.br")

    def open_youtube(self):
        """Abre o canal do YouTube"""
        import webbrowser
        webbrowser.open("https://youtube.com/@amathyzin")

    def open_discord(self):
        """Abre o servidor do Discord"""
        import webbrowser
        webbrowser.open("https://discord.gg/XBajMu5dcr")
