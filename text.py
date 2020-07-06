import datetime
import json
import sys
import os
from PySide2 import QtCore, QtGui, QtWidgets
import maya.cmds as cmds
from shiboken2 import wrapInstance
import maya.OpenMaya as om
import maya.OpenMayaUI as omui


def maya_main_window():
    # Return the maya main window
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class RigAssetViewer(QtWidgets.QDialog):

    ASSET_DIR_PATH = "D:\Rig"

    IMAGE_WIDTH = 400
    IMAGE_HEIGHT = IMAGE_WIDTH / 1.77778

    def __init__(self, parent=maya_main_window()):
        super(RigAssetViewer, self).__init__(parent)

        self.setWindowTitle("Rig Asset Viewer")
        self.setMinimumSize(400, 500)

        # windowFlags
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

        # self.set_edit_enabled(False)

        self.tree_wdg.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree_wdg.customContextMenuRequested.connect(self.show_context_menu)

        self.refresh_list()

    def create_actions(self):
        self.show_in_folder_action = QtWidgets.QAction("Show in Folder", self)

    def create_widgets(self):

        # file path and open the folder
        self.filepath_le = QtWidgets.QLineEdit()
        self.select_file_path_btn = QtWidgets.QPushButton()
        self.select_file_path_btn.setIcon(QtGui.QIcon(":fileOpen.png"))
        self.select_file_path_btn.setToolTip("Select File")

        self.tree_wdg = QtWidgets.QTreeWidget()
        self.tree_wdg.setHeaderHidden(True)

        self.open_rb = QtWidgets.QRadioButton("Open")
        self.open_rb.setChecked(True)
        self.reference_rb = QtWidgets.QRadioButton("Reference")

        self.apply_btn = QtWidgets.QPushButton("Apply")
        self.apply_btn.setMinimumWidth(200)
        self.create_btn = QtWidgets.QPushButton("Create New Rig Asset")

    def create_layout(self):

        # file path
        file_path_layout = QtWidgets.QHBoxLayout()
        file_path_layout.addWidget(self.filepath_le)
        file_path_layout.addWidget(self.select_file_path_btn)

        file_form_layout = QtWidgets.QFormLayout()
        file_form_layout.addRow("Folder Path:", file_path_layout)
        # radio : open, reference
        radio_btn_layout = QtWidgets.QHBoxLayout()
        radio_btn_layout.addWidget(self.open_rb)
        radio_btn_layout.addWidget(self.reference_rb)
        radio_btn_layout.addStretch()
        radio_btn_layout.addWidget(self.apply_btn)

        form_layout = QtWidgets.QFormLayout()
        #form_layout.addRow("Folder Path:", file_path_layout)
        form_layout.addRow("File list:", self.tree_wdg)
        form_layout.addRow("", radio_btn_layout)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.create_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)

        main_layout.addLayout(file_form_layout)

        main_layout.addLayout(form_layout)

        main_layout.addLayout(button_layout)

    def create_connections(self):

        self.show_in_folder_action.triggered.connect(self.show_in_folder)
        # file path button connect
        self.select_file_path_btn.clicked.connect(self.open_folder_dialog)

        self.apply_btn.clicked.connect(self.load_file)
        self.tree_wdg.itemClicked.connect(self.onItemClicked)

    def onItemClicked(self):
        folder_path = self.filepath_le.text()
        #print folder_path;

        item = self.tree_wdg.currentItem().text(0)
        print(item)

        file_parent = self.tree_wdg.currentItem().parent().text(0)
        #print file_parent

        get_file_path = folder_path + "/" + file_parent + "/" + item
        print get_file_path

    def open_folder_dialog(self):
        directory = str(QtWidgets.QFileDialog.getExistingDirectory())
        print directory

        self.filepath_le.setText('{}'.format(directory))

    def load_file(self):

        folder_path = self.filepath_le.text()
        item = self.tree_wdg.currentItem().text(0)
        file_parent = self.tree_wdg.currentItem().parent().text(0)
        get_file_path = folder_path + "/" + file_parent + "/" + item

        if not get_file_path:
            return

        file_info = QtCore.QFileInfo(get_file_path)
        if not file_info.exists():
            om.MGlobal.displayError("File does not exist: {0}".format(get_file_path))
            return

        if self.open_rb.isChecked():
            self.open_file(get_file_path)

        else:
            self.reference_file(get_file_path)

    def open_file(self, get_file_path):

        cmds.file(get_file_path, open=True, ignoreVersion=True, force=True)

    def reference_file(self, get_file_path):
        cmds.file(get_file_path, reference=True, ignoreVersion=True)

    def refresh_list(self):
        # self.tree_wdg.clear()
        folder_path = self.filepath_le.text()

        if folder_path:
            self.add_children(None, self.ASSET_DIR_PATH)

        # if not folder_path:
        #    return
        # else:

        #    self.add_children(None, self.ASSET_DIR_PATH)
        #self.add_children(None, self.ASSET_DIR_PATH)

    def add_children(self, parent_item, dir_path):
        print dir_path
        directory = QtCore.QDir(dir_path)

        files_in_directory = directory.entryList(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllEntries, QtCore.QDir.DirsFirst | QtCore.QDir.IgnoreCase)

        for file_name in files_in_directory:
            self.add_child(parent_item, dir_path, file_name)

    def add_child(self, parent_item, dir_path, file_name):

        file_path = "{0}/{1}".format(dir_path, file_name)

        file_info = QtCore.QFileInfo(file_path)

        # filter file suffix jpb,png,json,tga
        if file_info.suffix().lower() == "jpg":
            return

        if file_info.suffix().lower() == "png":
            return

        if file_info.suffix().lower() == "json":
            return

        if file_info.suffix().lower() == "tga":
            return

        item = QtWidgets.QTreeWidgetItem(parent_item, [file_name])
        item.setData(0, QtCore.Qt.UserRole, file_path)

        # if it is folder, will make the folder
        if file_info.isDir():
            self.add_children(item, file_info.absoluteFilePath())

        # items adding in wdg
        if not parent_item:
            self.tree_wdg.addTopLevelItem(item)

    def show_context_menu(self, pos):
        item = self.tree_wdg.itemAt(pos)

        if not item:
            return

        file_path = item.data(0, QtCore.Qt.UserRole)
        self.show_in_folder_action.setData(file_path)

        context_menu = QtWidgets.QMenu()
        context_menu.addAction(self.show_in_folder_action)
        context_menu.exec_(self.tree_wdg.mapToGlobal(pos))

    def show_in_folder(self):

        file_path = self.show_in_folder_action.data()
        print (file_path)

        if cmds.about(windows=True):
            if self.open_in_explorer(file_path):
                return

        # This only open the directory. It does not select the file.
        file_info = QtCore.QFileInfo(file_path)

        if file_info.isDir():
            QtGui.QDesktopServices.openUrl(file_path)
        else:
            QtGui.QDesktopServices.openUrl(file_info.path())

    def open_in_explorer(self, file_path):
        # Windows specific implementation
        file_info = QtCore.QFileInfo(file_path)
        args = []
        if not file_info.isDir():
            args.append("/select,")

        args.append(QtCore.QDir.toNativeSeparators(file_path))

        if QtCore.QProcess.startDetached("explorer", args):
            return True

        return False


if __name__ == "__main__":

    try:
        Rig_Asset_View.close()  # pylint: disable=E0601
        Rig_Asset_View.deleteLater()
    except:
        pass

    Rig_Asset_View = RigAssetViewer()
    Rig_Asset_View.show()
