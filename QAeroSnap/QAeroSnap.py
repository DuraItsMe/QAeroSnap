# QAeroSnap/QAeroSnap.py
from PyQt6 import QtCore, QtGui, QtWidgets

import win32gui

from typing import Optional

"""Usage:

>>> from QAeroSnap import QtAeroSnap

>>> QtAeroSnap(MainWindow, title_bar, 40, 5)

¬ MainWindow: QtWidgets.QMainWindow -> MainWindow
¬ title_bar: QtWidgets.QWidget      -> Custom Title Bar
¬ 40: int                           -> X Adjustment (Optional)
¬ 5: int                            -> Y Adjustment (Optional)

"""

# Global
painter_brush_color = QtGui.QColor(255, 255, 255, 12)
painter_pen_color   = QtGui.QColor(156, 156, 156, 128)
painter_pen_width   = 1
overlay_margin      = 9
mouse_edge_spacing  = 20

top_right           = 20
right_top           = 25

# Overlay
class Overlay(QtWidgets.QWidget):
    def __init__(self, screen_geometry: QtCore.QRect):
        super().__init__()
        
        self._width:    int = 0
        self._height:   int = 0
        self._x:        int = screen_geometry.center().x()
        self._y:        int = screen_geometry.y()
        
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint  |
                            QtCore.Qt.WindowType.WindowStaysOnTopHint |
                            QtCore.Qt.WindowType.Tool)
        
        self.setGeometry(self._x, self._y, self._width, self._height)
        
    @QtCore.pyqtProperty(QtCore.QRect)
    def geometry(self) -> QtCore.QRect:
        return QtCore.QRect(self._x, self._y, self._width, self._height)
        
    @geometry.setter
    def geometry(self, rect:QtCore.QRect):
        self._x:        int = rect.x()
        self._y:        int = rect.y()
        self._width:    int = rect.width()
        self._height:   int = rect.height()
        
        self.setGeometry(self._x, self._y, self._width, self._height)
        
    @QtCore.pyqtProperty(float)
    def opacity(self) -> float:
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
        
