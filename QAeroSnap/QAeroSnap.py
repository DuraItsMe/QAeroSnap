# QAeroSnap/QAeroSnap.py
from PyQt6 import QtCore, QtGui, QtWidgets

import win32api
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
mouse_top_spacing   = 10                                    # Spacing: 10px | Mouse Top Spacing

class Overlay(QtWidgets.QWidget):
    def __init__(self, screen_geometry: QtCore.QRect):
        super().__init__()
        
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint  |
                            QtCore.Qt.WindowType.WindowStaysOnTopHint |
                            QtCore.Qt.WindowType.Tool)
        
        self.setGeometry(screen_geometry)
        
    def paintEvent(self, event:QtGui.QPaintEvent):
        global painter_brush_color, painter_pen_color, painter_pen_width, overlay_margin
        
        painter = QtGui.QPainter(self)
        painter.setBrush(painter_brush_color)
        
        rect = self.rect().adjusted(overlay_margin, overlay_margin, -overlay_margin, -overlay_margin)
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
        
        screen_rect = QtCore.QRect(screen.geometry().x(), screen.geometry().y(), screen.geometry().width(), screen.geometry().height() - self.get_taskbar_height())
        
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
        if self.overlay.isVisible():
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
            
        screen_rect = win32api.GetMonitorInfo(win32api.EnumDisplayMonitors()[0][0])['Monitor']
        screen_left, screen_top, screen_right, screen_bottom = screen_rect
        
        if screen_top == y:
            self.spacing = True

        if self.spacing:
            if screen_top + mouse_top_spacing >= y >= screen_top:
                self.overlay.show()
            else:
                self.spacing = False
                self.overlay.hide()