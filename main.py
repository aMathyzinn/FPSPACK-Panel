#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FPSPACK PANEL - Sistema de Otimização Avançado
Desenvolvido por aMathyzin
Versão: 1.0.0
"""

import sys
import os
from PySide6.QtWidgets import QApplication, QSplashScreen, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QTimer, QPointF, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon, QFont, QPixmap, QTransform, QPainter, QPen, QColor
import math
from ui.main_window import MainWindow
from core.system_monitor import SystemMonitor
from core.thread_manager import get_thread_manager, shutdown_thread_manager
from utils.config import Config
from utils.logger import Logger
from utils.system_integration import ensure_admin, apply_debug_mode, is_admin

class FPSPackPanel:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.setup_application()
        self.main_window = None
        self.system_monitor = None
        self.thread_manager = None
        self.logger = Logger()
        
        # Configura finalização adequada
        self.app.aboutToQuit.connect(self.cleanup)
        
    def setup_application(self):
        """Configura a aplicação"""
        self.app.setApplicationName("FPSPACK PANEL")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("aMathyzin")
        
        # Define fonte padrão
        font = QFont("Segoe UI", 10)
        self.app.setFont(font)
        
        # Define ícone da aplicação — prioriza img/imgif.ico, com fallback para assets/icon.ico
        base_dir = os.path.dirname(__file__)
        preferred_icon = os.path.join(base_dir, "img", "imgif.ico")
        fallback_icon = os.path.join(base_dir, "assets", "icon.ico")

        if os.path.exists(preferred_icon):
            self.app.setWindowIcon(QIcon(preferred_icon))
        elif os.path.exists(fallback_icon):
            self.app.setWindowIcon(QIcon(fallback_icon))
    
    def initialize_components(self):
        """Inicializa os componentes principais"""
        try:
            # Inicializa configurações
            Config.load()
            
            # Inicializa gerenciador de threads
            self.thread_manager = get_thread_manager()
            
            # Inicializa monitor do sistema
            self.system_monitor = SystemMonitor()
            
            # Inicializa janela principal
            self.main_window = MainWindow(self.system_monitor)
            
            self.logger.info("Componentes inicializados com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar componentes: {e}")
            return False
    
    def run(self):
        """Executa a aplicação"""
        if not self.initialize_components():
            sys.exit(1)
        # Se houver uma imagem de splash, exibe por 4 segundos antes de mostrar a janela
        splash_path = os.path.join(os.path.dirname(__file__), "img", "splash.webp")
        if os.path.exists(splash_path):
            try:
                pix = QPixmap(splash_path)
                # Reduz tamanho do splash para largura máxima 640 mantendo proporção
                scaled_pix = pix.scaled(640, 360, Qt.KeepAspectRatio, Qt.SmoothTransformation)

                # Cria widget customizado para splash com imagem reduzida
                splash_widget = QWidget(None, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
                splash_widget.setAttribute(Qt.WA_TranslucentBackground)
                splash_widget_layout = QVBoxLayout(splash_widget)
                splash_widget_layout.setContentsMargins(0, 0, 0, 0)

                # Container absoluto para sobrepor spinner em cima da imagem
                img_w = scaled_pix.width()
                img_h = scaled_pix.height()
                container = QWidget()
                container.setFixedSize(img_w, img_h)
                container.setAttribute(Qt.WA_StyledBackground, False)

                # Imagem como filho do container
                img_label = QLabel(container)
                img_label.setPixmap(scaled_pix)
                img_label.setGeometry(0, 0, img_w, img_h)

                # Spinner sobre a imagem (central-inferior dentro da imagem)
                spinner_label = QLabel(container)
                spinner_label.setFixedSize(40, 40)
                spinner_label.setAttribute(Qt.WA_TranslucentBackground)
                # posição central-inferior (72% da altura)
                sx = int((img_w - spinner_label.width()) / 2)
                sy = int(img_h * 0.72)
                spinner_label.move(sx, sy)
                # garante fundo transparente e que fique acima da imagem
                spinner_label.setStyleSheet("background: transparent;")
                spinner_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
                spinner_label.raise_()

                splash_widget_layout.addWidget(container, alignment=Qt.AlignCenter)

                # Centraliza splash na tela
                splash_widget.adjustSize()
                screen = self.app.primaryScreen()
                if screen:
                    geo = screen.availableGeometry()
                    sw = splash_widget.width()
                    sh = splash_widget.height()
                    splash_widget.move(int((geo.width() - sw) / 2), int((geo.height() - sh) / 2))

                # Cria um spinner desenhado programaticamente (não usa logo)
                spinner_size = 40
                spinner_label.setFixedSize(spinner_size, spinner_size)

                # Parâmetros do spinner
                num_segments = 12
                angle = {"v": 0}

                def rotate_step():
                    try:
                        angle["v"] = (angle["v"] + 30) % 360
                        size = spinner_label.width()
                        pix = QPixmap(size, size)
                        pix.fill(Qt.transparent)

                        painter = QPainter(pix)
                        painter.setRenderHint(QPainter.Antialiasing)

                        center_x = size / 2.0
                        center_y = size / 2.0
                        radius = size * 0.4

                        for i in range(num_segments):
                            seg_angle = math.radians(angle["v"] + (i * (360.0 / num_segments)))
                            alpha = int(255 * ((i + 1) / num_segments))
                            pen = QPen(QColor('#F0F6FC'))
                            pen.setWidth(3)
                            color = QColor('#F0F6FC')
                            color.setAlpha(alpha)
                            pen.setColor(color)
                            painter.setPen(pen)

                            x1 = center_x + math.cos(seg_angle) * (radius * 0.4)
                            y1 = center_y + math.sin(seg_angle) * (radius * 0.4)
                            x2 = center_x + math.cos(seg_angle) * radius
                            y2 = center_y + math.sin(seg_angle) * radius
                            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

                        painter.end()
                        spinner_label.setPixmap(pix)
                    except Exception:
                        pass

                spinner_timer = QTimer()
                spinner_timer.timeout.connect(rotate_step)
                spinner_timer.start(60)

                # Aplica efeito de fade-in ao splash
                try:
                    opacity_effect = QGraphicsOpacityEffect(splash_widget)
                    splash_widget.setGraphicsEffect(opacity_effect)
                    fade_anim = QPropertyAnimation(opacity_effect, b"opacity")
                    fade_anim.setDuration(600)
                    fade_anim.setStartValue(0.0)
                    fade_anim.setEndValue(1.0)
                    fade_anim.setEasingCurve(QEasingCurve.InOutQuad)
                    # Mantém referência para não ser coletado
                    splash_widget._fade_anim = fade_anim
                    splash_widget.show()
                    fade_anim.start()
                except Exception:
                    splash_widget.show()
                self.app.processEvents()

                def _finish_splash():
                    try:
                        spinner_timer.stop()
                    except Exception:
                        pass

                    try:
                        # Fade out splash, fade in main window for a smooth transition
                        try:
                            # Prepare splash fade-out
                            splash_effect = splash_widget.graphicsEffect()
                            if not isinstance(splash_effect, QGraphicsOpacityEffect):
                                splash_effect = QGraphicsOpacityEffect(splash_widget)
                                splash_widget.setGraphicsEffect(splash_effect)

                            splash_fade = QPropertyAnimation(splash_effect, b"opacity")
                            splash_fade.setDuration(400)
                            # Current opacity if available
                            start_op = getattr(splash_effect, 'opacity', None)
                            if callable(start_op):
                                try:
                                    cur_op = splash_effect.opacity()
                                except Exception:
                                    cur_op = 1.0
                            else:
                                cur_op = 1.0
                            splash_fade.setStartValue(cur_op)
                            splash_fade.setEndValue(0.0)
                            splash_fade.setEasingCurve(QEasingCurve.InOutQuad)
                            splash_widget._splash_fade = splash_fade

                            # Prepare main window opacity and show it hidden
                            main_effect = QGraphicsOpacityEffect(self.main_window)
                            self.main_window.setGraphicsEffect(main_effect)
                            main_effect.setOpacity(0.0)
                            self.main_window.show()
                            self.app.processEvents()

                            main_fade = QPropertyAnimation(main_effect, b"opacity")
                            main_fade.setDuration(400)
                            main_fade.setStartValue(0.0)
                            main_fade.setEndValue(1.0)
                            main_fade.setEasingCurve(QEasingCurve.InOutQuad)
                            self.main_window._main_fade = main_fade

                            # When splash fade finishes, close it and start main fade
                            def _on_splash_faded():
                                try:
                                    splash_widget.close()
                                except Exception:
                                    pass
                                try:
                                    main_fade.start()
                                except Exception:
                                    pass

                            splash_fade.finished.connect(_on_splash_faded)
                            splash_fade.start()

                        except Exception:
                            # Fallback: immediate switch
                            try:
                                splash_widget.close()
                            except Exception:
                                pass
                            self.main_window.show()

                        # Inicia monitoramento do sistema
                        if self.system_monitor:
                            self.system_monitor.start_monitoring()
                        self.logger.info("FPSPACK PANEL iniciado com sucesso")

                    except Exception as e:
                        self.logger.error(f"Erro finalizando splash: {e}")

                QTimer.singleShot(4000, _finish_splash)

                return self.app.exec()
            except Exception as e:
                self.logger.error(f"Erro ao exibir splash: {e}")

        # Fallback: mostra janela normalmente
        self.main_window.show()
        
        # Inicia monitoramento do sistema
        self.system_monitor.start_monitoring()
        
        self.logger.info("FPSPACK PANEL iniciado com sucesso")
        
        return self.app.exec()
    
    def cleanup(self):
        """Limpa recursos antes de fechar"""
        self.logger.info("Iniciando limpeza de recursos...")
        
        try:
            # Para monitoramento do sistema
            if self.system_monitor:
                self.system_monitor.stop_monitoring()
                
            # Finaliza gerenciador de threads
            if self.thread_manager:
                shutdown_thread_manager()
                
            self.logger.info("Limpeza concluída")
            
        except Exception as e:
            self.logger.error(f"Erro durante limpeza: {e}")

def main():
    """Funcao principal"""
    try:
        config = Config()
        logger = Logger()

        if ensure_admin(config.get("advanced.require_admin", False), logger):
            return

        apply_debug_mode(config.get("advanced.debug_mode", False), logger)

        if os.name == "nt" and not is_admin() and not config.get("advanced.require_admin", False):
            print('[!] AVISO: Para melhor funcionamento, execute como administrador')
        elif os.name != "nt":
            try:
                if os.getuid() != 0:
                    print('[!] AVISO: Para melhor funcionamento, execute como administrador')
            except AttributeError:
                pass

        app = FPSPackPanel()
        sys.exit(app.run())

    except KeyboardInterrupt:
        print("\n[!] Aplicacao interrompida pelo usuario")
        sys.exit(0)
    except Exception as e:
        print(f"[x] Erro critico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()