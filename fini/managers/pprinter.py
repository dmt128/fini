import re, operator, ast
from colorama import Fore, Back, Style, Cursor
from functools import reduce  # forward compatibility for Python 3
from .. import util


__all__ = [
    "pos", "Fore", "Back", "Style", "Cursor"
]

# Common
pos = lambda x, y: Cursor.POS(x, y)

class draw_ctx:
    class __panel_proxy:
        def __init__(self, parent, panel, panel_name, debug=False):
            self._parent = parent._panels
            pnl = self._parent.get(panel_name, None)
            if not pnl:
                raise Exception("Panel '{}' does not exist! Make sure you create it first using the 'add_panel' method. Aborting...".format(panel_name))
            
            self._panel = panel
            self._debug = debug
        
        def add_line(self, str_fmt, data=None, validate=True):
            num_lines = self._panel['num_lines'] + 1

            if self._panel['height']:
                if num_lines > self._panel['height']:
                    raise Exception("Adding this line will exceed the height of the panel.")
            
            self._panel['num_lines'] = num_lines

            line_name = "line_{}".format(num_lines)
            self._panel['lines'][line_name] = {
                'str_fmt': str_fmt,
                'data': data,
                'validate':validate,
            }
    
    class __view_proxy:
        def __init__(self, parent, view, view_name, debug=False):
            self._parent = parent
            vw = self._parent._views.get(view_name, None)
            if not vw:
                raise Exception("View '{}' does not exist! Make sure you create it first using the 'add_view' method. Aborting...".format(view_name))
            
            self._view  = view
            self._debug = debug

        def _extract_position(self, pos):
            if type(pos) is not list:
                raise Exception("The pos argument must be a list of two elements")
            
            if len(pos) != 2:
                raise Exception("The pos argument must be a list of two elements")
            
            pos_x = pos[0]
            pos_y = pos[1]

            if type(pos_x) is str:
                pos_x = util.misc.DictUtil.get_by_path(self._view['panels'], pos_x)
            
            if type(pos_y) is str:
                pos_y = util.misc.DictUtil.get_by_path(self._view['panels'], pos_y)
            
            return pos_x, pos_y

        def add_panel(self, panel_name, pos=[0, 0]):
            # Check to see if panel exists
            if not self._parent._panels.get(panel_name, None):
                raise Exception("Panel '{}' does not exist! Make sure you create it first using the 'add_panel' method. Aborting...".format(panel_name))

            self._view['num_panels'] += 1

            pos_x, pos_y = self._extract_position(pos)

            self._view['panels'][panel_name] = {
                'width': self._parent._panels[panel_name]['width'],
                'height': self._parent._panels[panel_name]['height'],
                'pos_x': pos_x,
                'pos_y': pos_y,
            }

    def __init__(self, dims=(None,  None), debug=False):
        self._width, self._height  = dims
        self._panels = {}
        self._views  = {}
        self._debug  = debug

    def add_panel(self, panel_name, dims=(None, None), pos=(None, None)):
        if not self._panels.get(panel_name):
            self._panels[panel_name] = {
                'width': dims[0],
                'height': dims[1],   # height in this context is essentially the total number of lines
                'pos_x': pos[0],
                'pos_y': pos[1],
                'num_lines': 0,
                'lines': {}
            }
        else:
            raise Exception("Panel {} already exists!".format(panel_name))

    def panel(self, panel_name):
        panel = self._panels.get(panel_name, None)
        if panel:
            return self.__panel_proxy(self, panel, panel_name, debug=self._debug)
        else:
            raise Exception("Panel '{}' does not exist. Make sure you have created it first using the 'add_panel' method.".format(panel_name))

    def add_view(self, view_name):
        if not self._views.get(view_name):
            self._views[view_name] = {
                'width': None,
                'height': None,
                'pos_x': 0,
                'pos_y': 0,
                'num_panels': 0,
                'panels': {}
            }
        else:
            raise Exception("View {} already exists!".format(view_name))

    def view(self, view_name):
        view = self._views.get(view_name, None)
        if view:
            return self.__view_proxy(self, view, view_name, debug=self._debug)
        else:
            raise Exception("View '{}' does not exist. Make sure you have created it first using the 'add_view' method.".format(view_name))


def _convert_value_str_to_type(value):
    if value and value[0] == "#":
        value = "\"{}\"".format(value)
    try:
        value = ast.literal_eval(value)
    except Exception:
        value = "\"{}\"".format(value)
        try:
            value = ast.literal_eval(value)
        except Exception:
            return None
        return value
    return value

def _get_var(data, var_name):
    var = util.misc.DictUtil.get_by_path(data, var_name)
    if type(var) is list:
        if var:
            return var[data["active_record"]]
        else:
            return 0.0
    else:
        return var

