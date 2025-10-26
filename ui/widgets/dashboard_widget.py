#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget Dashboard do FPSPACK PANEL
Exibe informações do sistema em tempo real com gráficos
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                               QLabel, QProgressBar, QFrame, QGroupBox, QScrollArea)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont
import random
from typing import Dict, List
from utils.logger import Logger

class SimulatedGraphWidget(QWidget):
    """Widget simples que simula um gráfico sem dependências externas.

    Mostra uma barra animada que varia aleatoriamente e um histórico textual curto.
    """
    def __init__(self, title: str, color: str, unit: str = "%"):
        super().__init__()
        self.title = title
        self.color = color
        self.unit = unit
        self.history = []
        self.max_points = 60

        # Estado interno liso (EMA)
        self._value = 0.0
        self._ema_alpha = 0.14  # taxa de suavização (menor = mais suave)
        self._target = None
        self._target_hold_ms = 0

        self.setup_ui()
        # Timer interno para animação/atualização visual caso ninguém atualize
        self._sim_timer = QTimer(self)
        self._sim_timer.timeout.connect(self._simulate_step)
        self._sim_timer.start(900)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        title_label = QLabel(self.title)
        title_label.setObjectName("graph_title")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Barra visual representando valor atual
        self.value_bar = QFrame()
        self.value_bar.setFixedHeight(18)
        self.value_bar.setObjectName("sim_value_bar")
        layout.addWidget(self.value_bar)

        # Label do valor atual
        self.current_value_label = QLabel("0" + self.unit)
        self.current_value_label.setObjectName("current_value")
        self.current_value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.current_value_label)

        # Histórico simples
        self.history_label = QLabel("")
        self.history_label.setObjectName("sim_history")
        self.history_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.history_label.setFixedHeight(48)
        layout.addWidget(self.history_label)

    def _simulate_step(self):
        # Atualiza o alvo ocasionalmente e move o valor atual em direção ao alvo
        # para evitar saltos bruscos.
        if self._target is None or self._target_hold_ms <= 0:
            # Escolhe um novo alvo próximo do valor atual (mudança moderada)
            base = self._value if self._value is not None else 50.0
            delta = random.uniform(-12.0, 12.0)
            new_target = max(0.0, min(100.0, base + delta))
            self._target = new_target
            # Mantém o alvo por alguns ciclos (em ms)
            self._target_hold_ms = random.randint(1500, 4000)
        else:
            # diminui o contador
            self._target_hold_ms -= self._sim_timer.interval()

        # Move um passo em direção ao alvo (passo pequeno para suavizar)
        step = 0.18
        next_val = (1.0 - step) * self._value + step * self._target
        self.update_data(next_val)

    def update_data(self, value: float):
        """Recebe um valor (do monitor ou do simulador) e aplica EMA.

        Mantemos um histórico dos valores suavizados para exibir.
        """
        # Inicializa _value se necessário
        if not isinstance(self._value, float):
            self._value = float(value)

        # Se chamada externa fornecer um valor (ex.: system_monitor), usamos
        # esse valor como novo alvo e aplicamos suavização (EMA) para evitar
        # atualização instantânea brusca.
        try:
            incoming = float(value)
        except Exception:
            incoming = self._value

        # Atualiza o valor interno por EMA
        self._value = (self._ema_alpha * incoming) + ((1.0 - self._ema_alpha) * self._value)

        # Mantém histórico do valor suavizado
        self.history.append(self._value)
        if len(self.history) > self.max_points:
            self.history.pop(0)

        # Atualiza barra e labels
        display = self._value
        self.current_value_label.setText(f"{display:.1f}{self.unit}")
        percent = max(0.0, min(1.0, display / 100.0))
        bar_color = self.color
        qcolor = QColor(bar_color)
        # Estiliza com um gradiente proporcional ao valor
        self.value_bar.setStyleSheet(
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {qcolor.name()}, stop:{percent} {qcolor.name()}, stop:{percent} transparent);"
        )

        # Histórico textual (mostra os últimos 6 valores arredondados)
        recent = [f"{v:.0f}%" for v in self.history[-6:]]
        self.history_label.setText(" | ".join(recent))

