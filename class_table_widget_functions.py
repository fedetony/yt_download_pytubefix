"""
Class to handle a QTableWidget Object
Programmed by F.Garcia
"""

import logging
import re
from PyQt5 import QtCore, QtWidgets

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
logging.getLogger("").propagate = False


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

    data_id=Is the root item of your data_struct. This is not used in dictionary structures.

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
    data_id= "Id1" -> For getting only information on a specific 'ID' for list structure only.
    and
    reference_track=["Id1" "Item1" "Data_you_want_to_show"]
    """

    signal_data_change = QtCore.pyqtSignal(list, str, str, str)
    signal_item_button_clicked = QtCore.pyqtSignal(list)
    signal_item_button_right_clicked = QtCore.pyqtSignal(list,QtCore.QPoint)
    signal_item_combobox_currentindexchanged = QtCore.pyqtSignal(int, str, list)
    item_doubleclicked = QtCore.pyqtSignal(list)
    signal_item_checkbox_checked = QtCore.pyqtSignal(bool, list)

    def __init__(
        self,
        tablewidgetobj: QtWidgets.QTableWidget,
        data_struct: any,
        data_struct_mask: dict,
        data_id: str = None,
        reference_track: list[str] = None,
        /,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.__name__ = "tableWidget Functions"
        self.tablewidgetobj = tablewidgetobj
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
        self.show_dict = {}
        self.set_show_dict()
        # uses show dict
        self.modelobj = self.create_data_model_tablewidget(self.tablewidgetobj, False)
        self.data_struct_types = self.get_types_struct(self.data_struct)
        self.show_dict_types = self.get_types_struct(self.show_dict)
        self.set_items_icons()
        self.set_items_background_colors()
        self.set_items_tooltips()
        # initialize list of registered widgets
        self.widget_registered_list=[]
        self.set_items_widgets()
        self.set_items_rolevalues()

        self.restore_column_list = []
        self.restore_key_list = []
        self.resizetocontents = True
        # print(self.show_dict_types)
        self.refresh_tablewidget(self.show_dict, self.modelobj, self.tablewidgetobj)
        # connect action
        self.tablewidgetobj.clicked.connect(self._tablewidget_onclick)
        #Install event filter for right click
        self.tablewidgetobj.viewport().installEventFilter(self)
        
    
    def eventFilter(self, source, event):
        """Emits signal for right button clicked of item
        
        Args:
            source (QWidget): widget where the event is comming
            event (QtCore.QEvent): event to be filtered

        Returns:
            Event call: overwrites event in widget
        """
        if(event.type() == QtCore.QEvent.MouseButtonPress and
           event.buttons() == QtCore.Qt.RightButton and
           source is self.tablewidgetobj.viewport()):
            item = self.tablewidgetobj.itemAt(event.pos())
            #print('Right click Global Pos:', event.globalPos())
            if item is not None:
                # print('Right click Table Item:', item.row(), item.column())
                track=self.get_track_of_item_in_table(item)
                self.signal_item_button_right_clicked.emit(track,event.globalPos())
        return super().eventFilter(source, event)

    def _data_change(self, track: list[str], val: any, valtype: str, subtype: str):
        """Emits event data has changed and new value to parent

        Args:
            track (list[str]): Tracking list with path to follow in dictionary structure
            val (any): value on item
            valtype (str): string with value type
            subtype (str): if list inner value type
        """
        self.signal_data_change.emit(track, val, valtype, subtype)

    def _doubleclick_on_item(self, itm: QtWidgets.QTableWidgetItem):
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

    def _set_restore_columns(self, colkey: QtWidgets.QTableWidgetItem):
        """Sets dictionaries for restoring a value

        Args:
            colkey (QtWidgets.QTableWidgetItem): item in table
        """
        for iii, ti in enumerate(self.table_items):
            if colkey == ti:
                self.restore_key_list.append(colkey)
                self.restore_column_list.append(iii)

    def set_show_dict(self):
        """
        Sets show_dict in accordance to the reference path and data struct.
        """
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
        """Generates a copy of the structure (list or dictionary)
           replacing values with a string of the value type

        Args:
            dict_struct (any): struct

        Returns:
            any: struct with types
        """
        if isinstance(dict_struct, list):
            type_struct = []
            for a_data in dict_struct:
                type_struct.append(self.get_types_struct(a_data))
        elif isinstance(dict_struct, dict):
            type_struct = {}
            for a_data in dict_struct:
                if isinstance(dict_struct[a_data], dict):
                    nts = self.get_types_struct(dict_struct[a_data])
                    type_struct.update({a_data: nts})
                else:
                    type_struct.update({a_data: str(type(dict_struct[a_data]))})
        else:
            type_struct = {}
            type_struct.update({str(dict_struct): str(type(dict_struct))})

        return type_struct

    def get_gentrack_from_localtrack(self, track: list) -> list:
        """Adds refence track to a local track

        Args:
            track (list): local track (show_dict)

        Returns:
            list: general track (data_struct) using reference_track
        """
        gentrack = self.reference_track.copy()
        for iii in track:
            gentrack.append(iii)
        return gentrack

    def get_localtrack_from_gentrack(self, track: list) -> list:
        """Gets local track (show_dict) of a general track (data_struct) using reference_track
        Args:
            track (list): Track of Struct dict

        Returns:
            list: returns local track show_dict removing reference_track path
        """
        gentrack = self.reference_track.copy()
        trackc = track.copy()
        for iii in track:
            if track[iii] == gentrack[iii]:
                trackc.pop(0)
        return trackc

    def get_dictionary_from_structlist(self, data_struct: any, data_id=None) -> dict:
        """get the struct in dictionary form

        Args:
            data_struct (any): Data can be a list of dictionaries with 'ID' keys. Or dictionary form.
            data_id (_type_, optional): For getting only information on a specific 'ID' for list
            structure only. Defaults to None.
        Returns:
            dict: _description_
        """
        if isinstance(data_struct, list):
            for adict in data_struct:
                try:
                    if adict["ID"] == data_id:
                        # print('get my dict Found ID',data_id)
                        return adict.copy()
                except KeyError:
                    break
        elif isinstance(data_struct, dict) or data_id is None:
            # print('get my dict nochange is dict',data_id)
            return data_struct.copy()
        return {}

    def refresh_tablewidget(
        self, data_dict: any, modelobj: QtCore.QAbstractItemModel, tablewidgetobj: QtWidgets.QTableWidget
    ):
        """Refresh the Table Widget
        Before calling: set property resizetocontents (bool) to resize or not to contents
        Args:
            data_dict (any): Data to be shown in Table widget
            modelobj (QtCore.QAbstractItemModel): model object (reflects the table structure)
            tablewidgetobj (QtWidgets.QTableWidget): pointer to object
        """
        self.set_show_dict()
        tablewidgetobj.setRowCount(0)
        modelobj = self.create_data_model_tablewidget(tablewidgetobj, False)
        self.import_data_to_tablewidget(data_dict, modelobj, tablewidgetobj)
        if self.resizetocontents:
            tablewidgetobj.resizeColumnsToContents()
            # self.set_tableWidget_styles(tablewidgetobj.model())

    def _set_item_style(self, itm: QtWidgets.QTableWidgetItem):
        """Sets icon, background color and rolevalue to the item

        Args:
            itm (QtWidgets.QTableWidgetItem): item in table
        """
        self._set_icon_to_item(itm)
        self._set_backgroundcolor_to_item(itm)
        self._set_rolevalue_to_item(itm)

    def set_items_tooltips(self, tooltipdict: dict = {"track_list": [], "tooltip_list": []}) -> None:
        """Sets dictionary for tooltips of each item

        Args:
            tooltipdict (dict, optional): Lists must be of the same lengths. Dict must contain:
            "track_list": [TrackListItem1, ... , TrackListItemN]
            "tooltip_list": [TooltiptextItem1, ... , TooltiptextItemN]
            Defaults to {"track_list": [], "tooltip_list": []}.
        """
        self.tooltip_dict = tooltipdict

    def set_items_icons(self, icondict: dict = {"track_list": [], "icon_list": []}) -> None:
        """Sets dictionary for icons of each item

        Args:
            icondict (_type_, optional):(dict, optional): Lists must be of the same lengths. Dict must contain:
            "track_list": [TrackListItem1, ... , TrackListItemN]
            "icon_list": [IconObject1, ... , IconObjectN]
            IconObject is a QIcon object
            Defaults to {"track_list": [], "icon_list": []}.
        """
        self.icon_dict = icondict

    def set_items_background_colors(self, backgroundcolor_dict: dict = {"track_list": [], "color_list": []}) -> None:
        """Sets dictionary for background colors of each item

        Args:
            backgroundcolor_dict (_type_, optional): Lists must be of the same lengths. Dict must contain:
            "track_list": [TrackListItem1, ... , TrackListItemN].
            "color_list": [ColorObject1, ... , ColorObjectN]
            Color Object can be QBrush, QColor, GlobalColor or QGradient
            Defaults to {"track_list": [], "color_list": []}.
        """
        self.backgroundcolor_dict = backgroundcolor_dict

    def set_items_widgets(self, itemwidget_dict: dict = {"track_list": [], "widget_list": []}) -> None:
        """Sets dictionary for widgets of each item

        Args:
            itemwidget_dict (_type_, optional): Lists must be of the same lengths. Dict must contain:
            "track_list": [TrackListItem1, ... , TrackListItemN].
            "widget_list": [WidgetObject1, ... , WidgetObjectN]
            WidgetObject should be QtWidgets.QPushButton, QComboBox , QCheckBox, or QLabel objects
            Defaults to {"track_list": [], "widget_list": []}.
        """
        self.itemwidget_dict = itemwidget_dict

    def set_items_rolevalues(
        self, rolevalue_dict: dict = {"track_list": [], "role_list": [], "value_list": []}
    ) -> None:
        """Sets dictionary for role values of each item
            see: https://doc.qt.io/archives/qt-4.8/qt.html#ItemDataRole-enum
        Args:
            rolevalue_dict (_type_, optional): Lists must be of the same lengths. Dict must contain:
            "track_list": [TrackListItem1, ... , TrackListItemN].
            "role_list": [Role1, ... , RoleN]
            "value_list": [RoleValue1, ... , RoleValue1N]
            Defaults to {"track_list": [], "role_list": [], "value_list": []}.
        """
        self.itemrolevalue_dict = rolevalue_dict

    def _is_same_list(self, list1: list, list2: list) -> bool:
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

    def _item_button_clicked(self, track: list):
        """Emits signal for button clicked of item
        Args:
            track (list): track list of item clicked
        """
        # print('entered click {}'.format(track))
        self.signal_item_button_clicked.emit(track)

    def _item_combobox_indexchanged(self, cbw: QtWidgets.QComboBox, track: list = []):
        """Emits signal for item combobox widget

        Args:
            cbw (QtWidgets.QComboBox): combobox widget
            track (list, optional): track list of item . Defaults to [].
        """
        currenttxt = cbw.currentText()
        index = cbw.findText(currenttxt, QtCore.Qt.MatchFixedString)
        self.signal_item_combobox_currentindexchanged.emit(index, currenttxt, track)

    def _item_checkbox_checked(self, chb: QtWidgets.QCheckBox, track: list = []):
        """Emits signal for item checkbox

        Args:
            chb (QtWidgets.QCheckBox): checkbox widget
            track (list, optional): track list of item. Defaults to [].
        """
        currentstate = chb.isChecked()
        self.signal_item_checkbox_checked.emit(currentstate, track)

    def _is_registered_widget_track(self,track:list)->bool:
        """checks if track has been registered

        Args:
            track (list): track of item

        Returns:
            bool: if is on registered list or not
        """
        for tr in  self.widget_registered_list:
            if self._is_same_list(track, tr):
                return True
        return False
    
    def _remove_registered_widget_track_from_list(self,track):
        """removes track if has been registered
        Args:
            track (list): track of item
        """
        if self._is_registered_widget_track(track):
            new_reg_list=[]
            for tr in  self.widget_registered_list:
                if not self._is_same_list(track, tr):
                    new_reg_list.append(tr)
            self.widget_registered_list =  new_reg_list  
    
    def _add_registered_widget_track_to_list(self,track):
        """adds track if has been registered
        Args:
            track (list): track of item
        """
        if not self._is_registered_widget_track(track):
            self.widget_registered_list.append(track)
    
    def _remove_non_active_widgets_from_register(self):
        """Deletes the non existing widgets from track list
        """
        track_list = self.itemwidget_dict["track_list"]
        reg_list =self.widget_registered_list.copy()
        for tr in reg_list:
            in_track_list = False
            for track in track_list:
                if self._is_same_list(track, tr):
                    in_track_list = True
                    break
            if not in_track_list:
                self._remove_registered_widget_track_from_list(tr)
            
    def _set_widget_to_item(self, itm: QtWidgets.QTableWidgetItem):
        """Sets a widget to the item and connects the functionality
            works for QPushButton, QComboBox , QCheckBox, QLabel objects

        Args:
            itm (QtWidgets.QTableWidgetItem): Item to set the widget
        """
        self._remove_non_active_widgets_from_register()
        try:
            track = self.get_track_of_item_in_table(itm)
            track_list = self.itemwidget_dict["track_list"]
            widget_list = self.itemwidget_dict["widget_list"]
            
            for tr, iw in zip(track_list, widget_list):
                if self._is_same_list(track, tr):
                    if not self._is_registered_widget_track(tr):
                        # Only set once the widget else will be deleted
                        if not isinstance(iw, QtWidgets.QComboBox):
                            self.tablewidgetobj.setCellWidget(itm.row(), itm.column(), iw)
                        self._add_registered_widget_track_to_list(tr)
                    # Delegated behavior 
                    if isinstance(iw, QtWidgets.QComboBox):
                        delegate = Delegate(itm.row(), itm.column(), iw, parent=self.tablewidgetobj)
                        self.tablewidgetobj.setItemDelegateForColumn(itm.column(),delegate)
                        iw.currentIndexChanged.connect(lambda: self._item_combobox_indexchanged(iw,track))
                    
                    itm.setFlags(itm.flags() ^ QtCore.Qt.ItemIsEditable)
                    
                    if isinstance(iw, QtWidgets.QPushButton):
                        iw.clicked.connect(lambda: self._item_button_clicked(track))   
                    elif isinstance(iw, QtWidgets.QCheckBox):
                        iw.stateChanged.connect(lambda: self._item_checkbox_checked(iw, track))
                    elif isinstance(iw, QtWidgets.QLabel):
                        # self.tablewidgetobj.itemDoubleClicked.connect(self._doubleclick_on_item)
                        if self.resizetocontents:
                            self.tablewidgetobj.resizeColumnToContents(itm.column())
                            self.tablewidgetobj.resizeRowToContents(itm.row())
                    break
        except RuntimeError as err:
            log.error("RuntimeError setting widget_list to item: %s",err)
        except (AttributeError, TypeError)  as err:
            log.error("Setting widget_list to item: %s",err)

    def _set_icon_to_item(self, itm: QtWidgets.QTableWidgetItem):
        """Sets icon in icon_dict to item

        Args:
            itm (QtWidgets.QTableWidgetItem): Item in Table
        """
        try:
            track = self.get_track_of_item_in_table(itm)
            track_list = self.icon_dict["track_list"]
            icon_list = self.icon_dict["icon_list"]
            for tr, ic in zip(track_list, icon_list):
                if self._is_same_list(track, tr):
                    itm.setIcon(ic)
        except (AttributeError, TypeError):
            log.error("Setting icon_list to item")

    def _set_rolevalue_to_item(self, itm: QtWidgets.QTableWidgetItem):
        """Sets rolevalues in itemrolevalue_dict to item

        Args:
            itm (QtWidgets.QTableWidgetItem): Item in Table
        """
        try:
            track = self.get_track_of_item_in_table(itm)
            track_list = self.itemrolevalue_dict["track_list"]
            role_list = self.itemrolevalue_dict["role_list"]
            value_list = self.itemrolevalue_dict["value_list"]
            for tr, role, value in zip(track_list, role_list, value_list):
                if self._is_same_list(track, tr):
                    itm.setData(role, value)
        except (AttributeError, TypeError):
            log.error("Setting rolevalue to item")

    def _set_backgroundcolor_to_item(self, itm: QtWidgets.QTableWidgetItem):
        """Sets backgrounds in backgroundcolor_dict to item

        Args:
            itm (QtWidgets.QTableWidgetItem): Item in Table
        """
        try:
            track = self.get_track_of_item_in_table(itm)
            track_list = self.backgroundcolor_dict["track_list"]
            color_list = self.backgroundcolor_dict["color_list"]
            for tr, ic in zip(track_list, color_list):
                if self._is_same_list(track, tr):
                    itm.setBackground(ic)
        except (AttributeError, TypeError):
            log.error("Setting backgroundcolor to item")

    def _set_tooltiptext_to_item(self, itm: QtWidgets.QTableWidgetItem):
        """Sets tooltiptext in tooltip_dict to item.
        if limited_selection mask exists will write the selection options.
        Selection options are overwritten with tooltip_dict.

        Args:
            itm (QtWidgets.QTableWidgetItem): Item in Table
        """
        reslist, resvallist = self.get_item_restriction_resval(itm)
        for res, resval in zip(reslist, resvallist):
            if res in ["limited_selection", "is_list_item_limited_selection"]:
                itm.setToolTip(f"Options: {resval}")
        try:
            track = self.get_track_of_item_in_table(itm)
            track_list = self.tooltip_dict["track_list"]
            tooltip_list = self.tooltip_dict["tooltip_list"]
            for tr, itt in zip(track_list, tooltip_list):
                if self._is_same_list(track, tr):
                    itm.setToolTip(itt)
        except (AttributeError, TypeError):
            log.error("Setting ToolTiptext to item")

    def _tablewidget_onclick(self, index: QtCore.QModelIndex):
        """Onclick method on table widget restores or edits the item

        Args:
            index (QtCore.QModelIndex): Item being clicked
        """
        mycol = index.column()

        if self.resizetocontents:
            self.tablewidgetobj.resizeColumnToContents(mycol)
        itm = self.tablewidgetobj.itemFromIndex(index)
        self._set_icon_to_item(itm)
        self._set_widget_to_item(itm)
        self._set_tooltiptext_to_item(index)
        if mycol in self.restore_column_list:
            self._restore_a_tablewidget_item(index)
        else:
            val_ = itm.text()
            if self.check_restrictions.str_to_bool_or_none(val_) in [True, False]:
                self._set_checkbox_value_to_item(itm)
            self._edit_a_table_widget_item(index)

    def _set_checkbox_value_to_item(self, valueitem: QtWidgets.QTableWidgetItem):
        """Sets checkstate on checkbox when item is a boolean

        Args:
            valueitem (QtWidgets.QTableWidgetItem): Item
        """
        if self.check_restrictions.str_to_bool(valueitem.text()):
            valueitem.setCheckState(True)
        else:
            valueitem.setCheckState(False)

    def get_columnname_from_colpos(self, colpos: int) -> str:
        """Get an item from the column position

        Args:
            colpos (int): column position

        Returns:
            : item
        """
        for iii in self.table_items:
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
        return None

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
            track.append(self.get_columnname_from_colpos(mycol))
        return track

    def set_value_and_trigger_data_change(self,track:list,value:any,the_type:str,subtype:str=""):
        """Check if value is conform. If conform then set it and refresh Table
        
        Args:
            track (list): Track list
            value (any): Value (in the correct type)
            the_type (str): type of the value as string
            subtype (str, optional): if list, type type of the list items in list as string. Defaults to "".
        """
        value = self.check_restrictions.set_type_to_value(value,the_type,subtype)
        itm, itmindex, _, _ = self.get_item_from_track(track)
        #print("Got: ",itm, itmindex, itmtrack, itmindextrack)
        if itmindex:
            if self.check_item_value_for_edit(itmindex,value,True):
                self.set_tracked_value_to_dict(track,value,self.show_dict,subtype,True)
                if the_type == str(bool):
                    self._set_checkbox_value_to_item(itm)
                
                self.refresh_tablewidget(self.show_dict, self.modelobj, self.tablewidgetobj)
                self._tablewidget_onclick(itmindex)

    def _edit_a_table_widget_item(self, index: QtCore.QModelIndex):
        """Connects item to datachange fuction

        Args:
            index (QtCore.QModelIndex): item being edited
        """
        # print('_edit_a_table_widget_item',index)
        itm = self.tablewidgetobj.itemFromIndex(index)
        val = itm.text()
        # print('edit index set:',index.data())
        self._last_value_selected = val
        self.tablewidgetobj.itemChanged.connect(lambda: self._item_data_changed(index, val))

    # def get_list_of_tracks_of_children(self, parenttrack):
    #    self.get_gentrack_from_localtrack

    def get_item_from_track(self, track: list) -> None:
        """Get an item object and all related info

        Args:
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
            modelobj=self.tablewidgetobj.model()
            
            # Track is in tables [ rowname colname ]
            if len(track) > 1:
                col_pos = self.get_item_column_pos_in_table(track[1])
            else:
                col_pos = 0
 
            for tr in track:
                if parent is None:
                    log.debug('get_item_from_track if the size -> {}'.format(modelobj.rowCount()))
                    itm = None
                    for iii in range(modelobj.rowCount()):
                        itmindex = modelobj.index(iii, col_pos)
                        itm = self.tablewidgetobj.itemFromIndex(itmindex)
                        # itm = modelobj.itemFromIndex(itmindex)
                        if not self._is_item_text(itm, tr):
                            break  # item None or found
                    # not found
                    if not self._is_item_not_text(itm, tr):
                        break  # item none or not found
                else:
                    log.info('get_item_from_track else the size -> {}'.format(modelobj.rowCount(parent)))
                    itm = None
                    for iii in range(modelobj.rowCount(parent)):
                        itmindex = modelobj.index(iii, col_pos, parent)
                        #itm = modelobj.itemFromIndex(itmindex)
                        itm = self.tablewidgetobj.itemFromIndex(itmindex)
                        if not self._is_item_text(itm, tr):
                            break  # item None or found
                    # not found
                    if not self._is_item_not_text(itm, tr):
                        break  # item none or not found
                parent = itmindex
                parentitm = self.tablewidgetobj.itemFromIndex(itmindex)
                #parentitm = modelobj.itemFromIndex(parent)
                if parentitm.text() == "ID":
                    # parenttxt = parentitm.text()
                    parent = None
                    continue
                itmtrack.append(itm)
                itmindextrack.append(itmindex)
            return itm, itmindex, itmtrack, itmindextrack
        except (ValueError, KeyError, TypeError, AttributeError) as e:
            log.error("Get item from track: %s", e)
            return None, None, None, None

    def _is_item_not_text(self, itm, tr):
        """Helper function"""
        try:
            if tr != itm.text():
                return False
            return True
        except (UnboundLocalError,AttributeError):
            return False

    def _is_item_text(self, itm, tr):
        """Helper function"""
        try:
            if tr == itm.text():
                return False
            return True
        except (UnboundLocalError,AttributeError):
            return False

    def _item_data_changed(self, index: QtCore.QModelIndex, val: any):
        """If value has changed and item is editable, changes the value to new value
        only when value check is conform to mask and type. If not, sets the old value.

        Args:
            index (QtCore.QModelIndex): index of item
            val (any): new value to be set
        """
        old_value = val  # self._last_value_selected
        itm = self.tablewidgetobj.itemFromIndex(index)
        # when you click outside will be none
        if not itm:
            return
        new_value = itm.text()
        #print("item_data_changed")
        # self._set_item_style(self.tablewidgetobj.item(itm.row(),icol)) # column item
        if new_value != old_value and old_value is not None and index in self.tablewidgetobj.selectedIndexes():
            # indextype=index.siblingAtColumn(tcol)
            # typeitem=self.tablewidgetobj.itemFromIndex(indextype)
            track = self.get_track_of_item_in_table(self.tablewidgetobj.itemFromIndex(index))
            # Here check if value is ok if yes
            valisok = self.check_item_value_for_edit(index, new_value)
            log.info("Data changed -> New:%s Old:%s Track: %s isvalid: %s", new_value, old_value, track, valisok)
            subtype = ""
            if valisok:
                thetype, subtype = self._get_item_supposed_type_subtype(itm)
                new_valwt = self.check_restrictions.set_type_to_value(
                    new_value, thetype, subtype
                )  # Send value with correct type to dictionary
                do_refresh_tablewidget, self.show_dict = self.set_tracked_value_to_dict(
                    track, new_valwt, self.show_dict, subtype
                )
                if not do_refresh_tablewidget:
                    itm.setText(new_value)
                    if thetype == str(bool):
                        self._set_checkbox_value_to_item(itm)
                else:  # need to refresh only if value is changed
                    self.refresh_tablewidget(self.show_dict, self.modelobj, self.tablewidgetobj)
                # Here send signal data has changed
                self._data_change(track, new_value, thetype, subtype)
            else:  # reset old value
                thetype, subtype = self._get_item_supposed_type_subtype(itm)
                typestr = thetype
                if typestr == str(list):
                    gentrack = self.get_gentrack_from_localtrack(track)  # <-track is local!
                    subtype = self._get_listitem_subtype(gentrack)
                # Send value with correct type to dictionary
                old_valwt = self.check_restrictions.set_type_to_value(old_value, thetype, subtype)
                do_refresh_tablewidget, self.show_dict = self.set_tracked_value_to_dict(
                    track, old_valwt, self.show_dict, subtype
                )
                itm.setText(old_value)
                if thetype == str(bool):
                    self._set_checkbox_value_to_item(itm)

        self._last_value_selected = None

    def _is_item_supposed_to_be_a_list(self, itm: QtWidgets.QTableWidgetItem) -> bool:
        """Responds if Item is supposed to be a list or not looking at the mask

        Args:
            itm (QtWidgets.QTableWidgetItem): Item

        Returns:
            bool: True if Item should be a List
        """
        reslist, resvallist = self.get_item_restriction_resval(itm)
        for res, resval in zip(reslist, resvallist):
            if "is_list_item_" in res or (res == "is_value_type" and resval == str(list)):
                return True
        return False

    def _horizontalheaderclicked(self, index):
        """
        click test
        """
        print("_horizontalheaderclicked", index)

    def _verticalheaderclicked(self, index):
        """
        click test
        """
        print("_verticalheaderclicked", index)

    def _get_item_supposed_type_subtype(self, itm: QtWidgets.QTableWidgetItem) -> tuple[str, str]:
        """Gets items type and subtype

        Args:
            itm (QtWidgets.QTableWidgetItem): item

        Returns:
            tuple[str,str]: type and subtype of item
        """
        subtype = ""
        thetype = str(str)
        reslist, resvallist = self.get_item_restriction_resval(itm)
        if not self._is_item_supposed_to_be_a_list(itm):
            for res, resval in zip(reslist, resvallist):
                if res == "is_value_type":
                    thetype = resval
                    break
        else:
            thetype = str(list)
            for res, resval in zip(reslist, resvallist):
                if res == "is_list_item_type":
                    subtype = resval
                    break
        return thetype, subtype

    def _get_listitem_subtype(self, track: list) -> str:
        """Finds subtype for item in track from mask

        Args:
            track (list): track of item

        Returns:
            str: subtype
        """
        mask = self.get_mask_for_item(track)
        # log.info('Got for subtype: {} {}'.format(track,mask))
        for mmm in mask:
            keymmm = str(mmm)
            if "__m__" in keymmm:
                keyval = keymmm.replace("__m__", "__mv__")
                if mask[keymmm] == "is_list_item_type":
                    return mask[keyval]
        return ""

    def set_tracked_value_to_dict(
        self, track: list, val: any, dict_struct: any, subtype: str, emitsignal: bool = True
    ) -> tuple[bool, any]:
        """Track in the dictionary the item and set the value

        Args:
            track (list): Track list for setting value
            val (any): value to be set
            dict_struct (any): the data struct
            subtype (str): subtype of list values
            emitsignal (bool, optional): Emit signal when value is set. Defaults to True.

        Returns:
            bool: data changed needs to refresh table widget
            any: data struct with new data
        """
        do_refresh_tablewidget = False
        trlist = track.copy()
        selected = {}
        if isinstance(dict_struct, list):
            for a_data in dict_struct:
                if a_data["ID"] == trlist[0]:
                    trlist.pop(0)
                    selected = a_data  # .copy() #select dictionary
                    selected, trlist = self._get_selected_tracklist_one_item(selected, trlist)
                    # last tracked is variable
                    if len(trlist) == 1:
                        selected.update({trlist[0]: val})
                        # Change title of Data special case
                        # log.debug('setvaltodict_struct Here {} set to {}'.format(trlist[0],val))
                        if trlist[0] == "ID" and len(track) == 2:
                            do_refresh_tablewidget = True
                        if emitsignal:
                            trackstruct = track
                            self._data_change(trackstruct, str(val), str(type(val)), subtype)  # refresh on main
                        break
        elif isinstance(dict_struct, dict):
            selected = dict_struct  # .copy() #select dictionary
            selected, trlist = self._get_selected_tracklist_one_item(selected, trlist)
            # last tracked is variable
            #print("is dict instance")
            if len(trlist) == 1:
                selected.update({trlist[0]: val})
                # log.debug('setvaltodict_dict Here {} set to {}'.format(trlist[0],val))
                # update
                trackstruct = track.copy()
                #_, self.data_struct = self.set_tracked_value_to_dict(trackstruct, val, self.data_struct, subtype)
                if emitsignal:
                    self._data_change(trackstruct, str(val), str(type(val)), subtype)  # refresh on main
        return do_refresh_tablewidget, dict_struct

    # def get_track_struct_from_dict_track(self, dict_, track):
    #     if isinstance(dict_, dict):
    #         if self.data_id is not None:
    #             endtrack = [self.data_id].append(track)
    #             # print ('ini_track->',track,'endtrack->',endtrack)
    #             return endtrack
    #     return track

    def _get_selected_tracklist_one_item(self, selected: dict, trlist: list) -> tuple[dict, list]:
        """Helper function to reduce the selected track to 1 item

        Args:
            selected (dict): dict
            trlist (list): track list

        Returns:
            tuple[dict,list]: dict with track[0], 1 value list of track[0]
        """
        len_trlist = len(trlist)
        while len_trlist > 1:
            try:
                selected = selected[trlist[0]]
                trlist.pop(0)
                len_trlist = len(trlist)
            except (KeyError, IndexError, RecursionError):
                break
        return selected, trlist

    def check_item_value_for_edit(self, index: QtCore.QModelIndex, val: any, isok=True) -> bool:
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
        log.debug("bymask isok = %s", isok)
        return isok

    def get_item_restriction_resval(self, itm: QtWidgets.QTableWidgetItem):
        """Get item's restriction and restriction value

        Args:
            itm (QtWidgets.QTableWidgetItem): item

        Returns:
            list: restriction list
            list: restriction value list
        """
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

    def check_item_by_mask(self, index: QtCore.QModelIndex, val: any, isok=True) -> bool:
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
        log.debug("Checking the item by mask-> Masked Track: %s, Mask: %s", track, itmmask)
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
                        idlist = self.get_id_list()
                        if val in idlist:
                            isok = False
                    if not isok:
                        log.info("%s %s returned False", track, keyname)
                        break
        return isok

    def get_id_list(self) -> list:
        """Gets the id list for data_struct = [Datastruct1,...,DatastructN]
        where each DatastructX has 'ID' key.

        Returns:
            list: list of IDs
        """
        id_list = []
        try:
            for aaa in self.data_struct:
                id_list.append(aaa["ID"])
        except KeyError:
            id_list = []
        return id_list

    def get_mask_for_item(self, track: list) -> dict:
        """Gets the mask for the item in the track

        Args:
            track (list): Track list of item

        Returns:
            dict: Mask dictionary for the specific item
        """
        maskstruct = self.data_struct_mask
        if len(maskstruct) == 0 or len(track) == 0:
            return {}
        if isinstance(maskstruct,list):
            maskdict = maskstruct[0]
        elif isinstance(maskstruct,dict):
            maskdict = maskstruct
        mask_keylist=self.get_dict_key_list(maskdict)
        ttt_track = track.copy()
        
        mask = self.get_tracked_value_in_struct(ttt_track, maskdict)
        if not mask: 
            if '__any__' in mask_keylist:
                ttt_track.pop(0)
                # Need to add the base of the list in the track
                new_track=['__any__']+ttt_track
                mask = self.get_tracked_value_in_struct(new_track, maskdict)   

        if not mask:
            mask = {}
        # print("->",mask)
        return mask

    def str_to_list(self, astr: str) -> list:
        """Converts a string with list format into a list

        Args:
            astr (str): string

        Returns:
            list: List. None if the String has not the correct format
        """
        try:
            rema = re.search(r"^\[(.+,)*(.+)?\]$", astr)
            splited = None
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

    def _restore_a_tablewidget_item(self, index: QtCore.QModelIndex):
        """Restores the value of an item

        Args:
            index (QtCore.QModelIndex): item index_
        """
        itm = self.tablewidgetobj.itemFromIndex(index)
        # column = itm.column()
        track = self.get_track_of_item_in_table(self.tablewidgetobj.itemFromIndex(index))
        value = self.get_tracked_value_in_struct(track, self.data_struct)
        log.info("Restored %s to %s", track, value)
        itm.setText(str(value))

    def import_data_to_tablewidget(
        self, data: any, modelobj: QtCore.QAbstractItemModel, tablewidgetobj: QtWidgets.QTableWidget
    ) -> None:
        """Sets structure to the tablewidget

        Args:
            data (any): Can be in the list[dict] form with an 'ID' key in each dictionary. Or a Dictionary
            with {row1:{Col1:Val1, ..., ColN:ValN}} Form.
            modelobj (QtCore.QAbstractItemModel): model object (reflects the table structure)
            tablewidgetobj (QtWidgets.QTableWidget): pointer to object
        """
        tablewidgetobj.setRowCount(0)
        if isinstance(data, list):
            for adict in data:
                newdict = {}
                try:
                    newdict.update({adict["ID"]: adict})
                except KeyError:
                    pass
                self.dict_to_table(newdict, modelobj, tablewidgetobj, myparent=None)
            # return newdict
        elif isinstance(data, dict):
            self.dict_to_table(data, modelobj, tablewidgetobj, myparent="Data")

    def create_data_model_tablewidget(
        self, table_widget_parent: QtWidgets.QTableWidget, emitsignal=False
    ) -> QtCore.QAbstractItemModel:
        """Creates a model object for the table widget

        Args:
            table_widget_parent (QtWidgets.QTableWidget): the table widget
            emitsignal (bool, optional): Emit signals when values are set. Defaults to False.

        Returns:
            QtCore.QAbstractItemModel: Model object
        """
        if isinstance(self.show_dict, dict):
            data_dict = self.show_dict
            colcount = len(data_dict)
        else:
            data_dict = self.get_standard_dict_model()
            colcount = 0
        tableitems = []
        tableitems = self.get_table_item_list(data_dict)
        # Set Item,Value and Type to all items, set all dict entries to all items
        self.show_dict, self.table_items = self.get_minimumreqs_in_dict(data_dict, tableitems)
        self.set_tracked_value_to_dict(
            self.reference_track, self.show_dict, self.data_struct, subtype="", emitsignal=emitsignal
        )

        rowcount = len(self.table_items)
        # Row count
        table_widget_parent.setRowCount(rowcount)
        # Column count
        table_widget_parent.setColumnCount(colcount)
        model = table_widget_parent.model()
        for iii, t_item in enumerate(self.table_items):
            model.setHeaderData(iii, QtCore.Qt.Horizontal, t_item)
        # table_widget_parent.setModel(model)
        return model

    def get_minimumreqs_in_dict(self, data_dict: any, tableitems: list[str]) -> tuple[dict, list[str]]:
        """Sets a dictionary with minimum requirements
            for setting a model object. if data_dict is empty is used a default dictionary
            with 'Value' because empty models are not allowed. Returns a constructed dict
            usable in a modelobject.
        Args:
            data_dict (any): actual data structure
            tableitems (list): items in the tablewidget

        Returns:
            dict: new show_dictionary
            list: new table items list
        """
        if len(tableitems) == 0:
            if "Value" not in tableitems:
                tableitems.append("Value")
        tableitemsnivt = []
        for tbi in tableitems:
            tableitemsnivt.append(tbi)
        new_d_dict = {}
        for data in data_dict:
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

    def get_table_item_list(self, new_d_dict: dict, positem=0) -> list[str]:
        """Get a list of items at position of a dictionary

        Args:
            new_d_dict (dict): new data dictionary
            positem (int, optional): position of item. Defaults to 0.

        Returns:
            list[str]: list of items
        """
        new_d_items = []
        if len(new_d_dict) > 0:
            ndl = self.get_dict_key_list(new_d_dict)
            new_d_items = self.get_dict_key_list(new_d_dict[ndl[positem]])
        return new_d_items

    def get_item_column_pos_in_table(self, item: QtWidgets.QTableWidgetItem) -> int:
        """Gets Column position of an item

        Args:
            item (QtWidgets.QTableWidgetItem): item

        Returns:
            int: column position, None if not found
        """
        for iii, itm in enumerate(self.table_items):
            if itm == item:
                return iii
        return None

    def dict_to_table(
        self, adict: dict, modelobj: QtCore.QAbstractItemModel, tablewidgetobj: QtWidgets.QTableWidget, myparent=None
    ):
        """Set the dictionary to table widget

        Args:
            adict (dict): Dictionary to be set
            modelobj (QtCore.QAbstractItemModel): _description_
            tablewidgetobj (QtWidgets.QTableWidget): _description_
            myparent (_type_, optional): _description_. Defaults to None.
        """
        # print('Entered dict to table {}'.format(adict))

        key_list = self.get_dict_key_list(adict)
        if myparent is None:
            parent = "Data"
            if parent in key_list:
                self.dict_to_table(adict[parent], modelobj, tablewidgetobj, myparent=parent)
            return
        parent = myparent

        # Row count
        tablewidgetobj.setRowCount(len(key_list))
        # Column count
        tablewidgetobj.setColumnCount(len(self.table_items))
        # Set header labels
        tablewidgetobj.setHorizontalHeaderLabels(self.table_items)
        tablewidgetobj.setVerticalHeaderLabels(key_list)
        # tablewidgetobj.horizontalHeader().clicked.connect(lambda: self._horizontalheaderclicked)
        # tablewidgetobj.verticalHeader().clicked.connect(lambda: self._verticalheaderclicked)
        rowpos = 0
        for akey in key_list:
            table_line = adict[akey]
            # val_item=table_line['Item']
            # val_value =table_line['Value']
            # val_type=str(type(val_value))
            for ttt in self.table_items:
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
                        self._set_checkbox_value_to_item(at_item)
                    # Add tooltip text
                self._set_tooltiptext_to_item(at_item)
                self._set_icon_to_item(at_item)
                self._set_backgroundcolor_to_item(at_item)
                self._set_widget_to_item(at_item)
                self._set_rolevalue_to_item(at_item)

            rowpos = rowpos + 1
            # modelobj = tablewidgetobj.model()

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

    def get_tracked_value_in_struct(self, track: list, data_struct: any):
        """Get the value in the structure at tracked list.

        Args:
            track (list): list of position in the struct of value
            data_struct (any): structure with data

        Returns:
            any: value at structure position in track. None if not found.
        """
        try:
            trlist = track.copy()
            selected = {}
            if len(track) == 0:
                return None
            if isinstance(data_struct, list):
                for a_data in data_struct:
                    if a_data["ID"] == trlist[0]:
                        trlist.pop(0)
                        selected = a_data  # select dictionary
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
        except (KeyError, ValueError, TypeError):
            pass
        return None

    def get_dict_max_depth(self, adict: any, depth: int = 0, maxdepth: int = 0) -> int:
        """Get depth of a structure (dict or list) recursively.

        Args:
            adict (any): Structure
            depth (int, optional): Initial depth. Defaults to 0.
            maxdepth (int, optional): maxdepth. Defaults to 0.

        Returns:
            int: maximum depth
        """
        if isinstance(adict, dict) is False and isinstance(adict, list) and depth == 0:
            for iii in adict:
                adepth = self.get_dict_max_depth(iii, 0)
                if depth >= maxdepth:  # ???? not maxdepth = max(maxdepth, adepth)
                    maxdepth = adepth
        else:
            alist = self.get_dict_key_list(adict)
            for item in alist:
                resdict = adict[item]
                if isinstance(resdict, dict):
                    adepth = self.get_dict_max_depth(resdict, depth + 1, maxdepth)
                    maxdepth = max(maxdepth, adepth)
                maxdepth = max(maxdepth, depth)
        return maxdepth


