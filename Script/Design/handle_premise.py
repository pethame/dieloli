import math
import datetime
from typing import List
from uuid import UUID
from functools import wraps
from types import FunctionType
from Script.Core import cache_control, constant, game_type
from Script.Design import map_handle, game_time, attr_calculation, character, course
from Script.Config import game_config

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """


def add_premise(premise: int) -> FunctionType:
    """
    添加前提
    Keyword arguments:
    premise -- 前提id
    Return arguments:
    FunctionType -- 前提处理函数对象
    """

    def decoraror(func):
        @wraps(func)
        def return_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        constant.handle_premise_data[premise] = return_wrapper
        return return_wrapper

    return decoraror


def handle_premise(premise: int, character_id: int) -> int:
    """
    调用前提id对应的前提处理函数
    Keyword arguments:
    premise -- 前提id
    character_id -- 角色id
    Return arguments:
    int -- 前提权重加成
    """
    if premise in constant.handle_premise_data:
        return constant.handle_premise_data[premise](character_id)
    return 0


@add_premise(constant.Premise.IN_CAFETERIA)
def handle_in_cafeteria(character_id: int) -> int:
    """
    校验角色是否处于取餐区中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if now_scene_data.scene_tag == "Cafeteria":
        return 1
    return 0


@add_premise(constant.Premise.IN_RESTAURANT)
def handle_in_restaurant(character_id: int) -> int:
    """
    校验角色是否处于就餐区中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if now_scene_data.scene_tag == "Restaurant":
        return 1
    return 0


@add_premise(constant.Premise.IN_BREAKFAST_TIME)
def handle_in_breakfast_time(character_id: int) -> int:
    """
    校验当前时间是否处于早餐时间段
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_time = game_time.get_sun_time(character_data.behavior.start_time)
    return (now_time == 4) * 100


@add_premise(constant.Premise.IN_LUNCH_TIME)
def handle_in_lunch_time(character_id: int) -> int:
    """
    校验当前是否处于午餐时间段
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_time = game_time.get_sun_time(character_data.behavior.start_time)
    return (now_time == 7) * 100


@add_premise(constant.Premise.IN_DINNER_TIME)
def handle_in_dinner_time(character_id: int) -> int:
    """
    校验当前是否处于晚餐时间段
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_time = game_time.get_sun_time(character_data.behavior.start_time)
    return (now_time == 9) * 100


@add_premise(constant.Premise.HUNGER)
def handle_hunger(character_id: int) -> int:
    """
    校验角色是否处于饥饿状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.status.setdefault(27, 0)
    if character_data.status[27] > 15:
        return math.floor(character_data.status[27]) * 10
    return 0


@add_premise(constant.Premise.HAVE_FOOD)
def handle_have_food(character_id: int) -> int:
    """
    校验角色是否拥有食物
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    food_index = 0
    for food_id in character_data.food_bag:
        if character_data.food_bag[food_id].eat and 27 in character_data.food_bag[food_id].feel:
            food_index += 1
    return food_index


@add_premise(constant.Premise.NOT_HAVE_FOOD)
def handle_not_have_food(character_id: int) -> int:
    """
    校验角色是否没有食物
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    food_index = 1
    for food_id in character_data.food_bag:
        if character_data.food_bag[food_id].eat and 27 in character_data.food_bag[food_id].feel:
            return 0
    return food_index


@add_premise(constant.Premise.HAVE_TARGET)
def handle_have_target(character_id: int) -> int:
    """
    校验角色是否有交互对象
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.target_character_id == character_id:
        return 0
    return 1


@add_premise(constant.Premise.TARGET_NO_PLAYER)
def handle_target_no_player(character_id: int) -> int:
    """
    校验角色目标对像是否不是玩家
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.target_character_id > 0:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_DRAW_ITEM)
def handle_have_item_by_tag_draw(character_id: int) -> int:
    """
    校验角色是否拥有绘画类道具
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    for item_id in game_config.config_item_tag_data["Draw"]:
        if item_id in character_data.item:
            return 1
    return 0


@add_premise(constant.Premise.HAVE_SHOOTING_ITEM)
def handle_have_item_by_tag_shooting(character_id: int) -> int:
    """
    校验角色是否拥有射击类道具
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    for item_id in game_config.config_item_tag_data["Shooting"]:
        if item_id in character_data.item:
            return 1
    return 0


@add_premise(constant.Premise.HAVE_GUITAR)
def handle_have_guitar(character_id: int) -> int:
    """
    校验角色是否拥有吉他
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if 4 in character_data.item:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_HARMONICA)
def handle_have_harmonica(character_id: int) -> int:
    """
    校验角色是否拥有口琴
    Keyword arguments:
    character_id --角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if 5 in character_data.item:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_BAM_BOO_FLUTE)
def handle_have_bamboogflute(character_id: int) -> int:
    """
    校验角色是否拥有竹笛
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if 6 in character_data.item:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_BASKETBALL)
def handle_have_basketball(character_id: int) -> int:
    """
    校验角色是否拥有篮球
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if 0 in character_data.item:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_FOOTBALL)
def handle_have_football(character_id: int) -> int:
    """
    校验角色是否拥有足球
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if 1 in character_data.item:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_TABLE_TENNIS)
def handle_have_tabletennis(character_id: int) -> int:
    """
    校验角色是否拥有乒乓球
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if 2 in character_data.item:
        return 1
    return 0


@add_premise(constant.Premise.IN_SWIMMING_POOL)
def handle_in_swimming_pool(character_id: int) -> int:
    """
    校验角色是否在游泳池中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if now_scene_data.scene_tag == "SwimmingPool":
        return 1
    return 0


@add_premise(constant.Premise.IN_CLASSROOM)
def handle_in_classroom(character_id: int) -> int:
    """
    校验角色是否处于所属教室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    if now_scene_str == character_data.classroom:
        return 1
    return 0


@add_premise(constant.Premise.IS_STUDENT)
def handle_is_student(character_id: int) -> int:
    """
    校验角色是否是学生
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.age <= 18:
        return 1
    return 0


@add_premise(constant.Premise.IS_TEACHER)
def handle_is_teacher(character_id: int) -> int:
    """
    校验角色是否是老师
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return character_id in cache.teacher_school_timetable


@add_premise(constant.Premise.IN_SHOP)
def handle_in_shop(character_id: int) -> int:
    """
    校验角色是否在商店中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if now_scene_data.scene_tag == "Shop":
        return 1
    return 0