# QtAeroSnap
class QtAeroSnap():
    # __init__
    def __init__(self, MainWindow: QtWidgets.QMainWindow, title_bar: QtWidgets.QWidget, x_adj: int = 0, y_adj: int = 0):
        super().__init__()
        
        self.screen_rect: QtCore.QRect = MainWindow.geometry()
        
        self.spacing: bool = False
        
        self._is_active: bool = True
        
        self.default_pos: Optional[int] = None
        self.default_screen: Optional[QtGui.QScreen] = None
        
        self.setup_ui(MainWindow, title_bar, x_adj, y_adj)
    
    # setup_ui
    def setup_ui(self, MainWindow: QtWidgets.QMainWindow, title_bar: QtWidgets.QWidget, x_adj: int, y_adj: int):
        self.MainWindow = MainWindow
        
        title_bar.mousePressEvent = self.mousePressEvent
        title_bar.mouseMoveEvent = self.mouseMoveEvent
        title_bar.mouseReleaseEvent = self.mouseReleaseEvent
        
        self.x_adj = x_adj
        self.y_adj = y_adj
    
    # get taskbar height
    def get_taskbar_height(self) -> int:
        taskbar_hwnd = win32gui.FindWindow("Shell_TrayWnd", None)
        
        taskbar_rect = win32gui.GetWindowRect(taskbar_hwnd)
        
        taskbar_height = taskbar_rect[3] - taskbar_rect[1]
        
        return taskbar_height
    
    # setup overlay
    def setup_overlay(self, screen: QtGui.QScreen):
        
        screen_rect = QtCore.QRect(screen.geometry().x(),
                                   screen.geometry().y(),
                                   screen.geometry().width(),
                                   screen.geometry().height() - self.get_taskbar_height())
        
        self.overlay = Overlay(screen_rect)
        self.overlay.hide()
        
    # mouse press event
    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            if self.MainWindow.isMaximized():
                self.offset = event.pos()
                self.x_w = self.offset.x() // 2.4
            else:
                self.offset = event.pos()
                self.x_w = self.offset.x()
    
    # mouse move event
    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.move_to_position(event)
            self.check_snap_to_edge(event)
            self.screen_rect = self.MainWindow.screen().geometry()
    
    # mouse release event
    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        global mouse_edge_spacing
        
        screen_top = self.screen_rect.getCoords()[1]
        screen_right = self.screen_rect.getCoords()[2]
        screen_left = self.screen_rect.getCoords()[0]
        
        y = event.globalPosition().y()
        x = event.globalPosition().x()
        
        if screen_top + mouse_edge_spacing >= y >= screen_top and x < (screen_right - 5) and x > (screen_left + 5):
            self.MainWindow.move(self.default_screen.geometry().topLeft())
            self.MainWindow.showMaximized()
            self.overlay.hide()
            
    # move mainwindow
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
        
    # check border
    def check_snap_to_edge(self, event: QtGui.QMouseEvent):
        global mouse_edge_spacing
        
        y = event.globalPosition().y()
        x = event.globalPosition().x()
        
        pos = int(event.globalPosition().x())
        
        screens = QtWidgets.QApplication.screens()
        
        sorted_screens = sorted([(screen.geometry().getCoords()[0], i) for i, screen in enumerate(screens)])
        
        for i in range(len(sorted_screens)):
            try:
                if sorted_screens[i][0] <= pos < sorted_screens[i+1][0]:
                    screen = screens[sorted_screens[i][1]]
                    self.screen_rect = screen.geometry()
                    break
            except IndexError:
                if sorted_screens[i][0]*2 >= pos >= sorted_screens[i][0]:
                    screen = screens[sorted_screens[i][1]]
                    self.screen_rect = screen.geometry()
                    break
        
        if self.screen_rect.getCoords()[0] != self.default_pos:
            self.default_pos = self.screen_rect.getCoords()[0]
            self.default_screen = screen
            self.setup_overlay(screen)
            
        screen_top = self.screen_rect.getCoords()[1]
        screen_right = self.screen_rect.getCoords()[2]
        screen_left = self.screen_rect.getCoords()[0]
        
        if screen_top == y:
            self.spacing = True

        if self.spacing:
            self.timer = QtCore.QTimer()
            self.timer.setSingleShot(True)
            self.timer.timeout.connect(self.overlay.hide)
            
            if screen_top + mouse_edge_spacing >= y >= screen_top and x < (screen_right - 5) and x > (screen_left + 5):
                self.animation_size('full')
            else:
                self.animation_size_reverse()
                self.timer.start(250)
    
    # custom screen rect
    def type_screen_rect(self, args: str) -> QtCore.QRect:
        screen_geometry = self.screen_rect
        
        X = screen_geometry.x()
        Y = screen_geometry.y()
        WIDTH = screen_geometry.width()
        HEIGHT = screen_geometry.height()
        
        TASK_BAR = self.get_taskbar_height()
        
        if args == 'full' or args == 'right' or args == 'left':
            HEIGHT = HEIGHT - TASK_BAR
        if args == 'right' or args == 'left':
            WIDTH = WIDTH // 2
        if args == 'right' :
            X = X + WIDTH
        
        rect = QtCore.QRect(
                X,
                Y,
                WIDTH,
                HEIGHT
            )
        
        return rect
    
    # show overlay animation
    def animation_size(self, args: str):
        if self._is_active:            
            
            self.overlay.show()
            
            screen_geometry = self.screen_rect

            start_rect = QtCore.QRect(
                screen_geometry.center().x() - 50,
                screen_geometry.y(),
                100,
                10
            )

            target_rect = self.type_screen_rect(args)

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
    
    # hide overlay animation
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