class Delegate(QtWidgets.QStyledItemDelegate):
    def __init__(
        self,
        itm_row: int,
        itm_col: int,
        widget_obj: QtWidgets.QWidget,
        /,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.widget_obj = widget_obj
        self.itm_row = itm_row
        self.itm_col = itm_col
    
    def createEditor(self, parent, option, index):
        editor = None
        if isinstance(self.widget_obj, QtWidgets.QComboBox):
            self.widget_obj.setParent(parent)
            editor = QtWidgets.QComboBox(parent)
            index_cb= self.widget_obj.currentIndex()
            current_text=self.widget_obj.itemText(index_cb)
            editor.currentTextChanged.connect(self.handle_commit_close_editor)
            editor.setCurrentText(current_text)
        return editor

    def setEditorData(self, editor, index):
        if index.column() == self.itm_col and index.row() == self.itm_row:
            if isinstance(editor, QtWidgets.QComboBox):
                option = index.data()
                editor.clear()
                all_items = [self.widget_obj.itemText(iii) for iii in range(self.widget_obj.count())]
                editor.addItems(all_items)
                editor.setCurrentText(option)

    def setModelData(self, editor, model, index):
        if index.column() == self.itm_col and index.row() == self.itm_row:
            option = editor.currentText()
            model.setData(index, option, QtCore.Qt.DisplayRole)

    def handle_commit_close_editor(self):
        editor = self.sender()
        if isinstance(editor, QtWidgets.QWidget):
            self.commitData.emit(editor)
            self.closeEditor.emit(editor)

