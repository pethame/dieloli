import random
from functools import wraps
from types import FunctionType
from Script.Core import cache_control, game_type
from Script.Design import map_handle
from Script.UI.Moudle import draw
from Script.Config import normal_config, game_config

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """


def handle_talk(character_id):
    """
    处理行为结算对话
    Keyword arguments:
    character_id -- 角色id
    """
    character_data = cache.character_data[character_id]
    behavior_id = character_data.behavior.behavior_id
    now_talk_data = {}
    if behavior_id in game_config.config_talk_data:
        for talk_id in game_config.config_talk_data[behavior_id]:
            now_weight = 1
            for premise in game_config.config_talk_premise_data[talk_id]:
                now_add_weight = cache.handle_premise_data[premise](character_id)
                if now_add_weight:
                    now_weight += now_add_weight
                else:
                    now_weight = 0
                    break
            if now_weight:
                now_talk_data.setdefault(now_weight, set())
                now_talk_data[now_weight].add(talk_id)
    now_talk = ""
    if len(now_talk_data):
        talk_weight = max(list(now_talk_data.keys()))
        now_talk_id = random.choice(list(now_talk_data[talk_weight]))
        now_talk = game_config.config_talk[now_talk_id].context
    if now_talk != "":
        now_talk_text: str = now_talk
        scene_path = cache.character_data[0].position
        scene_path_str = map_handle.get_map_system_path_str_for_list(scene_path)
        scene_data = cache.scene_data[scene_path_str]
        scene_name = scene_data.scene_name
        player_data = cache.character_data[0]
        target_data = cache.character_data[character_data.target_character_id]
        now_talk_text = now_talk_text.format(
            NickName=character_data.nick_name,
            FoodName=character_data.behavior.food_name,
            Name=character_data.name,
            SceneName=scene_name,
            PlayerNickName=player_data.nick_name,
            TargetName=target_data.name,
        )
        now_draw = draw.LineFeedWaitDraw()
        now_draw.text = now_talk_text
        now_draw.width = normal_config.config_normal.text_width
        now_draw.draw()
