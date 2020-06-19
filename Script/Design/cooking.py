import random
from typing import Dict
from Script.Core.game_type import Recipes,Food
from Script.Core import constant,text_loading,cache_contorl,value_handle

def init_recipes():
    """ 初始化菜谱数据 """
    recipes_data = text_loading.get_game_data(constant.FilePath.RECIPES_PATH)
    cache_contorl.recipe_data = {}
    for recipe_dict in recipes_data:
        recipe = create_recipe(recipe_dict["Name"],recipe_dict["Time"],recipe_dict["Base"],recipe_dict["Ingredients"],recipe_dict["Seasoning"])
        cache_contorl.recipe_data[len(cache_contorl.recipe_data)] = recipe

def create_recipe(name:str,time:int,base:list,ingredients:list,seasoning:list) -> Recipes:
    """
    创建菜谱对象
    Keyword arguments:
    name -- 菜谱名字
    time -- 烹饪用时
    base -- 主食材列表
    ingredients -- 辅食材列表
    seasoning -- 调料列表
    Return arguments:
    Recipes -- 菜谱对象
    """
    recipe = Recipes()
    recipe.name = name
    recipe.time = time
    recipe.base = base
    recipe.ingredients = ingredients
    recipe.seasoning = seasoning
    return recipe

def create_food(food_id:str,food_quality:int,food_weight:int,food_feel:{},food_maker="",food_recipe=-1) -> Food:
    """
    创建食物对象
    Keyword arguments:
    food_id -- 食物配置id
    food_quality -- 食物品质
    food_weight -- 食物重量
    food_feel -- 食物效果
    food_maker -- 食物制作者
    food_recipe -- 食谱id
    """
    food = Food()
    food.id = food_id
    food.quality = food_quality
    food.weight = food_weight
    food.feel = food_feel
    food.maker = food_maker
    food.recipe = food_recipe
    return food

def create_rand_food(food_id:str,food_weight=-1,food_quality=-1) -> Food:
    """
    创建随机食材
    Keyword arguments:
    food_id -- 食物配置id
    food_weight -- 食物重量(为-1时随机)
    food_quality -- 食物品质(为-1时随机)
    """
    if food_weight == -1:
        food_weight = random.randint(1,1000000)
    if food_quality == -1:
        food_quality = random.randint(1,10)
    food_data = text_loading.get_game_data(constant.FilePath.FOOD_PATH)[food_id]
    return create_food(food_id,food_quality,food_weight,food_data["Feel"])

def cook(food_data:Dict[str,Food],recipe_id:int,cook_level:str,maker:str) -> Food:
    """
    按食谱烹饪食物
    Keyword arguments:
    food_data -- 食材数据
    recipe_id -- 菜谱id
    cook_level -- 烹饪技能等级
    maker -- 制作者
    Return arguments:
    Food -- 按菜谱制作得到的食物
    """
    recipe = cache_contorl.recipe_data[recipe_id]
    cook_judge = True
    feel_data = {}
    quality_data = text_loading.get_text_data(constant.FilePath.ATTR_TEMPLATE_PATH,"FoodQualityWeight")[cook_level]
    now_quality = int(value_handle.get_random_for_weight(quality_data))
    now_weight = 0
    for food in recipe.base:
        if food not in food_data:
            cook_judge = False
            break
        now_food = food_data[food]
        rand_weight = random.randint(75,125)
        if now_food.weight < rand_weight:
            cook_judge = False
            break
        for feel in now_food.feel:
            feel_data.setdefault(feel,0)
            feel_data[feel] += now_food.feel[feel] / now_food.weight * rand_weight
        now_food.weight -= rand_weight
        now_weight += rand_weight
    if !cook_judge:
        return create_food("KitchenWaste",now_quality,now_weight,[])
    for food in recipe.ingredients:
        if food not in food_data:
            cook_judge = False
            break
        now_food = food_data[food]
        rand_weight = random.randint(25,75)
        if now_food.weight < rand_weight:
            cook_judge = False
            break
        for feel in now_food.feel:
            feel_data.setdefault(feel,0)
            feel_data[feel] += now_food.feel[feel] / now_food.weight * rand_weight
        now_food.weight -= rand_weight
        now_weight += rand_weight
    if !cook_judge:
        return create_food("KitchenWaste",now_quality,now_weight,[])
    for food in recipe.seasoning:
        if food not in food_data:
            cook_judge = False
            break
        now_food = food_data[food]
        rand_weight = random.randint(3,7)
        if now_food.weight < rand_weight:
            cook_judge = False
            break
        for feel in now_food.feel:
            feel_data.setdefault(feel,0)
            feel_data[feel] += now_food.feel[feel] / now_food.weight * rand_weight
        now_food.weight -= rand_weight
        now_weight += rand_weight
    if !cook_judge:
        return create_food("KitchenWaste",now_quality,now_weight,[])
    return create_food("",now_quality,now_weight,feel_data,maker,recipe_id)