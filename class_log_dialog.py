import re
import logging
from PyQt5 import QtGui,QtCore,QtWidgets
from PyQt5.QtWidgets import *

import class_file_dialogs
import class_signal_tracker
import yt_pytubefix_log_dialog


class log_dialog(QWidget,yt_pytubefix_log_dialog.Ui_Dialog):   

    def __init__(self,pathandfile,icon_dialog, *args, **kwargs):        
        super(log_dialog, self).__init__( *args, **kwargs)    
        self.__name__="Log Dialog"
        self.a_dialog =class_file_dialogs.Dialogs()
        self.st=class_signal_tracker.SignalTracker()
        self.icon_dialog=icon_dialog
        self.pathandfile = pathandfile
        self.line_numberlistlW=[]
        self.line_numberlistnW=[]
        self.line_numberlistE=[]
        self.line_numberlistlP=[]
        self.log_level="INFO"
        self.open_log_dialog()
        self.setup_log_filters()
    
    def open_log_dialog(self):
        self.d_log_dialog = QtWidgets.QDialog()
        self.ld_ui = yt_pytubefix_log_dialog.Ui_Dialog()
        self.ld_ui.setupUi(self.d_log_dialog)        
        #self.d_log_dialog.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint|QtCore.Qt.WindowCloseButtonHint)
        #self.d_log_dialog.showMaximized()
        #Show dialog function in main
        self.d_log_dialog.show()    
        #self.is_dialog_open=True    
        # self.Setup_interface_objects()
        # self.Connect_actions()        
        #add max option
        #self.d_log_dialog.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint, True)
        #self.d_log_dialog.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, True)
        
        #self.closeEvent=self.d_log_dialog.closeEvent
        
        #self.setFixedSize(self.width(), self.height())
        # set the icon 
        self.d_log_dialog.setWindowIcon(self.icon_dialog) 
          
        
        # file_exists = os.path.exists(path_to_file)
        # #print(path_to_file+' '+str(file_exists))
        # if file_exists==True:
        #     self.d_log_dialog.setWindowIcon(self.iconDialog) 
        self.write_file_to_log(self.pathandfile)
    
    def setup_log_filters(self):
        """Sets combobox for log level filter"""
        self.ld_ui.comboBox_log_level.addItem("DEBUG")
        self.ld_ui.comboBox_log_level.addItem("INFO")     
        self.ld_ui.comboBox_log_level.addItem("CRITICAL")
        self.ld_ui.comboBox_log_level.addItem("ERROR")
        self.ld_ui.comboBox_log_level.addItem("WARNING")   
        self.ld_ui.comboBox_log_level.addItem("FATAL")
        self.ld_ui.comboBox_log_level.addItem("NOTSET")

        #Set default
        index= self.ld_ui.comboBox_log_level.findText(self.log_level,QtCore.Qt.MatchFixedString)
        self.ld_ui.comboBox_log_level.setCurrentIndex(index)
        #connect
        self.ld_ui.comboBox_log_level.currentIndexChanged.connect(self.cb_set_log_level)
        self.ld_ui.pushButton_log_clear.clicked.connect(self.clear_log)

    def cb_set_log_level(self):
        """Sets the log Level 
        """
        self.log_level=self.ld_ui.comboBox_log_level.currentText()
        self.st.send_ld_log_level(self.log_level)

    def clear_log(self):
        self.ld_ui.textEdit.clear()

    def write_file_to_log(self,pathandfile:str):
        """writes the log text to text edit

        Args:
            pathandfile (str): path and Filename
        """
        self.clear_log()
        self.pathandfile = pathandfile
        try:
            with open(pathandfile) as file:
                thelines=file.readlines()
                for line in thelines:
                    self.append_text_filtered(line)
        except FileNotFoundError:
            pass
        self.clear_highlights()
        self.ld_ui.textEdit.moveCursor(QtGui.QTextCursor.End)
        self.ld_ui.textEdit.verticalScrollBar().setValue(self.ld_ui.textEdit.verticalScrollBar().maximum())
        self.append_text_to_text_edit("+++++++++++++++++++++++++",True)

    def clear_highlights(self):
        self.line_numberlistlW=[]
        self.line_numberlistnW=[]
        self.line_numberlistE=[]
        self.line_numberlistlP=[]

    def append_text_filtered(self,text): 
        """"""  
        if self.log_level == "DEBUG":
            self.append_text_to_text_edit(text)
        elif self.log_level == "INFO":
            if "INFO" in text or "ERROR" in text: #or "WARNING" in text:
                self.append_text_to_text_edit(text)
        elif self.log_level == "ERROR":
            if "ERROR" in text:
                self.append_text_to_text_edit(text)
        elif self.log_level == "WARNING":
            if "WARNING" in text:
                self.append_text_to_text_edit(text)
        elif self.log_level == "CRITICAL":
            if any(re.search(f"[^{re.escape(match)}]", text) for match in [ "ERROR","WARNING","CRITICAL"]):
                self.append_text_to_text_edit(text)
        elif self.log_level == "FATAL":
            if any(re.search(f"[^{re.escape(match)}]", text) for match in [ "ERROR","FATAL","CRITICAL"]):
                self.append_text_to_text_edit(text)
        elif self.log_level == "NOTSET":
            self.append_text_to_text_edit(text)
        

    def append_text_to_text_edit(self,text,do_heighlighting=False):
        self.ld_ui.textEdit.moveCursor(QtGui.QTextCursor.End)
        self.ld_ui.textEdit.insertPlainText( text+'\r\n' )   
        self.ld_ui.textEdit.moveCursor(QtGui.QTextCursor.End)  
        if not do_heighlighting:
            return           
        try:
            lightblue=QtGui.QColor(0, 0, 255, 64)
            lightgreen=QtGui.QColor(0, 255, 0, 64)
            self.highlight_(self,self.ld_ui.textEdit,'[WARNING]','yellow',self.line_numberlistnW)
            self.highlight_(self,self.ld_ui.textEdit,'[ERROR]','red',self.line_numberlistE)        
            self.highlight_(self,self.ld_ui.textEdit,'Download finished for ID:',lightgreen,self.line_numberlistlW) 
            # self.highlight_(self,self.ld_ui.textEdit,'not in permitted list:',lightblue,self.line_numberlistlW)  
            # self.highlight_(self,self.ld_ui.textEdit,'++++++++++++',lightgreen,self.line_numberlistlP)  
            #_=self.get_linenumberlist_for_text(self.ld_ui.textEdit,text,[])# will select last line           
            #self.statusbar.setStatusTip('{} Warnings, {} Errors'.format(len(self.line_numberlistW),len(self.line_numberlistE)))
        except Exception as e:
            #since log created before setup
            #print('Here error is ',e)
            self.line_numberlistlW=[]
            self.line_numberlistnW=[]
            self.line_numberlistE=[]
            self.line_numberlistlP=[]
            pass        
        #self.send_log_to_all_dialogs(text)
    
    def set_highlights_(self,parent,obj,color,line_numberlist,justclear=False):        
        if isinstance(obj,QtWidgets.QTextEdit):            
            fmt=QtGui.QTextCharFormat()        
            fmt.setBackground(QtGui.QColor(color))
            try:
                highlight=parent.highligter
            except:
                highlight=SyntaxHighLighter(obj.document())
                parent.highligter=highlight

            if justclear==True:
                highlight.clearhighlight()                
                #print('Cleared Highligths, returning--->',line_numberlist)   
            else:
                try:
                    if len(line_numberlist)>0:
                        #print('Making Highligths, for--->',line_numberlist,obj)
                        for linenumber in line_numberlist:
                            highlight.highlightline(linenumber,fmt)
                except Exception as e:
                    print('Highlighting Error: {}'.format(e))        
        return line_numberlist
    
    def get_linenumberlist_for_text(self,obj,text,line_numberlist):        
        #print('----------got list:',line_numberlist,text,obj)
        if isinstance(line_numberlist,list) and isinstance(obj,QtWidgets.QTextEdit):                
            bntot=obj.document().blockCount()
            bnlast=-1
            bn=0
            count=0            
            position=0   
            iii=0                               
            while iii <= bntot:
                if iii==0:
                    cursor=None                
                index,cursor=self.set_cursor_toselectText(obj,text,cursor)   
                bn=cursor.blockNumber()                        
                if index==-1:     
                    iii=bntot+1
                if bn>0 and bn not in line_numberlist:
                    line_numberlist.append(bn)  
                    bnlast=bn 
                if bn>0:            
                    iii=iii+bn  
                else:
                    iii=iii+1            
        return line_numberlist    

    def set_cursor_toselectText(self,texteditobj,text,cursor=None):
        if cursor==None:
            cursor = texteditobj.document().find(text)
        findIndex = cursor.anchor()        
        content = texteditobj.toPlainText()
        length = len(text)        
        index = content.find(text, findIndex)
        if index!=-1:            
            start = index
            cursor = texteditobj.textCursor()
            cursor.clearSelection()
            cursor.movePosition(QtGui.QTextCursor.Start, QtGui.QTextCursor.MoveAnchor)
            cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.MoveAnchor, start + length)
            cursor.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.KeepAnchor, length)
            cursor.selectedText()
            texteditobj.setTextCursor(cursor)
        return index,cursor

    
    def highlight_(self,parentobj,obj,hltext,color,hllist):        
        try:
            try:                    
                hllist=self.get_linenumberlist_for_text(obj,hltext,hllist)            
            except Exception as e:
                print('clear error:',e)
                hllist=self.set_highlights_(parentobj,obj,color,[],True)
            hllist=self.set_highlights_(parentobj,obj,color,hllist,False)  

        except Exception as e:                
            print('Setting highlights {}'.format(e))     
            pass          