def _create_draw_lambda(rel_x, rel_y, fmt_color, fmt_str, line_data, var_name):
    if not var_name and not line_data:
        return lambda x, y, data: print( pos(x+rel_x, y+rel_y) + Style.RESET_ALL + fmt_color( None ) + fmt_str)
    elif line_data and not var_name:
        return lambda x, y, data: print( pos(x+rel_x, y+rel_y) + Style.RESET_ALL + fmt_color( None ) + fmt_str.format( var=line_data ) )
    elif var_name and not line_data:
        return lambda x, y, data: print( pos(x+rel_x, y+rel_y) + Style.RESET_ALL + fmt_color( _get_var(data, var_name) ) + fmt_str.format( var=_get_var(data, var_name) ) )
        # if var_name[-2:] == "[]":
        #     return lambda x, y, data: print( pos(x+rel_x, y+rel_y) + Style.RESET_ALL + fmt_color( util.misc.DictUtil.get_by_path(data, var_name[:-2])[data["active_record"]] ) + fmt_str.format( var=util.misc.DictUtil.get_by_path(data, var_name[:-2])[data["active_record"]] ) )
        # else:
        #     return lambda x, y, data: print( pos(x+rel_x, y+rel_y) + Style.RESET_ALL + fmt_color( util.misc.DictUtil.get_by_path(data, var_name)) ) + fmt_str.format( var=util.misc.DictUtil.get_by_path(data, var_name) ) )
    else:
        raise Exception("Unknown string format!")


def validate_panel(panel_name, panel, debug=False):
    regex_sline_pattern = "(?:@(.*)@)([.]*[^{]*)(\{.*\})?(.[^}]*)?"
    regex_variable_pattern = "\{(.*):([<>\^]?)(\d+(?:\.\d+)?)?(.*)\}"
    
    width  = panel['width'] #if panel['width'] else 0
    height = panel['height'] #if panel['height'] else 0
    lines  = panel['lines']
    
    final_panel_width  = 0
    final_panel_height = 0

    for lidx, line in enumerate(lines.values()):
        line_fmt  = line['str_fmt']
        line_data = line['data']
        validate  = line['validate']

        # First split the main lines into sublines (if any)
        sub_lines = line_fmt.split("!!")

        # Make sure line_data is in list format
        if type(line_data) is not list:
            line_data = [line_data]
        
        # Append dummy data to fit length of sublines
        if len(line_data) > len(sub_lines):
            raise Exception("Data cannot be more than the sublines! Aborting.")
        else:
            num_dummy_data_to_append = len(sub_lines) - len(line_data)
            for idx in range(num_dummy_data_to_append):
                line_data.append(None)

        line_width = 0
        for sidx, sline in enumerate(sub_lines):
            # Get main components of a subline
            _, color_fmt, pre_text, variable, post_text, _  = re.split(regex_sline_pattern, sline)
            color_fmt = color_fmt if color_fmt else ""
            pre_text  = pre_text if pre_text else ""
            post_text = post_text if post_text else ""

            if variable:
                # Get main components of variable in subline (if any)
                _, var_name, allignment, var_width, var_type, _ = re.split(regex_variable_pattern, variable)
                var_name   = var_name if var_name else ""                
                allignment = allignment if allignment else ""
                var_width  = var_width if var_width else ""
                var_type   = var_type if var_type else ""

            else:
                _, var_name, allignment, var_width, var_type, _ = (None, None, None, None, None, None)

            # Get width of printable components
            pre_w   = len(pre_text) if pre_text else 0
            var_w   = _convert_value_str_to_type( var_width.split(".")[0] if var_width else "0" )
            ldata_w = len(line_data[sidx]) if line_data[sidx] else 0
            post_w  = len(post_text) if post_text else 0
            sline_w = pre_w + var_w + ldata_w + post_w
            line_width += sline_w

            if width and validate:
                if sline_w > width:
                    raise Exception("Panel '{}', line # {}: Sub line # {} width ({} characters) is larger than panel's width ({} characters).".format(panel_name, lidx+1, sidx+1, sline_w, width))

        # Validate width
        # Update width only if line is included in the width validation (default case)
        if validate:
            # If the user has supplied panel dimensions, these should be respected 
            # by truncating the line
            if width:
                if line_width > width:
                    raise Exception("Panel '{}': Line # {} width ({} characters) is larger than panel's width ({} characters).".format(panel_name, lidx+1, line_width, width))
            else:
                if line_width > final_panel_width:
                    final_panel_width = line_width

        # Validate height
        final_panel_height += 1
        if height:
            if final_panel_height > height:
                raise Exception("Panel '{}': Line # {} makes panel '{}' lines in height which is larger than the pre-defined panel's height ({} lines).".format(panel_name, lidx+1, final_panel_height, height))
    
    if not width:
        panel['width']  = final_panel_width

    if not height:
        panel['height'] = final_panel_height
    
    if final_panel_height != panel['num_lines']:
        if debug:
            print("WARNING: NUmber of lines ({}) is different from calculated number of lines ({}). Adjusting.".format( panel['num_lines'], final_panel_height))
        panel['num_lines'] = final_panel_height