@add_premise(constant.Premise.IN_SLEEP_TIME)
def handle_in_sleep_time(character_id: int) -> int:
    """
    校验角色当前是否处于睡觉时间
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_time: datetime.datetime = datetime.datetime.fromtimestamp(
        character_data.behavior.start_time, game_time.time_zone
    )
    if now_time.hour >= 22 or now_time.hour <= 4:
        if now_time.hour >= 22:
            return (now_time.hour - 21) * 100
        return now_time.hour * 100 + 200
    return 0


@add_premise(constant.Premise.IN_SIESTA_TIME)
def handle_in_siesta_time(character_id: int) -> int:
    """
    校验角色是否处于午休时间
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_time: datetime.datetime = datetime.datetime.fromtimestamp(
        character_data.behavior.start_time, game_time.time_zone
    )
    if now_time.hour >= 12 or now_time.hour <= 15:
        return 100
    return 0


@add_premise(constant.Premise.TARGET_IS_FUTA_OR_WOMAN)
def handle_target_is_futa_or_woman(character_id: int) -> int:
    """
    校验角色的目标对象性别是否为女性或扶她
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.sex in {1, 2}:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_IS_FUTA_OR_MAN)
def handle_target_is_futa_or_man(character_id: int) -> int:
    """
    校验角色的目标对象性别是否为男性或扶她
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.sex in {0, 1}:
        return 1
    return 0


@add_premise(constant.Premise.IS_MAN)
def handle_is_man(character_id: int) -> int:
    """
    校验角色是否是男性
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if not character_data.sex:
        return 1
    return 0


@add_premise(constant.Premise.IS_WOMAN)
def handle_is_woman(character_id: int) -> int:
    """
    校验角色是否是女性
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.sex == 1:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_SAME_SEX)
def handle_target_same_sex(character_id: int) -> int:
    """
    校验角色目标对像是否与自己性别相同
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.sex == character_data.sex:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_AGE_SIMILAR)
def handle_target_age_similar(character_id: int) -> int:
    """
    校验角色目标对像是否与自己年龄相差不大
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if character_data.age >= target_data.age - 2 and character_data.age <= target_data.age + 2:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_AVERAGE_HEIGHT_SIMILAR)
def handle_target_average_height_similar(character_id: int) -> int:
    """
    校验角色目标身高是否与平均身高相差不大
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    age_tem = attr_calculation.judge_age_group(target_data.age)
    average_height = cache.average_height_by_age[age_tem][target_data.sex]
    if (
        target_data.height.now_height >= average_height * 0.95
        and target_data.height.now_height <= average_height * 1.05
    ):
        return 1
    return 0


@add_premise(constant.Premise.TARGET_AVERAGE_HEIGHT_LOW)
def handle_target_average_height_low(character_id: int) -> int:
    """
    校验角色目标的身高是否低于平均身高
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    age_tem = attr_calculation.judge_age_group(target_data.age)
    average_height = cache.average_height_by_age[age_tem][target_data.sex]
    if target_data.height.now_height <= average_height * 0.95:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_IS_PLAYER)
def handle_target_is_player(character_id: int) -> int:
    """
    校验角色目标是否是玩家
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.target_character_id == 0:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_AVERGAE_STATURE_SIMILAR)
def handle_target_average_stature_similar(character_id: int) -> int:
    """
    校验角色目体型高是否与平均体型相差不大
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    age_tem = attr_calculation.judge_age_group(target_data.age)
    if age_tem in cache.average_bodyfat_by_age:
        average_bodyfat = cache.average_bodyfat_by_age[age_tem][target_data.sex]
        if (
            target_data.bodyfat >= average_bodyfat * 0.95
            and target_data.bodyfat <= average_bodyfat * 1.05
        ):
            return 1
    return 0


@add_premise(constant.Premise.TARGET_NOT_PUT_ON_UNDERWEAR)
def handle_target_not_put_underwear(character_id: int) -> int:
    """
    校验角色的目标对象是否没穿上衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if (1 not in target_data.put_on) or (target_data.put_on[1] == ""):
        return 1
    return 0


@add_premise(constant.Premise.TARGET_NOT_PUT_ON_SKIRT)
def handle_target_put_on_skirt(character_id: int) -> int:
    """
    校验角色的目标对象是否穿着短裙
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if (3 not in target_data.put_on) or (target_data.put_on[3] == ""):
        return 0
    return 1


@add_premise(constant.Premise.IS_PLAYER)
def handle_is_player(character_id: int) -> int:
    """
    校验是否是玩家角色
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if not character_id:
        return 1
    return 0


@add_premise(constant.Premise.NO_PLAYER)
def handle_no_player(character_id: int) -> int:
    """
    校验是否不是玩家角色
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if character_id:
        return 1
    return 0


@add_premise(constant.Premise.IN_PLAYER_SCENE)
def handle_in_player_scene(character_id: int) -> int:
    """
    校验角色是否与玩家处于同场景中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_character_data: game_type.Character = cache.character_data[character_id]
    if now_character_data.position == cache.character_data[0].position:
        return 1
    return 0


@add_premise(constant.Premise.LEAVE_PLAYER_SCENE)
def handle_leave_player_scene(character_id: int) -> int:
    """
    校验角色是否是从玩家场景离开
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_character_data: game_type.Character = cache.character_data[character_id]
    if (
        now_character_data.behavior.move_src == cache.character_data[0].position
        and now_character_data.behavior.move_target != cache.character_data[0].position
        and now_character_data.position != cache.character_data[0].position
    ):
        return 1
    return 0


@add_premise(constant.Premise.TARGET_IS_ADORE)
def handle_target_is_adore(character_id: int) -> int:
    """
    校验角色当前目标是否是自己的爱慕对象
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_id = character_data.target_character_id
    character_data.social_contact.setdefault(5, set())
    if target_id in character_data.social_contact[5]:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_IS_ADMIRE)
def handle_target_is_admire(character_id: int) -> int:
    """
    校验角色当前的目标是否是自己的恋慕对象
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_id = character_data.target_character_id
    character_data.social_contact.setdefault(4, set())
    if target_id in character_data.social_contact[4]:
        return 1
    return 0


@add_premise(constant.Premise.PLAYER_IS_ADORE)
def handle_player_is_adore(character_id: int) -> int:
    """
    校验玩家是否是当前角色的爱慕对象
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    character_data.social_contact.setdefault(5, set())
    if 0 in character_data.social_contact[5]:
        return 1
    return 0


@add_premise(constant.Premise.EAT_SPRING_FOOD)
def handle_eat_spring_food(character_id: int) -> int:
    """
    校验角色是否正在食用春药品质的食物
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.behavior.food_quality == 4:
        return 1
    return 0