class SystemInfoCard(QFrame):
    """Card com informações do sistema"""
    
    def __init__(self, title: str, icon: str = ""):
        super().__init__()
        self.title = title
        self.icon = icon
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface do card"""
        self.setObjectName("info_card")
        self.setFixedHeight(120)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Ícone e título
        title_label = QLabel(f"{self.icon} {self.title}")
        title_label.setObjectName("card_title")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Valor principal
        self.main_value = QLabel("0")
        self.main_value.setObjectName("card_main_value")
        self.main_value.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.main_value)
        
        # Valor secundário
        self.secondary_value = QLabel("")
        self.secondary_value.setObjectName("card_secondary_value")
        self.secondary_value.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.secondary_value)
        
        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("card_progress")
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        layout.addWidget(self.progress_bar)
        
    def update_values(self, main_value: str, secondary_value: str = "", progress: int = 0):
        """Atualiza valores do card"""
        self.main_value.setText(main_value)
        self.secondary_value.setText(secondary_value)
        self.progress_bar.setValue(progress)

class ProcessListWidget(QWidget):
    """Widget para lista de processos"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface da lista de processos"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Título
        title_label = QLabel("🔥 Processos com Maior Uso")
        title_label.setObjectName("section_title")
        layout.addWidget(title_label)
        
        # Área de scroll
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("process_scroll")
        
        # Widget de conteúdo
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(5, 5, 5, 5)
        self.content_layout.setSpacing(2)
        
        scroll_area.setWidget(self.content_widget)
        layout.addWidget(scroll_area)
        
    def update_processes(self, processes: List[Dict]):
        """Atualiza lista de processos"""
        # Limpa lista atual
        for i in reversed(range(self.content_layout.count())):
            child = self.content_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
                
        # Adiciona novos processos
        for proc in processes[:8]:  # Top 8
            process_widget = self.create_process_item(proc)
            self.content_layout.addWidget(process_widget)
            
        self.content_layout.addStretch()
        
    def create_process_item(self, process: Dict) -> QWidget:
        """Cria item de processo"""
        widget = QFrame()
        widget.setObjectName("process_item")
        widget.setFixedHeight(40)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Nome do processo
        # Traduz padrão desconhecido para português
        name_label = QLabel(process.get('name', 'Desconhecido'))
        name_label.setObjectName("process_name")
        layout.addWidget(name_label)
        
        layout.addStretch()
        
        # CPU
        cpu_label = QLabel(f"{process.get('cpu_percent', 0):.1f}%")
        cpu_label.setObjectName("process_cpu")
        cpu_label.setFixedWidth(50)
        layout.addWidget(cpu_label)
        
        # RAM
        ram_label = QLabel(f"{process.get('memory_percent', 0):.1f}%")
        ram_label.setObjectName("process_ram")
        ram_label.setFixedWidth(50)
        layout.addWidget(ram_label)
        
        return widget

