import sys
from PyQt5.QtWidgets import QApplication, QDialog, QFormLayout,\
    QLineEdit, QTableWidgetItem, QSizePolicy, QLabel
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import pyqtSlot
from main_ui import Ui_Dialog
from login_ui import Ui_Login
from os import path
import dataset
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FC
from matplotlib.figure import Figure
import pandas as pd
import random


DBNAME = 'postgres'
DBUSERNAME = 'postgres'
DBPASSWORD = 'work01'


class Canvas(FC):
    # this is matplotlib Qt5 embed class
    def __init__(self, parent=None, width=7.1, height=5.95, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        FC.__init__(self, fig)
        # tying itself to the parent widget
        self.setParent(parent)

        FC.setSizePolicy(self,
                         QSizePolicy.Expanding,
                         QSizePolicy.Expanding)
        FC.updateGeometry(self)
        # setting up axes
        self.axes = self.figure.add_subplot(111)

    def plot(self, data, query_info, max_n=100):
        # figuring what column name is the legend
        legend_pop = query_info[-2]
        # clearing whats on the chart now
        self.axes.cla()
        legends = list()
        try:
            d = dict()
            x_titles = list()
            for i, row in enumerate(data):
                # only processing first max_n to prevent being overflown with data
                if i > max_n:
                    break
                # popping legend column
                legend = row.pop(legend_pop)
                for k in list(row.keys()):
                    # leaving on date columns
                    if not k.replace('/', '').isdigit():
                        row.pop(k)
                # setting up headers if wasnt done before
                if not x_titles:
                    d['x'] = [i for i in range(len(row))]
                    x_titles = list(row.keys())
                # saving data
                d[legend] = list(row.values())
            # converting our data dict to dataframe for matplotlibs
            df = pd.DataFrame(d)
            for y in d:
                # skipping X headers
                if y == 'x':
                    continue
                # drawing each line separately, making sure to pick color for it
                color = (random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1))
                legends.append((y, color))
                self.axes.plot('x', y, data=df, color=color, linewidth=2)
        except Exception as e:
            print(e)
            return
        self.draw()
        return legends


