import core.data as data
import os
from core.pycfg import gamepath

def configData():
    configPath = os.path.join(gamepath,'data','core_cfg.json')
    configData = data._loadjson(configPath)
    return configData

game_name = configData()['game_name']
background_color = configData()['background_color']
font_color = configData()['font_color']
onbutton = configData()['onbutton_color']
font = configData()['font']
font_comment = configData()['font_comment']
font_size = configData()['font_size']
title_fontsize = configData()['title_fontsize']
font_dpi = configData()['font_dpi']
language = configData()['language']