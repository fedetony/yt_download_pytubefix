"""
Class to handle a QTableWidget Object
Programmed by F.Garcia
"""

import logging
from PyQt5 import QtCore, QtWidgets
import re

import class_check_restrictions

# set up logging to file - see previous section for more details
log = logging.getLogger("")  # root logger
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s [%(levelname)s] (%(threadName)-10s) %(message)s", datefmt="%y-%m-%d %H:%M"
)
# define a Handler which writes INFO messages or higher to the sys.stderr
twconsole = logging.StreamHandler()
twconsole.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter("[%(levelname)s] (%(threadName)-10s) %(message)s")
# tell the handler to use this format
twconsole.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger("").addHandler(twconsole)


class TableWidgetFunctions(QtWidgets.QWidget):
    """
    Class to handle a QTableWidget Object
    Receives:
    data_struct: dictionary of with structure:
    Basic data_struct is a Show_Struct:
    Show_Struct= {
    "row1":{"Col1":ValueCol1,"Col2":ValueCol2},
    "row2":{"Col1":ValueCol1,"Col3":ValueCol3}, # No need to have all Columns
    ....
    }
    data_struct_mask must have same structure as the Show_struct,
    It contains the restrictions of each column or item.
    Notes:
    - row,col names/keys must match to apply restriction
    - if no mask no restriction.
    data_struct_mask:{ # Same as show_Struct
    "__any__":{ #For all rows
            "Col1":{
            '__m__':"desired_restriction1",'__mv__':restriction_value1,...
            ,'__m__N':"desired_restrictionN",'__mv__N':restriction_valueN}
            }
            "Col2":{
            '__m__':"desired_restriction1",'__mv__':restriction_value1,...
            ,'__m__N':"desired_restrictionN",'__mv__N':restriction_valueN}
            }
            ...
        }
    "row3": :{ #For row 3 only

            "Col3":{
            '__m__':"desired_restriction1",'__mv__':restriction_value1,...
            ,'__m__N':"desired_restrictionN",'__mv__N':restriction_valueN}
            }
            ...
        }
    }
    If the show_struct is contained in a data_struct, pass the reference_track
    data_struct={
    Item1:{
            "Whatever":"",
            ...
            "Data_you_want_to_show": Show_Struct
            }
    ...

    }
    reference_track references the data_struct to the place you want to show the info and allows to
    read/write values in the correspondent part of the structure, but just showing the
    Data_you_want_to_show in the TableWidget
    reference_track=["Item1" "Data_you_want_to_show"]

    data_id=Is the root item of your data_struct.

    If data_struct is a list like ->
    [data_struct1,data_struct2...]
    Each data_structX must contain an unique 'ID' key.
    data_struct1={
    'ID': "Id1"
    Item1:{
            "Whatever":"",
            ...
            "Data_you_want_to_show": Show_Struct
            }
    ...
    Then
    data_id= "Id1"
    and
    reference_track=["Id1" "Item1" "Data_you_want_to_show"]
    """

    data_change = QtCore.pyqtSignal(list, str, str, str)
    item_button_clicked = QtCore.pyqtSignal(list)
    item_combobox_currentIndexChanged = QtCore.pyqtSignal(int, str, list)
    item_doubleclicked = QtCore.pyqtSignal(list)
    item_checkbox_checked = QtCore.pyqtSignal(bool, list)

    def __init__(
        self,
        tablewidgetobj,
        data_struct: any,
        data_struct_mask: dict,
        data_id: str = None,
        reference_track: list[str] = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.__name__ = "tableWidget Functions"
        if isinstance(tablewidgetobj, QtWidgets.QTableWidget):
            self.tablewidgetobj = tablewidgetobj
        else:
            raise Exception("tableWidget object is Not a {} object".format(type(QtWidgets.QTableWidget)))
        self.data_struct = data_struct  # all info
        self.data_struct_mask = data_struct_mask
        self._last_value_selected = None
        self.data_id = data_id
        if reference_track:
            self.reference_track = reference_track
        else:
            self.reference_track = []
        # Set restriction checker
        self.check_restrictions = class_check_restrictions.CheckRestrictions()
        # displayed on tableWidget
        self.set_show_dict()
        # uses show dict
        self.modelobj = self.Create_Data_Model_tableWidget(self.tablewidgetobj, False)
        self.data_struct_types = self.get_types_struct(self.data_struct)
        self.show_dict_types = self.get_types_struct(self.show_dict)
        self.set_ItemIcons()
        self.set_ItemBackgroundColor()
        self.set_ItemTooltips()
        self.set_ItemWidget()
        self.set_Itemrolevalue()

        self.restore_column_list = []
        self.restore_key_list = []
        self.resizetocontents = True
        # print(self.show_dict_types)
        self.refresh_tableWidget(self.show_dict, self.modelobj, self.tablewidgetobj)
        # connect action
        self.tablewidgetobj.clicked.connect(self.tablewidget_onclick)

    def signal_data_change(self, track: list[str], val: any, valtype: str, subtype: str):
        """Emits event data has changed and new value to parent

        Args:
            track (list[str]): Tracking list with path to follow in dictionary structure
            val (any): value on item
            valtype (str): string with value type
            subtype (str): if list inner value type
        """
        self.data_change.emit(track, val, valtype, subtype)

    def doubleclick_on_item(self, itm: QtWidgets.QTableWidgetItem):
        """Emits doubleclick event on item, passes track list of item

        Args:
            itm (QtWidgets.QTableWidgetItem): item being doubleclicked
        """
        track = self.get_track_of_item_in_table(itm)
        self.item_doubleclicked.emit(track)

    def get_standard_dict_model(self, fieldname: str = "Datafield_1") -> dict:
        """Make a typical show dictionay

        Args:
            fieldname (str, optional): First row content value. Defaults to 'Datafield_1'.

        Returns:
            dict: Contains 'Value','Units','Info','Type' example columns
        """
        return {fieldname: {"Value": "", "Units": "", "Info": "", "Type": str(type(""))}}

    def set_restore_columns(self, colkey):
        for iii, ti in enumerate(self.tableitems):
            if colkey == ti:
                self.restore_key_list.append(colkey)
                self.restore_column_list.append(iii)

    def set_show_dict(self):
        if len(self.reference_track) == 0:
            showdict = self.get_dictionary_from_structlist(self.data_struct, self.data_id)
            # print('From len 0 showdict:\n',showdict)
        else:
            showdict = self.get_tracked_value_in_struct(self.reference_track, self.data_struct)
            # print('From else showdict:\n',showdict)
        if isinstance(showdict, dict):
            self.show_dict = showdict
        else:
            self.show_dict = self.data_struct

    def get_types_struct(self, dict_struct):
        if isinstance(dict_struct, list):
            type_Struct = []
            for aData in dict_struct:
                type_Struct.append(self.get_types_struct(aData))
        elif isinstance(dict_struct, dict):
            type_Struct = {}
            for aData in dict_struct:
                if isinstance(dict_struct[aData], dict):
                    nts = self.get_types_struct(dict_struct[aData])
                    type_Struct.update({aData: nts})
                else:
                    type_Struct.update({aData: str(type(dict_struct[aData]))})
        else:
            type_Struct = {}
            type_Struct.update({str(dict_struct): str(type(dict_struct))})

        return type_Struct

    def get_gentrack_from_localtrack(self, track: list):
        gentrack = self.reference_track.copy()
        for iii in track:
            gentrack.append(iii)
        return gentrack

    def get_localtrack_from_gentrack(self, track: list):
        gentrack = self.reference_track.copy()
        trackc = track.copy()
        for iii in track:
            if track[iii] == gentrack[iii]:
                trackc.pop(0)
        return trackc

    def get_dictionary_from_structlist(self, data_struct, data_id=None) -> dict:
        if isinstance(data_struct, list):
            for adict in data_struct:
                if adict["ID"] == data_id:
                    # print('get my dict Found ID',data_id)
                    return adict.copy()
        elif isinstance(data_struct, dict) or data_id is None:
            # print('get my dict nochange is dict',data_id)
            return data_struct.copy()
        else:
            return {}

    def refresh_tableWidget(self, data_dict, modelobj, tablewidgetobj):
        if isinstance(tablewidgetobj, QtWidgets.QTableWidget):
            self.set_show_dict()
            tablewidgetobj.setRowCount(0)
            modelobj = self.Create_Data_Model_tableWidget(tablewidgetobj, False)
            self.Data_importData_to_Table(data_dict, modelobj, tablewidgetobj)
            if self.resizetocontents:
                tablewidgetobj.resizeColumnsToContents()
            # self.set_tableWidget_styles(tablewidgetobj.model())
        else:
            raise Exception("tableWidget object is Not a {} object".format(type(QtWidgets.QTableWidget)))

    def set_item_style(self, itm: QtWidgets.QTableWidgetItem):
        self.set_icon_to_item(itm)
        self.set_backgroundcolor_to_item(itm)
        self.set_rolevalue_to_item(itm)

    def set_ItemTooltips(self, tooltipict: dict = {"track_list": [], "tooltip_list": []}) -> None:
        self.tooltip_dict = tooltipict

    def set_ItemIcons(self, icondict: dict = {"track_list": [], "icon_list": []}) -> None:
        self.icon_dict = icondict

    def set_ItemBackgroundColor(self, backgroundcolor_dict: dict = {"track_list": [], "color_list": []}) -> None:
        self.backgroundcolor_dict = backgroundcolor_dict

    def set_ItemWidget(self, itemwidget_dict: dict = {"track_list": [], "widget_list": []}) -> None:
        self.itemwidget_dict = itemwidget_dict

    def set_Itemrolevalue(self, rolevalue_dict: dict = {"track_list": [], "role_list": [], "value_list": []}) -> None:
        self.itemrolevalue_dict = rolevalue_dict

    def is_same_list(self, list1: list, list2: list) -> bool:
        """Compares two lists

        Args:
            list1 (list): list1
            list2 (list): list2

        Returns:
            bool: True if the same,False if different
        """
        if len(list1) != len(list2):
            return False
        for iii, jjj in zip(list1, list2):
            if iii != jjj:
                return False
        return True

    def itembuttonclicked(self, track: list):
        # print('entered click {}'.format(track))
        self.item_button_clicked.emit(track)

    def itemcomboboxindexchanged(self, cbw, track=[]):
        currenttxt = cbw.currentText()
        index = cbw.findText(currenttxt, QtCore.Qt.MatchFixedString)
        self.item_combobox_currentIndexChanged.emit(index, currenttxt, track)

    def itemcheckboxchecked(self, chb, track=[]):
        currentstate = chb.isChecked()
        self.item_checkbox_checked.emit(currentstate, track)

    def set_widget_to_item(self, itm: QtWidgets.QTableWidgetItem):
        try:
            track = self.get_track_of_item_in_table(itm)
            track_list = self.itemwidget_dict["track_list"]
            widget_list = self.itemwidget_dict["widget_list"]
            for tr, iw in zip(track_list, widget_list):
                if self.is_same_list(track, tr):

                    self.tablewidgetobj.setCellWidget(itm.row(), itm.column(), iw)
                    # itm.setWidget(iw)
                    itm.setFlags(itm.flags() ^ QtCore.Qt.ItemIsEditable)
                    # print('iw {}'.format(type(iw)))
                    if isinstance(iw, QtWidgets.QPushButton):
                        # print('Connected Buton')
                        iw.clicked.connect(lambda: self.itembuttonclicked(track))
                    elif isinstance(iw, QtWidgets.QComboBox):
                        iw.currentIndexChanged.connect(lambda: self.itemcomboboxindexchanged(iw, track=track))
                    elif isinstance(iw, QtWidgets.QCheckBox):
                        iw.stateChanged.connect(lambda: self.itemcheckboxchecked(iw, track))
                    elif isinstance(iw, QtWidgets.QLabel):
                        # self.tablewidgetobj.itemDoubleClicked.connect(self.doubleclick_on_item)
                        if self.resizetocontents:
                            self.tablewidgetobj.resizeColumnToContents(itm.column())
                            self.tablewidgetobj.resizeRowToContents(itm.row())
                    break
        except Exception as e:
            print("set_widget_to_item error--->", e)
            pass

    def set_icon_to_item(self, itm: QtWidgets.QTableWidgetItem):
        try:
            track = self.get_track_of_item_in_table(itm)
            track_list = self.icon_dict["track_list"]
            icon_list = self.icon_dict["icon_list"]
            for tr, ic in zip(track_list, icon_list):
                if self.is_same_list(track, tr):
                    itm.setIcon(ic)
        except:
            pass

    def set_rolevalue_to_item(self, itm: QtWidgets.QTableWidgetItem):
        try:
            track = self.get_track_of_item_in_table(itm)
            track_list = self.itemrolevalue_dict["track_list"]
            role_list = self.itemrolevalue_dict["role_list"]
            value_list = self.itemrolevalue_dict["value_list"]
            for tr, role, value in zip(track_list, role_list, value_list):
                if self.is_same_list(track, tr):
                    itm.setData(role, value)
        except:
            pass

    def set_backgroundcolor_to_item(self, itm: QtWidgets.QTableWidgetItem):
        try:
            track = self.get_track_of_item_in_table(itm)
            track_list = self.backgroundcolor_dict["track_list"]
            color_list = self.backgroundcolor_dict["color_list"]
            for tr, ic in zip(track_list, color_list):
                if self.is_same_list(track, tr):
                    itm.setBackground(ic)
        except:
            pass

    def set_tooltiptext(self, itm: QtWidgets.QTableWidgetItem):
        reslist, resvallist = self.get_item_restriction_resval(itm)
        for res, resval in zip(reslist, resvallist):
            if res in ["limited_selection", "is_list_item_limited_selection"]:
                itm.setToolTip("Options: {}".format(resval))
        try:
            track = self.get_track_of_item_in_table(itm)
            track_list = self.tooltip_dict["track_list"]
            tooltip_list = self.tooltip_dict["tooltip_list"]
            for tr, itt in zip(track_list, tooltip_list):
                if self.is_same_list(track, tr):
                    itm.setToolTip(itt)
        except:
            pass

    def tablewidget_onclick(self, index: QtCore.QModelIndex):
        """Onclick method on table widget restores or edits the item

        Args:
            index (QtCore.QModelIndex): Item being clicked
        """
        mycol = index.column()

        if self.resizetocontents:
            self.tablewidgetobj.resizeColumnToContents(mycol)
        itm = self.tablewidgetobj.itemFromIndex(index)
        self.set_icon_to_item(itm)
        self.set_widget_to_item(itm)
        self.set_tooltiptext(index)
        if mycol in self.restore_column_list:
            self.restore_a_tableWidget_Item(index)
        else:
            val_ = itm.text()
            if self.check_restrictions.str_to_bool_or_none(val_) in [True, False]:
                self.set_checkbox_value(itm)
            self.edit_a_table_widget_item(index)

    def set_checkbox_value(self, valueitem: QtWidgets.QTableWidgetItem):
        """Sets checkstate on checkbox when item is a boolean

        Args:
            valueitem (QtWidgets.QTableWidgetItem): Item
        """
        if self.check_restrictions.str_to_bool(valueitem.text()):
            valueitem.setCheckState(True)
        else:
            valueitem.setCheckState(False)

    def get_item_from_colpos(self, colpos):
        for iii in self.tableitems:
            cp = self.get_item_column_pos_in_table(iii)
            if cp == colpos:
                return iii
        return None

    def get_key_value_from_item(self, anitem: QtWidgets.QTableWidgetItem):
        """Gets the dictionary key for an item

        Args:
            anitem (QtWidgets.QTableWidgetItem): item in table

        Returns:
            _type_: key on dictionary related to the row the item is in
        """
        myrow = anitem.row()
        return self.get_key_value_from_row(myrow)

    def get_key_value_from_row(self, myrow: int):
        """Gets the dictionary key located in the row

        Args:
            myrow (int): row number

        Returns:
            any: key on dictionary related to the row
        """
        for iii, key in enumerate(self.show_dict):
            if iii == myrow:
                return key

    def get_track_of_item_in_table(self, anitem: QtWidgets.QTableWidgetItem) -> list:
        """Generates a track list of the item in the structure

        Args:
            anitem (QtWidgets.QTableWidgetItem): item object to be tracked

        Returns:
            list: track list of item
        """
        track = self.reference_track.copy()
        if isinstance(anitem, QtWidgets.QTableWidgetItem):
            myrow = anitem.row()
            mycol = anitem.column()
            valkey = self.get_key_value_from_row(myrow)
            track.append(valkey)
            track.append(self.get_item_from_colpos(mycol))
        return track

    def edit_a_table_widget_item(self, index):
        # print('edit_a_table_widget_item',index)
        itm = self.tablewidgetobj.itemFromIndex(index)
        val = itm.text()
        # print('edit index set:',index.data())
        self._last_value_selected = val
        self.tablewidgetobj.itemChanged.connect(lambda: self.Item_data_changed(index, val))

    # def get_list_of_tracks_of_children(self, parenttrack):
    #    self.get_gentrack_from_localtrack

    def get_item_from_track(self, modelobj: QtCore.QAbstractItemModel, track: list) -> None:
        """Get an item object and all related info

        Args:
            modelobj (QtCore.QAbstractItemModel): Table widget model object
            track (list): where is the item located track

        Returns:
            QtWidgets.QTableWidgetItem: Item
            QtCore.QModelIndex: Item index
            list: item track list
            list: track list of indexes

        """
        try:
            itmtrack = []
            itmindextrack = []
            parent = None
            for tr in track:
                if parent is None:
                    # log.info('the size -> {}'.format(modelobj.rowCount()))
                    for iii in range(modelobj.rowCount()):
                        itmindex = modelobj.index(iii, 0)
                        itm = modelobj.itemFromIndex(itmindex)
                        if itm is not None:
                            # log.info('got this-> {} search for {}'.format(itm.text(),tr))
                            if tr == itm.text():
                                break
                        else:
                            break
                    if itm is None:
                        break
                    if tr != itm.text():  # not found
                        break
                else:
                    # log.info('the size -> {}'.format(modelobj.rowCount(parent)))
                    for iii in range(modelobj.rowCount(parent)):
                        itmindex = modelobj.index(iii, 0, parent)
                        itm = modelobj.itemFromIndex(itmindex)
                        if itm is not None:
                            # log.info('parent got this-> {} search for {}'.format(itm.text(),tr))
                            if tr == itm.text():
                                break
                        else:
                            break
                    if itm is None:
                        break
                    if tr != itm.text():  # not found
                        break
                parent = itmindex
                parentitm = modelobj.itemFromIndex(parent)
                if parentitm.text() == "ID":
                    # parenttxt = parentitm.text()
                    parent = None
                    continue
                itmtrack.append(itm)
                itmindextrack.append(itmindex)
            return itm, itmindex, itmtrack, itmindextrack
        except Exception as e:
            log.error("get item from track: {}".format(e))
            return None, None, None, None

    def Item_data_changed(self, index, val):
        if isinstance(index, QtCore.QModelIndex):
            mycol = index.column()
            myrow = index.row()
        old_value = val  # self._last_value_selected
        # print('tvf Item changed->',index.data(),' old value->',old_value)
        itm = self.tablewidgetobj.itemFromIndex(index)
        new_value = itm.text()
        selindex = self.tablewidgetobj.selectedIndexes()
        # icol=self.get_item_column_pos_in_table('Item')
        # tcol=self.get_item_column_pos_in_table('Type')
        # self.set_item_style(self.tablewidgetobj.item(itm.row(),icol)) # column item
        if new_value != old_value and old_value is not None and index in selindex:
            # indextype=index.siblingAtColumn(tcol)
            # typeitem=self.tablewidgetobj.itemFromIndex(indextype)
            track = self.get_track_of_item_in_table(self.tablewidgetobj.itemFromIndex(index))
            # Here check if value is ok if yes
            valisok = self.check_item_value_for_edit(index, new_value, old_value, self.show_dict)
            log.info("Data changed -> New:{} Old:{} Track: {} isvalid: {}".format(new_value, old_value, track, valisok))
            if valisok == True:
                subtype = ""
                # if self.is_item_supposed_to_be_a_list(itm)==True:
                # gentrack=self.get_gentrack_from_localtrack(track)
                #    subtype=self.get_listitem_subtype(track)#gentrack)
                thetype, subtype = self.get_item_supposed_type_subtype(itm)
                new_valwt = self.set_type_to_value(
                    new_value, thetype, subtype
                )  # Send value with correct type to dictionary
                # _=self.set_tracked_value_to_dict(gentrack,new_valwt,self.data_struct,subtype,False) #doing it inside
                refreshtableWidget, self.show_dict = self.set_tracked_value_to_dict(
                    track, new_valwt, self.show_dict, subtype
                )
                if refreshtableWidget == False:
                    itm.setText(new_value)
                    if thetype == str(type(True)):
                        self.set_checkbox_value(itm)
                else:
                    self.refresh_tableWidget(
                        self.show_dict, self.modelobj, self.tablewidgetobj
                    )  # need to refresh only if value is changed
                # Here send signal to refresh
                self.signal_data_change(track, new_value, thetype, subtype)
            else:
                subtype = ""
                thetype, subtype = self.get_item_supposed_type_subtype(itm)
                typestr = thetype
                if typestr == str(type([])):
                    gentrack = self.get_gentrack_from_localtrack(track)  # <-track is local!
                    subtype = self.get_listitem_subtype(gentrack)
                old_valwt = self.set_type_to_value(
                    old_value, thetype, subtype
                )  # Send value with correct type to dictionary
                refreshtableWidget, self.show_dict = self.set_tracked_value_to_dict(
                    track, old_valwt, self.show_dict, subtype
                )
                itm.setText(old_value)
                if thetype == str(type(True)):
                    self.set_checkbox_value(itm)
        # reset old value
        self._last_value_selected = None

    def is_item_supposed_to_be_a_list(self, itm):
        reslist, resvallist = self.get_item_restriction_resval(itm)
        for res, resval in zip(reslist, resvallist):
            if "is_list_item_" in res or (res == "is_value_type" and resval == str(type([]))):
                return True
        return False

    def horizontalheaderclicked(self, index):
        print("horizontal", index)

    def verticalheaderclicked(self, index):
        print(index)

    def get_item_supposed_type_subtype(self, itm):
        subtype = ""
        thetype = str(type(""))
        reslist, resvallist = self.get_item_restriction_resval(itm)
        if self.is_item_supposed_to_be_a_list(itm) == False:
            for res, resval in zip(reslist, resvallist):
                if res == "is_value_type":
                    thetype = resval
                    break
        else:
            thetype = str(type([]))
            for res, resval in zip(reslist, resvallist):
                if res == "is_list_item_type":
                    subtype = resval
                    break
        return thetype, subtype

    def get_listitem_subtype(self, track):
        mask = self.get_mask_for_item(track)
        # log.info('Got for subtype: {} {}'.format(track,mask))
        for mmm in mask:
            keymmm = str(mmm)
            if "__m__" in keymmm:
                keyval = keymmm.replace("__m__", "__mv__")
                if mask[keymmm] == "is_list_item_type":
                    return mask[keyval]
        return ""

    def set_type_to_value(self, val, typestr, subtype=""):
        if typestr == str(type(1)):
            try:
                tyval = int(val)
            except:
                tyval = str(val)
        elif typestr == str(type(0.1)):
            try:
                tyval = float(val)
            except:
                tyval = str(val)
        elif typestr == str(type(True)):
            try:
                if val in ["1", "True", "true", "yes", "Yes"]:
                    tyval = True
                elif val in ["0", "False", "false", "no", "No"]:
                    tyval = False
                else:
                    tyval = int(val)
            except:
                tyval = str(val)
        elif typestr == str(type([])):
            try:
                split = self.str_to_list(val)
                if split is not None:
                    tyval = []
                    for iii in split:
                        if subtype == str(type(0.1)):
                            iiival = float(iii)
                        elif subtype == str(type(0)):
                            iiival = int(iii)
                        elif subtype == str(type("")):
                            iiival = str(iii)
                        else:
                            iiival = iii
                        tyval.append(iiival)
                else:
                    tyval = str(val)
            except:
                tyval = str(val)
        else:
            tyval = str(val)
        return tyval

    def set_tracked_value_to_dict(self, track, val, dict_struct, subtype, emitsignal=True):
        refreshtableWidget = False
        trlist = track.copy()
        selected = {}
        if isinstance(dict_struct, list):
            for aData in dict_struct:
                if aData["ID"] == trlist[0]:
                    trlist.pop(0)
                    selected = aData  # .copy() #select dictionary
                    while len(trlist) > 1:
                        try:
                            selected = selected[trlist[0]]
                            trlist.pop(0)
                        except:
                            break
                    # last tracked is variable
                    if len(trlist) == 1:
                        selected.update({trlist[0]: val})
                        # Change title of Data special case
                        # log.debug('setvaltodict_struct Here {} set to {}'.format(trlist[0],val))
                        if trlist[0] == "ID" and len(track) == 2:
                            refreshtableWidget = True
                        if emitsignal == True:
                            trackstruct = track
                            self.signal_data_change(trackstruct, str(val), str(type(val)), subtype)  # refresh on main
                        break
        elif isinstance(dict_struct, dict):
            selected = dict_struct  # .copy() #select dictionary
            while len(trlist) > 1:
                try:
                    selected = selected[trlist[0]]
                    trlist.pop(0)
                except:
                    break
            # last tracked is variable
            if len(trlist) == 1:
                selected.update({trlist[0]: val})
                # log.debug('setvaltodict_dict Here {} set to {}'.format(trlist[0],val))
                # update
                trackstruct = track.copy()
                _, self.data_struct = self.set_tracked_value_to_dict(trackstruct, val, self.data_struct, subtype)
                if emitsignal == True:
                    self.signal_data_change(trackstruct, str(val), str(type(val)), subtype)  # refresh on main
        return refreshtableWidget, dict_struct

    def get_track_struct_from_dict_track(self, dict_, track):
        if isinstance(dict_, dict):
            if self.data_id is not None:
                endtrack = [self.data_id].append(track)
                # print ('ini_track->',track,'endtrack->',endtrack)
                return endtrack
        return track

    def check_item_value_for_edit(self, index, val: any, isok=True) -> bool:
        """Check that the new value is conform to restrictions

        Args:
            index (_type_): index of item on TableWidget
            val (any): Value to be set
            isok (bool, optional): Result of previous checks. Defaults to True.

        Returns:
            bool: True if New Value conforms restrictions, False does not conform Restrictions
        """
        # No need to check type in table, inside mask

        isok = self.check_item_by_mask(index, val, isok)
        # print('bymask isok=',isok)
        log.debug("bymask isok={}".format(isok))
        return isok

    def get_item_restriction_resval(self, itm):
        track = self.get_track_of_item_in_table(itm)
        itmmask = self.get_mask_for_item(track)
        if itmmask == {}:
            itmmask = self.get_mask_for_item(self.get_gentrack_from_localtrack(track))
        reslist = []
        resvallist = []
        if len(itmmask) > 0:
            for mmm in itmmask:
                keyname = str(mmm)
                if "__m__" in keyname:
                    keyval = keyname.replace("__m__", "__mv__")
                    restriction = itmmask[keyname]
                    restrictionval = itmmask[keyval]
                    reslist.append(restriction)
                    resvallist.append(restrictionval)
        return reslist, resvallist

    def check_item_by_mask(self, index, val, isok=True) -> bool:
        """Checks a TableWidget Item value is conform with restrictions masks

        Args:
            index (QtCore.QModelIndex): Index of element of table
            val (_type_): Value desired to be set
            isok (bool, optional): Previous/other checks results. Defaults to True.

        Returns:
            bool: True if value is ok with the mask restrictions.
        """
        # Here to add specific value ranges,formats for example
        # like if list can have more items or if axis has to be only X or Y
        # if isinstance(index, QtCore.QModelIndex):
        #     mycol = index.column()
        #     myrow = index.row()
        # tcol=self.get_item_column_pos_in_table('Type')
        # indextype=index.siblingAtColumn(tcol)
        # typeitem=indextype.model().itemFromIndex(indextype)
        itm = self.tablewidgetobj.itemFromIndex(index)
        track = self.get_track_of_item_in_table(itm)
        itmmask = self.get_mask_for_item(track)
        if itmmask == {}:
            itmmask = self.get_mask_for_item(self.get_gentrack_from_localtrack(track))
        # print(self.data_struct_mask)
        print("Masked Track:", track, "Mask:", itmmask)
        # value=self.get_tracked_value_in_struct(track,data_struct)
        # print('Tracked value:',value)
        if len(itmmask) > 0:
            for mmm in itmmask:
                keyname = str(mmm)
                if "__m__" in keyname:
                    keyval = keyname.replace("__m__", "__mv__")
                    restriction = itmmask[keyname]
                    restrictionval = itmmask[keyval]
                    # print('Check restriction',restriction,'---->',restrictionval)
                    isok = self.check_restrictions.checkitem_value_with_mask(restriction, restrictionval, val)
                    if restriction == "is_unique" and "ID" in track:
                        idlist = self.get_ID_list()
                        if val in idlist:
                            isok = False
                    if isok == False:
                        log.info("{} {} returned False".format(track, keyname))
                        break
        return isok

    def get_ID_list(self):
        IDlist = []
        for aaa in self.data_struct:
            IDlist.append(aaa["ID"])
        return IDlist

    def get_mask_for_item(self, track):
        maskstruct = self.data_struct_mask
        if len(maskstruct) == 0:
            return {}
        maskdict = maskstruct[0]
        ttt_track = track.copy()
        count = 0
        new_track = []
        mask = {}
        while len(ttt_track) > 0:
            if count == 0:  # skip Data id
                ttt_track.pop(0)
            else:
                tr = ttt_track[0]
                ttt_track.pop(0)
                new_track.append(tr)
                try:
                    val = self.get_tracked_value_in_struct(new_track, maskdict)
                except:
                    val = None
                    pass
                if val is None:
                    last = len(new_track) - 1
                    new_track.pop(last)
                    new_track.append("__any__")
                    try:
                        val = self.get_tracked_value_in_struct(new_track, maskdict)
                    except:
                        val = None
                        pass
                    if val is None:
                        mask = {}
                        break
                if isinstance(val, dict):
                    klist = self.get_dict_key_list(val)
                    if "__m__" in klist:
                        mask = val
                        break
            count = count + 1
        return mask

    def str_to_list(self, astr: str) -> list:
        try:
            rema = re.search(r"^\[(.+,)*(.+)?\]$", astr)
            if rema.group() is not None:
                sss = astr.strip("[")
                sss = sss.strip("]")
                sss = sss.replace("'", "")  # string quotes
                sss = sss.replace(" ", "")  # spaces
                sss = sss.strip()  # spaces
                # sss=sss.strip("'")
                splited = sss.split(",")
                return splited
        except AttributeError:
            return None

    def restore_a_tableWidget_Item(self, index):
        itm = self.tablewidgetobj.itemFromIndex(index)
        # column = itm.column()
        track = self.get_track_of_item_in_table(self.tablewidgetobj.itemFromIndex(index))
        value = self.get_tracked_value_in_struct(track, self.data_struct)
        print("Restored {} to {}".format(track, value))
        itm.setText(str(value))

    def Data_importData_to_Table(self, data, modelobj, tablewidgetobj):
        if isinstance(tablewidgetobj, QtWidgets.QTableWidget):
            tablewidgetobj.setRowCount(0)
            if isinstance(data, list):
                for adict in data:
                    newdict = {}
                    try:
                        newdict.update({adict["ID"]: adict})
                    except:
                        pass
                    self.dict_to_Table(newdict, modelobj, tablewidgetobj, myparent=None)
                return newdict
            elif isinstance(data, dict):
                self.dict_to_Table(data, modelobj, tablewidgetobj, myparent="Data")
        else:
            raise Exception("tableWidget object is Not a {} object".format(type(QtWidgets.QTableWidget)))

    def Create_Data_Model_tableWidget(self, tableWidgetparent, emitsignal=False):
        if isinstance(tableWidgetparent, QtWidgets.QTableWidget):
            if isinstance(self.show_dict, dict):
                data_dict = self.show_dict
                colcount = len(data_dict)
            else:
                data_dict = self.get_standard_dict_model()
                colcount = 0
            tableitems = []
            tableitems = self.get_table_item_list(data_dict)
            # Set Item,Value and Type to all items, set all dict entries to all items
            data_dict, tableitems = self.get_minimumreqs_in_dict(data_dict, tableitems)
            self.show_dict = data_dict
            self.tableitems = tableitems
            self.set_tracked_value_to_dict(
                self.reference_track, data_dict, self.data_struct, subtype="", emitsignal=emitsignal
            )

            rowcount = len(tableitems)
            # Row count
            tableWidgetparent.setRowCount(rowcount)
            # Column count
            tableWidgetparent.setColumnCount(colcount)
            model = tableWidgetparent.model()
            for iii, t_item in enumerate(tableitems):
                model.setHeaderData(iii, QtCore.Qt.Horizontal, t_item)
            # tableWidgetparent.setModel(model)
            return model
        return None

    def get_minimumreqs_in_dict(self, data_dict, tableitems):
        if len(tableitems) == 0:
            if "Value" not in tableitems:
                tableitems.append("Value")
        tableitemsnivt = []
        for tbi in tableitems:
            tableitemsnivt.append(tbi)
        new_d_dict = {}
        for iii, data in enumerate(data_dict):
            nd = {}
            ddd = data_dict[data]
            items = self.get_dict_key_list(ddd)

            for itm in tableitemsnivt:
                if itm not in items:
                    nd.update({itm: ""})
                else:
                    nd.update({itm: ddd[itm]})

            new_d_dict.update({data: nd})
        new_d_items = self.get_table_item_list(new_d_dict)
        return new_d_dict, new_d_items

    def get_table_item_list(self, new_d_dict, positem=0):
        new_d_items = []
        if len(new_d_dict) > 0:
            ndl = self.get_dict_key_list(new_d_dict)
            new_d_items = self.get_dict_key_list(new_d_dict[ndl[positem]])
        return new_d_items

    def get_item_column_pos_in_table(self, item):
        for iii, itm in enumerate(self.tableitems):
            if itm == item:
                return iii
        return None

    def dict_to_Table(self, adict, modelobj, tablewidgetobj, myparent=None):
        # print('Entered dict to table {}'.format(adict))
        if isinstance(tablewidgetobj, QtWidgets.QTableWidget):
            if isinstance(adict, dict):
                key_list = self.get_dict_key_list(adict)
                if myparent is None:
                    parent = "Data"
                    if parent in key_list:
                        self.dict_to_Table(adict[parent], modelobj, tablewidgetobj, myparent=parent)
                    return
                else:
                    parent = myparent

                # Row count
                tablewidgetobj.setRowCount(len(key_list))
                # Column count
                tablewidgetobj.setColumnCount(len(self.tableitems))
                # Set header labels
                tablewidgetobj.setHorizontalHeaderLabels(self.tableitems)
                tablewidgetobj.setVerticalHeaderLabels(key_list)
                # tablewidgetobj.horizontalHeader().clicked.connect(lambda: self.horizontalheaderclicked)
                # tablewidgetobj.verticalHeader().clicked.connect(lambda: self.verticalheaderclicked)
                rowpos = 0
                for akey in key_list:
                    table_line = adict[akey]
                    # val_item=table_line['Item']
                    # val_value =table_line['Value']
                    # val_type=str(type(val_value))
                    for ttt in self.tableitems:
                        val_ = table_line[ttt]
                        # if ttt =='Type':
                        #    val_=val_type
                        at_item = QtWidgets.QTableWidgetItem(str(val_))
                        colpos = self.get_item_column_pos_in_table(ttt)
                        # print('{} set -> {},row={},col={}'.format(akey,val_,rowpos,colpos))
                        # set the item into table
                        tablewidgetobj.setItem(rowpos, colpos, at_item)
                        tablewidgetobj.resizeColumnToContents(colpos)
                        if self.check_restrictions.str_to_bool_or_none(val_) in [True, False]:
                            if isinstance(val_, bool):
                                self.set_checkbox_value(at_item)
                            # Add tooltip text
                        self.set_tooltiptext(at_item)
                        self.set_icon_to_item(at_item)
                        self.set_backgroundcolor_to_item(at_item)
                        self.set_widget_to_item(at_item)
                        self.set_rolevalue_to_item(at_item)

                    rowpos = rowpos + 1
                modelobj = tablewidgetobj.model()
        else:
            raise Exception("tableWidget object is Not a {} object".format(type(QtWidgets.QTableWidget)))

    def get_dict_key_list(self, a_dict: dict) -> list:
        """Generates a list of the keys in the dictionary

        Args:
            a_dict (dict): dictionary to analyze

        Returns:
            list: List with keys
        """
        alist = []
        for key in a_dict:
            alist.append(key)
        return alist

    def get_tracked_value_in_struct(self, track, data_struct):
        trlist = track.copy()
        selected = {}
        if len(track) == 0:
            return None
        if isinstance(data_struct, list):
            for aData in data_struct:
                if aData["ID"] == trlist[0]:
                    trlist.pop(0)
                    selected = aData  # select dictionary
                    while len(trlist) > 1:
                        selected = selected[trlist[0]]
                        trlist.pop(0)
                    # last tracked is variable
                    if len(trlist) == 1:
                        # print ('get tracked value list',trlist[0],selected[trlist[0]])
                        return selected[trlist[0]]
        elif isinstance(data_struct, dict):
            selected = data_struct  # select dictionary
            while len(trlist) > 1:
                selected = selected[trlist[0]]
                trlist.pop(0)
            # last tracked is variable
            if len(trlist) == 1:
                # print ('get tracked value dict',trlist[0],selected[trlist[0]])
                return selected[trlist[0]]

        return None

    def get_dict_max_depth(self, adict: any, depth: int = 0, maxdepth: int = 0) -> int:
        if isinstance(adict, dict) == False and isinstance(adict, list) and depth == 0:
            for iii in adict:
                adepth = self.get_dict_max_depth(iii, 0)
                if depth >= maxdepth:
                    maxdepth = adepth
        else:
            alist = self.get_dict_key_list(adict)
            for item in alist:
                resdict = adict[item]
                if isinstance(resdict, dict):
                    adepth = self.get_dict_max_depth(resdict, depth + 1, maxdepth)
                    if adepth >= maxdepth:
                        maxdepth = adepth
                if depth >= maxdepth:
                    maxdepth = depth
        return maxdepth