class MainDialog(QDialog):
    def __init__(self, login_dialog):
        super(MainDialog, self).__init__()
        # recovering UI from main_ui.py file
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # got to save user name and login dialog
        self._user = str()
        self.lg = login_dialog

        # connecting logout press to logout action
        self.ui.pushButton_4.clicked.connect(self.logout)

        # loading list of queries
        self.queries = list()
        fname = path.join('.profile', 'queries')
        if path.isfile(fname):
            for line in open(path.join('.profile', 'queries')).read().split(':;:'):
                if '::' not in line:
                    continue
                query = line.split(':::')
                self.queries.append(query)
        # sorting them in alphabetic order
        self.queries.sort(key=lambda x: x[0])
        # adding queries to combo boxes
        for query in self.queries:
            self.ui.comboBox.addItem(query[0])

        # connecting buttons to their respective actions
        self.ui.comboBox.currentIndexChanged.connect(self.query_changed)
        self.ui.pushButton_2.clicked.connect(self.new_query)
        self.ui.pushButton_3.clicked.connect(self.remove_query)
        self.ui.pushButton.clicked.connect(self.run_query)

        # connecting to the database
        self.db = dataset.connect(f'postgresql://{DBUSERNAME}:{DBPASSWORD}@localhost:5432/{DBNAME}')

        # creating plot and legend objects
        self.cv = Canvas(self.ui.frame_3)
        self.legend_labels = [(self.ui.label_2, self.ui.label_3)]

    # this is triggered when admin pressed "Remove query"
    @pyqtSlot()
    def remove_query(self):
        # removing cquery from combox box and list of queries
        index = self.ui.comboBox.currentIndex()
        self.queries.pop(index)
        self.ui.comboBox.removeItem(index)
        self.update()

    # this is triggered when user/admin presses 'Run Query' button
    @pyqtSlot()
    def run_query(self):
        # we get text of the current query from text field
        query = self.ui.plainTextEdit.toPlainText()
        # removing all rows from table widget
        self.ui.tableWidget.setRowCount(0)
        # creating vars for setting up headers
        columns_set = False
        header = list()
        try:
            for i, row in enumerate(self.db.query(query)):
                # adding new row to the table widget
                self.ui.tableWidget.insertRow(i)
                # setting up headers
                if not columns_set:
                    header = list(row.keys())
                    self.ui.tableWidget.setColumnCount(len(header))
                    self.ui.tableWidget.setHorizontalHeaderLabels(header)
                    columns_set = True
                # adding values to the fresh row
                for j, col in enumerate(header):
                    self.ui.tableWidget.setItem(i, j, QTableWidgetItem(str(row[col])))
        except Exception as e:
            print(type(e), e)
        # checking if this query is plottable and calling the plot function
        query_info = self.queries[self.ui.comboBox.currentIndex()]
        if query_info[-1].strip() == 'plotit':
            self.plot_chart(self.db.query(query), query_info)

    def plot_chart(self, data, query_info):
        # plots the chart
        # clears any legend widgets
        for lcolor, ltext in self.legend_labels:
            lcolor.setParent(None)
            ltext.setParent(None)
        self.legend_labels = list()
        # gets new legends from matplotlib object & plots the chart
        legends = self.cv.plot(data, query_info)
        # making sure plot is visible on its tab
        self.ui.tabWidget.setCurrentIndex(1)
        # we wont have space to show all the legends, so limiting it
        max_legend = 20
        try:
            # going through all legends returned and creating labels for them
            for i, leg in enumerate(legends):
                # breaknig is max legend number is met
                if i > max_legend:
                    break
                # creating color label
                lcolor = QLabel(parent=self.ui.groupBox, text="---")
                self.ui.formLayout.setWidget(i, QFormLayout.LabelRole, lcolor)
                # coloring it
                qp = QPalette()
                qp.setColor(lcolor.backgroundRole(), QColor(*[255 * l for l in leg[1]]))
                qp.setColor(lcolor.foregroundRole(), QColor(*[255 * l for l in leg[1]]))
                lcolor.setAutoFillBackground(True)
                lcolor.setPalette(qp)
                # creating legend name label
                ltext = QLabel(parent=self.ui.groupBox, text=leg[0])
                self.ui.formLayout.setWidget(i, QFormLayout.FieldRole, ltext)
                # saving this widget pair
                self.legend_labels.append((lcolor, ltext))
        except Exception as e:
            print(e)
        return

    # this is triggered when admin hits "Add Query" button
    @pyqtSlot()
    def new_query(self):
        # creating new query object
        query = (
            self.ui.lineEdit.text(),
            self.ui.plainTextEdit.toPlainText()
        )
        # adding it to queries and combobox
        self.queries.append(query)
        self.ui.comboBox.addItem(query[0])
        # setting new query as currently selected
        self.ui.comboBox.setCurrentIndex(len(self.queries) - 1)

    # this happens when combo box chooses another query
    @pyqtSlot()
    def query_changed(self):
        query = self.queries[self.ui.comboBox.currentIndex()]
        # updating edit field and query title fields
        self.ui.lineEdit.setText(query[0])
        self.ui.plainTextEdit.setPlainText(query[1])

    # this is for login window to call prior to displaying = sets up rights
    def set_user(self, user):
        self.ui.label.setText(f'Logged in as {user}')
        # admin has access to editing all
        if user == 'Admin':
            self.ui.plainTextEdit.setDisabled(False)
            self.ui.lineEdit.show()
            self.ui.pushButton_2.show()
            self.ui.pushButton_3.show()
        # users are more of a read only type
        else:
            self.ui.plainTextEdit.setDisabled(True)
            self.ui.lineEdit.hide()
            self.ui.pushButton_2.hide()
            self.ui.pushButton_3.hide()
        self.query_changed()
        self.ui.tableWidget.setRowCount(0)
        self.ui.tableWidget.setColumnCount(0)
        self.ui.tabWidget.setCurrentIndex(0)

    # this happens when login button is pressed
    @pyqtSlot()
    def logout(self):
        # going back to logout window
        self.hide()
        self.lg.show()

    # this is triggered when application is about to exit
    def closeEvent(self, a0):
        # saving queries to the file
        with open(path.join('.profile', 'queries'), 'w') as f:
            f.write(':;:'.join([f':::'.join(q) for q in self.queries]))
        a0.accept()


class LoginDialog(QDialog):
    def __init__(self):
        super(LoginDialog, self).__init__()
        # extracting UI from login_ui.py file
        self.ui = Ui_Login()
        self.ui.setupUi(self)

        # making password field echo asterisks instead of characters
        self.ui.lineEdit_2.setEchoMode(QLineEdit.Password)

        # connecting login action
        self.ui.pushButton.clicked.connect(self.login)

        # loading list of users and ther password
        self.users = dict()
        for line in open(path.join('.profile', 'users')).read().split('\n'):
            name, password = line.split('\t')
            self.users[name] = password

        # creating main dialog instance to launch it after login was successful
        self.md = MainDialog(self)

    # this happens when we press login button
    @pyqtSlot()
    def login(self):
        # checking if user exists
        user = self.ui.lineEdit.text()
        if user in self.users:
            # checking if his password is correct
            if self.ui.lineEdit_2.text() == self.users[user]:
                # displaying main dialog and hiding login dialog
                self.md.set_user(user)
                self.md.show()
                self.hide()
        # clearing input if user/pw do not match
        self.ui.lineEdit.setText('')
        self.ui.lineEdit_2.setText('')


if __name__ == '__main__':
    # creating QApplication instance
    app = QApplication(sys.argv)

    # Starting from login dialog
    lg = LoginDialog()
    lg.show()

    sys.exit(app.exec_())
