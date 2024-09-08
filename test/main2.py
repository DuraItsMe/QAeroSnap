from PyQt6 import QtCore, QtGui, QtWidgets
from QAeroSnap import QtAeroSnap

class Ui_MainWindow(object):
    def setupUi(self, MainWindow:QtWidgets.QMainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        MainWindow.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        
        default_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        
        hbox = QtWidgets.QHBoxLayout()
        
        logo = QtWidgets.QLabel()
        logo.setFixedSize(40, 40)
        logo.setStyleSheet('background-color:#f00;')
        
        title_bar = QtWidgets.QLabel('MainWindow')
        title_bar.setFixedHeight(30)
        title_bar.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        title_bar.setStyleSheet('background-color:#f82;')
        
        close_button = QtWidgets.QPushButton('X')
        close_button.clicked.connect(MainWindow.close)
        close_button.setFixedSize(40, 40)
        
        hbox.addWidget(logo)
        hbox.addWidget(title_bar)
        hbox.addWidget(close_button)
        hbox.setSpacing(0)
        
        #->print(hbox.spacing())
        
        aero_snap = QtAeroSnap(MainWindow, title_bar, 40, 5)
        
        default_layout.setContentsMargins(0, 0, 0, 0)
        #default_layout.addWidget(title_bar)
        default_layout.addLayout(hbox)
        default_layout.addStretch()

        self.retranslateUi(MainWindow)

    def retranslateUi(self, MainWindow:QtWidgets.QMainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())