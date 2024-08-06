import logging
from multiprocessing.sharedctypes import Value
from xmlrpc.client import boolean
from PyQt5 import QtCore, QtGui, QtWidgets
import re

# set up logging to file - see previous section for more details
log = logging.getLogger('') #root logger
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s [%(levelname)s] (%(threadName)-10s) %(message)s',
                    datefmt='%y-%m-%d %H:%M')
# define a Handler which writes INFO messages or higher to the sys.stderr
twconsole = logging.StreamHandler()
twconsole.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('[%(levelname)s] (%(threadName)-10s) %(message)s')
# tell the handler to use this format
twconsole.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(twconsole)


class tableWidget_functions(QtWidgets.QWidget):   
    data_change=QtCore.pyqtSignal(list,str,str,str)   
    item_button_clicked=QtCore.pyqtSignal(list)  
    item_combobox_currentIndexChanged =QtCore.pyqtSignal(int,str,list)
    item_doubleclicked=QtCore.pyqtSignal(list)  
    item_checkbox_checked=QtCore.pyqtSignal(bool,list)

    def Signal_Data_Change(self,track,val,valtype,subtype):
        #log.info('cTV Emmiting: {} {} {} {}'.format(track,val,valtype,subtype))
        self.data_change.emit(track,val,valtype,subtype)
    
    def doubleclick_on_item(self,itm):
        track=self.track_key_Table(itm)
        self.item_doubleclicked.emit(track)

    def __init__(self,tablewidgetobj,Data_Struct,Data_Struct_mask,Data_ID=None,Reftrack=[], *args, **kwargs):   
        super(tableWidget_functions, self).__init__(*args, **kwargs)             
        self.__name__="tableWidget Functions"
        if isinstance(tablewidgetobj,QtWidgets.QTableWidget):
            self.tablewidgetobj=tablewidgetobj
        else:
            raise Exception('tableWidget object is Not a {} object'.format(type(QtWidgets.QTableWidget)))                
        self.Data_Struct=Data_Struct #all info
        self.Data_Struct_mask=Data_Struct_mask
        self._last_value_selected=None
        self.Data_ID=Data_ID
        self.Reftrack=Reftrack
        #displayed on tableWidget
        self.set_show_dict()
        # uses show dict
        self.modelobj=self.Create_Data_Model_tableWidget(self.tablewidgetobj,False)        
        self.Data_Struct_types=self.get_types_struct(self.Data_Struct)   
        self.Show_dict_types=self.get_types_struct(self.Show_dict)   
        self.set_ItemIcons()
        self.set_ItemBackgroundColor()
        self.set_ItemTooltips()       
        self.set_ItemWidget() 
        self.set_Itemrolevalue()
        
        self.Restore_column_list=[]
        self.Restore_key_list=[]
        self.resizetocontents=True
        #print(self.Show_dict_types)                
        self.refresh_tableWidget(self.Show_dict,self.modelobj,self.tablewidgetobj) 
        # connect action
        self.tablewidgetobj.clicked.connect(self.tableWidget_OnClick)  
         
        
        
    def get_standard_dict_model(self,fieldname='Datafield_1'):
        return {fieldname:{'Value':'','Units':'','Info':'','Type':str(type(''))}}
    
    def set_Restore_Columns(self,colkey):
        for iii,ti in enumerate(self.tableitems):
            if colkey==ti:                
                self.Restore_key_list.append(colkey)
                self.Restore_column_list.append(iii)

    def set_show_dict(self):
        if len(self.Reftrack)==0:
            showdict=self.get_dictionary_from_structlist(self.Data_Struct,self.Data_ID)      
            #print('From len 0 showdict:\n',showdict)      
        else:
            showdict=self.get_tracked_value_in_struct(self.Reftrack,self.Data_Struct)            
            #print('From else showdict:\n',showdict)      
        if self.is_dict(showdict)==True:
            self.Show_dict=showdict
        else:
            self.Show_dict=self.Data_Struct


    def get_types_struct(self,dict_struct):         
        if self.is_list(dict_struct)==True:
            type_Struct=[]      
            for aData in dict_struct:
                type_Struct.append(self.get_types_struct(aData))                                
        elif self.is_dict(dict_struct)==True:
            type_Struct={}
            for aData in dict_struct:    
                if self.is_dict(dict_struct[aData])==True:  
                    nts=self.get_types_struct(dict_struct[aData])
                    type_Struct.update({aData:nts})
                else:
                    type_Struct.update({aData:str(type(dict_struct[aData]))})
        else:
            type_Struct={}
            type_Struct.update({str(dict_struct):str(type(dict_struct))})
        
        return type_Struct

    def get_gentrack_from_localtrack(self,track):
        gentrack=self.Reftrack.copy()
        for iii in track:
            gentrack.append(iii)
        return gentrack    
    
    def get_localtrack_from_gentrack(self,track):
        gentrack=self.Reftrack.copy()
        trackc=track.copy()
        for iii in track:
            if track[iii]==gentrack[iii]:
                trackc.pop(0)
        return trackc   

    def get_dictionary_from_structlist(self,Data_Struct,Data_ID=None):        
        if self.is_list(Data_Struct)==True:
            for adict in Data_Struct:
                if adict['ID']==Data_ID:
                    #print('get my dict Found ID',Data_ID)
                    return adict.copy()
        elif self.is_dict(Data_Struct)==True or Data_ID==None:
            #print('get my dict nochange is dict',Data_ID)
            return Data_Struct.copy()
        else:
            return {}        
    
    def refresh_tableWidget(self,data_dict,modelobj,tablewidgetobj):           
        if isinstance(tablewidgetobj,QtWidgets.QTableWidget):
            self.set_show_dict()             
            tablewidgetobj.setRowCount(0)
            modelobj=self.Create_Data_Model_tableWidget(tablewidgetobj,False)                    
            self.Data_importData_to_Table(data_dict,modelobj,tablewidgetobj)    
            if self.resizetocontents==True:
                tablewidgetobj.resizeColumnsToContents()      
            #self.set_tableWidget_styles(tablewidgetobj.model())
        else:
            raise Exception('tableWidget object is Not a {} object'.format(type(QtWidgets.QTableWidget)))        
    
    def set_item_style(self,itm):                               
        self.set_icon_to_item(itm)            
        self.set_backgroundcolor_to_item(itm)      
        self.set_rolevalue_to_item(itm)  

    def set_ItemTooltips(self,tooltipict={'track_list':[],'tooltip_list':[]}):
        self.Tooltip_dict=tooltipict 

    def set_ItemIcons(self,icondict={'track_list':[],'icon_list':[]}):
        self.icon_dict=icondict 
    
    def set_ItemBackgroundColor(self,backgroundcolor_dict={'track_list':[],'color_list':[]}):
        self.backgroundcolor_dict=backgroundcolor_dict
    
    def set_ItemWidget(self,itemwidget_dict={'track_list':[],'widget_list':[]}):
        self.itemwidget_dict=itemwidget_dict

    def set_Itemrolevalue(self,rolevalue_dict={'track_list':[],'role_list':[],'value_list':[]}):
        self.itemrolevalue_dict=rolevalue_dict
    
    
    def is_same_list(self,list1,list2):
        if len(list1)!=len(list2):
            return False        
        for iii,jjj in zip(list1,list2):
            if iii!=jjj:
                return False
        return True
    
    def itembuttonclicked(self,track):
        #print('entered click {}'.format(track))
        self.item_button_clicked.emit(track)
    def itemcomboboxindexchanged(self,cbw,track=[]):                
        currenttxt=cbw.currentText()
        index= cbw.findText(currenttxt,QtCore.Qt.MatchFixedString)
        self.item_combobox_currentIndexChanged.emit(index,currenttxt,track)
    def itemcheckboxchecked(self,chb,track=[]):                
        currentstate=chb.isChecked()        
        self.item_checkbox_checked.emit(currentstate,track)

    def set_widget_to_item(self,itm):
        try:
            if isinstance(itm,QtWidgets.QTableWidgetItem):
                track=self.track_key_Table(itm)
            else:
                return
            track_list=self.itemwidget_dict['track_list']
            widget_list=self.itemwidget_dict['widget_list']            
            for tr,iw in zip(track_list,widget_list):
                if self.is_same_list(track,tr)==True: 
                    
                    self.tablewidgetobj.setCellWidget(itm.row(),itm.column(),iw)           
                    #itm.setWidget(iw)
                    itm.setFlags( itm.flags() ^ QtCore.Qt.ItemIsEditable)
                    #print('iw {}'.format(type(iw)))
                    if isinstance(iw,QtWidgets.QPushButton):
                        #print('Connected Buton')
                        iw.clicked.connect(lambda:self.itembuttonclicked(track))                        
                    elif isinstance(iw,QtWidgets.QComboBox): 
                        iw.currentIndexChanged.connect(lambda:self.itemcomboboxindexchanged(iw,track=track))
                    elif isinstance(iw,QtWidgets.QCheckBox):                        
                        iw.stateChanged.connect(lambda:self.itemcheckboxchecked(iw,track))
                    elif isinstance(iw,QtWidgets.QLabel):                                                   
                        #self.tablewidgetobj.itemDoubleClicked.connect(self.doubleclick_on_item)                     
                        if self.resizetocontents==True:
                            self.tablewidgetobj.resizeColumnToContents(itm.column())
                            self.tablewidgetobj.resizeRowToContents(itm.row())
                    break
        except Exception as e:
            print('set_widget_to_item error--->',e)
            pass
    
    def set_icon_to_item(self,itm):
        try:
            track=self.track_key_Table(itm)
            track_list=self.icon_dict['track_list']
            icon_list=self.icon_dict['icon_list']            
            for tr,ic in zip(track_list,icon_list):
                if self.is_same_list(track,tr)==True:            
                    itm.setIcon(ic)
        except:
            pass
    
    def set_rolevalue_to_item(self,itm):
        try:
            track=self.track_key_Table(itm)
            track_list=self.itemrolevalue_dict['track_list']
            role_list=self.itemrolevalue_dict['role_list']    
            value_list=self.itemrolevalue_dict['value_list']         
            for tr,role,value in zip(track_list,role_list,value_list):
                if self.is_same_list(track,tr)==True:            
                    itm.setData(role,value)
        except:
            pass
        
    
    def set_backgroundcolor_to_item(self,itm):
        try:
            track=self.track_key_Table(itm)
            track_list=self.backgroundcolor_dict['track_list']
            color_list=self.backgroundcolor_dict['color_list']            
            for tr,ic in zip(track_list,color_list):
                if self.is_same_list(track,tr)==True:            
                    itm.setBackground(ic)            
        except:
            pass
   
    def set_tooltiptext(self,itm):
        reslist,resvallist=self.get_item_restriction_resval(itm)    
        for res,resval in zip(reslist,resvallist):            
            if res in ['limited_selection','is_list_item_limited_selection']:                
                itm.setToolTip('Options: {}'.format(resval))
        try:
            track=self.track_key_Table(itm)
            track_list=self.Tooltip_dict['track_list']
            tooltip_list=self.Tooltip_dict['tooltip_list']            
            for tr,itt in zip(track_list,tooltip_list):
                if self.is_same_list(track,tr)==True:            
                    itm.setToolTip(itt)            
        except:
            pass
            

        
    def tableWidget_OnClick(self,index):        
        if isinstance(index,QtCore.QModelIndex):
            mycol=index.column()
            myrow=index.row()
        '''
        icol=self.get_item_column_pos_in_table('Item')
        vcol=self.get_item_column_pos_in_table('Value')
        tcol=self.get_item_column_pos_in_table('Type')
        #Set items editable                        
        #self.tablewidgetobj.resizeColumnToContents(mycol)
        indexitem=index.siblingAtColumn(icol)
        itm=self.tablewidgetobj.itemFromIndex(indexitem)        
        indexvalue=index.siblingAtColumn(vcol)
        valueitem=self.tablewidgetobj.itemFromIndex(indexvalue)        
        indextype=index.siblingAtColumn(tcol)
        typeitem=self.tablewidgetobj.itemFromIndex(indextype)
        '''
        if self.resizetocontents==True:
            self.tablewidgetobj.resizeColumnToContents(mycol)
        itm=self.tablewidgetobj.itemFromIndex(index)        
        self.set_icon_to_item(itm)
        self.set_widget_to_item(itm)
        self.set_tooltiptext(index)        
        if mycol in self.Restore_column_list:
            self.restore_a_tableWidget_Item(index)            
            return  
        else:  
            val_=itm.text()
            if self.str_to_bool_or_none(val_) in [True,False]:                                                        
                self.set_checkbox_value(itm)  
            self.edit_a_tableWidget_Item(index)            
                   

    def set_checkbox_value(self,valueitem):        
        if self.str_to_bool(valueitem.text())==True:
            valueitem.setCheckState (True)                     
        else:                    
            valueitem.setCheckState(False)

    def get_item_from_colpos(self,colpos):
        for iii in self.tableitems:
            cp=self.get_item_column_pos_in_table(iii)
            if cp==colpos:
                return iii
        return None

    def get_key_value_from_item(self,anitem):
        if isinstance(anitem,QtWidgets.QTableWidgetItem):        
            myrow=anitem.row()
            return self.get_key_value_from_row(myrow)
    
    def get_key_value_from_row(self,myrow):
        for iii,key in enumerate(self.Show_dict):
            if iii==myrow:
                return key


    def track_key_Table(self,anitem):
        track=self.Reftrack.copy()
        if isinstance(anitem,QtWidgets.QTableWidgetItem):        
            myrow=anitem.row()
            mycol=anitem.column()  
            valkey=self.get_key_value_from_row(myrow)                      
            track.append(valkey)            
            track.append(self.get_item_from_colpos(mycol))                                       
        return track  

    def edit_a_tableWidget_Item(self,index):    
        #print('edit_a_tableWidget_Item',index)                         
        itm = self.tablewidgetobj.itemFromIndex(index)        
        val=itm.text()                     
        #print('edit index set:',index.data())
        self._last_value_selected=val        
        self.tablewidgetobj.itemChanged.connect(lambda: self.Item_data_changed(index,val))        
 
    def get_list_of_tracks_of_children(self,parenttrack):
        self.get_gentrack_from_localtrack

    def get_item_from_track(self,modelobj,track):
        if isinstance(modelobj,QtCore.QAbstractItemModel):
            try:
                itmtrack=[]
                itmindextrack=[]
                parent=None
                for ttt,tr in enumerate(track):                    
                    if parent==None:
                        #log.info('the size -> {}'.format(modelobj.rowCount())) 
                        for iii in range(modelobj.rowCount()):
                            itmindex=modelobj.index(iii, 0)                                 
                            itm = modelobj.itemFromIndex(itmindex)    
                            if itm!=None:                
                                #log.info('got this-> {} search for {}'.format(itm.text(),tr))
                                if tr==itm.text():
                                    break
                            else:
                                break
                        if itm==None:
                            break
                        if tr!=itm.text(): # not found
                            break
                    else:
                        #log.info('the size -> {}'.format(modelobj.rowCount(parent))) 
                        for iii in range(modelobj.rowCount(parent)):
                            itmindex=modelobj.index(iii, 0, parent)                             
                            itm = modelobj.itemFromIndex(itmindex)                        
                            if itm!=None:         
                                #log.info('parent got this-> {} search for {}'.format(itm.text(),tr))       
                                if tr==itm.text():
                                    break
                            else:                                    
                                break
                        if itm==None:
                            break
                        if tr!=itm.text(): # not found
                            break                                                                                                     
                    parent=itmindex 
                    parentitm = modelobj.itemFromIndex(parent)                     
                    if parentitm.text()=='ID':
                        parenttxt=parentitm.text()              
                        parent=None
                        continue
                    itmtrack.append(itm)
                    itmindextrack.append(itmindex)
                return itm,itmindex,itmtrack,itmindextrack
            except Exception as e:
                log.error('get item from track: {}'.format(e))    

    def Item_data_changed(self,index,val):   
        if isinstance(index,QtCore.QModelIndex):
            mycol=index.column()
            myrow=index.row()             
        old_value=val #self._last_value_selected        
        #print('tvf Item changed->',index.data(),' old value->',old_value)
        itm = self.tablewidgetobj.itemFromIndex(index)         
        new_value=itm.text()       
        selindex=self.tablewidgetobj.selectedIndexes()                   
        #icol=self.get_item_column_pos_in_table('Item')
        #tcol=self.get_item_column_pos_in_table('Type')
        #self.set_item_style(self.tablewidgetobj.item(itm.row(),icol)) # column item
        if new_value!=old_value and old_value!=None and index in selindex:            
            #indextype=index.siblingAtColumn(tcol)
            #typeitem=self.tablewidgetobj.itemFromIndex(indextype)
            track=self.track_key_Table(self.tablewidgetobj.itemFromIndex(index))                        
            #Here check if value is ok if yes
            valisok=self.check_item_value_for_edit(index,new_value,old_value,self.Show_dict)
            #print('class_tableWidgetFunctions Datachanged-> New:',new_value,'Old:',old_value,'Track:',track,'isvalid:',valisok)
            log.info('Data changed -> New:{} Old:{} Track: {} isvalid: {}'.format(new_value,old_value,track,valisok))
            if valisok==True:
                subtype=''  
                #if self.is_item_supposed_to_be_a_list(itm)==True:                    
                    #gentrack=self.get_gentrack_from_localtrack(track)
                #    subtype=self.get_listitem_subtype(track)#gentrack)
                thetype,subtype=self.get_item_supposed_type_subtype(itm)
                new_valwt=self.set_type_to_value(new_value,thetype,subtype) #Send value with correct type to dictionary                                                    
                #_=self.set_tracked_value_to_dict(gentrack,new_valwt,self.Data_Struct,subtype,False) #doing it inside
                refreshtableWidget,self.Show_dict=self.set_tracked_value_to_dict(track,new_valwt,self.Show_dict,subtype)                   
                if refreshtableWidget==False:
                    itm.setText(new_value)
                    if thetype==str(type(True)):
                        self.set_checkbox_value(itm)
                else:                    
                    self.refresh_tableWidget(self.Show_dict,self.modelobj,self.tablewidgetobj) # need to refresh only if value is changed
                #Here send signal to refresh                 
                self.Signal_Data_Change(track,new_value,thetype,subtype)
            else:
                subtype=''
                thetype,subtype=self.get_item_supposed_type_subtype(itm)
                typestr=thetype
                if typestr==str(type([])):        
                    gentrack=self.get_gentrack_from_localtrack(track) # <-track is local!            
                    subtype=self.get_listitem_subtype(gentrack)
                old_valwt=self.set_type_to_value(old_value,thetype,subtype) #Send value with correct type to dictionary
                refreshtableWidget,self.Show_dict=self.set_tracked_value_to_dict(track,old_valwt,self.Show_dict,subtype)                
                itm.setText(old_value)
                if thetype==str(type(True)):
                    self.set_checkbox_value(itm)
        # reset old value        
        self._last_value_selected=None

    def is_item_supposed_to_be_a_list(self,itm):
        reslist,resvallist=self.get_item_restriction_resval(itm)    
        for res,resval in zip(reslist,resvallist):            
            if 'is_list_item_' in res or (res=='is_value_type' and resval==str(type([]))):
                return True
        return False
    
    def horizontalheaderclicked(self,index):
        print('horizontal',index)
    def verticalheaderclicked(self,index):
        print(index)
    
    def get_item_supposed_type_subtype(self,itm):
        subtype=''
        thetype=str(type(''))
        reslist,resvallist=self.get_item_restriction_resval(itm)    
        if self.is_item_supposed_to_be_a_list(itm)==False:            
            for res,resval in zip(reslist,resvallist):            
                if res=='is_value_type':
                    thetype=resval
                    break
        else:
            thetype=str(type([]))
            for res,resval in zip(reslist,resvallist):            
                if res=='is_list_item_type':
                    subtype=resval
                    break
        return thetype,subtype

    def get_listitem_subtype(self,track):        
        mask=self.get_mask_for_item(track)
        #log.info('Got for subtype: {} {}'.format(track,mask))
        for mmm in mask:
            keymmm=str(mmm)            
            if '__m__' in keymmm:
                keyval=keymmm.replace('__m__','__mv__')
                if mask[keymmm]=='is_list_item_type':
                    return mask[keyval]
        return ''

    def set_type_to_value(self,val,typestr,subtype=''):
        if typestr==str(type(1)):
            try:
                tyval=int(val)
            except:
                tyval=str(val)
        elif typestr==str(type(0.1)):
            try:
                tyval=float(val)
            except:
                tyval=str(val)
        elif typestr==str(type(True)):
            try:
                if val in ['1','True','true','yes','Yes']: 
                    tyval=True                     
                elif val in ['0','False','false','no','No']:                    
                    tyval=False
                else:
                    tyval=int(val)
            except:
                tyval=str(val)                
        elif typestr==str(type([])):
            try:
                split=self.str_to_list(val)
                if split!=None:
                    tyval=[]
                    for iii in split:
                        if subtype==str(type(0.1)):
                            iiival=float(iii)
                        elif subtype==str(type(0)):
                            iiival=int(iii)
                        elif subtype==str(type('')):
                            iiival=str(iii)
                        else:
                            iiival=iii
                        tyval.append(iiival)                    
                else:
                    tyval=str(val)
            except:
                tyval=str(val)
        else:
            tyval=str(val)
        return tyval

    def set_tracked_value_to_dict(self,track,val,dict_struct,subtype,emitsignal=True):
        refreshtableWidget=False
        trlist=track.copy()
        selected={}  
        if self.is_list(dict_struct)==True:      
            for aData in dict_struct:
                if aData['ID']==trlist[0]:
                    trlist.pop(0)
                    selected=aData#.copy() #select dictionary
                    while len(trlist)>1:
                        try:
                            selected=selected[trlist[0]]
                            trlist.pop(0)
                        except:
                            break
                    #last tracked is variable
                    if len(trlist)==1:
                        selected.update({trlist[0]:val})
                        # Change title of Data special case
                        #log.debug('setvaltodict_struct Here {} set to {}'.format(trlist[0],val))
                        if trlist[0]=='ID' and len(track)==2:
                            #print('2 Here name is',self.get_tracked_value_in_struct(['Unique Name 1', 'ID'],self.Data_Struct),track,val)                              
                            refreshtableWidget=True
                        if emitsignal==True:
                            trackstruct=track
                            self.Signal_Data_Change(trackstruct,str(val),str(type(val)),subtype)  #refresh on main
                        break                
        elif self.is_dict(dict_struct)==True:
            selected=dict_struct#.copy() #select dictionary
            while len(trlist)>1:
                try:
                    selected=selected[trlist[0]]
                    trlist.pop(0)
                except:
                    break
            #last tracked is variable
            if len(trlist)==1:
                selected.update({trlist[0]:val})
                #log.debug('setvaltodict_dict Here {} set to {}'.format(trlist[0],val))
                # update
                trackstruct=track.copy()
                _,self.Data_Struct=self.set_tracked_value_to_dict(trackstruct,val,self.Data_Struct,subtype)
                if emitsignal==True:
                    self.Signal_Data_Change(trackstruct,str(val),str(type(val)),subtype)  #refresh on main          
        return refreshtableWidget,dict_struct            
    
    def get_track_struct_from_dict_track(self,dict_,track):
        if self.is_dict(dict_)==True:
            if self.Data_ID!=None:
                endtrack=[self.Data_ID].append(track) 
                #print ('ini_track->',track,'endtrack->',endtrack)
                return endtrack                   
        return track


    def check_item_value_for_edit(self,index,val,old_val,Data_Struct,isok=True):
        #No need to check type in table, inside mask
        #isok=self.check_item_by_type(index,val,old_val,isok)   
        #print('bytype isok=',isok)     
        #log.debug('bytype isok={}'.format(isok))     
        isok=self.check_item_by_mask(index,val,old_val,Data_Struct,isok)
        #print('bymask isok=',isok)     
        log.debug('bymask isok={}'.format(isok))
        return isok

    def get_item_restriction_resval(self,itm):        
        track=self.track_key_Table(itm)
        itmmask=self.get_mask_for_item(track)
        if itmmask=={}:
            itmmask=self.get_mask_for_item(self.get_gentrack_from_localtrack(track))
        reslist=[]
        resvallist=[]
        if len(itmmask)>0:
            for mmm in itmmask:
                keyname=str(mmm)
                if '__m__' in keyname:                    
                    keyval=keyname.replace('__m__','__mv__')   
                    restriction=itmmask[keyname]
                    restrictionval=itmmask[keyval]      
                    reslist.append(restriction)
                    resvallist.append(restrictionval)
        return reslist,resvallist
                    
        

    def check_item_by_mask(self,index,val,old_val,Data_Struct,isok=True):        
        #Here to add specific value ranges,formats for example like if list can have more items or if axis has to be only X or Y  
        if isinstance(index,QtCore.QModelIndex):
            mycol=index.column()
            myrow=index.row()        
        #tcol=self.get_item_column_pos_in_table('Type')   
        #indextype=index.siblingAtColumn(tcol)                
        #typeitem=indextype.model().itemFromIndex(indextype)
        itm = self.tablewidgetobj.itemFromIndex(index) 
        track=self.track_key_Table(itm)
        itmmask=self.get_mask_for_item(track)
        if itmmask=={}:
            itmmask=self.get_mask_for_item(self.get_gentrack_from_localtrack(track))
        #print(self.Data_Struct_mask)
        print('Masked Track:',track,'Mask:',itmmask)
        #value=self.get_tracked_value_in_struct(track,Data_Struct)
        #print('Tracked value:',value)
        if len(itmmask)>0:
            for mmm in itmmask:
                keyname=str(mmm)
                if '__m__' in keyname:                    
                    keyval=keyname.replace('__m__','__mv__')   
                    restriction=itmmask[keyname]
                    restrictionval=itmmask[keyval]      
                    #print('Check restriction',restriction,'---->',restrictionval)           
                    isok=self.checkitem_value_with_mask(restriction,restrictionval,val)  
                    if restriction=='is_unique' and 'ID' in track:
                        idlist=self.get_ID_list()     
                        if val in idlist:
                            isok=False
                    if isok==False:
                        log.info('{} {} returned False'.format(track,keyname))
                        break  
        return isok
    
    def get_ID_list(self):
        IDlist=[]
        for aaa in self.Data_Struct:
            IDlist.append(aaa['ID'])
        return IDlist

    def str_to_bool_or_none(self,astr):
        if self.is_bool(astr)==True:
            return astr
        elif type(astr)==type(''):
            if astr.lower() in ['true']:   
                return True
            elif astr.lower() in ['false']:   
                return False
            else:
                return None
        else:
            return None

    def str_to_bool(self,val):
        if self.is_bool(val)==True:
            return val
        else:
            if val.lower() in ['true']:   
                return True
            else:
                return False

    def checkitem_value_with_mask(self,restriction,restrictionval,value):
        isok=True
        if restriction=='is_list_item_type':            
            strlist=self.str_to_list(value)   
            #print('got value:',value,type(value),'the list:',strlist,'resval:',restrictionval)         
            try:
                for iii in strlist:
                    #print(iii)
                    if restrictionval==str(type(0)):
                        _=int(iii.strip())                                                
                        rema=re.search('^[-+]?[0-9]+$',iii.strip())
                        if rema:
                            isok=True
                        else:
                            isok=False                        
                    elif restrictionval==str(type(0.1)):
                        _=float(iii)
                    elif restrictionval==str(type(True)):
                        ans=self.str_to_bool_or_none(iii) 
                        if ans==None:
                            isok=False  
                    else:
                        isok=self.check_type(restrictionval,iii,isok)                      
            except Exception as e:
                #print(e)
                isok=False
        elif restriction=='is_list_length':
            strlist=self.str_to_list(value)
            #print('got value:',value,type(value),'the list:',strlist,'resval:',restrictionval)
            try:
                if restrictionval!=len(strlist):
                    isok=False
            except Exception as e:
                #print(e)
                isok=False
        elif restriction=='is_list_lengthGT':
            strlist=self.str_to_list(value)
            try:
                if restrictionval<=len(strlist):
                    isok=False
            except:
                isok=False
        elif restriction=='is_list_lengthLT':
            strlist=self.str_to_list(value)
            try:
                if restrictionval>=len(strlist):
                    isok=False
            except:
                isok=False
        elif restriction=='limited_selection':                        
            try:
                if value not in restrictionval:
                    isok=False
                    log.info("Selection '{}' not in permitted list: {}".format(value,restrictionval))                
            except:                
                isok=False
        elif restriction=='is_list_item_limited_selection':                        
            try:
                if self.is_list(value)==False:
                    alist=self.str_to_list(value)
                else:
                    alist=value
                for aval in alist:
                    if aval not in restrictionval:
                        isok=False
                        log.info("Selection '{}' not in permitted list: {}".format(aval,restrictionval))                                        
            except:                
                isok=False
        elif restriction=='is_list_item_format':                        
            try:
                if self.is_list(value)==False:
                    alist=self.str_to_list(value)
                else:
                    alist=value
                for aval in alist:
                    if aval!='':
                        try:
                            rema=re.search(restrictionval,aval)              
                            if rema.group()!=None:
                                isok=True
                        except:
                            isok=False
                            break                                        
            except:                
                isok=False
        elif restriction=='is_list_item_value_LT':
            try:
                if self.is_list(value)==False:
                    alist=self.str_to_list(value)
                else:
                    alist=value
                for aval in alist:                    
                    val=float(aval)            
                    if restrictionval<=val:                                      
                        isok=False
                        log.info("Selection '{}' not in permitted list: {}".format(aval,restrictionval))                                        
            except:                
                isok=False            
        elif restriction=='is_list_item_value_GT':
            try:
                if self.is_list(value)==False:
                    alist=self.str_to_list(value)
                else:
                    alist=value
                for aval in alist:                    
                    val=float(aval)            
                    if restrictionval>=val:                                      
                        isok=False
                        log.info("Selection '{}' not in permitted list: {}".format(aval,restrictionval))                                        
            except:                
                isok=False            
        elif restriction=='is_list_item_value_EQ':
            try:
                if self.is_list(value)==False:
                    alist=self.str_to_list(value)
                else:
                    alist=value
                for aval in alist:                    
                    val=float(aval)            
                    if restrictionval==val:                                      
                        isok=False
                        log.info("Selection '{}' not in permitted list: {}".format(aval,restrictionval))                                        
            except:
                isok=False
        elif restriction=='is_list_item_value_LTEQ':
            try:
                if self.is_list(value)==False:
                    alist=self.str_to_list(value)
                else:
                    alist=value
                for aval in alist:                    
                    val=float(aval)            
                    if restrictionval<val:                                      
                        isok=False
                        log.info("Selection '{}' not in permitted list: {}".format(aval,restrictionval))               
            except:
                isok=False
        elif restriction=='is_list_item_value_GTEQ':
            try:
                if self.is_list(value)==False:
                    alist=self.str_to_list(value)
                else:
                    alist=value
                for aval in alist:                    
                    val=float(aval)            
                    if restrictionval>val:                                      
                        isok=False
                        log.info("Selection '{}' not in permitted list: {}".format(aval,restrictionval))
            except:
                isok=False
        elif restriction=='is_list_item_value_NEQ':
            try:
                if self.is_list(value)==False:
                    alist=self.str_to_list(value)
                else:
                    alist=value
                for aval in alist:                    
                    val=float(aval)            
                    if restrictionval!=val:                                      
                        isok=False
                        log.info("Selection '{}' not in permitted list: {}".format(aval,restrictionval))
            except:
                isok=False              
        elif restriction=='is_format':
            if value!='':
                try:
                    rema=re.search(restrictionval,value)              
                    if rema.group()!=None:
                        isok=True
                except:
                    isok=False
        elif restriction=='is_unique':
            isok=True #None
        elif restriction=='is_not_change':
            isok=False
        elif restriction=='is_value_LT':
            try:
                val=float(value)            
                if restrictionval<=val:                                      
                    isok=False
            except:
                isok=False
        elif restriction=='is_value_GT':
            try:
                val=float(value)                            
                if restrictionval>=val:                                        
                    isok=False
            except:
                isok=False
        elif restriction=='is_value_EQ':
            try:
                val=float(value)            
                if restrictionval==val:                                  
                    isok=False
            except:
                isok=False
        elif restriction=='is_value_LTEQ':
            try:
                val=float(value)            
                if restrictionval<val:                                       
                    isok=False
            except:
                isok=False
        elif restriction=='is_value_GTEQ':
            try:
                val=float(value)            
                if restrictionval>val:                                     
                    isok=False
            except:
                isok=False
        elif restriction=='is_value_NEQ':
            try:
                val=float(value)            
                if restrictionval!=val:                                     
                    isok=False
            except:
                isok=False                
        elif restriction=='is_value_type':
            if restrictionval==str(type(0)):
                try:
                    _=int(value.strip())                        
                    rema=re.search('^[-+]?[0-9]+$',value.strip())
                    if rema:
                        isok=True
                    else:
                        isok=False                    
                except:
                    isok=False
            elif restrictionval==str(type(0.1)):
                try:
                    _=float(value.strip())                                            
                except:
                    isok=False
            elif restrictionval==str(type(True)):
                try:
                    ans=self.str_to_bool_or_none(value.strip()) 
                    if ans==None:
                        isok=False
                except:
                    isok=False
            else:
                isok=self.check_type(restrictionval,value.strip(),isok)                      

        return isok

    def get_mask_for_item(self,track):
        maskstruct=self.Data_Struct_mask
        if len(maskstruct)==0:
            return {}
        maskdict=maskstruct[0]
        ttt_track=track.copy()
        count=0
        new_track=[]
        mask={}
        while len(ttt_track)>0:        
            if count==0: #skip Data id
                ttt_track.pop(0)
            else:   
                tr=ttt_track[0]
                ttt_track.pop(0)
                new_track.append(tr)
                try:
                    val=self.get_tracked_value_in_struct(new_track,maskdict) 
                except:
                    val=None
                    pass
                if val==None:
                    last=len(new_track)-1
                    new_track.pop(last)
                    new_track.append('__any__')
                    try:
                        val=self.get_tracked_value_in_struct(new_track,maskdict)
                    except:
                        val=None
                        pass
                    if val==None:
                        mask={}
                        break
                if type(val)==dict:
                    klist=self.get_dict_key_list(val)
                    if '__m__' in klist:
                        mask=val
                        break
            count=count+1
        return mask

    def check_item_by_type(self,index,val,old_val,isok=True):
        if isinstance(index,QtCore.QModelIndex):
            mycol=index.column()
            myrow=index.row()
        
        tcol=self.get_item_column_pos_in_table('Type')   
        indextype=index.siblingAtColumn(tcol)
        typeitem=self.tablewidgetobj.itemFromIndex(indextype)
        the_type=typeitem.text()
        #print('item type', the_type)
        return self.check_type(the_type,val,isok)

    def check_type(self,the_type,val,isok=True):
        if the_type==str(type(0)):
            try:
                res=int(val)
            except:
                isok=False
                pass
        elif the_type==str(type(True)):
            try:
                ans=self.str_to_bool_or_none(val)
                if ans not in [True,False]:
                    isok=False
            except:
                isok=False
                pass
        elif the_type==str(type(0.1)):
            try:
                res=float(val)
            except:
                isok=False
                pass
        elif the_type==str(type('str')):
            try:
                res=str(val)
            except:
                isok=False
                pass
        elif the_type==str(type({})):
            isok=True
        elif the_type==str(type([])):
            try:
                isok=self.is_list(self.str_to_list(val))                          
            except:
                isok=False
                pass        
        return isok

    def str_to_list(self,astr):        
        try:         
            rema=re.search('^\[(.+,)*(.+)?\]$',astr)              
            if rema.group()!=None:
                sss=astr.strip("[")
                sss=sss.strip("]")                
                sss=sss.replace("'","")#string quotes 
                sss=sss.replace(" ","")#spaces 
                sss=sss.strip() #spaces
                #sss=sss.strip("'")                
                splited=sss.split(",")
                return splited
        except:
            return None
        


    def restore_a_tableWidget_Item(self,index):
        itm = self.tablewidgetobj.itemFromIndex(index)
        #column = itm.column()
        track=self.track_key_Table(self.tablewidgetobj.itemFromIndex(index))        
        value=self.get_tracked_value_in_struct(track,self.Data_Struct)
        print('Restored {} to {}'.format(track,value))   
        itm.setText(str(value))
    

    def Data_importData_to_Table(self,data, modelobj,tablewidgetobj):
        if isinstance(tablewidgetobj,QtWidgets.QTableWidget):
            tablewidgetobj.setRowCount(0)        
            if self.is_list(data):
                for adict in data:            
                    newdict={}
                    try:
                        newdict.update({adict['ID']:adict})
                    except:
                        pass
                    self.dict_to_Table(newdict,modelobj,tablewidgetobj,myparent=None)
                return newdict
            elif self.is_dict(data):            
                self.dict_to_Table(data,modelobj,tablewidgetobj,myparent='Data')  
        else:
            raise Exception('tableWidget object is Not a {} object'.format(type(QtWidgets.QTableWidget)))      

    
    def Create_Data_Model_tableWidget(self,tableWidgetparent,emitsignal=False):
        if isinstance(tableWidgetparent,QtWidgets.QTableWidget):                    
            if self.is_dict(self.Show_dict)==True:
                data_dict=self.Show_dict
                colcount=len(data_dict)
            else:
                data_dict=self.get_standard_dict_model()
                colcount=0
            tableitems=[]                
            tableitems=self.get_table_item_list(data_dict)        
            #Set Item,Value and Type to all items, set all dict entries to all items
            data_dict,tableitems=self.get_minimumreqs_in_dict(data_dict,tableitems)        
            self.Show_dict=data_dict
            self.tableitems=tableitems
            self.set_tracked_value_to_dict(self.Reftrack,data_dict,self.Data_Struct,subtype='',emitsignal=emitsignal)

            rowcount=len(tableitems)
            #Row count
            tableWidgetparent.setRowCount(rowcount) 
            #Column count
            tableWidgetparent.setColumnCount(colcount)            
            model=tableWidgetparent.model()
            for iii,t_item in enumerate(tableitems):
                model.setHeaderData(iii,QtCore.Qt.Horizontal,t_item)        
            #tableWidgetparent.setModel(model)        
            return model
        return None
    
    def get_minimumreqs_in_dict(self,data_dict,tableitems):                
        if len(tableitems)==0:        
            if 'Value' not in tableitems:
                tableitems.append('Value')        
        tableitemsnivt=[]        
        for tbi in tableitems:            
            tableitemsnivt.append(tbi)        
        new_d_dict={}
        for iii,data in enumerate(data_dict):   
            nd={}
            ddd=data_dict[data]            
            items=self.get_dict_key_list(ddd)                          
            
            for itm in tableitemsnivt:
                if itm not in items:                            
                    nd.update({itm:''})
                else:
                    nd.update({itm:ddd[itm]})
            
            new_d_dict.update({data:nd})                    
        new_d_items=self.get_table_item_list(new_d_dict)        
        return new_d_dict,new_d_items

    def get_table_item_list(self,new_d_dict,positem=0):
        new_d_items=[]
        if len(new_d_dict)>0:
            ndl=self.get_dict_key_list(new_d_dict)
            new_d_items=self.get_dict_key_list(new_d_dict[ndl[positem]])
        return new_d_items
    
    def get_item_column_pos_in_table(self,item):
        for iii,itm in enumerate(self.tableitems):
            if itm==item:
                return iii
        return None

    def dict_to_Table(self,adict,modelobj,tablewidgetobj,myparent=None): 
        #print('Entered dict to table {}'.format(adict))     
        if isinstance(tablewidgetobj,QtWidgets.QTableWidget):                    
            if self.is_dict(adict)==True:                                         
                key_list=self.get_dict_key_list(adict)
                if myparent==None:                                                            
                        parent = 'Data'                             
                        if parent in key_list:
                            self.dict_to_Table(adict[parent],modelobj,tablewidgetobj,myparent=parent)  
                        return
                else:                
                    parent=myparent
                
                #Row count
                tablewidgetobj.setRowCount(len(key_list))         
                #Column count
                tablewidgetobj.setColumnCount(len(self.tableitems)) 
                #Set header labels
                tablewidgetobj.setHorizontalHeaderLabels(self.tableitems)
                tablewidgetobj.setVerticalHeaderLabels(key_list)
                #tablewidgetobj.horizontalHeader().clicked.connect(lambda: self.horizontalheaderclicked)          
                #tablewidgetobj.verticalHeader().clicked.connect(lambda: self.verticalheaderclicked) 
                rowpos=0
                for akey in key_list:                                        
                    table_line=adict[akey]                        
                    #val_item=table_line['Item']
                    #val_value =table_line['Value']
                    #val_type=str(type(val_value))
                    for ttt in self.tableitems:
                        val_=table_line[ttt]
                        #if ttt =='Type':
                        #    val_=val_type                        
                        at_item= QtWidgets.QTableWidgetItem(str(val_))
                        colpos =self.get_item_column_pos_in_table(ttt)                        
                        #print('{} set -> {},row={},col={}'.format(akey,val_,rowpos,colpos))
                        #set the item into table
                        tablewidgetobj.setItem(rowpos,colpos,at_item)
                        tablewidgetobj.resizeColumnToContents(colpos)
                        if self.str_to_bool_or_none(val_) in [True,False]:                                                        
                            if self.is_bool(val_)==True:                                   
                                self.set_checkbox_value(at_item)                                                          
                            #Add tooltip text                                                                                              
                        self.set_tooltiptext(at_item)                                                         
                        self.set_icon_to_item(at_item) 
                        self.set_backgroundcolor_to_item(at_item)
                        self.set_widget_to_item(at_item)
                        self.set_rolevalue_to_item(at_item)
                        
                        

                    rowpos=rowpos+1
                modelobj=tablewidgetobj.model()
        else:
            raise Exception('tableWidget object is Not a {} object'.format(type(QtWidgets.QTableWidget)))

    def get_dict_key_list(self,dict):
        alist=[]
        for key in dict:
            alist.append(key)
        return alist
    
    def is_bool(self,var):
        return isinstance(var,bool)

    def is_dict(self,var):
        return isinstance(var,dict)

    def is_list(self,var):
        return isinstance(var,list)
        
    def get_tracked_value_in_struct(self,track,Data_Struct):
        trlist=track.copy()
        selected={}
        if len(track)==0:
            return None
        if self.is_list(Data_Struct)==True:
            for aData in Data_Struct:
                if aData['ID']==trlist[0]:
                    trlist.pop(0)
                    selected=aData #select dictionary
                    while len(trlist)>1:
                        selected=selected[trlist[0]]
                        trlist.pop(0)
                    #last tracked is variable   
                    if len(trlist)==1:                 
                        #print ('get tracked value list',trlist[0],selected[trlist[0]])             
                        return selected[trlist[0]]                    
        elif self.is_dict(Data_Struct)==True:
            selected=Data_Struct #select dictionary
            while len(trlist)>1:
                selected=selected[trlist[0]]
                trlist.pop(0)                
            #last tracked is variable              
            if len(trlist)==1: 
                #print ('get tracked value dict',trlist[0],selected[trlist[0]])             
                return selected[trlist[0]]            
        
        return None
    
    def get_dict_max_depth(self,adict,depth=0,maxdepth=0):         
        if self.is_dict(adict)==False and self.is_list(adict)==True and depth==0:     
            for iii in adict:       
                adepth=self.get_dict_max_depth(iii,0)
                if depth>=maxdepth:
                    maxdepth=adepth            
        else:            
            alist=self.get_dict_key_list(adict)                                     
            for item in alist:                  
                resdict=adict[item]            
                if self.is_dict(resdict)==True:                
                    adepth=self.get_dict_max_depth(resdict,depth+1,maxdepth)                           
                    if adepth>=maxdepth:
                        maxdepth=adepth
                if depth>=maxdepth:
                    maxdepth=depth
        return maxdepth


    
        






