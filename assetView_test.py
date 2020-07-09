import json
import sys
import os
from PySide2 import QtCore, QtWidgets


class Second(QtWidgets.QDialog):

    # file filters, only json
    FILE_FILTERS = "(*.json);; *.json;;All Files (*.*)"
    old_asset = {}

    def __init__(self, parent=None):
        super(Second, self).__init__(parent)

        self.setWindowTitle("Add assetviewer")
        self.setMinimumSize(400, 300)

        # windowFlags
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):

        self.name_le = QtWidgets.QLineEdit()
        self.description_plaintext = QtWidgets.QPlainTextEdit()
        self.description_plaintext.setFixedHeight(100)

        # file path and open the folder
        self.filepath_le = QtWidgets.QLineEdit()
        self.select_file_path_btn = QtWidgets.QPushButton()
        self.select_file_path_btn.setToolTip("Select File")
        self.save_btn = QtWidgets.QPushButton("Save")

    def create_layout(self):

        # file path
        file_path_layout = QtWidgets.QHBoxLayout()
        file_path_layout.addWidget(self.filepath_le)
        file_path_layout.addWidget(self.select_file_path_btn)

        file_form_layout = QtWidgets.QFormLayout()
        file_form_layout.addRow("File Path:", file_path_layout)

        details_layout = QtWidgets.QFormLayout()
        details_layout.addRow("Name:", self.name_le)
        details_layout.addRow("Description:", self.description_plaintext)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.save_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.addLayout(file_form_layout)
        main_layout.addLayout(details_layout)
        main_layout.addLayout(button_layout)

    def create_connections(self):
        self.save_btn.clicked.connect(self.save_asset_details)
        self.select_file_path_btn.clicked.connect(self.show_file_select_dialog)

    def show_file_select_dialog(self):
        self.file_path, self.selected_filter = QtWidgets.QFileDialog.getOpenFileName(self, "Select File", "", self.FILE_FILTERS)
        if self.file_path:
            self.filepath_le.setText(self.file_path)
            self.load_assets_from_json()

    def load_assets_from_json(self):

        with open(self.file_path, "r") as file_for_read:
            self.assets = json.load(file_for_read)
        old_asset = self.assets
        for asset_code in self.assets.keys():
            print (asset_code)
        print (old_asset)

    def save_assets_to_json(self):
        os.chmod(self.file_path, 0777)
        with open(self.file_path, "w") as file_for_write:
            json.dump(self.assets, file_for_write, indent=4)

    def save_asset_details(self):

        New_asset = self.name_le.text()

        self.assets.update({'name': self.name_le.text()})
        self.assets.update({'description': self.description_plaintext.toPlainText()})
        self.save_assets_to_json()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = Second()
    window.show()

    app.exec_()
