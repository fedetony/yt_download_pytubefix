# -*- coding: utf-8 -*-
#*********************************
# Author :F. Garcia
# Created 19.08.2022
#*********************************
__author__="FG"
__version__="1.0.0 Beta"
__creationdate__="04.08.2024"
__gitaccount__="<a href=\"https://github.com/fedetony\">' Github for fedetony'</a>"

# Form implementation generated automaticaly from reading ui file 'yt_pytubefix_gui.ui'
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to 'yt_pytubefix_gui.py' will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

from genericpath import isfile
from operator import index
import sys
import os
import logging
import yaml

from PyQt5 import QtCore, QtGui, QtWidgets
import class_File_Dialogs
import class_tableWidgetFunctions
import yt_pytubefix_gui
import requests

#import datetime
#import json
#import re

#Setup Logger
# set up logging to file - see previous section for more details
log = logging.getLogger('') #root logger
#For file
'''
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s [%(levelname)s] (%(threadName)-10s) %(message)s',
                    datefmt='%y-%m-%d %H:%M',
                    filename='/temp/__last_run__.log',
                    filemode='w')
'''
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s [%(levelname)s] (%(threadName)-10s) %(message)s',
                    datefmt='%y-%m-%d %H:%M')
# define a Handler which writes INFO messages or higher to the sys.stderr
#console = logging.StreamHandler()
console = logging.StreamHandler(sys.stdout)
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('[%(levelname)s] (%(threadName)-10s) %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)


class Ui_MainWindow_yt(yt_pytubefix_gui.Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(Ui_MainWindow_yt, self).__init__(*args, **kwargs) 

    def start_up(self):        
        log.info("UI started!")
        #Initial conditions variables
        self.app_path=self.get_appPath()   
        self.General_Config=self.get_general_config() 
        try:
            self.download_path = self.General_Config["Last_Path_for_Download"]
            if not os.path.exists(self.download_path):
                self.download_path = self.app_path
        except:
            self.download_path = self.app_path
        self.url_struct = {}
        self.url_id_counter = 0
 
    def setupUi2(self, MainWindow):   
        # Add objects by code here additional to objects in GUI_PostProcessing
        # Or set configuration of objects  
        #initial conditions
        self.start_up()
        #------------- Mainwindow
        # set the icon           
        path_to_file=self.app_path+os.sep+"img"+os.sep+"main_icon.png"
        file_exists = os.path.exists(path_to_file)
        self.iconMainpixmap=None
        self.iconMain=None        
        if file_exists==True:
            self.iconMainpixmap=QtGui.QPixmap(path_to_file)
            self.iconMain = QtGui.QIcon(QtGui.QPixmap(path_to_file))
            MainWindow.setWindowIcon(self.iconMain)   
            
        # set the title
        MainWindow.setWindowTitle("Gui for pytubefix by "+ __author__+" V"+__version__)
        #MainWindow.showMaximized()      

        #-----------tableWidget_functions 
        
        self.twf=class_tableWidgetFunctions.tableWidget_functions(self.tableWidget_url,self.url_struct,{},None,[])               
        #self.model=self.twf.modelobj
        #self.twf.data_change[list,str,str,str].connect(self.refresh_dialog_treeview)
        #self.icons_dict={'Plots':self.iconMain} 
        
        #self.tvf.Expand_to_Depth(1)      
        #self.tvf.set_Icons(self.icons_dict)    
        #-----------Splitter 
        #self.set_splitter_pos(400,1/3) #initial position
        #--------------
        self.set_path_labels()
        aDialog.set_default_dir(self.app_path)
        self.Connect_Actions()
        
    def get_general_config(self):
        """
        Returns the configuration set in yml file 
        """
        self.default_config_path=self.app_path+os.sep+'config'+os.sep+'cfg.yml'        
        return self.open_configuration_yml_file(self.default_config_path)  
    
    def open_configuration_yml_file(self,path_config_file):   
        """
        Opens configuration file in yml format 
        """     
        path_config=''
        try:
            with open(path_config_file) as file:
                path_config = yaml.load(file, Loader=yaml.SafeLoader)
                log.info("Environment configuration loaded") 
                self.path_config_file=path_config_file       
        except FileNotFoundError:
            log.error("Environment configuration file not found at "+ path_config_file )
            self.send_critical_msgbox('Configuration File not Found!','Please select location of configuration File' )            
            errpath=aDialog.openFileNameDialog(7) #7->yml Files (*.yml)
            if errpath==None:
                with open(errpath) as file:
                    path_config = yaml.load(file, Loader=yaml.SafeLoader)
                    log.info("Environment configuration loaded") 
                    log.warning('Save configuration path as {} to not be prompted for a file'.format(self.default_config_path))                                 
            else:
                raise
            #print(f"Create new {config_file} file?")                
            #input_config(config_parameters)
            #generate_config_file(config_parameters)                    
        return path_config
        
    def Connect_Actions(self):
        """
        Connect all objects
        """
        """      
        #right click menu
        self.treeView.customContextMenuRequested.connect(self.listItemRightClicked)  
        """
        self.lineEdit_url.textChanged.connect(self.lineedit_url_changed)
        self.actionAbout.triggered.connect(self.Show_aboutbox)
        self.actionSet_Path.triggered.connect(self.Set_download_Path)
        self.pushButton_url.pressed.connect(self.pushbutton_url_pressed)

    def pushbutton_url_pressed(self):
        """
        On pressed url button add to list
        """
        try:
            urlexists = self.does_url_exist(self.lineEdit_url.text())
        except:
            urlexists = False
        if urlexists:
            self.add_item_to_url_struct()
    
    def get_id_list(self):
        """
        Get the ids of the items in view
        """
        return self.get_dict_key_list(self.url_struct)
 
    def is_id_taken(self, id):
        """
        Check if the id is taken
        """
        idlist=self.get_id_list()
        if id in idlist:
            return True
        return False

    def get_unique_id(self,desired_id):
        if self.is_id_taken(desired_id)==False and desired_id!='' and desired_id!=None:
            return desired_id
        
        if desired_id==None or desired_id!='':
            desired_id='UID_'
        iii=1
        copydid=desired_id+str(iii)            
        while self.is_id_taken(copydid)==True:
            iii=iii+1
            copydid=desired_id+str(iii)
        return copydid

    def add_item_to_url_struct(self):
        """
        Adds item to list
        """
        print("3"*333)
        print(self.twf.Data_Struct)
        newId=self.get_unique_id('URL'+str(self.url_id_counter))
        self.url_struct.update({
        newId:{"url":self.lineEdit_url.text(),
                    "Name":" ",
                    "Size":0,
                    },
        })
        self.url_id_counter = self.url_id_counter + 1
        
        self.twf.Data_Struct=self.url_struct
        self.twf.set_show_dict()
        self.twf.refresh_tableWidget(self.twf.Show_dict,self.twf.modelobj,self.twf.tablewidgetobj)
    
    def does_url_exist(self,url):
        """
        Check if the given url exists or not
        """
        try:
            response = requests.get(url)
        except:
            return False
        if response.status_code == 200:
            return True
        return False

    def Set_download_Path(self):
        """
        Sets the path for download and stores the configuration
        """
        dl_dir=aDialog.getOpenFilesAndDirs(caption='Select Download directory')
        log.info("Download dir: %s", dl_dir)
        self.General_Config["Last_Path_for_Download"] = dl_dir
        self.set_General_Config_to_yml_file()
        self.download_path = self.General_Config["Last_Path_for_Download"]
        self.label_DownloadPath.setText("Downloading to: {}".format(self.download_path))

    def set_General_Config_to_yml_file(self):    
        """
        Saves the general configuration
        """    
        try:
            if os.path.exists(self.path_config_file)==True:
                with open(self.path_config_file, 'w') as file:
                    yaml.dump(self.General_Config, file)
        except Exception as e:
            log.error('Saving yml configuration file!')
            log.error(e)    

    def lineedit_url_changed(self):
        """
        When line edit changed
        """
        urlexists=self.does_url_exist(self.lineEdit_url.text())
        if urlexists:
            self.lineEdit_url.setToolTip("Exists!")
        else:
            self.lineEdit_url.setToolTip("")

    def set_splitter_pos(self,pos,per=None):
        """
        Sets the position of the splitter
        """
        sizes=self.splitter.sizes()
        tot=sizes[1]+sizes[0]
        if per!=None and per>=0 and per<=1:            
            pos=int(tot*per)
            newsizes=[pos,tot-pos]
            self.splitter.setSizes(newsizes)
        elif pos<=tot:            
            newsizes=[pos,tot-pos]            
            self.splitter.setSizes(newsizes)
        self.splitter.adjustSize()
         
    def get_dict_key_list(self,dict):
        """
        Return a list of keys in dictionary
        """
        alist=[]
        for key in dict:
            alist.append(key)
        return alist
    
    def set_path_labels(self):        
        """
        Set texts and labels in Gui
        """
        self.groupBox.setTitle("List of URLs:")
        self.groupBox_2.setTitle("Processed URLs:")
        self.label_DownloadPath.setText("Downloading to: {}".format(self.download_path))
    
    def send_questionYesNo_msgbox(self,title,amsg):
        """
        Makes yes/no messagebox 
        """
        msgbox = QtWidgets.QMessageBox()
        result = QtWidgets.QMessageBox.question(msgbox,
                      title,
                      amsg,
                      QtWidgets.QMessageBox.Yes| QtWidgets.QMessageBox.No)        
        if result == QtWidgets.QMessageBox.Yes:
            return True
        if result == QtWidgets.QMessageBox.No:
            return False
        return None

    def send_critical_msgbox(self,title,amsg):
        """
        Makes critical messagebox 
        """
        msgbox = QtWidgets.QMessageBox()
        msgbox.setWindowTitle(title)
        msgbox.setIcon(QtWidgets.QMessageBox.Critical)
        msgbox.setText(amsg)            
        msgbox.exec_()

    def send_informative_msgbox(self,title,amsg):
        """
        Makes informative messagebox 
        """
        msgbox = QtWidgets.QMessageBox()
        msgbox.setWindowTitle(title)
        msgbox.setIcon(QtWidgets.QMessageBox.Information)
        msgbox.setText(amsg)            
        msgbox.exec_()
    
    def Show_aboutbox(self):
        """
        Shows About box
        """
        title='About YT Downloader PytubeFix Tool'
        amsg='<h1 style="font-size:160%;color:red;">Programmed with love</h1>'+'<h1 style="font-size:160%;color:black;">by '+ __author__+'</h1> <p style="color:black;">github: '+__gitaccount__+'</p> <p style="color:black;"> Current version: V'+__version__+'</p> <p style="color:black;">Creation date: '+__creationdate__+"</p>"
        #msgbox = QtWidgets.QMessageBox.about(MainWindow,title,amsg)        
        msgbox = QtWidgets.QMessageBox()
        msgbox.setWindowTitle(title)
        #msgbox.setIcon(QtWidgets.QMessageBox.Information)
        msgbox.setWindowIcon(self.iconMain)
        if self.iconMainpixmap!=None:            
            thepm=self.iconMainpixmap.scaled(160,160, QtCore.Qt.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)#QtCore.Qt.FastTransformation)
            #thepm.scaledToWidth(90,QtCore.Qt.TransformationMode.SmoothTransformation)#  QtCore.Qt.TransformationMode.SmoothTransformation) #QtCore.Qt.AspectRatioMode.KeepAspectRatio)            
            msgbox.setIconPixmap(thepm)
        msgbox.setText(amsg)           
        msgbox.setTextFormat(QtCore.Qt.RichText)
        msgbox.exec_()
    
    def extract_filename(self,filename,withextension=True):
        """
        Extracts filename of path+File+ext
        """
        fn= os.path.basename(filename)  # returns just the name
        fnnoext, fext = os.path.splitext(fn)
        fnnoext=fnnoext.replace(fext,'')
        fn=fnnoext+fext        
        if withextension==True:
            return fn
        else:                
            return  fnnoext 

    def extract_path(self,filename):
        """
        Extracts path of path+File+ext
        """
        fn= os.path.basename(filename)  # returns just the name
        fpath = os.path.abspath(filename)
        fpath = fpath.replace(fn,'')
        return fpath
    
    def get_appPath(self):
        """
        gets this application path when running/installed
        """
        # determine if application is a script file or frozen exe
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)
        return application_path
    
class MyWindow(QtWidgets.QMainWindow):           
    '''
    Override Window events to close
    '''    
    def closeEvent(self,event):
        
        # ask to leave?
        result = QtWidgets.QMessageBox.question(self,
                      "Confirm Exit...",
                      "Are you sure you want to exit ?",
                      QtWidgets.QMessageBox.Yes| QtWidgets.QMessageBox.No)
        event.ignore()

        if result == QtWidgets.QMessageBox.Yes:
            #print('inside class')       
            # self.CCDialog      
        
            try:                
                ui.CCDialog.quit()                   
            except Exception as e:
                #log.error(e)     
                pass      
          
            event.accept()

if __name__ == "__main__":    
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = MyWindow() #QtWidgets.QMainWindow() #Modified to close windows
    ui = Ui_MainWindow_yt() #GUI_PostProcessing.Ui_MainWindow()
    aDialog=class_File_Dialogs.Dialogs()
    # Create Queue and redirect sys.stdout to this queue
    #sys.stdout = WriteStream(a_queue)
    # Log handler
    

    ui.setupUi(MainWindow)
    ui.setupUi2(MainWindow)
    
    
    MainWindow.show()    
    sys.exit(app.exec_())