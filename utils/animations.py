#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Animações do FPSPACK PANEL
Animações suaves e efeitos visuais
"""

from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QSequentialAnimationGroup
from PySide6.QtWidgets import QGraphicsOpacityEffect
from PySide6.QtGui import QColor
from typing import Optional

class AnimationManager:
    """Gerenciador de animações"""
    
    def __init__(self):
        self.animations = []
        
    def fade_in(self, widget, duration: int = 300):
        """Animação de fade in"""
        effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(effect)
        
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self.animations.append(animation)
        animation.start()
        
    def fade_out(self, widget, duration: int = 300):
        """Animação de fade out"""
        effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(effect)
        
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(1.0)
        animation.setEndValue(0.0)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self.animations.append(animation)
        animation.start()
        
    def slide_in(self, widget, direction: str = "left", duration: int = 400):
        """Animação de slide in"""
        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.OutBack)
        
        start_pos = widget.pos()
        
        if direction == "left":
            animation.setStartValue(start_pos.x() - widget.width(), start_pos.y())
        elif direction == "right":
            animation.setStartValue(start_pos.x() + widget.width(), start_pos.y())
        elif direction == "top":
            animation.setStartValue(start_pos.x(), start_pos.y() - widget.height())
        elif direction == "bottom":
            animation.setStartValue(start_pos.x(), start_pos.y() + widget.height())
            
        animation.setEndValue(start_pos)
        
        self.animations.append(animation)
        animation.start()
        
    def pulse(self, widget, duration: int = 1000):
        """Animação de pulso"""
        effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(effect)
        
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(1.0)
        animation.setKeyValueAt(0.5, 0.5)
        animation.setEndValue(1.0)
        animation.setLoopCount(-1)  # Loop infinito
        animation.setEasingCurve(QEasingCurve.InOutSine)
        
        self.animations.append(animation)
        animation.start()
        
    def bounce(self, widget, duration: int = 600):
        """Animação de bounce"""
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.OutBounce)
        
        start_geometry = widget.geometry()
        animation.setStartValue(start_geometry)
        animation.setEndValue(start_geometry)
        
        self.animations.append(animation)
        animation.start()
        
    def glow_effect(self, widget, color: QColor = QColor(0, 212, 255), duration: int = 2000):
        """Efeito de brilho"""
        # Implementação básica - pode ser expandida com shaders
        self.pulse(widget, duration)
        
    def loading_animation(self, widget, duration: int = 1500):
        """Animação de loading"""
        rotation_animation = QPropertyAnimation(widget, b"rotation")
        rotation_animation.setDuration(duration)
        rotation_animation.setStartValue(0)
        rotation_animation.setEndValue(360)
        rotation_animation.setLoopCount(-1)
        rotation_animation.setEasingCurve(QEasingCurve.Linear)
        
        self.animations.append(rotation_animation)
        rotation_animation.start()
        
    def progress_animation(self, progress_bar, target_value: int, duration: int = 1000):
        """Animação de barra de progresso"""
        animation = QPropertyAnimation(progress_bar, b"value")
        animation.setDuration(duration)
        animation.setStartValue(progress_bar.value())
        animation.setEndValue(target_value)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self.animations.append(animation)
        animation.start()
        
    def stop_all_animations(self):
        """Para todas as animações"""
        for animation in self.animations:
            if animation.state() == QPropertyAnimation.Running:
                animation.stop()
        self.animations.clear()