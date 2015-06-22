from PySide.QtCore import *
from PySide.QtGui import *
import sys

import pyFile

class app(QMainWindow,pyFile.Ui_MainWindow):
	def __init__(self,parent=None):
		super(app,self).__init__(parent)
		self.setupUi(self)

		self.connect(self.upload,SIGNAL("clicked()"),self.uploadData)
		self.connect(self.cancel,SIGNAL("clicked()"),self.cancelUpload)
		self.connect(self.settingsOk,SIGNAL("clicked()"),self.settingsOkClicked)
	def uploadData(self):
		QMessageBox.information(self,"Test","UPLOAD")
	def cancelUpload(self):
		QMessageBox.information(self,"Test","CANCEL")
	def settingsOkClicked(self):
		QMessageBox.information(self,"Test",self.ip.text()+', '+self.port.text())


obj=QApplication(sys.argv)
form=app()
form.show()
obj.exec_()