@add_premise(constant.Premise.IS_HUMOR_MAN)
def handle_is_humor_man(character_id: int) -> int:
    """
    校验角色是否是一个幽默的人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    value = 0
    character_data: game_type.Character = cache.character_data[character_id]
    for i in {0, 1, 2, 5, 13, 14, 15, 16}:
        nature = character_data.nature[i]
        if nature > 50:
            value -= nature - 50
        else:
            value += 50 - nature
    value = max(value, 0)
    return value


@add_premise(constant.Premise.TARGET_IS_BEYOND_FRIENDSHIP)
def handle_target_is_beyond_friendship(character_id: int) -> int:
    """
    校验是否对目标抱有超越友谊的想法
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if (
        character_data.target_character_id in character_data.social_contact_data
        and character_data.social_contact_data[character_data.target_character_id] > 2
    ):
        return character_data.social_contact_data[character_data.target_character_id]
    return 0


@add_premise(constant.Premise.IS_BEYOND_FRIENDSHIP_TARGET)
def handle_is_beyond_friendship_target(character_id: int) -> int:
    """
    校验目标是否对自己抱有超越友谊的想法
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if (
        character_id in target_data.social_contact_data
        and target_data.social_contact_data[character_id] > 2
    ):
        return target_data.social_contact_data[character_id]
    return 0


@add_premise(constant.Premise.SCENE_HAVE_OTHER_CHARACTER)
def handle_scene_have_other_target(character_id: int) -> int:
    """
    校验场景里是否有其他角色
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    scene_path = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path]
    now_weight = (len(scene_data.character_list) - 1) / 10
    if 0 < now_weight < 1:
        now_weight = 1
    return now_weight


@add_premise(constant.Premise.NO_WEAR_UNDERWEAR)
def handle_no_wear_underwear(character_id: int) -> int:
    """
    校验角色是否没穿上衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if (
        1 not in character_data.put_on
        or character_data.put_on[1] is None
        or character_data.put_on[1] == ""
    ):
        return 1
    return 0


@add_premise(constant.Premise.NO_WEAR_UNDERPANTS)
def handle_no_wear_underpants(character_id: int) -> int:
    """
    校验角色是否没穿内裤
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if (
        7 not in character_data.put_on
        or character_data.put_on[7] is None
        or character_data.put_on[7] == ""
    ):
        return 1
    return 0


@add_premise(constant.Premise.NO_WEAR_BRA)
def handle_no_wear_bra(character_id: int) -> int:
    """
    校验角色是否没穿胸罩
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if (
        6 not in character_data.put_on
        or character_data.put_on[6] is None
        or character_data.put_on[6] == ""
    ):
        return 1
    return 0


@add_premise(constant.Premise.NO_WEAR_PANTS)
def handle_no_wear_pants(character_id: int) -> int:
    """
    校验角色是否没穿裤子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if (
        2 not in character_data.put_on
        or character_data.put_on[2] is None
        or character_data.put_on[2] == ""
    ):
        return 1
    return 0


@add_premise(constant.Premise.NO_WEAR_SKIRT)
def handle_no_wear_skirt(character_id: int) -> int:
    """
    校验角色是否没穿短裙
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if (
        3 not in character_data.put_on
        or character_data.put_on[3] is None
        or character_data.put_on[3] == ""
    ):
        return 1
    return 0


@add_premise(constant.Premise.NO_WEAR_SHOES)
def handle_no_wear_shoes(character_id: int) -> int:
    """
    校验角色是否没穿鞋子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if (
        4 not in character_data.put_on
        or character_data.put_on[4] is None
        or character_data.put_on[4] == ""
    ):
        return 1
    return 0


@add_premise(constant.Premise.NO_WEAR_SOCKS)
def handle_no_wear_socks(character_id: int) -> int:
    """
    校验角色是否没穿袜子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if (
        5 not in character_data.put_on
        or character_data.put_on[5] is None
        or character_data.put_on[5] == ""
    ):
        return 1
    return 0


@add_premise(constant.Premise.WANT_PUT_ON)
def handle_want_put_on(character_id: int) -> int:
    """
    校验角色是否想穿衣服
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return (not character_data.no_wear) * 10


@add_premise(constant.Premise.HAVE_UNDERWEAR)
def handle_have_underwear(character_id: int) -> int:
    """
    校验角色是否拥有上衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if 1 in character_data.clothing and character_data.clothing[1]:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_UNDERPANTS)
def handle_have_underpants(character_id: int) -> int:
    """
    校验角色是否拥有内裤
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if 7 in character_data.clothing and character_data.clothing[7]:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_BRA)
def handle_have_bra(character_id: int) -> int:
    """
    校验角色是否拥有胸罩
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if 6 in character_data.clothing and character_data.clothing[6]:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_PANTS)
def handle_have_pants(character_id: int) -> int:
    """
    校验角色是否拥有裤子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if 2 in character_data.clothing and character_data.clothing[2]:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_SKIRT)
def handle_have_skirt(character_id: int) -> int:
    """
    校验角色是否拥有短裙
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if 3 in character_data.clothing and character_data.clothing[3]:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_SHOES)
def handle_have_shoes(character_id: int) -> int:
    """
    校验角色是否拥有鞋子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if 4 in character_data.clothing and character_data.clothing[4]:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_SOCKS)
def handle_have_socks(character_id: int) -> int:
    """
    校验角色是否拥有袜子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if 5 in character_data.clothing and character_data.clothing[5]:
        return 1
    return 0


@add_premise(constant.Premise.IN_DORMITORY)
def handle_in_dormitory(character_id: int) -> int:
    """
    校验角色是否在宿舍中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_position = map_handle.get_map_system_path_str_for_list(character_data.position)
    return now_position == character_data.dormitory


@add_premise(constant.Premise.CHEST_IS_NOT_CLIFF)
def handle_chest_is_not_cliff(character_id: int) -> int:
    """
    校验角色胸围是否不是绝壁
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return attr_calculation.judge_chest_group(character_data.chest.now_chest)


@add_premise(constant.Premise.EXCELLED_AT_PLAY_MUSIC)
def handle_excelled_at_play_music(character_id: int) -> int:
    """
    校验角色是否擅长演奏乐器
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    weight = 1 + character_data.knowledge_interest[25]
    if 25 in character_data.knowledge:
        level = attr_calculation.get_experience_level_weight(character_data.knowledge[25])
        return weight * level
    return weight


@add_premise(constant.Premise.EXCELLED_AT_SINGING)
def handle_excelled_at_singing(character_id: int) -> int:
    """
    校验角色是否擅长演唱
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    weight = 1 + character_data.knowledge_interest[15]
    if 15 in character_data.knowledge:
        level = attr_calculation.get_experience_level_weight(character_data.knowledge[15])
        return weight * level
    return weight


@add_premise(constant.Premise.IN_MUSIC_CLASSROOM)
def handle_in_music_classroom(character_id: int) -> int:
    """
    校验角色是否处于音乐活动室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if now_scene_data.scene_tag == "MusicClassroom":
        return 1
    return 0


