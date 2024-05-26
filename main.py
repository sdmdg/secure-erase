"""
SecureErase
Version 0.1.1

Author: Malaka D.Gunawardana.

Release Notes:
- Version 0.1.1 (2023/12/16)

For Updates and Contributions:
    Visit the GitHub repository:
    - https://github.com/sdmdg/secure-erase

Report issues or contribute to the development. :)
"""

import os, sys, platform, random, string, time, pywintypes, win32file, win32con, multiprocessing
from PyQt5 import uic
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QLineEdit, QDialog, QListView, QTextEdit
from PyQt5.QtGui import QPixmap, QIcon, QStandardItemModel, QStandardItem, QTextCursor
from PyQt5.QtCore import Qt, QThread

class SecureErase(QMainWindow):
    def __init__(self):
        super(SecureErase, self).__init__()
        # Setup UI
        uic.loadUi(resource_path('data/main.ui'), self)
        self.setWindowIcon(QIcon(resource_path("./data/icon.png")))
        self.setWindowTitle("SecureErase " + App_version)
        self.lbl_version.setText(f"v{App_version}")
        self.lbl_icon.setPixmap(QPixmap(resource_path("./data/main.png")))
        self.aniblock.setVisible(False)
        self.logger = Logger(None)

        # Main
        self.btn_about.clicked.connect(self.f_btn_about)

        # Tab #1
        self.listview_1_model = QStandardItemModel()
        self.listView_1.setModel(self.listview_1_model)
        self.btn_1_add_files.clicked.connect(lambda: self.A_add_items())
        self.btn_1_delete_files.clicked.connect(self.A_delete_item)
        self.btn_1_clear_files.clicked.connect(self.A_clear_items)
        erase_files_thread = self.EraseFilesThread(self)
        self.btn_1_start.clicked.connect(erase_files_thread.start)

        # Tab #2
        self.btn_2_refresh.clicked.connect(self.update_available_drives)
        erase_free_space_thread = self.EraseFreeSpaceThread(self)
        self.btn_2_start.clicked.connect(erase_free_space_thread.start)


        self.update_available_drives()
        self.logger.write("Load UI complete.")
        self.show()

    class EraseFilesThread(QThread):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.parent = parent
        def run(self):
            self.parent.erase_files()

    class EraseFreeSpaceThread(QThread):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.parent = parent
        def run(self):
            self.parent.erase_free_space()

    def erase_files(self):
        if (self.listview_1_model.rowCount() > 0):
            self.disable_ui()
            self.logger.write(f"-------------------------------------------------------------------------------------")
            self.logger.write("SecureFileErase process has been started...", status=0)
            self.logger.write("Please don't close this window.", status=2)
            self.logger.write(f"-------------------------------------------------------------------------------------")
            # Read user inputs
            self.steps = int(self.cmb_1_steps.currentText())
            match self.cmb_1_speed.currentText():
                case "High":self.buffersize = 1024*1024*10
                case "Medium":self.buffersize = 1024*1024*5
                case "Low":self.buffersize = 1024*1024
            if self.rbtn_1_random.isChecked():self.method = "_"
            elif self.rbtn_1_0s.isChecked():self.method = "0"
            elif self.rbtn_1_1s.isChecked():self.method = "1"

            for row in range(self.listview_1_model.rowCount()):
                self.f_erase_file(self.listview_1_model.item(row).text())

            self.enable_ui()
            self.logger.write(f"-------------------------------------------------------------------------------------")
            self.logger.write("SecureFileErase process is finished.", status=0)
        else:
            self.logger.write("Please add file(s) to the queue.", status=1)

    def f_erase_file(self, filename):
        self.logger.write(f"-------------------------------------------------------------------------------------")
        try:
            # Get the size of the file
            file_size = os.path.getsize(filename)
            for i in range(self.steps):
                self.logger.write(f"Overwriting {filename} | Pass [{i+1}] of [{self.steps}].")
                percentge = 0
                # Open the file in write mode
                with open(filename, 'rb+') as file:
                    file.seek(0)
                    for i in range(file_size//self.buffersize):
                        sys.stdout.write('\r' + "[" + int(percentge//10)*"*" + int(10 - percentge//10)*" " + f"]  {(percentge//10)*10} %")
                        sys.stdout.flush()
                        match self.method:
                            case "0": file.write(b'\x00' * self.buffersize)
                            case "1": file.write(b'\x01' * self.buffersize)
                            case "_": file.write(os.urandom(self.buffersize))
                        percentge = (i/(file_size//self.buffersize)) * 100
                    match self.method:
                        case "0": file.write(b'\x00' * (file_size%self.buffersize))
                        case "1": file.write(b'\x01' * (file_size%self.buffersize))
                        case "_": file.write(os.urandom(file_size%self.buffersize))
                    sys.stdout.write('\r' + "[**********]  100 % \n")
            # Generate a random file name
            random_name = ''.join(random.choices(string.ascii_letters + string.digits, k=15))
            directory = os.path.dirname(filename)
            new_path = os.path.join(directory, random_name)
            os.rename(filename, new_path)
            # Change file times
            current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
            # Convert times to epoch (Unix timestamp)
            atime = time.mktime(time.strptime(current_time, '%Y-%m-%d %H:%M:%S'))
            mtime = time.mktime(time.strptime(current_time, '%Y-%m-%d %H:%M:%S'))
            # Change the access and modification times
            os.utime(new_path, (atime, mtime))
            # Change creation date (Windows only)
            if os.name == 'nt':
                # Convert to Windows file time
                wintime = pywintypes.Time(time.mktime(time.strptime(current_time, '%Y-%m-%d %H:%M:%S')))
                # Open file
                handle = win32file.CreateFile(new_path, win32con.GENERIC_WRITE, win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE, None, win32con.OPEN_EXISTING, win32con.FILE_ATTRIBUTE_NORMAL, None)
                # Set creation time
                win32file.SetFileTime(handle, wintime, None, None)
                handle.close()
            # Delete the file
            os.remove(new_path)
            self.logger.write(f"File '{os.path.basename(filename)}' has been securely overwritten and deleted.")

        except FileNotFoundError:
            self.logger.write(f"The file {os.path.basename(filename)} does not exist.", status=2)
            return
        except PermissionError:
            self.logger.write(f"Permission denied: unable to write {os.path.basename(filename)}.", status=2)
            return
        except Exception as e:
            print(e)
            return

    def get_free_space(self, directory):
        """
        Get the free space of the given directory.
        Works on both Unix-like systems and Windows.
        """
        if platform.system() == 'Windows':
            import ctypes
            _, total, free = ctypes.c_ulonglong(), ctypes.c_ulonglong(), ctypes.c_ulonglong()
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(directory), ctypes.byref(_), ctypes.byref(total), ctypes.byref(free))
            return free.value
        else:
            statvfs = os.statvfs(directory)
            return statvfs.f_bavail * statvfs.f_frsize
        
    def erase_free_space(self):
        selected_indexes = self.listView_2.selectedIndexes()
        if selected_indexes:
            for index in selected_indexes:
                selected_drive = self.listview_2_model.item(index.row()).text()
                directory = selected_drive + ":\\"
                # Calculate free space
                free_space = self.get_free_space(directory)

                self.disable_ui()
                self.logger.write(f"-------------------------------------------------------------------------------------")
                self.logger.write("SecureErase-FreeSpace process has been started...", status=0)
                self.logger.write("Please don't close this window.", status=2)
                self.logger.write(f"Selected Drive is [{selected_drive}]", status=2)
                self.logger.write(f"Detected free space is [{free_space // (1024*1024)} MB]", status=2)
                self.logger.write(f"-------------------------------------------------------------------------------------")
                # Read user inputs
                self.steps = int(self.cmb_2_steps.currentText())
                match self.cmb_2_speed.currentText():
                    case "High":self.buffersize = 1024*1024*10
                    case "Medium":self.buffersize = 1024*1024*5
                    case "Low":self.buffersize = 1024*1024
                if self.rbtn_2_random.isChecked():self.method = "_"
                elif self.rbtn_2_0s.isChecked():self.method = "0"
                elif self.rbtn_2_1s.isChecked():self.method = "1"

                try:
                    max_file_size = 1024*1024*1024*2
                    # Create multiple files to overwrite the free space
                    for pass_num in range(self.steps):
                        file_index = 0
                        self.logger.write(f"Writing data to Drive ({directory}) | Pass [{pass_num+1}] of [{self.steps}].")
                        percentge = 0
                        remaining_space = free_space
                        while remaining_space > 0:
                            current_file_size = min(remaining_space, max_file_size)
                            try:
                                with open(os.path.join(directory, f'00000tempfile_{file_index}.bin'), 'wb+') as file:
                                    file.seek(0)
                                    for i in range(current_file_size // self.buffersize):
                                        sys.stdout.write('\r' + "[" + int(percentge // 10) * "*" + int(10 - percentge // 10) * " " + f"]  {(percentge // 10) * 10} % of 2 GB")
                                        sys.stdout.flush()
                                        match self.method:
                                            case "0": file.write(b'\x00' * self.buffersize)
                                            case "1": file.write(b'\x01' * self.buffersize)
                                            case "_": file.write(os.urandom(self.buffersize))
                                        percentge = (i / (current_file_size // self.buffersize)) * 100
                                    match self.method:
                                        case "0": file.write(b'\x00' * (current_file_size % self.buffersize))
                                        case "1": file.write(b'\x01' * (current_file_size % self.buffersize))
                                        case "_": file.write(os.urandom(current_file_size % self.buffersize))
                                    sys.stdout.write('\r' + "[**********]  100 % \n")
                            except OSError as e:
                                self.logger.write(f"Failed to write to {directory}. Reason: {e}", status=2)
                                break
                            file_index += 1
                            remaining_space -= current_file_size

                        # Delete the temporary files
                        for file in range(file_index):
                            try:
                                os.remove(os.path.join(directory, f'00000tempfile_{file}.bin'))
                            except OSError as e:
                                self.logger.write(f"Failed to delete temporary file {file}. Reason: {e}", status=2)

                except FileNotFoundError:
                    self.logger.write(f"The path {directory} does not exist.", status=2)
                except PermissionError:
                    self.logger.write(f"Permission denied: unable to write {directory}.", status=2)
                except Exception as e:
                    print(e)
             
                self.enable_ui()
                self.logger.write(f"-------------------------------------------------------------------------------------")
                self.logger.write("SecureErase-FreeSpace process is finished.", status=0)
        else:
            self.logger.write("No Drives detected.", status=1)

    def disable_ui(self):
        self.main_tabs.setEnabled(False)
        self.aniblock.setVisible(True)

    def enable_ui(self):
        self.main_tabs.setEnabled(True)
        self.aniblock.setVisible(False)

    def update_available_drives(self):
        self.listview_2_model = QStandardItemModel()
        self.listView_2.setModel(self.listview_2_model)
        drives = get_drives()
        self.logger.write("Drives list updated.")
        if drives:
            for i in drives:
                item = QStandardItem(i)
                self.listview_2_model.appendRow(item)
        self.fix_ui()
        
    def fix_ui(self):
        style = """ QWidget {color: rgb(200, 200, 200);border: 1px solid rgb(80, 80, 80);border-radius: 6px;background-color: rgb(30, 30, 30);}
                    QScrollBar {border: 1px solid #252525;background: #191919;border-radius: 5px;}
                    QScrollBar:horizontal {height: 15px;margin: 0px 0px 0px 32px;}
                    QScrollBar:vertical {width: 15px;margin: 32px 0px 0px 0px;}
                    QScrollBar::handle {background: #252525;border: 1px solid #252525;border-radius: 4px;}
                    QScrollBar::handle:horizontal {border-width: 0px 1px 0px 1px;}
                    QScrollBar::handle:vertical {border-width: 1px 0px 1px 0px;}
                    QScrollBar::handle:horizontal {min-width: 20px;}
                    QScrollBar::handle:vertical {min-height: 20px;}
                    QScrollBar::add-line, QScrollBar::sub-line {background:#252525;border: 1px solid #252525;subcontrol-origin: margin;border-radius: 4px;}
                    QScrollBar::add-line {position: absolute;}
                    QScrollBar::add-line:horizontal {width: 15px;subcontrol-position: left;left: 15px;}
                    QScrollBar::add-line:vertical {height: 15px;subcontrol-position: top;top: 15px;}
                    QScrollBar::sub-line:horizontal {width: 15px;subcontrol-position: top left;}
                    QScrollBar::sub-line:vertical {height: 15px;subcontrol-position: top;}
                    QScrollBar:left-arrow, QScrollBar::right-arrow, QScrollBar::up-arrow, QScrollBar::down-arrow {border: 1px solid #5A5A5A;width: 3px;height: 3px;}
                    QScrollBar::add-page, QScrollBar::sub-page {background: none;}"""
        self.listView_1.setStyleSheet(style)
        self.listView_2.setStyleSheet(style)

    def A_add_items(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Select file(s)", "", "All Files (*)", options=options)
        if files:
            for i in files:
                item = QStandardItem(i)
                self.listview_1_model.appendRow(item)

            seen = set()
            duplicates = []
            for row in range(self.listview_1_model.rowCount()):
                item = self.listview_1_model.item(row)
                if item.text() in seen:
                    duplicates.append(row)
                else:
                    seen.add(item.text())
            for row in reversed(duplicates):
                self.listview_1_model.removeRow(row)
            self.logger.write("Added " + str(len(files) - len(duplicates)) + " file(s) to the queue.")
            self.fix_ui()

    def A_delete_item(self):
        selected_indexes = self.listView_1.selectedIndexes()
        if selected_indexes:
            for index in selected_indexes:
                self.listview_1_model.removeRow(index.row())
        self.fix_ui()
        
    def A_clear_items(self):
        self.listview_1_model.clear()
        self.logger.write("The queue has been cleared.")
        self.fix_ui()

    def f_btn_about(self):
        dialog = sys_AboutDialog()
        dialog.exec()

class Logger():
    def __init__(self, placeholder):
        self.placeholder = placeholder
    
    def write(self, data, status=0):
        print(data)
        #match status:
        #    case 0:
        #        html = '<p style="color: green;">' + datetime.today().strftime('%Y-%m-%d %H:%M:%S') + " : " + data + '</p>'
        #    case 1:
        #        html = '<p style="color: yellow;">' + datetime.today().strftime('%Y-%m-%d %H:%M:%S') + " : " + data + '</p>'
        #    case 2:
        #        html = '<p style="color: red;">' + datetime.today().strftime('%Y-%m-%d %H:%M:%S') + " : " + data + '</p>'

        # Insert the HTML into the QTextEdit
        #self.placeholder.insertHtml(html)
        # Optionally, add a line break after the red line
        #self.placeholder.insertHtml('<br>')
        #self.placeholder.moveCursor(QTextCursor.End)

class sys_AboutDialog(QDialog):   
    def __init__(self, parent=None):
        super(sys_AboutDialog, self).__init__(parent)
        # Display the about window
        self = uic.loadUi(resource_path('data/dlg_about.ui'), self)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle("About")
        self.setWindowIcon(QIcon(resource_path("./data/icon.png")))
        self.dummy_3.setText(''.join(chr(ord(char) - 1) for char in "Efwfmpqfe!cz;!Nbmblb!E/Hvobxbsebob/"))
        self.lbl_name_and_version.setText("Name : SecureErase\nVersion : " + App_version)
        pixmap = QPixmap(resource_path("./data/icon.png"))
        pixmap = pixmap.scaledToWidth(200, Qt.SmoothTransformation)
        self.icon.setPixmap(pixmap)
        self.btn_ok.clicked.connect(self.accept)
        self.btn_ok.setDefault(True)
        self.show()

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def get_drives():
    system = platform.system()
    
    if system == "Windows":
        # On Windows, check each letter from A to Z and see if it's a valid drive
        drives = []
        bitmask = os.popen("wmic logicaldisk get caption").read().split()
        for drive in bitmask:
            if len(drive) == 2 and drive[1] == ':':
                drives.append(drive[:-1])
        return drives
    

# Main

if __name__ == '__main__':
    app = QApplication(sys.argv)
    working_directory = os.getcwd()
    # INFO
    App_version = "0.1.1"
    main_window = SecureErase()
    
    sys.exit(app.exec_())