"""Common Dialogs needed in several programs
Programmed with Love by: F.Garcia
Creation Date: 05.12.2022
"""

import os
import sys
import re
import subprocess

# from PyQt5 import QtCore
from PyQt5.QtWidgets import QFileDialog, QWidget, QMessageBox, QInputDialog
from PyQt5.QtWidgets import QDialog, QStackedWidget, QListView, QLineEdit


def get_file_manager_path():
    """Get filemanager path

    Raises:
        OSError: not supported
    Returns:
        str: path of file manager in windows, linux, macos
    """
    if os.name == "nt":  # Windows
        return os.path.join(os.getenv("WINDIR"), "explorer.exe")  # "/c/Windows/Shell/explorer.exe"
    if os.name in ["posix", "linux"]:  # Linux/MacOS
        return "/usr/bin/xdg-open"
    raise OSError(f"Unsupported OS: {os.name}")


FILEBROWSER_PATH = get_file_manager_path()


class Dialogs(QWidget):
    """
    Utils for opening flies, saving files and messageboxes used commonly in GUI
    Args:
        QWidget (_type_): _description_
    """

    def __init__(self):
        super().__init__()
        self.options = QFileDialog.Options()
        self.options |= QFileDialog.DontUseNativeDialog
        self.dir = ""
        self.filters = ""
        self._regex_pattern = ""
        self.selected_filter = ""
        self.filter_dict = {
            "0": {
                "filter": "All Files (*);;Gcode Files (*.gcode);;Linux Gcode Files (*.ngc)",
                "selected_filter": "Gcode Files (*.gcode)",
            },
            "1": {
                "filter": "All Files (*);;Images (*.png *.xpm *.jpg *.bmp)",
                "selected_filter": "Images (*.png *.xpm *.jpg *.bmp)",
            },
            "2": {"filter": "All Files (*);;Text Files (*.txt)", "selected_filter": "Text Files (*.txt)"},
            "3": {
                "filter": "All Files (*);;Configuration Files (*.cccfg *.iccfg *.rccfg);;\
                Interface Files (*.iccfg);;Read Files (*.rccfg);;Command Files (*.cccfg)",
                "selected_filter": "Configuration Files (*.cccfg *.iccfg *.rccfg)",
            },
            "4": {
                "filter": "All Files (*);;Gcode Files (*.gcode);;Linux Gcode Files (*.ngc);;Action Files (*.acode)",
                "selected_filter": "Gcode Files (*.gcode)",
            },
            "5": {
                "filter": "All Files (*);;Batton Configuration Files (*.btncfg)",
                "selected_filter": "Batton Configuration Files (*.btncfg)",
            },
            "6": {"filter": "All Files (*);;CSV Files (*.csv)", "selected_filter": "CSV Files (*.csv)"},
            "7": {"filter": "All Files (*);;yml Files (*.yml)", "selected_filter": "yml Files (*.yml)"},
            "8": {"filter": "All Files (*);;json Files (*.json)", "selected_filter": "json Files (*.json)"},
            "all": {"filter": "All Files (*)", "selected_filter": "All Files (*)"},
        }
        # set default filter "all"
        self.get_filter("all")

    def _check_selected_filter(self, filter_string: str, selected_filter: str) -> bool:
        """Check for selected filter in the filters list

        Args:
            filter_string (str): filter
            selected_filter (str): filterlist
        Returns:
            bool: if selected filter is ok
        """
        if not self._check_filter_string(filter_string):
            return False
        # Split the filter string into individual filters
        filters = filter_string.split(";;")
        # Remove the "All Files (*);" part if it exists
        # if filters[0] == "All Files (*)":
        #    filters = filters[1:]
        # Check if the selected filter is in the list of filters
        for afilter in filters:
            if afilter.strip() == selected_filter.strip():
                return True
        return False

    def _check_filter_string(self, filter_string: str) -> bool:
        """checks if filter string is correctly formatted

        Args:
            filter_string (str): _description_

        Returns:
            bool: If filter string is formatted correctly
        """
        pattern1 = r"^(All Files \(\*\);;)?(?:[\w]+ Files \(\*\.(?:[\w]+(?: \*.[\w]+)*)\))"
        pattern2 = r"(?:;;(?:[\w]+ Files \(\*\.(?:[\w]+(?: \*.[\w]+)*)\)))*$"
        pattern = pattern1 + pattern2
        self._regex_pattern = pattern
        if re.match(pattern, filter_string):
            return True
        return False

    def explore(self, path: str):
        """Open windows explorer on path

        Args:
            path (str): path to open
        """
        if os.path.exists(path):
            # explorer would choke on forward slashes
            path = os.path.normpath(path)
            try:
                if os.path.isdir(path):
                    subprocess.run([FILEBROWSER_PATH, path], check=True)
                elif os.path.isfile(path):
                    subprocess.run([FILEBROWSER_PATH, "/select,", path], check=True)
            except (subprocess.CalledProcessError, subprocess.SubprocessError):
                pass

    def set_default_dir(self, adir: str):
        """Sets the dialogs default directory when opened

        Args:
            dir (str): path to directory
        """
        if os.path.exists(adir):
            self.dir = adir
        else:
            print("Directory does not exist")
            self.dir = self.get_app_path()

    def set_filter(self, filtername: str, afilter: str, selectedfilter: str, prompt_msgbox: bool = False) -> bool:
        """Sets a filter for file dialogs

        Args:
            filtername (str): name key for filter
            filter (str): filter text
            selectedfilter (str): selected filter
            prompt_msgbox (bool): Prompt with messagebox when error found. Defaults to False.

        Returns:
            bool: True if filter was set
        """
        passed = True
        if not self._check_filter_string(afilter):
            msg = "Make sure the filter looks like:\n All Files (*);;json Files (*.json) \nMust comply to pattern:\n"
            msg = msg + self._regex_pattern
            if prompt_msgbox:
                self.send_critical_msgbox("Wrong Filter Pattern", msg)
            passed = False

        if self._check_selected_filter(afilter, selectedfilter) and passed:
            self.filter_dict.update({filtername: {"filter": afilter, "selected_filter": selectedfilter}})
        elif not self._check_selected_filter(afilter, selectedfilter) and passed:
            msg = """Selected Pattern must be exactly the same as one of the filters"""
            if prompt_msgbox:
                self.send_critical_msgbox("Wrong Selected Filter Pattern", msg)
            passed = False
        return passed

    def get_filter(self, afilter):
        """Sets filter and selected_filter to the desired filter in filter_dict.

        Args:
            filter (any): the key name in the filter_dict
        """
        if str(afilter) in self.filter_dict:
            f_dict = self.filter_dict[str(afilter)]
            self.filters = f_dict["filter"]
            self.selected_filter = f_dict["selected_filter"]
        else:
            f_dict = self.filter_dict["all"]
            self.filters = f_dict["filter"]
            self.selected_filter = f_dict["selected_filter"]

    def open_file_dialog(self, afilter: str = "all") -> str:
        """Open one file dialog

        Args:
            filter (str, optional): filter to be selected. Defaults to "all".
            predifined filters:
            0->Gcode Files (*.gcode *.ncg)
            1->Images (*.png *.xpm *.jpg *.bmp)
            2->Text Files (*.txt)
            3->Configuration Files (*.cccfg *.iccfg *.rccfg)
            4->Gcode and Action Files (*.gcode *.ncg *.acode)
            5->Batton Configuration Files (*.btncfg)
            6->CSV Files (*.csv)
            7->yml Files (*.yml)
            8->json Files (*.json)
            all-> all Files

        Returns:
            str: File name. None when canceled
        """

        self.get_filter(afilter)
        try:
            file_obj = QFileDialog.getOpenFileName(
                self, "Open File dialog ", self.dir, self.filters, self.selected_filter, options=self.options
            )
            file_name, _ = file_obj
        except (FileExistsError, PermissionError, FileNotFoundError, IsADirectoryError, NotImplementedError):
            return None
        if file_name:
            return file_name
        return None

    def open_files_dialog(self, afilter: str = "all") -> list[str]:
        """Open several files dialog

        Args:
            filter (str, optional): filter to be selected. Defaults to "all".
            predifined filters:
            0->Gcode Files (*.gcode *.ncg)
            1->Images (*.png *.xpm *.jpg *.bmp)
            2->Text Files (*.txt)
            3->Configuration Files (*.cccfg *.iccfg *.rccfg)
            4->Gcode and Action Files (*.gcode *.ncg *.acode)
            5->Batton Configuration Files (*.btncfg)
            6->CSV Files (*.csv)
            7->yml Files (*.yml)
            8->json Files (*.json)
            all-> all Files

        Returns:
            list[str]: List of File names. None when canceled
        """
        try:
            self.get_filter(afilter)
            files, _ = QFileDialog.getOpenFileNames(
                self, "Open File Names Dialog", self.dir, self.filters, self.selected_filter, options=self.options
            )
        except (FileExistsError, PermissionError, FileNotFoundError, IsADirectoryError, NotImplementedError):
            return None
        if files:
            return files
        return None

    def save_file_dialog(self, afilter: str = "all") -> str:
        """Save file dialog

        Args:
            filter (str, optional): filter to be selected. Defaults to "all".
            predifined filters:
            0->Gcode Files (*.gcode *.ncg)
            1->Images (*.png *.xpm *.jpg *.bmp)
            2->Text Files (*.txt)
            3->Configuration Files (*.cccfg *.iccfg *.rccfg)
            4->Gcode and Action Files (*.gcode *.ncg *.acode)
            5->Batton Configuration Files (*.btncfg)
            6->CSV Files (*.csv)
            7->yml Files (*.yml)
            8->json Files (*.json)
            all-> all Files

        Returns:
            str: File name. None when canceled
        """
        try:
            self.get_filter(afilter)
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Save File dialog ", self.dir, self.filters, self.selected_filter, options=self.options
            )
        except (FileExistsError, PermissionError, FileNotFoundError, IsADirectoryError, NotImplementedError):
            return None
        if file_name:
            return file_name
        return None

    def extract_filename(self, filename: str, with_extension: bool = True) -> str:
        """Extracts filename of a path+filename string

        Args:
            filename (str): path+filename
            with_extension (bool, optional): return filename including the extension. Defaults to True.

        Returns:
            str: string with filename
        """
        fn = os.path.basename(filename)  # returns just the name
        fnnoext, fext = os.path.splitext(fn)
        fnnoext = fnnoext.replace(fext, "")
        fn = fnnoext + fext
        if with_extension:
            return fn
        return fnnoext

    def extract_path(self, filename: str, with_separator: bool = True) -> str:
        """Extracts path of a path+filename string

        Args:
            filename (str): path+filename
            with_separator (bool, optional): return path including the separator. Defaults to True.

        Returns:
            str: string with path
        """
        fn = os.path.basename(filename)  # returns just the name
        fpath = os.path.abspath(filename)
        if with_separator:
            fpath = fpath.replace(fn, "")
        else:
            fpath = fpath.replace(os.sep + fn, "")
        return fpath

    def get_app_path(self) -> str:
        """Gets Appliction path

        Returns:
            str: Application path
        """
        # determine if application is a script file or frozen exe
        application_path = ""
        if getattr(sys, "frozen", False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)
        return application_path

    def open_directory_dialog(self, parent=None, caption="", directory="", afilter="", initial_filter="", options=None):
        """Open Directory selection

        Args:
            parent (_type_, optional): parent. Defaults to None.
            caption (str, optional): Title of Dialog. Defaults to ''.
            directory (str, optional): initial path for opening. Defaults to ''.
            filter (str, optional): filters. Defaults to ''.
            initial_filter (str, optional): selected filter. Defaults to ''.
            options (dict, optional): Options dict. Defaults to None.

            Returns:
            str: Directory path name. None when canceled
        """

        def update_text():
            # update the contents of the line edit widget with the selected files
            selected = []
            for index in view.selectionModel().selectedRows():
                selected.append(f'"{index.data()}"')
            line_edit.setText(" ".join(selected))

        dialog = QFileDialog(parent, windowTitle=caption)
        dialog.setFileMode(dialog.ExistingFiles)
        if options:
            dialog.setOptions(options)
        dialog.setOption(dialog.DontUseNativeDialog, True)
        if directory:
            dialog.setDirectory(directory)
        if afilter:
            dialog.setNameFilter(afilter)
            if initial_filter:
                dialog.selectNameFilter(initial_filter)

        # by default, if a directory is opened in file listing mode,
        # QFileDialog.accept() shows the contents of that directory, but we
        # need to be able to "open" directories as we can do with files, so we
        # just override accept() with the default QDialog implementation which
        # will just return exec_()
        dialog.accept = lambda: QDialog.accept(dialog)

        # there are many item views in a non-native dialog, but the ones displaying
        # the actual contents are created inside a QStackedWidget; they are a
        # QTreeView and a QListView, and the tree is only used when the
        # viewMode is set to QFileDialog.Details, which is not this case
        stacked_widget = dialog.findChild(QStackedWidget)
        view = stacked_widget.findChild(QListView)
        view.selectionModel().selectionChanged.connect(update_text)

        line_edit = dialog.findChild(QLineEdit)
        # clear the line edit contents whenever the current directory changes
        dialog.directoryEntered.connect(lambda: line_edit.setText(""))

        result = dialog.exec_()  # 1 when accepted 0 when rejected/cancelled/closed
        # print(result)
        if result == 1:
            return dialog.selectedFiles()
        return []

    def send_question_yes_no_msgbox(self, title: str, amsg: str) -> bool:
        """Makes yes/no messagebox

        Args:
            title (str): Title
            amsg (str): Message content

        Returns:
            bool: True if Yes, False if No, None if Cancelled/closed
        """
        msgbox = QMessageBox()
        result = QMessageBox.question(msgbox, title, amsg, QMessageBox.Yes | QMessageBox.No)
        if result == QMessageBox.Yes:
            return True
        if result == QMessageBox.No:
            return False
        return None

    def send_critical_msgbox(self, title: str, amsg: str):
        """
        Makes critical messagebox
        Args:
            title (str): Title
            amsg (str): Message content
        """
        msgbox = QMessageBox()
        msgbox.setWindowTitle(title)
        msgbox.setIcon(QMessageBox.Critical)
        msgbox.setText(amsg)
        msgbox.exec_()

    def send_informative_msgbox(self, title: str, amsg: str):
        """
        Makes informative messagebox
        Args:
            title (str): Title
            amsg (str): Message content
        """
        msgbox = QMessageBox()
        msgbox.setWindowTitle(title)
        msgbox.setIcon(QMessageBox.Information)
        msgbox.setText(amsg)
        msgbox.exec_()

    def get_text_dialog(self, title: str, amsg: str) -> str:
        """Makes text input Dialog

        Args:
            title (str): dialog title
            amsg (str): dialog message

        Returns:
            str: input text
        """
        text = QInputDialog.getText(self, title, amsg)
        if text[1]:
            return str(text[0])
        return None

    def get_int_dialog(self, title: str, amsg: str):
        """Makes int input dialog

        Args:
            title (str): dialog title
            amsg (str): dialog message

        Returns:
            int: input value
        """
        num = QInputDialog.getInt(self, title, amsg)
        if num[1]:
            return num[0]
        return None

    def get_item_selection(self, items: list[str], title: str, amsg: str) -> str:
        """Selection input dialog

        Args:
            items (list[str]): item list for selecting
            title (str): dialog title
            amsg (str): dialog message

        Returns:
            str: selection
        """
        if len(items) == 0:
            return None
        selection = QInputDialog.getItem(self, title, amsg, items, current=0, editable=False)

        if selection[1]:
            return str(selection[0])
        return None