@add_premise(constant.Premise.NO_EXCELLED_AT_SINGING)
def handle_no_excelled_at_singing(character_id: int) -> int:
    """
    校验角色是否不擅长演唱
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    weight = 8
    if 15 in character_data.knowledge:
        level = attr_calculation.get_experience_level_weight(character_data.knowledge[15])
        return 8 - level
    return weight


@add_premise(constant.Premise.SCENE_NO_HAVE_OTHER_CHARACTER)
def handle_scene_no_have_other_character(character_id: int) -> int:
    """
    校验场景中没有自己外的其他角色
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    scene_path = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path]
    return len(scene_data.character_list) == 1


@add_premise(constant.Premise.TARGET_HEIGHT_LOW)
def handle_target_height_low(character_id: int) -> int:
    """
    校验交互对象身高是否低于自身身高
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.height.now_height < character_data.height.now_height:
        return character_data.height.now_height - target_data.height.now_height
    return 0


@add_premise(constant.Premise.TARGET_ADORE)
def handle_target_adore(character_id: int) -> int:
    """
    校验是否被交互对象爱慕
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.social_contact.setdefault(5, set())
    if character_id in target_data.social_contact[5]:
        return 1
    return 0


@add_premise(constant.Premise.NO_EXCELLED_AT_PLAY_MUSIC)
def handle_no_excelled_at_play_music(character_id: int) -> int:
    """
    校验角色是否不擅长演奏
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    weight = 8
    if 25 in character_data.knowledge:
        level = attr_calculation.get_experience_level_weight(character_data.knowledge[25])
        return 8 - level
    return weight


@add_premise(constant.Premise.ARROGANT_HEIGHT)
def handle_arrogant_height(character_id: int) -> int:
    """
    校验角色是否傲慢情绪高涨
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.status.setdefault(15, 0)
    return int(character_data.status[15] / 10)


@add_premise(constant.Premise.IS_LIVELY)
def handle_is_lively(character_id: int) -> int:
    """
    校验角色是否是一个活跃的人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.nature[0] >= 50


@add_premise(constant.Premise.IS_INFERIORITY)
def handle_is_inferiority(character_id: int) -> int:
    """
    校验角色是否是一个自卑的人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.nature[16] < 50


@add_premise(constant.Premise.IS_AUTONOMY)
def handle_is_autonomy(character_id: int) -> int:
    """
    校验角色是否是一个自律的人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.nature[7] >= 50


@add_premise(constant.Premise.SCENE_CHARACTER_ONLY_PLAYER_AND_ONE)
def handle_scene_character_only_player_and_one(character_id: int) -> int:
    """
    校验场景中是否只有包括玩家在内的两个角色
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data: game_type.Scene = cache.scene_data[now_scene_str]
    if 0 not in now_scene_data.character_list:
        return 0
    return len(now_scene_data.character_list) == 2


@add_premise(constant.Premise.IS_SOLITARY)
def handle_is_solitary(character_id: int) -> int:
    """
    校验角色是否是一个孤僻的人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.nature[1] < 50


@add_premise(constant.Premise.NO_BEYOND_FRIENDSHIP_TARGET)
def handle_no_beyond_friendship_target(character_id: int) -> int:
    """
    校验目标是否对自己没有超越友谊的想法
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if (
        character_id in target_data.social_contact_data
        and target_data.social_contact_data[character_id] < 3
    ):
        return 5 - target_data.social_contact_data[character_id]
    if character_id not in target_data.social_contact_data:
        return 5
    return 0


@add_premise(constant.Premise.TARGET_IS_HEIGHT)
def handle_target_is_height(character_id: int) -> int:
    """
    校验角色目标身高是否与平均身高相差不大
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.height.now_height >= character_data.height.now_height * 1.05:
        return 1
    return 0


@add_premise(constant.Premise.BEYOND_FRIENDSHIP_TARGET_IN_SCENE)
def handle_beyond_friendship_target_in_scene(character_id: int) -> int:
    """
    校验是否对场景中某个角色抱有超越友谊的想法
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data: game_type.Scene = cache.scene_data[now_scene_str]
    for i in {3, 4, 5}:
        character_data.social_contact.setdefault(i, set())
        for c in character_data.social_contact[i]:
            if c in now_scene_data.character_list:
                return 1
    return 0


@add_premise(constant.Premise.HYPOSTHENIA)
def handle_hyposthenia(character_id: int) -> int:
    """
    校验角色是否体力不足
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_weight = int((character_data.hit_point_max - character_data.hit_point) / 5)
    now_weight += int((character_data.mana_point_max - character_data.mana_point) / 10)
    return now_weight


@add_premise(constant.Premise.PHYSICAL_STRENGHT)
def handle_physical_strenght(character_id: int) -> int:
    """
    校验角色是否体力充沛
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_weight = int((character_data.hit_point_max / 2 - character_data.hit_point) / 5)
    now_weight += int((character_data.mana_point_max / 2 - character_data.mana_point) / 10)
    now_weight = max(now_weight, 0)
    return now_weight


@add_premise(constant.Premise.IS_INDULGE)
def handle_is_indulge(character_id: int) -> int:
    """
    校验角色是否是一个放纵的人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.nature[7] < 50


@add_premise(constant.Premise.IN_FOUNTAIN)
def handle_in_fountain(character_id: int) -> int:
    """
    校验角色是否在喷泉场景中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.position == ["8"]


@add_premise(constant.Premise.TARGET_IS_SOLITARY)
def handle_target_is_solitary(character_id: int) -> int:
    """
    校验交互对象是否是一个孤僻的人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.nature[1] < 50


@add_premise(constant.Premise.TARGET_CHEST_IS_CLIFF)
def handle__target_chest_is_cliff(character_id: int) -> int:
    """
    校验交互对象胸围是否是绝壁
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not attr_calculation.judge_chest_group(target_data.chest.now_chest)


@add_premise(constant.Premise.IS_ENTHUSIASM)
def handle_is_enthusiasm(character_id: int) -> int:
    """
    校验角色是否是一个热情的人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.nature[15] >= 50


@add_premise(constant.Premise.TARGET_ADMIRE)
def handle_target_admire(character_id: int) -> int:
    """
    校验角色是否被交互对象恋慕
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.social_contact.setdefault(4, set())
    if character_id in target_data.social_contact[4]:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_AVERAGE_STATURE_HEIGHT)
def handle_target_average_stature_height(character_id: int) -> int:
    """
    校验角色目体型高是否比平均体型更胖
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    age_tem = attr_calculation.judge_age_group(target_data.age)
    if age_tem in cache.average_bodyfat_by_age:
        average_bodyfat = cache.average_bodyfat_by_age[age_tem][target_data.sex]
        if target_data.bodyfat > average_bodyfat * 1.05:
            return 1
    return 0


@add_premise(constant.Premise.TARGET_NO_FIRST_KISS)
def handle_target_no_first_kiss(character_id: int) -> int:
    """
    校验交互对象是否初吻还在
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.first_kiss == -1


