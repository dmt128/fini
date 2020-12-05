import os, operator
from functools import reduce  # forward compatibility for Python 3
from . import screen

__all__ = ['DictUtil']


class DictUtil:
    @staticmethod
    def _parse_items(items):
        if type(items) is str:
            return items.split(".")
        elif type(items) is not list:
            raise Exception("DictUtil ERROR: 'items' argument must be either a list of strings or a string path.")
        return items

    #================================================
    # Functions to deal with nested dictionaries
    #================================================
    # As described in https://stackoverflow.com/questions/14692690/access-nested-dictionary-items-via-a-list-of-keys
    @staticmethod
    def get_by_path(root, items, debug=False):
        """Access a nested object in root by item sequence."""
        try:
            items = DictUtil._parse_items(items)
            return reduce(operator.getitem, items, root)
        except Exception as e:
            if debug:
                print("get_by_path ERROR in {}: {}".format(".".join(items), e))
            return None
    
    @staticmethod
    def path_exists(root, items):
        try:
            items = DictUtil._parse_items(items)
            value = reduce(operator.getitem, items, root)
            if value is None:
                return False
            else:
                return True
        except:
            return False

    @staticmethod
    def set_by_path(root, items, value, debug=False):
        """Set a value in a nested object in root by item sequence."""
        try:
            items = DictUtil._parse_items(items)
            element = DictUtil.get_by_path(root, items[:-1])
            if element and element.get(items[-1], None) is not None:
                element[items[-1]] = value
            else:
                raise Exception("Item '{}' does not exist. Add it with 'add_by_path' method first".format(".".join(items)))
        except:
            raise Exception("Item '{}' does not exist. Add it with 'add_by_path' method first".format(".".join(items)))

    @staticmethod
    def del_by_path(root, items, debug=False):
        """Delete a key-value in a nested object in root by item sequence."""
        items = DictUtil._parse_items(items)
        element = DictUtil.get_by_path(root, items[:-1])
        if element and element.get(items[-1], None) is not None:
            del element[items[-1]]
        else:
            raise Exception("Item '{}' does not exist. Cannot delete.".format(".".join(items)))

    @staticmethod
    def add_by_path(root, entries, value, debug=False):
        entries = DictUtil._parse_items(entries)
        if entries:
            if root.get(entries[0], None) is None:
                root[entries[0]] = {}
                if entries[1:]:
                    DictUtil.add_by_path(root[entries[0]], entries[1:], value, debug)
                else:
                    root[entries[0]] = value
            else:
                if entries[1:]:
                    DictUtil.add_by_path(root[entries[0]], entries[1:], value, debug)
                else:
                    root[entries[0]] = value

    @staticmethod
    def get_max_key_length(dictionary, parent=None, max_length=0):
        
        if type(dictionary) is dict:
            for key, value in dictionary.items():
                if type(value) is dict:
                    if parent:
                        if len(parent + "." + key) > max_length:
                            max_length = len(parent + "." + key)

                        max_length = DictUtil.get_max_key_length(value, parent + "." + key, max_length)
                    else:
                        if len(key) > max_length:
                            max_length = len(key)
                        max_length = DictUtil.get_max_key_length(value, key, max_length)
                else:
                    if parent:
                        key = parent + "." + key
                    if len(key)>max_length:
                        max_length = len(key)
        else:
            if len(parent) > max_length:
                max_length = len(parent)
                
        return max_length

    @staticmethod
    def display(
        dictionary, 
        parent=None,
        title_msg="",
        max_key_len=30, 
        style_title=screen.Style.RESET_ALL + screen.Fore.CYAN + screen.Style.BRIGHT,
        style_key=screen.Style.RESET_ALL + screen.Fore.CYAN + screen.Style.NORMAL, 
        style_val=screen.Style.RESET_ALL + screen.Fore.CYAN + screen.Style.DIM):

        if type(dictionary) is dict:
            for key, value in dictionary.items():
                if type(value) is dict:
                    if parent:
                        DictUtil.display(
                            value, 
                            parent + "." + key,
                            title_msg=title_msg,
                            max_key_len=max_key_len,
                            style_title=style_title,
                            style_key=style_key,
                            style_val=style_val
                        )
                    else:
                        print(screen.Style.RESET_ALL + style_title + "\n{key} {title_msg}".format(key=key.upper(), title_msg=title_msg.upper()))
                        DictUtil.display(
                            value, 
                            key,
                            title_msg=title_msg,
                            max_key_len=max_key_len,
                            style_key=style_key,
                            style_val=style_val
                        )
                else:
                    if parent:
                        key = parent + "." + key
                    print(screen.Style.RESET_ALL + style_key + "{key:<{l}}: ".format(key=key, l=max_key_len) + style_val + "{val}".format(val=value))
        else:
            print(screen.Style.RESET_ALL + style_key + "{key:<{l}}: ".format(key=parent, l=max_key_len) + style_val + "{val}".format(val=dictionary))
        