class SyntaxHighLighter(QtGui.QSyntaxHighlighter):               
    def __init__(self,parent):
        super().__init__(parent)
        self.highlightlines={}
    def highlightline(self,line_number,fmt):
        if isinstance(line_number,int) and isinstance(fmt,QtGui.QTextCharFormat):
            if line_number>0:
                self.highlightlines[line_number]=fmt
                block=self.document().findBlockByLineNumber(line_number)
                self.rehighlightBlock(block)
    def clearhighlight(self):
        self.highlightlines={}
        self.rehighlight()
    
    #def highlightBlock(self, text: str) -> None:
    #    return super().highlightBlock(text)
    def highlightBlock(self, text):
        blocknumber=self.currentBlock().blockNumber()
        fmt=self.highlightlines.get(blocknumber)
        if fmt is not None:
            self.setFormat(0,len(text),fmt)

class QTextEditLogger(logging.Handler):
    def __init__(self, log_qtextedit_obj):
        super().__init__()
        if isinstance(log_qtextedit_obj,QtWidgets.QTextEdit):
            self.widget = log_qtextedit_obj
            self.widget.setReadOnly(True)

    def emit(self, record):
        """Emit the record
        Args:
            record (str): string to emit
        """
        #self.widget.textCursor().insertText(self.format(record))
        self.widget.insertPlainText(str(self.format(record)+'\r\n'))