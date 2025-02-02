from functools import wraps
from types import FunctionType
from Script.Core import cache_control, constant, game_type, get_text, text_handle
from Script.Design import attr_text
from Script.UI.Moudle import panel
from Script.Config import game_config, normal_config

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
width = normal_config.config_normal.text_width
""" 屏幕宽度 """
_: FunctionType = get_text._
""" 翻译api """


def handle_settle_behavior(character_id: int, now_time: int):
    """
    处理结算角色行为
    Keyword arguments:
    character_id -- 角色id
    now_time -- 结算的时间戳
    """
    now_character_data: game_type.Character = cache.character_data[character_id]
    status_data = game_type.CharacterStatusChange()
    start_time = now_character_data.behavior.start_time
    add_time = int((now_time - start_time) / 60)
    behavior_id = now_character_data.behavior.behavior_id
    if behavior_id in game_config.config_behavior_effect_data:
        for effect_id in game_config.config_behavior_effect_data[behavior_id]:
            constant.settle_behavior_effect_data[effect_id](
                character_id, add_time, status_data, now_time
            )
    change_character_favorability_for_time(character_id, now_time)
    change_character_social(character_id, status_data)
    now_judge = False
    if character_id:
        return
    if status_data is None:
        return
    if status_data.mana_point:
        now_judge = True
    if status_data.hit_point:
        now_judge = True
    if status_data.knowledge:
        now_judge = True
    if status_data.language:
        now_judge = True
    if status_data.status:
        now_judge = True
    if status_data.sex_experience:
        now_judge = True
    if status_data.target_change and not character_id:
        now_judge = True
    if now_judge:
        now_text_list = []
        if status_data.hit_point and round(status_data.hit_point, 2) != 0:
            now_text_list.append(
                _("体力:") + text_handle.number_to_symbol_string(round(status_data.hit_point, 2))
            )
        if status_data.mana_point and round(status_data.mana_point, 2) != 0:
            now_text_list.append(
                _("气力:") + text_handle.number_to_symbol_string(round(status_data.mana_point, 2))
            )
        if status_data.status:
            now_text_list.extend(
                [
                    f"{game_config.config_character_state[i].name}:{attr_text.get_value_text(status_data.status[i])}"
                    for i in status_data.status
                ]
            )
        if status_data.knowledge:
            now_text_list.extend(
                [
                    f"{game_config.config_knowledge[i].name}:{attr_text.get_value_text(status_data.knowledge[i])}"
                    for i in status_data.knowledge
                ]
            )
        if status_data.language:
            now_text_list.extend(
                [
                    f"{game_config.config_language[i].name}:{attr_text.get_value_text(status_data.language[i])}"
                    for i in status_data.language
                ]
            )
        if status_data.sex_experience:
            now_text_list.extend(
                [
                    game_config.config_organ[i].name
                    + _("经验:")
                    + text_handle.number_to_symbol_string(round(status_data.sex_experience[i], 2))
                    for i in status_data.sex_experience
                ]
            )
        if status_data.target_change:
            for target_character_id in status_data.target_change:
                if character_id and target_character_id:
                    continue
                target_change: game_type.TargetChange = status_data.target_change[
                    target_character_id
                ]
                target_data: game_type.Character = cache.character_data[target_character_id]
                now_text = f"\n{target_data.name}:"
                judge = 0
                if target_change.favorability:
                    now_text += _(" 对{character_name}好感").format(
                        character_name=now_character_data.name
                    ) + text_handle.number_to_symbol_string(round(target_change.favorability, 2))
                    judge = 1
                if target_change.new_social != target_change.old_social:
                    now_text += (
                        " "
                        + game_config.config_social_type[target_change.old_social].name
                        + "->"
                        + game_config.config_social_type[target_change.new_social].name
                    )
                    judge = 1
                if target_change.status:
                    for status_id in target_change.status:
                        if target_change.status[status_id]:
                            now_text += (
                                " "
                                + game_config.config_character_state[status_id].name
                                + text_handle.number_to_symbol_string(
                                    round(target_change.status[status_id], 2)
                                )
                            )
                            judge = 1
                if target_change.sex_experience:
                    for organ in target_change.sex_experience:
                        if target_change.sex_experience[organ]:
                            now_text += (
                                " "
                                + game_config.config_organ[organ].name
                                + _("经验:")
                                + text_handle.number_to_symbol_string(
                                    round(target_change.sex_experience[organ], 2)
                                )
                            )
                            judge = 1
                if judge:
                    now_text_list.append(now_text)
        now_panel = panel.LeftDrawTextListWaitPanel()
        now_panel.set(now_text_list, width, 8)
        return now_panel


