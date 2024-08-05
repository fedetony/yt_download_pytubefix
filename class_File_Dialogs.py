from PyQt5.QtWidgets import *
import os
import sys

class Dialogs(QWidget):
    def __init__(self):
        super().__init__()
        self.options = QFileDialog.Options()
        self.options |= QFileDialog.DontUseNativeDialog
        self.dir=""

    def set_default_dir(self,dir):
        self.dir=dir

    def get_filter(self,filter):
        if filter==0:
            self.filters="All Files (*);;Gcode Files (*.gcode);;Linux Gcode Files (*.ngc)"
            self.selected_filter = "Gcode Files (*.gcode)"
        elif filter==1:
            self.filters="All Files (*);;Images (*.png *.xpm *.jpg *.bmp)"
            self.selected_filter = "Images (*.png *.xpm *.jpg *.bmp)"
        elif filter==2:
            self.filters="All Files (*);;Text Files (*.txt)"
            self.selected_filter = "Text Files (*.txt)"
        elif filter==3:
            self.filters="All Files (*);;Configuration Files (*.cccfg *.iccfg *.rccfg);;Interface Files (*.iccfg);;Read Files (*.rccfg);;Command Files (*.cccfg)"
            self.selected_filter = "Configuration Files (*.cccfg *.iccfg *.rccfg)" 
        elif filter==4:
            self.filters="All Files (*);;Gcode Files (*.gcode);;Linux Gcode Files (*.ngc);;Action Files (*.acode)"
            self.selected_filter = "Gcode Files (*.gcode)"   
        elif filter==5:
            self.filters="All Files (*);;Batton Configuration Files (*.btncfg)"
            self.selected_filter = "Batton Configuration Files (*.btncfg)"
        elif filter==6:
            self.filters="All Files (*);;CSV Files (*.csv)"
            self.selected_filter = "CSV Files (*.csv)"
        elif filter==7:
            self.filters="All Files (*);;yml Files (*.yml)"
            self.selected_filter = "yml Files (*.yml)"
        elif filter==8:
            self.filters="All Files (*);;json Files (*.json)"
            self.selected_filter = "json Files (*.json)"
        else:
            self.filters="All Files (*)"
            self.selected_filter = "All Files (*)"    

    def openFileNameDialog(self,filter=0):
        '''
        filters:
        0->Gcode Files (*.gcode *.ncg)
        1->Images (*.png *.xpm *.jpg *.bmp)
        2->Text Files (*.txt)
        3->Configuration Files (*.cccfg *.iccfg *.rccfg)
        4->Gcode and Action Files (*.gcode *.ncg *.acode) 
        5->Batton Configuration files (*.btncfg)
        6->CSV Files (*.csv)
        7->yml Files (*.yml)
        8->json Files (*.json)
        else all Files
        '''        
        #dir = self.sourceDir
        self.get_filter(filter)        
        try:
            fileObj = QFileDialog.getOpenFileName(self, "Open File dialog ", self.dir, self.filters, self.selected_filter, options=self.options)
            fileName, _ = fileObj
        except:
            return None
        if fileName:
            return fileName
        else:
            return None    
    
    def openFileNamesDialog(self,filter=0):
        '''
        filters:
        0->Gcode Files (*.gcode *.ncg)
        1->Images (*.png *.xpm *.jpg *.bmp)
        2->Text Files (*.txt)
        3->Configuration Files (*.cccfg *.iccfg *.rccfg)
        4->Gcode and Action Files (*.gcode *.ncg *.acode) 
        5->Batton Configuration files (*.btncfg)
        6->CSV Files (*.csv)
        7->yml Files (*.yml)
        8->json Files (*.json)
        else all Files
        '''
        try:
            self.get_filter(filter) 
            files, _ = QFileDialog.getOpenFileNames(self, "Open File Names Dialog", self.dir, self.filters, self.selected_filter, options=self.options)
        except:
            return None
        if files:
            return files
        else:
            return None    
    
    def saveFileDialog(self,filter=0): 
        '''
        filters:
        0->Gcode Files (*.gcode *.ncg)
        1->Images (*.png *.xpm *.jpg *.bmp)
        2->Text Files (*.txt)
        3->Configuration Files (*.cccfg *.iccfg *.rccfg)
        4->Gcode and Action Files (*.gcode *.ncg *.acode) 
        5->Batton Configuration files (*.btncfg)
        6->CSV Files (*.csv)
        7->yml Files (*.yml)
        8->json Files (*.json)
        else all Files
        '''    
        try:
            self.get_filter(filter)         
            fileName, _ = QFileDialog.getSaveFileName(self, "Save File dialog ", self.dir, self.filters, self.selected_filter, options=self.options)
        except:
            return None
        if fileName:
            return fileName
        else:
            return None

    def extract_filename(self,filename,withextension=True):
        fn= os.path.basename(filename)  # returns just the name
        fnnoext, fext = os.path.splitext(fn)
        fnnoext=fnnoext.replace(fext,'')
        fn=fnnoext+fext        
        if withextension==True:
            return fn
        else:                
            return  fnnoext 

    def extract_path(self,filename,wsep=True):
        fn= os.path.basename(filename)  # returns just the name
        fpath = os.path.abspath(filename)
        if wsep==True:
            fpath = fpath.replace(fn,'')
        else:
            fpath = fpath.replace(os.sep+fn,'')
        return fpath
    
    def get_appPath(self):
        # determine if application is a script file or frozen exe
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)
        return application_path
    
    def getOpenFilesAndDirs(parent=None, caption='', directory='', 
                        filter='', initialFilter='', options=None):
        def updateText():
            # update the contents of the line edit widget with the selected files
            selected = []
            for index in view.selectionModel().selectedRows():
                selected.append('"{}"'.format(index.data()))
            lineEdit.setText(' '.join(selected))

        dialog = QFileDialog(parent, windowTitle=caption)
        dialog.setFileMode(dialog.ExistingFiles)
        if options:
            dialog.setOptions(options)
        dialog.setOption(dialog.DontUseNativeDialog, True)
        if directory:
            dialog.setDirectory(directory)
        if filter:
            dialog.setNameFilter(filter)
            if initialFilter:
                dialog.selectNameFilter(initialFilter)

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
        stackedWidget = dialog.findChild(QStackedWidget)
        view = stackedWidget.findChild(QListView)
        view.selectionModel().selectionChanged.connect(updateText)

        lineEdit = dialog.findChild(QLineEdit)
        # clear the line edit contents whenever the current directory changes
        dialog.directoryEntered.connect(lambda: lineEdit.setText(''))

        dialog.exec_()
        return dialog.selectedFiles()
