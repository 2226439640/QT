from PySide2.QtWidgets import QApplication
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile
import requests


class postboy:
    def __init__(self):
        qfile = QFile('./postboy.ui')
        qfile.open(QFile.ReadOnly)
        qfile.close()

        self.ui = QUiLoader().load(qfile)
        self.ui.comboBox.addItems(['GET', 'POST', 'PUT', 'DELETE'])
        self.ui.sendButton.clicked.connect(self._handerSendButton)
        self.ui.clear.clicked.connect(lambda: self.ui.logtext.clear())
        self.ui.addButton.clicked.connect(self._handerAddButton)
        self.ui.removeButton.clicked.connect(self._handerRemoveButton)

    def _handerSendButton(self):
        method = self.ui.comboBox.currentText()
        url = self.ui.lineEdit.text()
        headers = dict()
        for k in range(self.ui.headtW.rowCount()):
            headers[self.ui.headtW.item(k, 0).text()] = self.ui.headtW.item(k, 1).text()
        res = requests.request(method=method, url=url, headers=headers).text
        self.ui.logtext.setPlainText(res)

    def _handerAddButton(self):
        self.ui.headtW.insertRow(self.ui.headtW.rowCount())

    def _handerRemoveButton(self):
        self.ui.headtW.removeRow(self.ui.headtW.currentRow())

    # def _handerClearButton(self):
    #     self.ui.clear.clear()


if __name__ == '__main__':
    app = QApplication()
    p = postboy()
    p.ui.show()
    app.exec_()

