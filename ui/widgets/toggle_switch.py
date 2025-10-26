from PySide6.QtCore import Qt, QSize, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush
from PySide6.QtWidgets import QCheckBox


class ToggleSwitch(QCheckBox):
    """A modern toggle switch that behaves like a QCheckBox.

    It keeps the same API as QCheckBox (isChecked, setChecked, toggled, etc.)
    so it can drop-in replace regular checkboxes in the UI.
    """

    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self._switch_width = 44
        self._switch_height = 24
        self._margin = 2
        # Improve click area while keeping compact rendering
        self.setCursor(Qt.PointingHandCursor)
        self.setContentsMargins(0, 0, 0, 0)

    def sizeHint(self) -> QSize:
        text_size = super().sizeHint()
        # Reserve space for the switch indicator plus spacing to the label
        indicator_width = self._switch_width + 8
        return QSize(indicator_width + text_size.width(), max(self._switch_height, text_size.height()))

    def minimumSizeHint(self) -> QSize:
        return self.sizeHint()

    def paintEvent(self, event):  # noqa: N802 - Qt API
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Geometry for the toggle on the left
        y_center = self.rect().center().y()
        indicator_rect = QRectF(0, y_center - self._switch_height / 2, self._switch_width, self._switch_height)

        # Colors
        bg_off = QColor(38, 44, 56)
        bg_on = QColor(0, 199, 255)
        border_color = QColor(60, 68, 80)
        knob_color = QColor(240, 240, 240)

        # Background capsule
        painter.setPen(QPen(border_color, 1))
        painter.setBrush(QBrush(bg_on if self.isChecked() else bg_off))
        painter.drawRoundedRect(indicator_rect, self._switch_height / 2, self._switch_height / 2)

        # Knob
        knob_diameter = self._switch_height - 2 * self._margin
        knob_x = (
            indicator_rect.right() - self._margin - knob_diameter
            if self.isChecked()
            else indicator_rect.left() + self._margin
        )
        knob_rect = QRectF(knob_x, indicator_rect.top() + self._margin, knob_diameter, knob_diameter)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(knob_color))
        painter.drawEllipse(knob_rect)

        # Text label area to the right of the switch
        text_rect = self.rect().adjusted(int(self._switch_width + 8), 0, 0, 0)
        painter.setPen(self.palette().color(self.foregroundRole()))
        painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, self.text())
        painter.end()


