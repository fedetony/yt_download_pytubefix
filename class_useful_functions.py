"""
Class for checking restriction parameters
Programed by: F.Garcia
"""

class UsefulFunctions:
    """
    Some functions that can be used in several places

    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.__name__ = "Useful Functions"
    
    def get_dict_wo_key(self, dictionary: dict, key) -> dict:
        """Returns a **shallow** copy of the dictionary without a key."""
        _dict = dictionary.copy()
        _dict.pop(key, None)
        return _dict
    
    def get_dict_key_list(self,a_dict:dict)->list:
        """_summary_

        Args:
            a_dict (dict): dictionary

        Returns:
            list: list with keys
        """
        a_list=[]
        for key in a_dict:
            a_list.append(key)
        return a_list

    def is_id_in_list(self, an_id:any,list_of_ids:list) -> bool:
        """Check if the id is in the list of ids
        Args:
            an_id (any): id to check
            list_of_ids (list): list of ids

        Returns:
            bool: True if is in list
        """
        return an_id in list_of_ids


    def get_unique_id(self, desired_id:str,list_of_ids:list,prefix:str="UID_")->str:
        """Gets a unique id with a prefix that is not in the list of ids.

        Args:
            desired_id (_type_): 

        Returns:
            str: An id which is not taken.

        Args:
            desired_id (str): wanted id
            list_of_ids (list): list od ids to compare
            prefix (str, optional): Prefix for id naming "{prefix}#". Defaults to "UID_".

        Returns:
            str: Unique id using "{prefix}#" format
        """
        if not self.is_id_in_list(desired_id,list_of_ids) and desired_id != "" and desired_id is not None:
            return desired_id

        if desired_id is None or desired_id != "":
            desired_id = prefix
        iii = 1
        copydid = desired_id + str(iii)
        while self.is_id_in_list(copydid ,list_of_ids):
            iii = iii + 1
            copydid = desired_id + str(iii)
        return copydid
    
    def recursive_copy_dict(self, indict: any) -> dict:
        """Makes a copy of the dictionary recursively

        Args:
            indict (any): input dictionary

        Returns:
            dict: output dictionary
        """
        outdict = {}
        if isinstance(indict, dict):
            keylist = self.get_dict_key_list(indict)
            for iii in keylist:
                if isinstance(indict[iii], dict):
                    outdict.update({iii: self.recursive_copy_dict(indict[iii])})
                else:
                    outdict.update({iii: indict[iii]})
        else:
            return indict
        return outdict

    