@add_premise(constant.Premise.NO_FIRST_KISS)
def handle_no_first_kiss(character_id: int) -> int:
    """
    校验是否初吻还在
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.first_kiss == -1


@add_premise(constant.Premise.IS_TARGET_FIRST_KISS)
def handle_is_target_first_kiss(character_id: int) -> int:
    """
    校验是否是交互对象的初吻对象
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return character_id == target_data.first_kiss


@add_premise(constant.Premise.HAVE_OTHER_TARGET_IN_SCENE)
def handle_have_other_target_in_scene(character_id: int) -> int:
    """
    校验场景中是否有自己和交互对象以外的其他人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    return len(scene_data.character_list) > 2


@add_premise(constant.Premise.NO_HAVE_OTHER_TARGET_IN_SCENE)
def handle_no_have_other_target_in_scene(character_id: int) -> int:
    """
    校验场景中是否没有自己和交互对象以外的其他人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    return len(scene_data.character_list) <= 2


@add_premise(constant.Premise.TARGET_HAVE_FIRST_KISS)
def handle_target_have_first_kiss(character_id: int) -> int:
    """
    校验交互对象是否初吻不在了
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.first_kiss != -1


@add_premise(constant.Premise.HAVE_FIRST_KISS)
def handle_have_first_kiss(character_id: int) -> int:
    """
    校验是否初吻不在了
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.first_kiss != -1


@add_premise(constant.Premise.HAVE_LIKE_TARGET)
def handle_have_like_target(character_id: int) -> int:
    """
    校验是否有喜欢的人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.social_contact.setdefault(4, set())
    character_data.social_contact.setdefault(5, set())
    return len(character_data.social_contact[4]) + len(character_data.social_contact[5])


@add_premise(constant.Premise.HAVE_LIKE_TARGET_IN_SCENE)
def handle_have_like_target_in_scene(character_id: int) -> int:
    """
    校验是否有喜欢的人在场景中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.social_contact.setdefault(4, set())
    character_data.social_contact.setdefault(5, set())
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    character_list = []
    for i in {4, 5}:
        for c in character_data.social_contact[i]:
            if c in scene_data.character_list:
                character_list.append(c)
    return len(character_list)


@add_premise(constant.Premise.TARGET_IS_STUDENT)
def handle_target_is_student(character_id: int) -> int:
    """
    校验交互对象是否是学生
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.age <= 18


@add_premise(constant.Premise.TARGET_IS_ASTUTE)
def handle_target_is_astute(character_id: int) -> int:
    """
    校验交互对象是否是一个机敏的人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.nature[11] >= 50


@add_premise(constant.Premise.TARGET_IS_INFERIORITY)
def handle_target_is_inferiority(character_id: int) -> int:
    """
    校验交互对象是否是一个自卑的人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.nature[16] < 50


@add_premise(constant.Premise.TARGET_IS_ENTHUSIASM)
def handle_target_is_enthusiasm(character_id: int) -> int:
    """
    校验交互对象是否是一个热情的人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.nature[15] >= 50


@add_premise(constant.Premise.TARGET_IS_SELF_CONFIDENCE)
def handle_target_is_self_confidence(character_id: int) -> int:
    """
    校验交互对象是否是一个自信的人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.nature[16] >= 50


@add_premise(constant.Premise.IS_ASTUTE)
def handle_is_astute(character_id: int) -> int:
    """
    校验是否是一个机敏的人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.nature[11] >= 50


@add_premise(constant.Premise.TARGET_IS_HEAVY_FEELING)
def handle_target_is_heavy_feeling(character_id: int) -> int:
    """
    校验交互对象是否是一个重情的人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.nature[5] >= 50


@add_premise(constant.Premise.TARGET_NO_FIRST_HAND_IN_HAND)
def handle_target_no_first_hand_in_hand(character_id: int) -> int:
    """
    校验交互对象是否没有牵过手
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.first_hand_in_hand == -1


@add_premise(constant.Premise.NO_FIRST_HAND_IN_HAND)
def handle_no_first_hand_in_hand(character_id: int) -> int:
    """
    校验是否没有牵过手
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.first_hand_in_hand == -1


@add_premise(constant.Premise.IS_HEAVY_FEELING)
def handle_is_heavy_feeling(character_id: int) -> int:
    """
    校验是否是一个重情的人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.nature[5] >= 50


@add_premise(constant.Premise.HAVE_LIKE_TARGET_NO_FIRST_KISS)
def handle_have_like_target_no_first_kiss(character_id: int) -> int:
    """
    校验是否有自己喜欢的人的初吻还在
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_index = 0
    for i in {4, 5}:
        character_data.social_contact.setdefault(i, set())
        for c in character_data.social_contact[i]:
            c_data: game_type.Character = cache.character_data[c]
            if c_data.first_kiss == -1:
                character_index += 1
    return character_index


@add_premise(constant.Premise.TARGET_IS_APATHY)
def handle_target_is_apathy(character_id: int) -> int:
    """
    校验交互对象是否是一个冷漠的人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.nature[15] < 50


@add_premise(constant.Premise.TARGET_UNARMED_COMBAT_IS_HIGHT)
def handle_target_unarmed_combat_is_hight(character_id: int) -> int:
    """
    校验交互对象徒手格斗技能是否比自己高
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    character_data.knowledge.setdefault(32, 0)
    target_data.knowledge.setdefault(32, 0)
    character_level = attr_calculation.get_experience_level_weight(character_data.knowledge[32])
    target_level = attr_calculation.get_experience_level_weight(target_data.knowledge[32])
    if target_level > character_level:
        return target_level - character_level
    return 0


@add_premise(constant.Premise.TARGET_DISGUST_IS_HIGHT)
def handle_target_disgust_is_hight(character_id: int) -> int:
    """
    校验交互对象是否反感情绪高涨
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.status.setdefault(12, 0)
    return target_data.status[12]


@add_premise(constant.Premise.TARGET_LUST_IS_HIGHT)
def handle_target_lust_is_hight(character_id: int) -> int:
    """
    校验交互对象是否色欲高涨
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.status.setdefault(21, 0)
    return target_data.status[21]


@add_premise(constant.Premise.TARGET_IS_WOMAN)
def handle_target_is_woman(character_id: int) -> int:
    """
    校验交互对象是否是女性
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.sex == 1