def add_settle_behavior_effect(behavior_effect_id: int):
    """
    添加行为结算处理
    Keyword arguments:
    behavior_id -- 行为id
    """

    def decorator(func):
        @wraps(func)
        def return_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        constant.settle_behavior_effect_data[behavior_effect_id] = return_wrapper
        return return_wrapper

    return decorator


def get_cut_down_favorability_for_consume_time(consume_time: int):
    """
    从经过的时间计算出扣除的好感度
    Keyword arguments:
    consume_time -- 经过时间
    """
    if consume_time < 10:
        return consume_time
    if 10 <= consume_time < 100:
        return (consume_time - 9) * 10 + 9
    if 100 <= consume_time < 1000:
        return (consume_time - 99) * 100 + 909
    return (consume_time - 999) * 1000 + 90909


def change_character_favorability_for_time(character_id: int, now_time: int):
    """
    按最后社交时间扣除角色好感度
    Keyword arguments:
    character_id -- 角色id
    now_time -- 当前时间戳
    """
    character_data: game_type.Character = cache.character_data[character_id]
    for now_character in character_data.favorability:
        if character_data.favorability[now_character] <= 500:
            continue
        character_data.social_contact_last_time.setdefault(now_character, now_time)
        last_add_time = character_data.social_contact_last_time[now_character]
        now_consume_time = int((now_time - last_add_time) / 60)
        if now_consume_time < 60:
            continue
        now_cut_down = get_cut_down_favorability_for_consume_time(int(now_consume_time / 60))
        if now_character in character_data.social_contact_last_cut_down_time:
            last_cut_down_time = character_data.social_contact_last_cut_down_time[now_character]
            old_consume_time = int((last_cut_down_time - last_add_time) / 60)
            old_cut_down = get_cut_down_favorability_for_consume_time(int(old_consume_time / 60))
            now_cut_down -= old_cut_down
        character_data.favorability[now_character] -= now_cut_down
        if character_data.favorability[now_character] < 0:
            character_data.favorability[now_character] = 0
        change_character_social_now(now_character, character_id)


def change_character_social(character_id: int, change_data: game_type.CharacterStatusChange):
    """
    处理角色关系变化
    Keyword argumenys:
    character_id -- 状态变化数据所属角色id
    change_data -- 状态变化数据
    """
    for now_character in change_data.target_change:
        change_character_social_now(character_id, now_character, change_data)


def change_character_social_now(
    character_id: int,
    target_id: int,
    change_data: game_type.CharacterStatusChange = game_type.CharacterStatusChange(),
):
    """
    执行角色关系变化
    Keyword arguments:
    character_id -- 状态变化数据所属角色id
    target_id -- 关系变化角色id
    change_data -- 状态变化数据
    """
    if target_id in change_data.target_change:
        target_change: game_type.TargetChange = change_data.target_change[target_id]
    target_data: game_type.Character = cache.character_data[target_id]
    old_social = 0
    new_social = 0
    if character_id in target_data.social_contact_data:
        old_social = target_data.social_contact_data[character_id]
    target_data.favorability.setdefault(character_id, 0)
    now_favorability = target_data.favorability[character_id]
    new_social = get_favorability_social(now_favorability)
    if new_social != old_social:
        if target_id in change_data.target_change:
            target_change.old_social = old_social
            target_change.new_social = new_social
        target_data.social_contact.setdefault(old_social, set())
        target_data.social_contact.setdefault(new_social, set())
        if character_id in target_data.social_contact[old_social]:
            target_data.social_contact[old_social].remove(character_id)
        target_data.social_contact[new_social].add(character_id)
        target_data.social_contact_data[character_id] = new_social


def get_favorability_social(favorability: int) -> int:
    """
    获取好感度对应社交关系
    Keyword arguments:
    favorability -- 好感度
    Return arguments:
    int -- 社交关系
    """
    if favorability < 500:
        return 0
    if favorability < 10000:
        return 1
    if favorability < 200000:
        return 2
    if favorability < 4000000:
        return 3
    if favorability < 80000000:
        return 4
    return 5
