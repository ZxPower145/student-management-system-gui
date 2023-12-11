from PyQt6.QtWidgets import QApplication, QLabel, QGridLayout, QLineEdit, QPushButton, QMainWindow, \
    QTableWidget, QTableWidgetItem, QDialog, QVBoxLayout, QComboBox, QToolBar, QStatusBar, QMessageBox
from PyQt6.QtGui import QAction, QIcon
import sys
from PyQt6.QtCore import Qt
import qdarktheme
import mysql.connector


class DataBaseConnection:
    def __init__(self, host="localhost", user="root", password="QWEshadeR123", database="school"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        connection = mysql.connector.connect(host=self.host, user=self.user, password=self.password,
                                             database=self.database)
        return connection


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(504, 500)
        # Connect to the database
        connection = DataBaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students")
        self.row_number = len(cursor.fetchall())

        # Create the tooltip
        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")
        # Add actions to the tooltip
        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.triggered.connect(self.about)

        search_action = QAction(QIcon("icons/search.png"), "Search", self)
        edit_menu_item.addAction(search_action)
        search_action.triggered.connect(self.search_diag)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("ID", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 150)
        self.setCentralWidget(self.table)

        # Create the toolbar
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        # Add TOOLBAR elements
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # Create the STATUS bar and add elements to it
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Detect a cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        # Remove all the things from the status bar before adding them back on click
        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)
        label_children = self.findChildren(QLabel)
        if label_children:
            for child in label_children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

        # Add the students count
        students_number = QLabel(f"{str(self.row_number)} students total")
        self.statusbar.addWidget(students_number)

    def load_data(self):
        connection = DataBaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students")
        result = cursor.fetchall()
        self.table.setRowCount(0)
        for row_nr, row_data in enumerate(result):
            self.table.insertRow(row_nr)
            for column_nr, data in enumerate(row_data):
                self.table.setItem(row_nr, column_nr, QTableWidgetItem(str(data)))
        connection.close()

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search_diag(self):
        dialog = SearchDialog()
        dialog.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
        This app was created by ZxPower
        Feel free to modify/use this app!
        """
        self.setText(content)


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search for a student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        self.search_student = QLineEdit()
        self.search_student.setPlaceholderText("Student Name")
        layout.addWidget(self.search_student)

        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.search)
        layout.addWidget(search_btn)

        self.setLayout(layout)

    def search(self):
        name = self.search_student.text()
        connection = DataBaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students WHERE name = %s", (name,))
        result = cursor.fetchall()
        items = student_management.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            student_management.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()
        # Add student name widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Student Name")
        layout.addWidget(self.student_name)
        # Add course list combobox
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics", "Python"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)
        # Add mobile
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)
        # Add student btn
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_student)
        layout.addWidget(add_btn)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()
        connection = DataBaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (%s, %s, %s)",
                       (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        student_management.load_data()


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Edit Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        # Layout setup
        layout = QVBoxLayout()

        # Get student name from selected row
        index = student_management.table.currentRow()

        # Set the default data on the edit dialog
        selected_student_name = student_management.table.item(index, 1).text()
        selected_course = student_management.table.item(index, 2).text()
        selected_mobile = student_management.table.item(index, 3).text()

        # Get ID from the selected row
        self.student_id = student_management.table.item(index, 0).text()

        # Add student name widgets
        student_name_label = QLabel("Student Name:")
        layout.addWidget(student_name_label)
        self.student_name = QLineEdit(selected_student_name)
        self.student_name.setPlaceholderText("Enter Student Name")
        layout.addWidget(self.student_name)

        # Add course list combobox
        course_name_label = QLabel("Course:")
        layout.addWidget(course_name_label)
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics", "Python"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(selected_course)
        layout.addWidget(self.course_name)

        # Add mobile
        mobile_label = QLabel("Mobile:")
        layout.addWidget(mobile_label)
        self.mobile = QLineEdit(selected_mobile)
        self.mobile.setPlaceholderText("Enter Mobile Number")
        layout.addWidget(self.mobile)

        # Add save button
        edit_btn = QPushButton("Save")
        edit_btn.clicked.connect(self.update_student)
        layout.addWidget(edit_btn)

        # Set layout for the dialog
        self.setLayout(layout)

    def update_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()
        connection = DataBaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = %s, course = %s, mobile = %s WHERE id = %s",
                       (name, course, mobile, self.student_id))
        connection.commit()
        cursor.close()
        connection.close()
        # Refresh the table
        student_management.load_data()
        self.close()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")

        layout = QGridLayout()

        confirmation = QLabel("Are you sure you want to delete?")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)
        self.setLayout(layout)

        yes.clicked.connect(self.delete_student)
        no.clicked.connect(self.no)

    def no(self):
        self.close()

    def delete_student(self):
        # Get the current index of the selected student
        index = student_management.table.currentRow()
        # Get the ID of the selected student
        student_id = student_management.table.item(index, 0).text()
        # Connect to the DB
        connection = DataBaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM students WHERE id = %s", (student_id, ))
        connection.commit()
        cursor.close()
        connection.close()
        student_management.load_data()

        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The record was deleted successfully!")
        confirmation_widget.exec()


app = QApplication(sys.argv)
# Apply dark theme
qdarktheme.setup_theme()
student_management = MainWindow()
student_management.show()
student_management.load_data()
sys.exit(app.exec())