@add_premise(constant.Premise.TARGET_IS_NAKED)
def handle_target_is_naked(character_id: int) -> int:
    """
    校验交互对象是否一丝不挂
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    for i in target_data.put_on:
        if isinstance(target_data.put_on[i], UUID):
            return 0
    return 1


@add_premise(constant.Premise.TARGET_CLITORIS_LEVEL_IS_HIGHT)
def handle_target_clitoris_is_hight(character_id: int) -> int:
    """
    校验交互对象是否阴蒂开发度高
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.sex_experience.setdefault(2, 0)
    return attr_calculation.get_experience_level_weight(target_data.sex_experience[2])


@add_premise(constant.Premise.TARGET_IS_MAN)
def handle_target_is_man(character_id: int) -> int:
    """
    校验交互对象是否是男性
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.sex


@add_premise(constant.Premise.SEX_EXPERIENCE_IS_HIGHT)
def handle_sex_experience_is_hight(character_id: int) -> int:
    """
    校验角色是否性技熟练
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.knowledge.setdefault(9, 0)
    return attr_calculation.get_experience_level_weight(character_data.knowledge[9])


@add_premise(constant.Premise.IS_COLLECTION_SYSTEM)
def handle_is_collection_system(character_id: int) -> int:
    """
    校验玩家是否已启用收藏模式
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return cache.is_collection


@add_premise(constant.Premise.UN_COLLECTION_SYSTEM)
def handle_un_collection_system(character_id: int) -> int:
    """
    校验玩家是否未启用收藏模式
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not cache.is_collection


@add_premise(constant.Premise.TARGET_IS_COLLECTION)
def handle_target_is_collection(character_id: int) -> int:
    """
    校验交互对象是否已被玩家收藏
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    player_data: game_type.Character = cache.character_data[0]
    return character_data.target_character_id in player_data.collection_character


@add_premise(constant.Premise.TARGET_IS_NOT_COLLECTION)
def handle_target_is_not_collection(character_id: int) -> int:
    """
    校验交互对象是否未被玩家收藏
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    player_data: game_type.Character = cache.character_data[0]
    return character_data.target_character_id not in player_data.collection_character


@add_premise(constant.Premise.TARGET_IS_LIVE)
def handle_target_is_live(character_id: int) -> int:
    """
    校验交互对象是否未死亡
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.dead


@add_premise(constant.Premise.THIRSTY)
def handle_thirsty(character_id: int) -> int:
    """
    校验角色是否处于口渴状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.status.setdefault(28, 0)
    return math.floor(character_data.status[28]) * 10


@add_premise(constant.Premise.HAVE_DRINKS)
def handle_have_drinks(character_id: int) -> int:
    """
    校验角色背包中是否有饮料
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    drinks_list = []
    for food_id in character_data.food_bag:
        now_food: game_type.Food = character_data.food_bag[food_id]
        if now_food.eat and 28 in now_food.feel:
            drinks_list.append(food_id)
    return len(drinks_list)


@add_premise(constant.Premise.NO_HAVE_DRINKS)
def handle_no_have_drinks(character_id: int) -> int:
    """
    校验角色背包中是否没有饮料
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    for food_id in character_data.food_bag:
        now_food: game_type.Food = character_data.food_bag[food_id]
        if now_food.eat and 28 in now_food.feel:
            return 0
    return 1


@add_premise(constant.Premise.ATTEND_CLASS_TODAY)
def handle_attend_class_today(character_id: int) -> int:
    """
    校验角色今日是否需要上课
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return game_time.judge_attend_class_today(character_id)


@add_premise(constant.Premise.APPROACHING_CLASS_TIME)
def handle_approaching_class_time(character_id: int) -> int:
    """
    校验角色是否临近上课时间
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_time: datetime.datetime = datetime.datetime.fromtimestamp(
        character_data.behavior.start_time
    )
    now_time_value = now_time.hour * 100 + now_time.minute
    next_time = 0
    if character_data.age <= 18:
        school_id = 0
        if character_data.age in range(13, 16):
            school_id = 1
        elif character_data.age in range(16, 19):
            school_id = 2
        for session_id in game_config.config_school_session_data[school_id]:
            session_config = game_config.config_school_session[session_id]
            if (
                session_config.start_time > now_time_value
                and next_time == 0
                or session_config.start_time < next_time
            ):
                next_time = session_config.start_time
        if next_time == 0:
            return 0
    if character_id in cache.teacher_school_timetable:
        now_week = now_time.weekday()
        timetable_list: List[game_type.TeacherTimeTable] = cache.teacher_school_timetable[
            character_id
        ]
        for timetable in timetable_list:
            if timetable.week_day != now_week:
                continue
            if timetable.time > now_time_value and next_time == 0 or timetable.time < next_time:
                next_time = timetable.time
        if next_time == 0:
            return 0
    next_value = int(next_time / 100) * 60 + next_time % 100
    now_value = int(now_time_value / 100) * 60 + now_time_value % 100
    add_time = next_value - now_value
    if add_time > 30:
        return 0
    add_time = max(add_time, 1)
    return 3000 / (add_time * 10)


@add_premise(constant.Premise.IN_CLASS_TIME)
def handle_in_class_time(character_id: int) -> int:
    """
    校验角色是否处于上课时间
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return character.judge_character_in_class_time(character_id) * 500


@add_premise(constant.Premise.NO_IN_CLASSROOM)
def handle_no_in_classroom(character_id: int) -> int:
    """
    校验角色是否不在所属教室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    if now_scene_str != character_data.classroom:
        return 1
    return 0


@add_premise(constant.Premise.TEACHER_NO_IN_CLASSROOM)
def handle_teacher_no_in_classroom(character_id: int) -> int:
    """
    校验角色所属班级的老师是否不在教室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if not game_time.judge_attend_class_today(character_id):
        return 1
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.classroom == "":
        return 1
    classroom: game_type.Scene = cache.scene_data[character_data.classroom]
    now_time: datetime.datetime = datetime.datetime.fromtimestamp(
        character_data.behavior.start_time, game_time.time_zone
    )
    now_week = now_time.weekday()
    school_id, phase = course.get_character_school_phase(character_id)
    now_time_value = now_time.hour * 100 + now_time.minute
    if now_week in cache.course_time_table_data[school_id][phase]:
        now_course_index = 0
        next_time = 0
        for session_config_id in game_config.config_school_session_data[school_id]:
            session_config = game_config.config_school_session[session_config_id]
            if not next_time:
                if session_config.start_time >= now_time_value:
                    next_time = session_config.start_time
                    now_course_index = session_config.session
                elif session_config.end_time >= now_time_value:
                    next_time = session_config.end_time
                    now_course_index = session_config.session
                continue
            if (
                session_config.start_time >= now_time_value
                and session_config.start_time < next_time
            ):
                next_time = session_config.start_time
                now_course_index = session_config.session
            elif session_config.end_time >= now_time_value and session_config.end_time < next_time:
                next_time = session_config.start_time
                now_course_index = session_config.session
        if school_id not in cache.class_timetable_teacher_data:
            return 1
        if phase not in cache.class_timetable_teacher_data[school_id]:
            return 1
        if character_data.classroom not in cache.class_timetable_teacher_data[school_id][phase]:
            return 1
        if (
            now_week
            not in cache.class_timetable_teacher_data[school_id][phase][character_data.classroom]
        ):
            return 1
        if (
            now_course_index
            not in cache.class_timetable_teacher_data[school_id][phase][character_data.classroom][
                now_week
            ]
        ):
            return 1
        now_teacher = cache.class_timetable_teacher_data[school_id][phase][
            character_data.classroom
        ][now_week][now_course_index]
        if now_teacher not in classroom.character_list:
            return 1
        return 0
    return 1


@add_premise(constant.Premise.TEACHER_IN_CLASSROOM)
def handle_teacher_in_classroom(character_id: int) -> int:
    """
    校验角色所属班级的老师是否在教室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_teacher_no_in_classroom(character_id)


