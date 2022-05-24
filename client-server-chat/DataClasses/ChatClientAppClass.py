from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog
import ui
from DataClasses import ClientClass


class ChatClientApp(QtWidgets.QMainWindow, ui.Ui_Window_Main):
    curr_client = ClientClass.Client()

    def __init__(self):
        # TODO: update listView

        super().__init__()
        self.setupUi(self)
        self.curr_client.set_chat(self.listWidget_Messages)
        self.curr_client.set_connect_button(self.Button_Connect)
        self.curr_client.set_login_tb(self.TextBox_Login)

    def select_file(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)
        file_path, _ = dlg.getOpenFileName(self, 'Select file to send')
        self.curr_client.attached_file = file_path
        self.Label_AttachedFile.setText(file_path)

    def setup_bindings(self):
        self.Button_AddAttach.clicked.connect(self.select_file)
        self.Button_Send.clicked.connect(lambda: self.curr_client.send(self.TextBox_Message.toPlainText(),
                                                                       self.TextBox_Receiver.toPlainText()))
        self.Button_Connect.clicked.connect(lambda: self.curr_client.connect(self.TextBox_Login.toPlainText()))
        self.Button_Connect.clicked.connect(self.curr_client.listen)
        self.Button_SetupFolder.clicked.connect(self.setup_folder)

    def setup_folder(self):
        dlg = QFileDialog()
        #dlg.setFileMode(QFileDialog.FileMode.DirectoryOnly)
        path = dlg.getExistingDirectory(self, 'Select folder for saving files')
        self.curr_client.folder_for_saving = path
        self.Label_FolderPath.setText(path)




