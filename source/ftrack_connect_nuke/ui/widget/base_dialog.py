import os
import ftrack
from PySide import QtGui, QtCore
from ftrack_connect.ui.widget.header import HeaderWidget



class BaseDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(BaseDialog, self).__init__(parent=parent)
        self.current_task = ftrack.Task(
            os.getenv('FTRACK_TASKID', os.getenv('FTRACK_SHOTID'))
        )
        self.initUI()

    def initUI(self):
        css_task_global = """
        QFrame { padding: 3px; border-radius: 4px;
                 background: #252525; color: #FFF; }
        """
        main_layout = QtGui.QVBoxLayout()
        self.setLayout(main_layout)
        self.header = HeaderWidget()
        main_layout.addWidget(self.header)

        self.tasks_layout = QtGui.QHBoxLayout(self)

        self.tasks_cbbx = QtGui.QComboBox()
        self.tasks_cbbx.setMinimumHeight(23)

        self.tasks_cbbx.currentIndexChanged.connect(self.update_task_global)
        self.tasks_btn = QtGui.QPushButton("Browse all tasks...")
        self.tasks_btn.setMinimumWidth(125)
        self.tasks_btn.setMaximumWidth(125)
        self.tasks_btn.clicked.connect(self.browse_all_tasks)

        self.tasks_layout.addWidget(self.tasks_cbbx)
        self.tasks_layout.addWidget(self.tasks_btn)

        main_layout.addLayout(self.tasks_layout)

        layout_buttons = QtGui.QHBoxLayout()
        layout_buttons.setSpacing(10)
        self._save_btn = QtGui.QPushButton("Save", self)
        self._cancel_btn = QtGui.QPushButton("Cancel", self)

        self._cancel_btn.clicked.connect(self.reject)
        
        spacer = QtGui.QSpacerItem( 40, 20,
                                    QtGui.QSizePolicy.Expanding,
                                    QtGui.QSizePolicy.Minimum )
    
        layout_buttons.addItem(spacer)
        layout_buttons.addWidget(self._cancel_btn)
        layout_buttons.addWidget(self._save_btn)

        self.content_layout = QtGui.QVBoxLayout()
        self.layout().addLayout(self.content_layout)

    def _get_task_parents(self, task):
        task = ftrack.Task(task)
        parents = [t.getName() for t in task.getParents()]
        parents.reverse()
        parents.append(task.getName())
        parents = ' / '.join(parents)
        return parents

    def browse_all_tasks(self):
        from browser_dialog import BrowserDialog

        browser = BrowserDialog(self.current_task, self)
        if browser.result():
            self.set_task(browser.task)    


    def update_task_global(self):
        self.initiate_error_box()

        if self.current_task == None:
          error = "You don't have any task assigned to you."
          self.set_error(error)
          self.set_empty_task_mode(True)

        if not self.is_error():
          self.set_loading_mode(False)

        self.update_task()

    def update_task(self):
        raise NotImplementedError

    def set_enabled(self, bool_result):
        self._save_btn.setEnabled(bool_result)