@add_premise(constant.Premise.IS_NAKED)
def handle_is_naked(character_id: int) -> int:
    """
    校验角色是否一丝不挂
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    for i in character_data.put_on:
        if isinstance(character_data.put_on[i], UUID):
            return 0
    return 1


@add_premise(constant.Premise.IS_BEYOND_FRIENDSHIP_TARGET_IN_SCENE)
def handle_is_beyond_friendship_target_in_scene(character_id: int) -> int:
    """
    校验场景中是否有角色对自己抱有超越友谊的想法
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    now_weight = 0
    for now_character in scene_data.character_list:
        if now_character == character_id:
            continue
        now_character_data: game_type.Character = cache.character_data[now_character]
        if (
            character_id in now_character_data.social_contact_data
            and now_character_data.social_contact_data[character_id] > 2
        ):
            now_weight += now_character_data.social_contact_data[character_id]
    return now_weight


@add_premise(constant.Premise.HAVE_STUDENTS_IN_CLASSROOM)
def handle_have_students_in_classroom(character_id: int) -> int:
    """
    校验是否有所教班级的学生在教室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.age <= 18:
        return 0
    if character_id not in cache.teacher_school_timetable:
        return 0
    now_date: datetime.datetime = datetime.datetime.fromtimestamp(
        character_data.behavior.start_time
    )
    now_week = now_date.weekday()
    now_classroom = []
    now_time = 0
    timetable_list: List[game_type.TeacherTimeTable] = cache.teacher_school_timetable[character_id]
    now_time_value = now_date.hour * 100 + now_date.minute
    for timetable in timetable_list:
        if timetable.week_day != now_week:
            continue
        if now_time == 0:
            if timetable.time >= now_time_value:
                now_time = timetable.time
                now_classroom = timetable.class_room
            elif timetable.end_time >= now_time_value:
                now_time = timetable.end_time
                now_classroom = timetable.class_room
                break
            continue
        if timetable.time >= now_time_value and timetable.time < now_time:
            now_time = timetable.time
            now_classroom = timetable.class_room
            continue
        if timetable.end_time >= now_time_value and timetable.end_time < now_time:
            now_time = timetable.end_time
            now_classroom = timetable.class_room
    now_room_path_str = map_handle.get_map_system_path_str_for_list(now_classroom)
    now_scene_data: game_type.Scene = cache.scene_data[now_room_path_str]
    class_data = cache.classroom_students_data[now_room_path_str]
    return len(class_data & now_scene_data.character_list)


@add_premise(constant.Premise.GOOD_AT_ELOQUENCE)
def handle_good_at_eloquence(character_id: int) -> int:
    """
    校验角色是否擅长口才
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    weight = 1 + character_data.knowledge_interest[12]
    if 12 in character_data.knowledge:
        level = attr_calculation.get_experience_level_weight(character_data.knowledge[12])
        return weight * level
    return weight


@add_premise(constant.Premise.GOOD_AT_LITERATURE)
def handle_good_at_literature(character_id: int) -> int:
    """
    校验角色是否擅长文学
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    weight = 1 + character_data.knowledge_interest[2]
    if 2 in character_data.knowledge:
        level = attr_calculation.get_experience_level_weight(character_data.knowledge[2])
        return weight * level
    return weight


@add_premise(constant.Premise.GOOD_AT_WRITING)
def handle_good_at_writing(character_id: int) -> int:
    """
    校验角色是否擅长写作
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    weight = 1 + character_data.knowledge_interest[28]
    if 28 in character_data.knowledge:
        level = attr_calculation.get_experience_level_weight(character_data.knowledge[28])
        return weight * level
    return weight


@add_premise(constant.Premise.GOOD_AT_DRAW)
def handle_good_at_draw(character_id: int) -> int:
    """
    校验角色是否擅长绘画
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    weight = 1 + character_data.knowledge_interest[13]
    if 13 in character_data.knowledge:
        level = attr_calculation.get_experience_level_weight(character_data.knowledge[13])
        return weight * level
    return weight


@add_premise(constant.Premise.GOOD_AT_ART)
def handle_good_at_art(character_id: int) -> int:
    """
    校验角色是否擅长艺术
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    weight = 1 + character_data.knowledge_interest[5]
    if 5 in character_data.knowledge:
        level = attr_calculation.get_experience_level_weight(character_data.knowledge[5])
        return weight * level
    return weight


@add_premise(constant.Premise.TARGET_LITTLE_KNOWLEDGE_OF_RELIGION)
def handle_target_little_knowledge_of_religion(character_id: int) -> int:
    """
    校验交互对象是否对宗教一知半解
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if 7 in target_data.knowledge:
        level = attr_calculation.get_experience_level_weight(target_data.knowledge[7])
        if level <= 2:
            return 1
    return 0


@add_premise(constant.Premise.TARGET_LITTLE_KNOWLEDGE_OF_FAITH)
def handle_target_little_knowledge_of_faith(character_id: int) -> int:
    """
    校验交互对象是否对信仰一知半解
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if 8 in target_data.knowledge:
        level = attr_calculation.get_experience_level_weight(target_data.knowledge[8])
        if level <= 2:
            return 1
    return 0


@add_premise(constant.Premise.TARGET_LITTLE_KNOWLEDGE_OF_ASTRONOMY)
def handle_target_little_knowledge_of_astronomy(character_id: int) -> int:
    """
    校验交互对象是否对天文学一知半解
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if 53 in target_data.knowledge:
        level = attr_calculation.get_experience_level_weight(target_data.knowledge[53])
        if level <= 2:
            return 1
    return 0


@add_premise(constant.Premise.TARGET_LITTLE_KNOWLEDGE_OF_ASTROLOGY)
def handle_target_little_knowledge_of_astrology(character_id: int) -> int:
    """
    校验交互对象是否对占星学一知半解
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if 75 in target_data.knowledge:
        level = attr_calculation.get_experience_level_weight(target_data.knowledge[75])
        if level <= 2:
            return 1
    return 0


