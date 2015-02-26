import os
import ftrack
from PySide import QtGui, QtCore
from ftrack_connect.ui.widget.header import HeaderWidget
from ftrack_connect_nuke.millftrack_nuke.controller import Controller

class BaseDialog(QtGui.QDialog):
    def __init__(self, parent=None, disable_tasks_list=False):
        super(BaseDialog, self).__init__(parent=parent)
        self.current_task = ftrack.Task(
            os.getenv('FTRACK_TASKID', os.getenv('FTRACK_SHOTID'))
        )
        self._tasks_dict = {}
        self.disable_tasks_list = disable_tasks_list
        self._user = ftrack.User(os.getenv('LOGNAME'))

    def setupUI(self):
        css_task_global = """
        QFrame { padding: 3px; border-radius: 4px;
                 background: #252525; color: #FFF; }
        """
        main_layout = QtGui.QVBoxLayout()
        self.setLayout(main_layout)
        self.header = HeaderWidget()
        main_layout.addWidget(self.header)

        self.tasks_layout = QtGui.QHBoxLayout(self)

        self._tasks_cbbx = QtGui.QComboBox()
        self._tasks_cbbx.setMinimumHeight(23)

        self._tasks_cbbx.currentIndexChanged.connect(self.update_task_global)
        if self.disable_tasks_list:
            self._tasks_cbbx.setHidden(True)

        self._tasks_btn = QtGui.QPushButton("Browse all tasks...")
        self._tasks_btn.setMinimumWidth(125)
        self._tasks_btn.setMaximumWidth(125)
        self._tasks_btn.clicked.connect(self.browse_all_tasks)
        if self.disable_tasks_list:
            self._tasks_btn.setHidden(True)

        self.tasks_layout.addWidget(self._tasks_cbbx)
        self.tasks_layout.addWidget(self._tasks_btn)

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

        self.content_layout = QtGui.QVBoxLayout()
        self.layout().addLayout(self.content_layout)

        # layout_buttons.addWidget(self._cancel_btn)
        # layout_buttons.addWidget(self._save_btn)

    def _get_tasks(self):
        for task in self._user.getTasks():
            parent = self._get_task_parents(task)
            self._tasks_dict[parent] = task

        if self.current_task != None:
          current_parents = self._get_task_parents(self.current_task.getId())
          if current_parents not in self._tasks_dict.keys():
            self._tasks_dict[current_parents] = self.current_task


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
        if self.current_task == None:
          error = "You don't have any task assigned to you."
          self.header.setMessage(error, 'error')
          self.set_empty_task_mode(True)

        self.update_task()

    def update_task(self):
        raise NotImplementedError

    def set_enabled(self, bool_result):
        self._save_btn.setEnabled(bool_result)

    def set_task(self, task):
        if task is None:
            return
        parents = self._get_task_parents(task)

        if parents in self._tasks_dict.keys():
            index = self._tasks_cbbx.findText( parents, QtCore.Qt.MatchFixedString )
            self._tasks_cbbx.setCurrentIndex(index)
        else:
            self._tasks_dict[parents] = task
            self._tasks_cbbx.insertItem(0,parents)
            self._tasks_cbbx.setCurrentIndex(0)

    def initiate_tasks(self):
        self._tasks_dict = dict()

        # self.set_loading_mode(True)

        # Thread that...
        self._controller = Controller(self._get_tasks)
        self._controller.completed.connect(self.set_tasks)
        self._controller.start()
