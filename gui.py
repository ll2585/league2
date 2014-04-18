import os, sys 
import controller
from PyQt4 import QtGui, QtCore

class NoTypeTextEdit(QtGui.QTextEdit):

	def keyPressEvent(self, event):
		event.ignore()

class MainWidget(QtGui.QWidget):
	
	def __init__(self, parent):
		super(MainWidget, self).__init__(parent)
		self.parent = parent
		self.initUI()
		
	def initUI(self):
		alertLabel = QtGui.QLabel('You must have a riot API key and access to this API')
		tab_widget = QtGui.QTabWidget() 
		tab1 = QtGui.QWidget() 
		tab2 = OptionsTab(self.parent, self)
		
		p1_vertical = QtGui.QVBoxLayout(tab1) 
		
		tab_widget.addTab(tab1, "Output") 
		tab_widget.addTab(tab2, "Options")
		 
		button1 = QtGui.QPushButton("button1") 
		logBox = NoTypeTextEdit()

		p1_vertical.addWidget(logBox)


		

		#p2_grid.addWidget(verticalLine, 0, 1, 8, 1)
		 
		vbox = QtGui.QVBoxLayout() 
		vbox.addWidget(alertLabel)
		vbox.addWidget(tab_widget)
		vbox.setContentsMargins(0,0,0,0)

		self.setLayout(vbox)

		self.optionsTab = tab2

	def editKeys(self):
		print("OK")

	def start(self):
		print(self.optionsTab.getDelay())
		controller.startRunning()

class OptionsTab(QtGui.QWidget):
	
	def __init__(self, parent, parentWidget):
		super(OptionsTab, self).__init__(parent)
		self.parent = parent
		self.parentWidget = parentWidget
		self.initUI()

		
	def initUI(self):
		self.layout = QtGui.QHBoxLayout() 

		self.apiKeysLayout = QtGui.QGridLayout()

		self.apiKeyTable = APIKeyTable(controller.apiKeys())
		self.apiKeysLayout.addWidget(self.apiKeyTable, 0, 1, 1, 2)

		editKeysButton = QtGui.QPushButton('Edit Keys', self)
		editKeysButton.clicked.connect(self.parentWidget.editKeys)
		self.apiKeysLayout.addWidget(editKeysButton, 1, 2, )
		self.layout.addLayout(self.apiKeysLayout)

		spacer = QtGui.QSpacerItem(200,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
		self.layout.addItem(spacer)

		verticalLine 	=  QtGui.QFrame()
		verticalLine.setFrameStyle(QtGui.QFrame.VLine)
		verticalLine.setSizePolicy(QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
		self.layout.addWidget(verticalLine)

		self.rightSide = QtGui.QVBoxLayout()
		self.rightForm = QtGui.QFormLayout()
		self.delay = QtGui.QLineEdit(str(30))
		self.rightForm.addRow('Delay:', self.delay)

		self.rightSide.addLayout(self.rightForm)

		self.startButton = QtGui.QPushButton('Start', self)
		self.startButton.clicked.connect(self.startThread)
		self.rightSide.addWidget(self.startButton)

		self.layout.addLayout(self.rightSide)
		self.setLayout(self.layout)

	def getDelay(self):
		return int(self.delay.text())

	def startThread(self):
		self.parentWidget.start()
		self.startButton.setEnabled(False)



class MainWindow(QtGui.QMainWindow):
	
	def __init__(self):
		super(MainWindow, self).__init__()
		self.mainWidget = MainWidget(self) 
		self.setCentralWidget(self.mainWidget)
		self.initUI()
		
	def initUI(self):
		self.setWindowTitle('Macys Suit Getter')
		self.setGeometry(300,300,622,280)
		self.show()
	
	def showAbout(self):
		msgBox = QtGui.QMessageBox()
		msgBox.setWindowTitle("About")
		msgBox.setText("Copy a Macys Suit URl into the field and press the button. Enter a file name (with .csv or whatever). It makes it a csv.\nCreated by Luke Li on March 10, 2014")
		msgBox.exec_()

class APIKeyTable(QtGui.QTableWidget):
	def __init__(self, data, *args):
		QtGui.QTableWidget.__init__(self, *args)
		self.data = data
		self.setColumnCount(2)
		headerLabels = ['API', 'Has Key']
		self.setHorizontalHeaderLabels(headerLabels)
		self.verticalHeader().hide()
		self.setData()
		self.resizeColumnsToContents()

	def setData(self):
		self.setRowCount(len(self.data))
		n = 0
		for key in self.data:
			labelItem = QtGui.QTableWidgetItem(key)
			labelItem.setFlags(QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled)
			hasKey = self.data[key] != ''
			valueItem =  QtGui.QTableWidgetItem(str(hasKey))
			valueItem.setFlags(QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled)
			self.setItem(n, 0, labelItem)
			self.setItem(n, 1, valueItem)
			n += 1

def main():
	
	app = QtGui.QApplication(sys.argv)
	ex = MainWindow()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()  