@add_premise(constant.Premise.RICH_EXPERIENCE_IN_SEX)
def handle_rich_experience_in_sex(character_id: int) -> int:
    """
    校验角色是否性经验丰富
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_exp = 0
    for i in character_data.sex_experience:
        now_exp += character_data.sex_experience[i]
    return attr_calculation.get_experience_level_weight(now_exp)


@add_premise(constant.Premise.TARGET_IS_SLEEP)
def handle_target_is_sleep(character_id: int) -> int:
    """
    校验交互对象是否正在睡觉
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.state == constant.CharacterStatus.STATUS_SLEEP


@add_premise(constant.Premise.IN_ROOFTOP_SCENE)
def handle_in_rooftop_scene(character_id: int) -> int:
    """
    校验是否处于天台场景
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if now_scene_data.scene_tag == "Rooftop":
        return 1
    return 0


@add_premise(constant.Premise.TONIGHT_IS_FULL_MOON)
def handle_tonight_is_full_moon(character_id: int) -> int:
    """
    校验今夜是否是满月
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_time = character_data.behavior.start_time
    if not now_time:
        now_time = cache.game_time
    moon_phase = game_time.get_moon_phase(now_time)
    if moon_phase in {11, 12}:
        return 1
    return 0


@add_premise(constant.Premise.IS_STARAIGHTFORWARD)
def handle_is_staraightforward(character_id: int) -> int:
    """
    校验角色是否是一个爽直的人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.nature[13] >= 50


@add_premise(constant.Premise.NO_GOOD_AT_ELOQUENCE)
def handle_no_good_at_eloquence(character_id: int) -> int:
    """
    校验角色是否不擅长口才
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    weight = 8
    if 12 in character_data.knowledge:
        level = attr_calculation.get_experience_level_weight(character_data.knowledge[12])
        return 8 - level
    return weight


@add_premise(constant.Premise.TARGET_NO_EXPERIENCE_IN_SEX)
def handle_target_no_experience_in_sex(character_id: int) -> int:
    """
    校验交互对象是否没有性经验
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    for i in character_data.sex_experience:
        if character_data.sex_experience[i]:
            return 0
    return 1


@add_premise(constant.Premise.LUST_IS_HIGHT)
def handle_lust_is_hight(character_id: int) -> int:
    """
    校验角色是否色欲高涨
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.status.setdefault(21, 0)
    return character_data.status[21]


@add_premise(constant.Premise.IN_GROVE)
def handle_in_grove(character_id: int) -> int:
    """
    校验角色是否处于小树林中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    if now_position[0] == "7":
        return 1
    return 0


@add_premise(constant.Premise.NO_IN_GROVE)
def handle_no_in_grove(character_id: int) -> int:
    """
    校验角色是否未处于小树林中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    if now_position[0] != "7":
        return 1
    return 0


@add_premise(constant.Premise.NAKED_CHARACTER_IN_SCENE)
def handle_naked_character_in_scene(character_id: int) -> int:
    """
    校验场景中是否有人一丝不挂
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    scene_path = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path]
    for now_character in scene_data.character_list:
        if handle_is_naked(now_character):
            return 1
    return 0


@add_premise(constant.Premise.TARGET_IS_SING)
def handle_target_is_sing(character_id: int) -> int:
    """
    校验交互对象是否正在唱歌
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_id = character_data.target_character_id
    if target_id != character_id:
        target_data: game_type.Character = cache.character_data[target_id]
        return target_data.state == constant.CharacterStatus.STATUS_SINGING
    return 0


@add_premise(constant.Premise.NO_HAVE_GUITAR)
def handle_no_have_guitar(character_id: int) -> int:
    """
    校验角色是否未拥有吉他
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return 4 not in character_data.item


@add_premise(constant.Premise.IN_ITEM_SHOP)
def handle_in_item_shop(character_id: int) -> int:
    """
    校验角色是否在超市中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.position == ["11"]


@add_premise(constant.Premise.NO_IN_ITEM_SHOP)
def handle_no_in_item_shop(character_id: int) -> int:
    """
    校验角色是否不在超市中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.position != ["11"]


@add_premise(constant.Premise.IN_STUDENT_UNION_OFFICE)
def handle_in_student_union_office(character_id: int) -> int:
    """
    校验角色是否在学生会办公室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.position == ["3", "1", "4"]


@add_premise(constant.Premise.TARGET_CHEST_IS_NOT_CLIFF)
def handle_target_chest_is_not_cliff(character_id: int) -> int:
    """
    校验交互对象胸围是否不是绝壁
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return attr_calculation.judge_chest_group(target_data.chest.now_chest)


@add_premise(constant.Premise.LUST_IS_LOW)
def handle_lust_is_low(character_id: int) -> int:
    """
    校验角色是否色欲低下
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.status.setdefault(21, 0)
    return (character_data.status[21] / 100) < 10


@add_premise(constant.Premise.IS_MAN_OR_WOMAN)
def handle_is_man_or_woman(character_id: int) -> int:
    """
    校验角色是否是男性或女性
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.sex in {0, 1}


@add_premise(constant.Premise.IS_NOT_ASEXUAL)
def handle_is_not_asexual(character_id: int) -> int:
    """
    校验角色是否不是无性
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.sex != 3


@add_premise(constant.Premise.IS_PRIMARY_SCHOOL_STUDENTS)
def handle_is_primary_school_students(character_id: int) -> int:
    """
    校验角色是否是小学生
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.age <= 12


@add_premise(constant.Premise.NO_RICH_EXPERIENCE_IN_SEX)
def handle_no_rich_experience_in_sex(character_id: int) -> int:
    """
    校验角色是否性经验不丰富
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_exp = 0
    for i in character_data.sex_experience:
        now_exp += character_data.sex_experience[i]
    return 8 - attr_calculation.get_experience_level_weight(now_exp)


@add_premise(constant.Premise.NO_IN_CAFETERIA)
def handle_no_in_cafeteria(character_id: int) -> int:
    """
    校验角色是否未处于取餐区中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if now_scene_data.scene_tag == "Cafeteria":
        return 0
    return 1


@add_premise(constant.Premise.NO_IN_RESTAURANT)
def handle_no_in_restaurant(character_id: int) -> int:
    """
    校验角色是否未处于就餐区中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if now_scene_data.scene_tag == "Restaurant":
        return 0
    return 1
