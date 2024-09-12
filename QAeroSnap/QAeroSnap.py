# QAeroSnap/QAeroSnap.py
from PyQt6 import QtCore, QtGui, QtWidgets

import win32gui

"""Usage:

>>> from QAeroSnap import QtAeroSnap

>>> QtAeroSnap(MainWindow, title_bar, 40, 5)

¬ MainWindow: QtWidgets.QMainWindow -> MainWindow
¬ title_bar: QtWidgets.QWidget      -> Custom Title Bar
¬ 40: int                           -> X Adjustment (Optional)
¬ 5: int                            -> Y Adjustment (Optional)

"""

painter_brush_color = QtGui.QColor(255, 255, 255, 12)       # Opacity: 4.7% | Brush Color
painter_pen_color   = QtGui.QColor(156, 156, 156, 128)      # Opacity: 50%  | Pen Color
painter_pen_width   = 1                                     # Width: 1px    | Pen Width
overlay_margin      = 9                                     # Margin: 9px   | Overlay Margin
mouse_top_spacing   = 20                                    # Spacing: 10px | Mouse Top Spacing

class Overlay(QtWidgets.QWidget):
    def __init__(self, screen_geometry: QtCore.QRect):
        super().__init__()
        
        self._width = 0
        self._height = 0
        self._x = screen_geometry.center().x()
        self._y = screen_geometry.y()
        
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint  |
                            QtCore.Qt.WindowType.WindowStaysOnTopHint |
                            QtCore.Qt.WindowType.Tool)
        
        self.setGeometry(self._x, self._y, self._width, self._height)
        
    @QtCore.pyqtProperty(QtCore.QRect)
    def geometry(self):
        return QtCore.QRect(self._x, self._y, self._width, self._height)
        
    @geometry.setter
    def geometry(self, rect:QtCore.QRect):
        self._x = rect.x()
        self._y = rect.y()
        self._width = rect.width()
        self._height = rect.height()
        
        self.setGeometry(self._x, self._y, self._width, self._height)
        
    @QtCore.pyqtProperty(float)
    def opacity(self):
        return self.windowOpacity()
    
    @opacity.setter
    def opacity(self, value:float):
        self.setWindowOpacity(value)
        
    def paintEvent(self, event:QtGui.QPaintEvent):
        global painter_brush_color, painter_pen_color, painter_pen_width, overlay_margin
        
        painter = QtGui.QPainter(self)
        painter.setBrush(painter_brush_color)
        
        rect = QtCore.QRect(0, 0, self._width, self._height).adjusted(overlay_margin, overlay_margin, -overlay_margin, -overlay_margin)
        painter.drawRect(rect)
        
        pen = QtGui.QPen(painter_pen_color)
        pen.setWidth(painter_pen_width)
        painter.setPen(pen)
        
        painter.drawRect(rect.adjusted(1 // 2, 1 // 2, -(1 // 2), -(1 // 2)))

class QtAeroSnap():
    def __init__(self, MainWindow: QtWidgets.QMainWindow, title_bar: QtWidgets.QWidget, x_adj: int = 0, y_adj: int = 0):
        super().__init__()
        
        self.screen_rect = MainWindow.geometry()
        
        self.spacing = False
        
        self._is_active = True
        
        self.setup_ui(MainWindow, title_bar, x_adj, y_adj)
    
    def setup_ui(self, MainWindow: QtWidgets.QMainWindow, title_bar: QtWidgets.QWidget, x_adj: int, y_adj: int):
        self.MainWindow = MainWindow
        
        title_bar.mousePressEvent = self.mousePressEvent
        title_bar.mouseMoveEvent = self.mouseMoveEvent
        title_bar.mouseReleaseEvent = self.mouseReleaseEvent
        
        self.x_adj = x_adj
        self.y_adj = y_adj
    
    def get_taskbar_height(self):
        taskbar_hwnd = win32gui.FindWindow("Shell_TrayWnd", None)
        
        taskbar_rect = win32gui.GetWindowRect(taskbar_hwnd)
        
        taskbar_height = taskbar_rect[3] - taskbar_rect[1]
        
        return taskbar_height
    
    def setup_overlay(self):
        screens = QtWidgets.QApplication.screens()
        
        for i, screen in enumerate(screens):
            if screen.geometry().intersects(self.screen_rect):
                screen_num = i
                break
            
        screen = screens[screen_num]
        
        screen_rect = QtCore.QRect(screen.geometry().x(),
                                   screen.geometry().y(),
                                   screen.geometry().width(),
                                   screen.geometry().height() - self.get_taskbar_height())
        
        self.overlay = Overlay(screen_rect)
        self.overlay.hide()
        
    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            if self.MainWindow.isMaximized():
                self.offset = event.pos()
                self.x_w = self.offset.x() // 2.4
            
            else:
                self.offset = event.pos()
                self.x_w = self.offset.x()
                
            self.setup_overlay()
            
    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.move_to_position(event)
            self.check_snap_to_edge(event)
            self.screen_rect = self.MainWindow.screen().geometry()
            
    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        global mouse_top_spacing
        
        screen_top = self.screen_rect.getCoords()[1]
        
        y = event.globalPosition().y()
        
        if screen_top + mouse_top_spacing >= y >= screen_top:
            self.MainWindow.showMaximized()
            self.overlay.hide()
            
    def move_to_position(self, event: QtGui.QMouseEvent):
        x = event.globalPosition().x()
        y = event.globalPosition().y()
        
        y_w = self.offset.y()
        x_w = self.x_w
        
        x_adj = self.x_adj
        y_adj = self.y_adj
        
        if self.MainWindow.isMaximized():
            self.MainWindow.showNormal()

        self.MainWindow.move(int(x - x_w - x_adj), int(y - y_w - y_adj))
        
    def check_snap_to_edge(self, event: QtGui.QMouseEvent):
        global mouse_top_spacing
        
        y = event.globalPosition().y()
        
        if self.screen_rect.getCoords()[0] != self.MainWindow.screen().geometry().getCoords()[0]:
            self.screen_rect = self.MainWindow.screen().geometry()
            self.setup_overlay()
            
        screen_top = self.screen_rect.getCoords()[1]
        
        if screen_top == y:
            self.spacing = True

        if self.spacing:
            self.timer = QtCore.QTimer()
            self.timer.setSingleShot(True)
            self.timer.timeout.connect(self.overlay.hide)
            
            if screen_top + mouse_top_spacing >= y >= screen_top:
                self.animation_size()
            else:
                self.animation_size_reverse()
                self.timer.start(250)
                
    def animation_size(self):
        if self._is_active:            
            
            self.overlay.show()

            screen_geometry = self.MainWindow.screen().geometry()

            start_rect = QtCore.QRect(
                screen_geometry.center().x() - 50,
                screen_geometry.y(),
                100,
                10
            )

            target_rect = QtCore.QRect(
                screen_geometry.x(),
                screen_geometry.y(),
                screen_geometry.width(),
                screen_geometry.height() - self.get_taskbar_height()
            )

            self.animation_geometry = QtCore.QPropertyAnimation(self.overlay, b"geometry")
            self.animation_geometry.setDuration(150)
            self.animation_geometry.setStartValue(start_rect)
            self.animation_geometry.setEndValue(target_rect)
            self.animation_geometry.setEasingCurve(QtCore.QEasingCurve.Type.InOutCubic)
            
            self.animation_opacity = QtCore.QPropertyAnimation(self.overlay, b"opacity")
            self.animation_opacity.setDuration(250)
            self.animation_opacity.setStartValue(0.0)
            self.animation_opacity.setEndValue(1.0)
            self.animation_opacity.setEasingCurve(QtCore.QEasingCurve.Type.InOutSine)
            
            self.animation_group = QtCore.QParallelAnimationGroup()
            self.animation_group.addAnimation(self.animation_geometry)
            self.animation_group.addAnimation(self.animation_opacity)
            self.animation_group.start()

            self._is_active = False
            
    def animation_size_reverse(self):
        if not self._is_active:
            
            self.animation_group.stop()
            
            self.animation_opacity_reverse = QtCore.QPropertyAnimation(self.overlay, b"opacity")
            self.animation_opacity_reverse.setDuration(250)
            self.animation_opacity_reverse.setStartValue(self.overlay.windowOpacity())
            self.animation_opacity_reverse.setEndValue(0.0)
            self.animation_opacity_reverse.setEasingCurve(QtCore.QEasingCurve.Type.InOutSine)
            
            self.animation_opacity_reverse.start()

            self._is_active = True
            
            self.spacing = False