def validate_view(view_name, view, debug=False):
    # We need to find the width and height of the view
    x_left = 0
    x_right = 0
    y_top = 0
    y_bottom = 0

    for panel_name, panel in view["panels"].items():
        if panel["pos_x"] <= x_left:
            x_left = panel["pos_x"]
        if panel["pos_x"] + panel["width"] >= x_right:
            x_right = panel["pos_x"] + panel["width"]
        if panel["pos_y"] <= y_top:
            y_top = panel["pos_y"]
        if panel["pos_y"] + panel["height"] >= y_bottom:
            y_bottom = panel["pos_y"] + panel["height"]
        
    view["width"]  = x_right  - x_left
    view["height"] = y_bottom - y_top 

def generate_draw_commands(provider_id, panel, fmt, debug=False):
    regex_sline_pattern = "(?:@(.*)@)([.]*[^{]*)(\{.*\})?(.[^}]*)?"
    regex_variable_pattern = "\{(.*):([<>\^]?)(\d+(?:\.\d+)?)?(.*)\}"
    width     = panel['width']
    height    = panel['height']
    pos_x     = panel['pos_x']
    pos_y     = panel['pos_y']
    num_lines = panel['num_lines']
    lines     = panel['lines']

    if not width:
        raise Exception("Panel width is not set! Cannot continiue. Make sure you run 'validate_panel' first.")
    
    if not height:
        raise Exception("Panel height is not set! Cannot continiue. Make sure you run 'validate_panel' first.")
    
    if not num_lines:
        raise Exception("Panel num_lines is not set! Cannot continiue. Make sure you run 'validate_panel' first.")

    draw_commands = []
    rel_y = 0
    for line in lines.values():
        line_fmt  = line['str_fmt']
        line_data = line['data']

        # First split the main lines into sublines (if any)
        sub_lines = line_fmt.split("!!")

        # Make sure line_data is in list format
        if type(line_data) is not list:
            line_data = [line_data]
        
        # Append dummy data to fit length of sublines
        if len(line_data) > len(sub_lines):
            raise Exception("Data cannot be more than the sublines! Aborting.")
        else:
            num_dummy_data_to_append = len(sub_lines) - len(line_data)
            for idx in range(num_dummy_data_to_append):
                line_data.append(None)

        # For each subline create the draw command
        line_width = 0
        sub_lines_to_join = []
        
        rel_x = 0
        prev_sline_width = 0
        prev_color_fmt = ""
        for sidx, sline in enumerate(sub_lines):
            # Get main components of a subline
            _, color_fmt, pre_text, variable, post_text, _  = re.split(regex_sline_pattern, sline)
            color_fmt = ".".join([provider_id, color_fmt]) if color_fmt else ""
            pre_text  = pre_text if pre_text else ""
            post_text = post_text if post_text else ""
            if variable:
                # Get main components of variable in subline (if any)
                _, var_name, allignment, var_width, var_type, _ = re.split(regex_variable_pattern, variable)
                var_name   = var_name if var_name else ""                
                allignment = allignment if allignment else ""
                var_width  = var_width if var_width else ""
                var_type   = var_type if var_type else ""

                # try to estimate optimum var_width based on pre and post text of subline
                if not var_width:
                    pre_t = len(pre_text)
                    post_t = len(post_text)
                    var_width = "{}".format(width - (rel_x + pre_t + post_t) )

                # Create format string
                fmt_str = "{pre_text}{{var:{allignment}{var_width}{var_type}}}{post_text}".format(
                        pre_text=pre_text,
                        allignment=allignment,
                        var_width=var_width,
                        var_type=var_type,
                        post_text=post_text
                    ) 
            else:
                _, var_name, allignment, var_width, var_type, _ = (None, None, None, None, None, None)
                # Create format string
                fmt_str = "{pre_text}".format(
                        pre_text=pre_text
                    ) 

            # Create draw command and add to list of draw commands
            if debug:
                print("DEBUG: rel_x:{:<3} rel_y:{:<3}, fmt:{}".format(rel_x, rel_y, fmt_str))
            cmd = _create_draw_lambda(rel_x, rel_y, fmt._settings[color_fmt], fmt_str, line_data[sidx], var_name)

            # Append draw command to the list
            draw_commands.append(cmd)

            # Update relative x position for next subline
            var_w  = _convert_value_str_to_type( var_width.split(".")[0] if var_width else "0" )
            pre_w  = len(pre_text) if pre_text else 0
            post_w = len(post_text) if post_text else 0
            ldata_w = len(line_data[sidx]) if line_data[sidx] else 0
            rel_x +=  pre_w + var_w + post_w + ldata_w
            prev_color_fmt = color_fmt
        
        # Add any remaining trailing space to match the panel's width
        if rel_x < width:
            space_to_add = width - rel_x
            trailing_str = " "*space_to_add
            cmd = _create_draw_lambda(rel_x, rel_y, fmt._settings[prev_color_fmt], trailing_str, None, None)
            draw_commands.append(cmd)
        
        # Update relative y position for next subline
        rel_y += 1
    
    return draw_commands

