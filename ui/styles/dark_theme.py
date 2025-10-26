#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tema Dark Moderno para FPSPACK PANEL
Glassmorphism, gradientes e animações
"""

class DarkTheme:
    
    # Cores principais
    PRIMARY_BG = "#0D1117"
    SECONDARY_BG = "#161B22"
    ACCENT_BG = "#21262D"
    GLASS_BG = "rgba(33, 38, 45, 0.8)"
    
    # Cores de destaque
    NEON_BLUE = "#00D4FF"
    NEON_PURPLE = "#8B5CF6"
    NEON_GREEN = "#00FF88"
    NEON_RED = "#FF4757"
    NEON_ORANGE = "#FFA726"
    
    # Cores de texto
    TEXT_PRIMARY = "#F0F6FC"
    TEXT_SECONDARY = "#8B949E"
    TEXT_MUTED = "#6E7681"
    
    # Bordas e sombras
    BORDER_COLOR = "#30363D"
    SHADOW_COLOR = "rgba(0, 0, 0, 0.5)"
    GLOW_COLOR = "rgba(0, 212, 255, 0.3)"
    
    @staticmethod
    def get_stylesheet():
        # Keep the stylesheet compatible with Qt's subset of CSS.
        # Removed unsupported properties (transition, box-shadow, transform, text-shadow)
        return f"""
        QMainWindow {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {DarkTheme.PRIMARY_BG}, stop:0.5 {DarkTheme.SECONDARY_BG}, stop:1 {DarkTheme.PRIMARY_BG});
            color: {DarkTheme.TEXT_PRIMARY};
            font-family: 'Segoe UI', Arial, sans-serif;
        }}

        QWidget {{
            background: transparent;
            color: {DarkTheme.TEXT_PRIMARY};
            font-size: 11px;
        }}

        QFrame#sidebar {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {DarkTheme.SECONDARY_BG}, stop:1 {DarkTheme.ACCENT_BG});
            border-right: 2px solid {DarkTheme.BORDER_COLOR};
        }}

        QLabel#title {{
            font-size: 28px;
            font-weight: bold;
            color: {DarkTheme.NEON_BLUE};
            margin-bottom: 5px;
        }}

        QLabel#subtitle {{
            font-size: 16px;
            font-weight: 300;
            color: {DarkTheme.TEXT_SECONDARY};
        }}

        QPushButton#nav_button {{
            background: transparent;
            border: none;
            border-radius: 8px;
            padding: 12px 16px;
            text-align: left;
            font-size: 14px;
            color: {DarkTheme.TEXT_SECONDARY};
        }}

        QPushButton#nav_button:checked {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {DarkTheme.NEON_BLUE}, stop:1 {DarkTheme.NEON_PURPLE});
            color: white;
            font-weight: bold;
        }}

        /* Hover effect for sidebar navigation buttons */
        QPushButton#nav_button:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(0,212,255,0.06), stop:1 rgba(139,92,246,0.04));
            color: white;
            font-weight: 600;
        }}

        QPushButton#turbo_button {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {DarkTheme.NEON_RED}, stop:1 {DarkTheme.NEON_ORANGE});
            border: none;
            border-radius: 12px;
            padding: 10px;
            font-size: 13px;
            color: white;
        }}

        QPushButton#turbo_button:hover {{
            /* Slightly stronger gradient on hover */
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(255,71,87,0.95), stop:1 rgba(255,167,38,0.95));
            border: 1px solid rgba(255,71,87,0.8);
        }}

        QFrame#content_frame {{
            background: {DarkTheme.GLASS_BG};
            border-radius: 0px;
            border: 1px solid {DarkTheme.BORDER_COLOR};
        }}

        QFrame#header {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(0,212,255,0.06), stop:0.5 rgba(139,92,246,0.05), stop:1 rgba(0,212,255,0.06));
            border: 1px solid {DarkTheme.BORDER_COLOR};
            border-radius: 0px;
            margin-bottom: 12px;
        }}

        QFrame#info_frame {{
            background: {DarkTheme.ACCENT_BG};
            border: 1px solid {DarkTheme.BORDER_COLOR};
            border-radius: 0px;
            margin: 0px 6px;
        }}

        QLabel#info_title {{
            font-size: 10px;
            font-weight: bold;
            color: {DarkTheme.TEXT_SECONDARY};
            text-transform: uppercase;
        }}

        QLabel#value {{
            font-size: 15px;
            font-weight: bold;
            color: {DarkTheme.NEON_BLUE};
        }}

        /* Generic button style for app buttons */
        QPushButton#optimization_button,
        QPushButton#cleanup_button,
        QPushButton#settings_button {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {DarkTheme.ACCENT_BG}, stop:1 {DarkTheme.SECONDARY_BG});
            border: 1px solid {DarkTheme.BORDER_COLOR};
            border-radius: 0px;
            padding: 8px 14px;
            font-size: 12px;
            color: {DarkTheme.TEXT_PRIMARY};
        }}

        QPushButton#optimization_button_primary {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {DarkTheme.NEON_GREEN}, stop:1 {DarkTheme.NEON_BLUE});
            border: none;
            border-radius: 0px;
            padding: 10px 16px;
            color: white;
            font-weight: 600;
            font-size: 13px;
        }}

        QPushButton#optimization_button_primary:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(0, 255, 127, 0.9), stop:1 rgba(0, 200, 100, 0.9));
        }}

        QPushButton#optimization_button:hover,
        QPushButton#cleanup_button:hover,
        QPushButton#settings_button:hover {{
            border-color: {DarkTheme.NEON_BLUE};
        }}

        QPushButton#optimization_button:pressed,
        QPushButton#cleanup_button:pressed,
        QPushButton#settings_button:pressed {{
            background: {DarkTheme.SECONDARY_BG};
        }}

        /* Primary variants */
        QPushButton#cleanup_button_primary,
        QPushButton#settings_button_primary {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {DarkTheme.NEON_BLUE}, stop:1 {DarkTheme.NEON_PURPLE});
            border: none;
            border-radius: 0px;
            padding: 10px 16px;
            color: white;
            font-weight: 600;
        }}

        QPushButton#cleanup_button_primary:hover,
        QPushButton#settings_button_primary:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(0, 255, 127, 0.9), stop:1 rgba(0, 200, 100, 0.9));
        }}

        QPushButton#quick_action {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {DarkTheme.ACCENT_BG}, stop:1 {DarkTheme.SECONDARY_BG});
            border: 1px solid {DarkTheme.BORDER_COLOR};
            border-radius: 0px;
            padding: 8px 14px;
            font-size: 12px;
            color: {DarkTheme.TEXT_PRIMARY};
        }}

        QProgressBar {{
            background: {DarkTheme.SECONDARY_BG};
            border: 1px solid {DarkTheme.BORDER_COLOR};
            border-radius: 8px;
            text-align: center;
            color: {DarkTheme.TEXT_PRIMARY};
            height: 22px;
        }}

        QProgressBar::chunk {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {DarkTheme.NEON_BLUE}, stop:1 {DarkTheme.NEON_PURPLE});
            border-radius: 6px;
        }}

        QGroupBox {{
            background: {DarkTheme.GLASS_BG};
            border: 1px solid {DarkTheme.BORDER_COLOR};
            border-radius: 0px;
            font-size: 13px;
            color: {DarkTheme.TEXT_PRIMARY};
            margin-top: 8px;
            padding-top: 10px;
        }}

        QCheckBox {{
            color: {DarkTheme.TEXT_PRIMARY};
            font-size: 12px;
        }}

        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border: 1px solid {DarkTheme.BORDER_COLOR};
            background: {DarkTheme.SECONDARY_BG};
        }}

        QCheckBox::indicator:checked {{
            background: {DarkTheme.NEON_BLUE};
            border: 1px solid {DarkTheme.NEON_BLUE};
        }}

        QSlider::groove:horizontal {{
            background: {DarkTheme.SECONDARY_BG};
            height: 8px;
            border-radius: 0px;
            border: 1px solid {DarkTheme.BORDER_COLOR};
        }}

        QSlider::handle:horizontal {{
            background: {DarkTheme.NEON_BLUE};
            border: 1px solid {DarkTheme.NEON_BLUE};
            width: 18px;
            height: 18px;
            border-radius: 0px;
            margin: -5px 0;
        }}

        QComboBox {{
            background: {DarkTheme.SECONDARY_BG};
            border: 1px solid {DarkTheme.BORDER_COLOR};
            border-radius: 0px;
            padding: 6px 10px;
            font-size: 12px;
            color: {DarkTheme.TEXT_PRIMARY};
        }}

        QTextEdit {{
            background: {DarkTheme.SECONDARY_BG};
            border: 1px solid {DarkTheme.BORDER_COLOR};
            border-radius: 0px;
            padding: 8px;
            font-family: 'Consolas', monospace;
            font-size: 11px;
            color: {DarkTheme.TEXT_PRIMARY};
        }}

        /* Improved vertical scrollbar: thin, rounded thumb with subtle hover and track */
        QScrollBar:vertical {{
            background: transparent;
            width: 12px;
            margin: 8px 0 8px 0;
        }}

        QScrollBar::handle:vertical {{
            background: rgba(255,255,255,0.08);
            min-height: 28px;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.06);
        }}

        QScrollBar::handle:vertical:hover {{
            background: rgba(0,212,255,0.12);
            border: 1px solid rgba(0,212,255,0.18);
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
            subcontrol-origin: margin;
        }}

        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: transparent;
        }}

        QToolTip {{
            background: {DarkTheme.ACCENT_BG};
            border: 1px solid {DarkTheme.NEON_BLUE};
            border-radius: 6px;
            padding: 6px;
            color: {DarkTheme.TEXT_PRIMARY};
            font-size: 11px;
        }}

        QStatusBar {{
            background: {DarkTheme.SECONDARY_BG};
            border-top: 1px solid {DarkTheme.BORDER_COLOR};
            color: {DarkTheme.TEXT_PRIMARY};
            font-size: 11px;
        }}

        /* Settings tabs */
        QTabWidget::pane {{
            background: {DarkTheme.GLASS_BG};
            border: 1px solid {DarkTheme.BORDER_COLOR};
            border-radius: 0px;
        }}

        QTabBar::tab {{
            background: {DarkTheme.SECONDARY_BG};
            color: {DarkTheme.TEXT_PRIMARY};
            padding: 6px 10px;
            border: 1px solid {DarkTheme.BORDER_COLOR};
            border-bottom: none;
            margin-right: 4px;
        }}

        QTabBar::tab:selected {{
            background: {DarkTheme.ACCENT_BG};
            color: {DarkTheme.NEON_BLUE};
            border: 1px solid {DarkTheme.NEON_BLUE};
            border-bottom: none;
        }}

        QTabBar::tab:hover {{
            color: {DarkTheme.NEON_BLUE};
            border-color: {DarkTheme.NEON_BLUE};
        }}

        /* Scroll areas */
        QScrollArea {{
            background: transparent;
            border: none;
        }}

        QAbstractScrollArea::viewport {{
             background: transparent;
         }}

         /* Inputs */
         QSpinBox {{
             background: {DarkTheme.SECONDARY_BG};
             border: 1px solid {DarkTheme.BORDER_COLOR};
             border-radius: 0px;
             padding: 4px 8px;
             color: {DarkTheme.TEXT_PRIMARY};
         }}

         QSpinBox::up-button, QSpinBox::down-button {{
             background: {DarkTheme.ACCENT_BG};
             border: 1px solid {DarkTheme.BORDER_COLOR};
             width: 16px;
         }}

         QComboBox QAbstractItemView {{
             background: {DarkTheme.SECONDARY_BG};
             color: {DarkTheme.TEXT_PRIMARY};
             selection-background-color: {DarkTheme.ACCENT_BG};
             selection-color: {DarkTheme.TEXT_PRIMARY};
             border: 1px solid {DarkTheme.BORDER_COLOR};
         }}

         /* Targeted settings tabs styling */
         QTabWidget#settings_tabs::pane {{
             background: {DarkTheme.GLASS_BG};
             border: 1px solid {DarkTheme.BORDER_COLOR};
             border-radius: 0px;
         }}
         """