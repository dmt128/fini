from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style as PPT_Style

__all__ = [
    'PromptSession', 'FileHistory', 'PPT_Style'
    'get_prompt_style_from_settings',
    'get_prompt_message_from_settings',
]

def get_prompt_style_from_settings(settings):
    promt_settings = settings['global']['prompt']
    return PPT_Style.from_dict( {
        '': "#" + promt_settings['cmd_colour'],
        'prompt': "#" + promt_settings['colour']
    })

def get_prompt_message_from_settings(settings):
    return [ 
        ('class:prompt', settings['global']['prompt']['message']), 
    ]