class DashboardWidget(QWidget):
    """Widget principal do dashboard"""
    
    status_updated = Signal(str)
    
    def __init__(self, system_monitor):
        super().__init__()
        self.system_monitor = system_monitor
        self.logger = Logger()
        
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Configura a interface do dashboard"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(20)
        
        # Título da seção
        title_label = QLabel("📊 Dashboard do Sistema")
        title_label.setObjectName("page_title")
        main_layout.addWidget(title_label)
        
        # Cards de informações
        self.create_info_cards(main_layout)
        
        # Gráficos em tempo real
        self.create_graphs_section(main_layout)
        
        # Seção inferior com processos e informações adicionais
        self.create_bottom_section(main_layout)
        
    def create_info_cards(self, parent_layout):
        """Cria cards de informações"""
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)
        
        # Card CPU
        self.cpu_card = SystemInfoCard("CPU", "🔥")
        cards_layout.addWidget(self.cpu_card)
        
        # Card RAM
        self.ram_card = SystemInfoCard("Memória", "🧠")
        cards_layout.addWidget(self.ram_card)
        
        # Card Disco
        self.disk_card = SystemInfoCard("Disco", "💾")
        cards_layout.addWidget(self.disk_card)
        
        # Card Rede
        self.network_card = SystemInfoCard("Rede", "🌐")
        cards_layout.addWidget(self.network_card)
        
        parent_layout.addLayout(cards_layout)
        
    def create_graphs_section(self, parent_layout):
        """Cria seção de gráficos"""
        graphs_group = QGroupBox("📈 Monitoramento em Tempo Real")
        graphs_group.setObjectName("graphs_group")
        
        graphs_layout = QGridLayout(graphs_group)
        graphs_layout.setSpacing(15)
        
        # Gráficos simulados (sem dependência externa)
        self.cpu_graph = SimulatedGraphWidget("CPU", "#00D4FF", "%")
        graphs_layout.addWidget(self.cpu_graph, 0, 0)

        self.ram_graph = SimulatedGraphWidget("Memória RAM", "#8B5CF6", "%")
        graphs_layout.addWidget(self.ram_graph, 0, 1)

        self.disk_graph = SimulatedGraphWidget("Uso do Disco", "#00FF88", "%")
        graphs_layout.addWidget(self.disk_graph, 1, 0)

        self.temp_graph = SimulatedGraphWidget("Temperatura", "#FF4757", "°C")
        graphs_layout.addWidget(self.temp_graph, 1, 1)
        
        parent_layout.addWidget(graphs_group)
        
    def create_bottom_section(self, parent_layout):
        """Cria seção inferior"""
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)
        
        # Lista de processos
        processes_group = QGroupBox("⚡ Processos Ativos")
        processes_group.setObjectName("processes_group")
        processes_group.setFixedWidth(400)
        
        processes_layout = QVBoxLayout(processes_group)
        self.process_list = ProcessListWidget()
        processes_layout.addWidget(self.process_list)
        
        bottom_layout.addWidget(processes_group)
        
        # Informações do sistema
        system_info_group = QGroupBox("💻 Informações do Sistema")
        system_info_group.setObjectName("system_info_group")
        
        system_info_layout = QVBoxLayout(system_info_group)
        
        # Informações estáticas
        self.system_info_labels = {}
        info_items = [
            ("OS", "Sistema Operacional"),
            ("CPU", "Processador"),
            ("RAM", "Memória Total"),
            ("Uptime", "Tempo Ligado"),
            ("Processes", "Total de Processos")
        ]
        
        for key, label in info_items:
            info_layout = QHBoxLayout()
            
            label_widget = QLabel(f"{label}:")
            label_widget.setObjectName("info_label")
            info_layout.addWidget(label_widget)
            
            value_widget = QLabel("Carregando...")
            value_widget.setObjectName("info_value")
            info_layout.addWidget(value_widget)
            
            info_layout.addStretch()
            
            self.system_info_labels[key] = value_widget
            system_info_layout.addLayout(info_layout)
            
        system_info_layout.addStretch()
        bottom_layout.addWidget(system_info_group)
        
        parent_layout.addLayout(bottom_layout)
        
    def setup_connections(self):
        """Configura conexões"""
        if self.system_monitor:
            self.system_monitor.system_updated.connect(self.update_dashboard)
            
    def update_dashboard(self, system_data: Dict):
        """Atualiza dashboard com novos dados"""
        try:
            # Atualiza cards
            self.update_info_cards(system_data)
            
            # Atualiza gráficos
            self.update_graphs(system_data)
            
            # Atualiza lista de processos
            if 'processes' in system_data:
                self.process_list.update_processes(system_data['processes']['top_processes'])
                
            # Atualiza informações do sistema
            self.update_system_info(system_data)
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar dashboard: {e}")
            
    def update_info_cards(self, system_data: Dict):
        """Atualiza cards de informação"""
        try:
            # CPU Card
            if 'cpu' in system_data:
                cpu_data = system_data['cpu']
                self.cpu_card.update_values(
                    f"{cpu_data['percent']:.1f}%",
                    f"{cpu_data['frequency_current']:.0f} MHz",
                    int(cpu_data['percent'])
                )
                
            # RAM Card
            if 'memory' in system_data:
                memory_data = system_data['memory']
                self.ram_card.update_values(
                    f"{memory_data['used_gb']:.1f} GB",
                    f"de {memory_data['total_gb']:.1f} GB",
                    int(memory_data['percent'])
                )
                
            # Disk Card
            if 'disk' in system_data:
                disk_data = system_data['disk']
                self.disk_card.update_values(
                    f"{disk_data['used_gb']:.1f} GB",
                    f"de {disk_data['total_gb']:.1f} GB",
                    int(disk_data['percent'])
                )
                
            # Network Card
            if 'network' in system_data:
                network_data = system_data['network']
                self.network_card.update_values(
                    f"↓ {network_data['download_speed_mbps']:.1f} MB/s",
                    f"↑ {network_data['upload_speed_mbps']:.1f} MB/s",
                    min(int((network_data['download_speed_mbps'] + network_data['upload_speed_mbps']) * 10), 100)
                )
                
        except Exception as e:
            self.logger.error(f"Erro ao atualizar cards: {e}")
            
    def update_graphs(self, system_data: Dict):
        """Atualiza gráficos"""
        try:
            # CPU Graph
            if 'cpu' in system_data:
                self.cpu_graph.update_data(system_data['cpu']['percent'])
                
            # RAM Graph
            if 'memory' in system_data:
                self.ram_graph.update_data(system_data['memory']['percent'])
                
            # Disk Graph
            if 'disk' in system_data:
                self.disk_graph.update_data(system_data['disk']['percent'])
                
            # Temperature Graph
            if 'temperature' in system_data:
                self.temp_graph.update_data(system_data['temperature']['cpu_temp'])
                
        except Exception as e:
            self.logger.error(f"Erro ao atualizar gráficos: {e}")
            
    def update_system_info(self, system_data: Dict):
        """Atualiza informações do sistema"""
        try:
            import platform
            import time
            
            # Sistema Operacional
            self.system_info_labels['OS'].setText(f"{platform.system()} {platform.release()}")
            
            # CPU
            if 'cpu' in system_data:
                cpu_info = f"{system_data['cpu']['cores_physical']} cores ({system_data['cpu']['cores_logical']} threads)"
                self.system_info_labels['CPU'].setText(cpu_info)
                
            # RAM Total
            if 'memory' in system_data:
                self.system_info_labels['RAM'].setText(f"{system_data['memory']['total_gb']:.1f} GB")
                
            # Uptime
            try:
                import psutil
                boot_time = psutil.boot_time()
                uptime_seconds = time.time() - boot_time
                uptime_hours = int(uptime_seconds // 3600)
                uptime_minutes = int((uptime_seconds % 3600) // 60)
                self.system_info_labels['Uptime'].setText(f"{uptime_hours}h {uptime_minutes}m")
            except:
                self.system_info_labels['Uptime'].setText("N/A")
                
            # Total de Processos
            if 'processes' in system_data:
                self.system_info_labels['Processes'].setText(str(system_data['processes']['total_processes']))
                
        except Exception as e:
            self.logger.error(f"Erro ao atualizar informações do sistema: {e}")