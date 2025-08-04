import sys
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QApplication,
    QLabel,   QLineEdit,    QMainWindow,    QVBoxLayout,
    QWidget,
    QScrollArea,
    QFrame, QPushButton,QHBoxLayout,QCheckBox, QDialog,QInputDialog)
from PySide6.QtGui import QIcon
import psycopg2
from postFILE import get_connection

import sys
import os

def resource_path(relative_path):

    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)




class functions:

    def __init__(self, layoutContent, taskInput):
        self.layoutContent = layoutContent
        self.taskInput = taskInput
        self.conn = get_connection()
        self.cur = self.conn.cursor()

    def bind_checkbox(self, checkbox: QCheckBox, task_id: int):
        checkbox.stateChanged.connect(lambda state: self.update_task_completed(task_id, state))

    def update_task_completed(self, task_id, state):

        completed = (state == Qt.CheckState.Checked.value)
        self.cur.execute("UPDATE tasks SET completed = %s WHERE id = %s", (completed, task_id))
        self.conn.commit()

    def load_tasks(self):

        self.cur.execute("SELECT id, task, completed FROM tasks ORDER BY id")


        rows = self.cur.fetchall()

        for row in rows:
            task_id, task_text, completed = row

            label = QLabel(f" {task_text}")
            task_widget = QWidget()
            task_widget.setStyleSheet("""
                background-color: white;
                border: 1px solid white;
                border-radius: 6px;
                padding: 8px;
            """)

            task_layout = QHBoxLayout(task_widget)

            checkbox = QCheckBox()
            checkbox.blockSignals(True)
            checkbox.setChecked(completed)
            checkbox.blockSignals(False)
            self.bind_checkbox(checkbox, task_id)


            checkbox.setStyleSheet(""" /* Your checkbox style here */ """)
            icon_path = resource_path("img2-round.png")

            checkbox.setStyleSheet(f"""
                QCheckBox::indicator {{
                    width: 20px;
                    height: 20px;
                }}
                QCheckBox::indicator:unchecked {{
                    border: 2px solid #0b49db;
                    background-color: white;
                    border-radius: 5px;
                }}
                QCheckBox::indicator:checked {{
                    border: 2px solid #0b49db;
                    background-color: white;
                    image: url("{icon_path.replace('\\', '/')}");
                    border-radius: 5px;
                }}
            """)




            more_button = QPushButton("⋮")
            more_button.setStyleSheet(""" /* Your more button style here */ """)

            more_button.setStyleSheet("""
                           QPushButton {
                               background-color: #bcbdcf;
                               color: white;
                               border: none;
                               border-radius: 6px;
                               padding: 4px 8px;
                               font-weight: bold;
                               font-size: 24px;    /* Make the ⋮ bigger */
                               min-width: 20px;    /* Smaller width */
                               max-width: 20px;
                               max-height: 20px;
                               line-height: 24px;
                           }
                           QPushButton:hover {
                               background-color: #f7161e;
                           }
                           QPushButton:pressed {
                               background-color: #1a6f2a;
                           }
                       """)



            task_layout.addWidget(checkbox)
            task_layout.addWidget(label)
            task_layout.addStretch()
            task_layout.addWidget(more_button)
            task_layout.setContentsMargins(0, 0, 0, 0)

            self.layoutContent.addWidget(task_widget)
            more_button.clicked.connect(lambda _, lbl=label, w=task_widget, tid=task_id: self.show_more(lbl, w, tid))




    def show_more(self, label: QLabel, task_widget: QWidget, task_id: int):
        dialog=QDialog()
        dialog.setWindowTitle(" ")
        dialog.setWindowIcon(QIcon(resource_path("blank_more.png")))
        layout = QVBoxLayout(dialog)
        edit_button = QPushButton("Edit")
        delete_button = QPushButton("Delete")
        layout.addWidget(edit_button)
        layout.addWidget(delete_button)

        def edit_task():
            dialog = QInputDialog(task_widget)
            dialog.setWindowTitle(" ")
            dialog.setLabelText(" ")
            dialog.setFixedSize(200,10)

            dialog.setTextValue(label.text())
            dialog.setWindowIcon(QIcon(resource_path("blank_more.png")))


            dialog.setStyleSheet("""
                    QDialog {
                        background-color: white;
                        border-radius: 12px;
                    }
                    QLineEdit {
                        padding: 8px;
                        font-size: 14px;
                        border: 2px solid #0b49db;
                        border-radius: 6px;
                    }
                    QPushButton {
                        padding: 6px 12px;
                        font-size: 14px;
                        border-radius: 6px;
                        background-color: #0b49db;
                        color: white;
                    }
                    QPushButton:hover {
                        background-color: #218838;
                    }
                    QPushButton:pressed {
                        background-color: #1a6f2a;
                    }
                """)


            if dialog.exec() == QDialog.Accepted:
                new_text = dialog.textValue()
                if new_text:
                    label.setText(new_text)
                    self.cur.execute("UPDATE tasks SET task = %s WHERE id = %s", (new_text, task_id))
                    self.conn.commit()
        def delete_task():
            task_widget.setParent(None)
            self.cur.execute("DELETE FROM tasks WHERE id=%s", (task_id,))

            self.conn.commit()
            dialog.close()
            dialog.close()
        edit_button.clicked.connect(edit_task)
        delete_button.clicked.connect(delete_task)

        dialog.exec()





    def addtask(self):
        print("addtask")
        text = self.taskInput.text().strip()

        if not text:
            return

        self.cur.execute("INSERT INTO tasks (task, completed) VALUES (%s, %s) RETURNING id", (text, False))
        task_id = self.cur.fetchone()[0]
        self.conn.commit()

        label = QLabel(f" {text}")
        task_widget = QWidget()
        task_widget.setStyleSheet("""
            background-color: white;
            border: 1px solid white;
            border-radius: 6px;
            padding: 8px;
        """)

        task_layout = QHBoxLayout(task_widget)

        checkbox = QCheckBox()
        checkbox.blockSignals(True)
        checkbox.setChecked(False)
        checkbox.blockSignals(False)
        self.bind_checkbox(checkbox, task_id)

        checkbox.setObjectName("customCheckbox")

        checkbox.setStyleSheet("""
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #0b49db;
                background-color: white;
                border-radius: 5px;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #0b49db;
                background-color: white;
                image: url(img2-round.png);
                border-radius: 5px;
            }
        """)

        more_button = QPushButton("⋮")
        more_button.setStyleSheet("""
            QPushButton {
                background-color: #bcbdcf;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 4px 8px;
                font-weight: bold;
                font-size: 24px;
                min-width: 20px;
                max-width: 20px;
                max-height: 20px;
                line-height: 24px;
            }
            QPushButton:hover {
                background-color: #f7161e;
            }
            QPushButton:pressed {
                background-color: #1a6f2a;
            }
        """)

        task_layout.addWidget(checkbox)
        task_layout.addWidget(label)
        task_layout.addStretch()
        task_layout.addWidget(more_button)
        task_layout.setContentsMargins(0, 0, 0, 0)

        self.layoutContent.addWidget(task_widget)
        more_button.clicked.connect(lambda _, lbl=label, w=task_widget, tid=task_id: self.show_more(lbl, w, tid))

        self.taskInput.clear()