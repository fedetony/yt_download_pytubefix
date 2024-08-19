"""
Class for checking restriction parameters
Programed by: F.Garcia
"""

import re
import logging

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

class CheckRestrictions:
    """
    Restriction checker for masks

    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.__name__ = "Check Restrictions"

    def str_to_bool_or_none(self, astr: any) -> bool:
        """Convert a string to a bool with None possibilty

        Args:
            val (any): value/string/bool to convert

        Returns:
            bool: True/False if bool True/False if string True/true or False/false, else None
        """
        if isinstance(astr, bool):
            return astr
        if isinstance(astr, str):
            if astr.lower() in ["true"]:
                return True
            if astr.lower() in ["false"]:
                return False
        return None

    def str_to_bool(self, val: any) -> bool:
        """Convert a string to a bool

        Args:
            val (any): value/string/bool to convert

        Returns:
            bool: True if bool True or string True/true, else False
        """
        if self.str_to_bool_or_none(val):
            return True
        return False

    def _is_list_item_type(self, value: any, restriction_value: any, isok: bool) -> bool:
        """
        Restrict list items to type
        """
        strlist = self._str_to_list(value)
        # print('got value:',value,type(value),'the list:',strlist,'resval:',restriction_value)
        try:
            for iii in strlist:
                # print(iii)
                if restriction_value == str(int):
                    _ = int(iii.strip())
                    rema = re.search(r"^[-+]?[0-9]+$", iii.strip())
                    isok = bool(rema)
                elif restriction_value == str(float):
                    _ = float(iii)
                elif restriction_value == str(bool):
                    ans = self.str_to_bool_or_none(iii)
                    if ans is None:
                        isok = False
                else:
                    isok = self.check_type(restriction_value, iii, isok)
        except (AttributeError, ValueError, TypeError):
            isok = False
        return isok

    def _is_list_length(self, value: any, restriction_value: any, isok: bool) -> bool:
        """
        Restrict list length
        """
        strlist = self._str_to_list(value)
        # print('got value:',value,type(value),'the list:',strlist,'resval:',restriction_value)
        try:
            if restriction_value != len(strlist):
                isok = False
        except (ValueError, TypeError):
            # print(e)
            isok = False
        return isok

    def _is_list_lengthgt(self, value: any, restriction_value: any, isok: bool) -> bool:
        """
        Restrict list length greater than
        """
        strlist = self._str_to_list(value)
        try:
            if restriction_value <= len(strlist):
                isok = False
        except (ValueError, TypeError):
            isok = False
        return isok

    def _is_list_lengthlt(self, value: any, restriction_value: any, isok: bool) -> bool:
        """
        Restrict list length less than
        """
        strlist = self._str_to_list(value)
        try:
            if restriction_value >= len(strlist):
                isok = False
        except (ValueError, TypeError):
            isok = False
        return isok

    def _limited_selection(self, value: any, restriction_value: any, isok: bool) -> bool:
        """
        Restrict item is on the limited list
        """
        try:
            if value not in restriction_value:
                isok = False
                log.info("Selection '%s' not in permitted list: %s", value, restriction_value)
        except (ValueError, TypeError):
            isok = False
        return isok

    def _is_list_item_limited_selection(self, value: any, restriction_value: any, isok: bool) -> bool:
        """
        Restrict list item value is on the limited list
        """
        try:
            if not isinstance(value, list):
                alist = self._str_to_list(value)
            else:
                alist = value
            for aval in alist:
                if aval not in restriction_value:
                    isok = False
                    log.info("Selection '%s' not in permitted list: %s", aval, restriction_value)
        except (ValueError, TypeError):
            isok = False
        return isok

    def _is_list_item_format(self, value: any, restriction_value: any, isok: bool) -> bool:
        """
        Restrict list item has regex format
        """
        try:
            if not isinstance(value, list):
                alist = self._str_to_list(value)
            else:
                alist = value
            for aval in alist:
                if aval != "":
                    try:
                        rema = re.search(restriction_value, aval)
                        if rema.group() is not None:
                            isok = True
                    except (ValueError, TypeError):
                        isok = False
                        break
        except (AttributeError, ValueError, TypeError):
            isok = False
        return isok

    def _is_list_item_value_lt(self, value: any, restriction_value: any, isok: bool) -> bool:
        """
        Restrict list item value less than
        """
        try:
            if not isinstance(value, list):
                alist = self._str_to_list(value)
            else:
                alist = value
            for aval in alist:
                val = float(aval)
                if restriction_value <= val:
                    isok = False
                    log.info("Selection '%s' not in permitted list: %s", aval, restriction_value)
        except (ValueError, TypeError):
            isok = False
        return isok

    def _is_list_item_value_gt(self, value: any, restriction_value: any, isok: bool) -> bool:
        """
        Restrict list item value greater than
        """
        try:
            if not isinstance(value, list):
                alist = self._str_to_list(value)
            else:
                alist = value
            for aval in alist:
                val = float(aval)
                if restriction_value >= val:
                    isok = False
                    log.info("Selection '%s' not in permitted list: %s", aval, restriction_value)
        except (ValueError, TypeError):
            isok = False
        return isok

    def _is_list_item_value_eq(self, value: any, restriction_value: any, isok: bool) -> bool:
        """
        Restrict list item value is equal to
        """
        try:
            if not isinstance(value, list):
                alist = self._str_to_list(value)
            else:
                alist = value
            for aval in alist:
                val = float(aval)
                if restriction_value == val:
                    isok = False
                    log.info("Selection '%s' not in permitted list: %s", aval, restriction_value)
        except (ValueError, TypeError):
            isok = False
        return isok

    def _is_list_item_value_lteq(self, value: any, restriction_value: any, isok: bool) -> bool:
        """
        Restrict list item value less or equal to
        """
        try:
            if not isinstance(value, list):
                alist = self._str_to_list(value)
            else:
                alist = value
            for aval in alist:
                val = float(aval)
                if restriction_value < val:
                    isok = False
                    log.info("Selection '%s' not in permitted list: %s", aval, restriction_value)
        except (ValueError, TypeError):
            isok = False
        return isok

    def _is_list_item_value_gteq(self, value: any, restriction_value: any, isok: bool) -> bool:
        """
        Restrict list item value greater or equal to
        """
        try:
            if not isinstance(value, list):
                alist = self._str_to_list(value)
            else:
                alist = value
            for aval in alist:
                val = float(aval)
                if restriction_value > val:
                    isok = False
                    log.info("Selection '%s' not in permitted list: %s", aval, restriction_value)
        except (ValueError, TypeError):
            isok = False
        return isok

    def _is_list_item_value_neq(self, value: any, restriction_value: any, isok: bool) -> bool:
        """
        Restrict list item value is not equal to
        """
        try:
            if not isinstance(value, list):
                alist = self._str_to_list(value)
            else:
                alist = value
            for aval in alist:
                val = float(aval)
                if restriction_value != val:
                    isok = False
                    log.info("Selection '%s' not in permitted list: %s", aval, restriction_value)
        except (ValueError, TypeError):
            isok = False
        return isok

    def _is_format(self, value: any, restriction_value: any, isok: bool) -> bool:
        """
        Restrict value has regex format
        """
        if value != "":
            try:
                rema = re.search(restriction_value, value)
                if rema.group() is not None:
                    isok = True
            except (AttributeError, ValueError, TypeError):
                isok = False
        return isok

    def _is_unique(self, value: any, restriction_value: any, isok: bool) -> bool:
        """
        Restrict item is unique (always unique)
        """
        _ = value
        _ = restriction_value
        isok = True
        return isok  # None

    def _is_not_change(self, value: any, restriction_value: any, isok: bool) -> bool:
        """
        Restrict value not changed
        """
        _ = value
        _ = restriction_value
        isok = False
        return isok

    def _is_value_lt(self, value: any, restriction_value: any, isok: bool) -> bool:
        """
        Restrict value less than
        """
        try:
            val = float(value)
            if restriction_value <= val:
                isok = False
        except (ValueError, TypeError):
            isok = False
        return isok

    def _is_value_gt(self, value: any, restriction_value: any, isok: bool) -> bool:
        """
        Restrict value greater than
        """
        try:
            val = float(value)
            if restriction_value >= val:
                isok = False
        except (ValueError, TypeError):
            isok = False
        return isok

    def _is_value_eq(self, value: any, restriction_value: any, isok: bool) -> bool:
        """
        Restrict value equal to
        """
        try:
            val = float(value)
            if restriction_value == val:
                isok = False
        except (ValueError, TypeError):
            isok = False
        return isok

    def _is_value_lteq(self, value: any, restriction_value: any, isok: bool) -> bool:
        """
        Restrict value less or equal to
        """
        try:
            val = float(value)
            if restriction_value < val:
                isok = False
        except (ValueError, TypeError):
            isok = False
        return isok

    def _is_value_gteq(self, value: any, restriction_value: any, isok: bool) -> bool:
        """
        Restrict value greater or equal to
        """
        try:
            val = float(value)
            if restriction_value > val:
                isok = False
        except (ValueError, TypeError):
            isok = False
        return isok

    def _is_value_neq(self, value: any, restriction_value: any, isok: bool) -> bool:
        """
        Restrict value not equal to
        """
        try:
            val = float(value)
            if restriction_value != val:
                isok = False
        except (ValueError, TypeError):
            isok = False
        return isok

    def _is_value_type(self, value: any, restriction_value: any, isok: bool) -> bool:
        """
        Restrict value type
        """
        if restriction_value == str(int):
            try:
                _ = int(value.strip())
                rema = re.search(r"^[-+]?[0-9]+$", value.strip())
                isok = bool(rema)
            except (AttributeError, ValueError, TypeError):
                isok = False

        elif restriction_value == str(float):
            try:
                _ = float(value.strip())
            except (ValueError, TypeError):
                isok = False
        elif restriction_value == str(bool):
            ans = self.str_to_bool_or_none(value.strip())
            if ans is None:
                isok = False
        else:
            isok = self.check_type(restriction_value, value.strip(), isok)
        return isok

    def checkitem_value_with_mask(self, restriction: str, restriction_value: any, value: any) -> bool:
        """Check if value is restricted to the condition specified in restriction for the restriction value.
            example:  Value should start with "A"
                      restriction="is_format"
                      restriction_value= r"(^[A])"
                      will return True for Value "Astrid"
                      will return False for Value "Thomas"
            examples:
            "should not be 5 val=0",checkitem_value_with_mask("is_value_eq",5,0) -> True
            "should not be 0 val=0",checkitem_value_with_mask("is_value_eq",0,0) -> False
            "should be 5 only val=0",checkitem_value_with_mask("is_value_neq",5,0)) -> False
            "should be 0 only val=0",checkitem_value_with_mask("is_value_neq",0,0)) -> True
            "should be 0 or 5 only val=0",checkitem_value_with_mask("is_limited",[0,5],0) -> True

        Args:
            restriction (str): text that selects the restriction
            restriction_value (any): value of the restriction can be anything
            value (any): could be any value or object as it also checks for type

        Returns:
            bool: True if is congruent
        """
        isok = True
        try:
            isok = getattr(self, "_" + restriction.lower())(value, restriction_value, isok)
        except AttributeError:
            pass

        return isok

    def check_type(self, the_type: str, val: any, isok: bool = True) -> bool:
        """Check Type of value

        Args:
            the_type (str): string of the type
            val (any): value to be checked
            isok (bool, optional): True If value is of type the_type. Defaults to True.

        Returns:
            bool: _description_
        """
        if the_type == str(int):
            try:
                _ = int(val)
            except (ValueError, TypeError):
                isok = False
        elif the_type == str(bool):
            ans = self.str_to_bool_or_none(val)
            if ans not in [True, False]:
                isok = False
        elif the_type == str(float):
            try:
                _ = float(val)
            except (ValueError, TypeError):
                isok = False
        elif the_type == str(str):
            try:
                _ = str(val)
            except (ValueError, TypeError):
                isok = False
        elif the_type == str(dict):
            isok = True
        elif the_type == str(list):
            try:
                isok = isinstance(self._str_to_list(val), list)
            except (ValueError, TypeError):
                isok = False
        return isok

    def string_to_list(self, astr: str) -> list:
        """Set string input to a list if the string resmbles a list with
        format [value1, Value2,.. , ValueN]

        Args:
            astr (str): String input

        Returns:
            list: String as list or None
        """
        return self._str_to_list(astr)

    def _str_to_list(self, astr: str) -> list:
        """Set string input to a list if the string resmbles a list with
        format [value1, Value2,.. , ValueN]

        Args:
            astr (str): String input

        Returns:
            list: String as list or None
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
            pass
        return None

    def set_type_to_value(self, val: any, typestr: str, subtype: str = "") -> any:
        """Set the specified type to a val, if possible

        Args:
            val (any): _description_
            typestr (str): _description_
            subtype (str, optional): For list inner values. Defaults to "".

        Returns:
            any: Value in specified type
        """
        try:
            if typestr == str(int):
                tyval = int(val)
            elif typestr == str(float):
                tyval = float(val)
            elif typestr == str(bool):
                if str(val).lower() in ["1", "true", "yes", "y", "t"]:
                    tyval = True
                elif str(val).lower() in ["0", "false", "no", "n", "f"]:
                    tyval = False
                else:
                    tyval = int(val)
            elif typestr == str(list):
                split = self._str_to_list(val)
                if split is not None:
                    tyval = []
                    for iii in split:
                        iiival = self.set_type_to_value(iii, subtype, "")
                        tyval.append(iiival)
                else:
                    tyval = str(val)
            else:
                tyval = str(val)
        except (TypeError, ValueError):
            tyval = str(val)
        return tyval
