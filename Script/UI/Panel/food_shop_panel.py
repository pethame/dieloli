from typing import Tuple
from types import FunctionType
from uuid import UUID
from Script.Core import (
    cache_control,
    game_type,
    get_text,
    flow_handle,
    text_handle,
    constant,
    py_cmd,
)
from Script.Design import map_handle, cooking
from Script.UI.Moudle import draw, panel
from Script.Config import game_config, normal_config

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """


class FoodShopPanel:
    """
    用于查看食物商店界面面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("主食")
        """ 当前绘制的食物类型 """
        self.handle_panel: panel.PageHandlePanel = None
        """ 当前名字列表控制面板 """

    def draw(self):
        """绘制对象"""
        scene_position = cache.character_data[0].position
        scene_position_str = map_handle.get_map_system_path_str_for_list(scene_position)
        scene_name = cache.scene_data[scene_position_str].scene_name
        title_draw = draw.TitleLineDraw(scene_name, self.width)
        food_type_list = [_("主食"), _("零食"), _("饮品"), _("水果"), _("食材"), _("调料")]
        self.handle_panel = panel.PageHandlePanel(
            [], SeeFoodListByFoodNameDraw, 10, 5, self.width, 1, 1, 0
        )
        while 1:
            py_cmd.clr_cmd()
            food_name_list = list(
                cooking.get_restaurant_food_type_list_buy_food_type(self.now_panel).items()
            )
            self.handle_panel.text_list = food_name_list
            self.handle_panel.update()
            title_draw.draw()
            return_list = []
            for food_type in food_type_list:
                if food_type == self.now_panel:
                    now_draw = draw.CenterDraw()
                    now_draw.text = f"{food_type}]"
                    now_draw.style = "onbutton"
                    now_draw.width = self.width / len(food_type_list)
                    now_draw.draw()
                else:
                    now_draw = draw.CenterButton(
                        f"[{food_type}]",
                        food_type,
                        self.width / len(food_type_list),
                        cmd_func=self.change_panel,
                        args=(food_type,),
                    )
                    now_draw.draw()
                    return_list.append(now_draw.return_text)
            line_feed.draw()
            line = draw.LineDraw("+", self.width)
            line.draw()
            self.handle_panel.draw()
            return_list.extend(self.handle_panel.return_list)
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def change_panel(self, food_type: str):
        """
        切换当前面板显示的食物类型
        Keyword arguments:
        food_type -- 要切换的食物类型
        """
        self.now_panel = food_type
        food_name_list = list(
            cooking.get_restaurant_food_type_list_buy_food_type(self.now_panel).items()
        )
        self.handle_panel = panel.PageHandlePanel(
            food_name_list, SeeFoodListByFoodNameDraw, 10, 5, self.width, 1, 1, 0
        )


class SeeFoodListByFoodNameDraw:
    """
    点击后可查看食物列表的食物名字按钮对象
    Keyword arguments:
    text -- 食物名字
    width -- 最大宽度
    is_button -- 绘制按钮
    num_button -- 绘制数字按钮
    button_id -- 数字按钮id
    """

    def __init__(
        self, text: Tuple[str, str], width: int, is_button: bool, num_button: bool, button_id: int
    ):
        """初始化绘制对象"""
        self.text = text[1]
        """ 食物名字 """
        self.cid = text[0]
        """ 食物在食堂内的表id """
        self.draw_text: str = ""
        """ 食物名字绘制文本 """
        self.width: int = width
        """ 最大宽度 """
        self.num_button: bool = num_button
        """ 绘制数字按钮 """
        self.button_id: int = button_id
        """ 数字按钮的id """
        self.button_return: str = str(button_id)
        """ 按钮返回值 """
        name_draw = draw.NormalDraw()
        if is_button:
            if num_button:
                index_text = text_handle.id_index(button_id)
                button_text = f"{index_text}{self.text}"
                name_draw = draw.LeftButton(
                    button_text,
                    self.button_return,
                    self.width,
                    cmd_func=self.see_food_shop_food_list,
                )
            else:
                button_text = f"[{self.text}]"
                name_draw = draw.CenterButton(
                    button_text, self.text, self.width, cmd_func=self.see_food_shop_food_list
                )
                self.button_return = text
            self.draw_text = button_text
        else:
            name_draw = draw.CenterDraw()
            name_draw.text = f"[{self.text}]"
            name_draw.width = self.width
            self.draw_text = name_draw.text
        self.now_draw = name_draw
        """ 绘制的对象 """

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()

    def see_food_shop_food_list(self):
        """按食物名字显示食物商店的食物列表"""
        title_draw = draw.TitleLineDraw(self.text, window_width)
        now_food_list = [(self.cid, x) for x in cache.restaurant_data[self.cid]]
        page_handle = panel.PageHandlePanel(
            now_food_list, BuyFoodByFoodNameDraw, 10, 1, window_width, 1, 1, 0
        )
        while 1:
            return_list = []
            title_draw.draw()
            page_handle.update()
            page_handle.draw()
            return_list.extend(page_handle.return_list)
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                break
            page_handle.text_list = [(self.cid, x) for x in cache.restaurant_data[self.cid]]


class BuyFoodByFoodNameDraw:
    """
    点击后可购买食物的食物名字按钮对象
    Keyword arguments:
    text -- 食物id
    width -- 最大宽度
    is_button -- 绘制按钮
    num_button -- 绘制数字按钮
    button_id -- 数字按钮id
    """

    def __init__(
        self, text: Tuple[str, UUID], width: int, _unused: bool, num_button: bool, button_id: int
    ):
        """初始化绘制对象"""
        self.text: UUID = text[1]
        """ 食物uid """
        self.cid: str = text[0]
        """ 食物商店索引id """
        self.draw_text: str = ""
        """ 食物名字绘制文本 """
        self.width: int = width
        """ 最大宽度 """
        self.num_button: bool = num_button
        """ 绘制数字按钮 """
        self.button_id: int = str(button_id)
        """ 按钮返回值 """
        self.button_return: str = str(button_id)
        """ 按钮返回值 """
        name_draw = draw.NormalDraw()
        food_data: game_type.Food = cache.restaurant_data[self.cid][self.text]
        quality_text_data = [_("垃圾"), _("饲料"), _("粮食"), _("美味"), _("春药")]
        food_name = ""
        if isinstance(self.cid, str):
            food_recipe: game_type.Recipes = cache.recipe_data[int(self.cid)]
            food_name = food_recipe.name
        else:
            food_config = game_config.config_food[self.cid]
            food_name = food_config.name
        hunger_text = _("热量:")
        if 27 in food_data.feel:
            hunger_text = f"{hunger_text}{round(food_data.feel[27],2)}"
        else:
            hunger_text = f"{hunger_text}0.00"
        thirsty_text = _("水份:")
        if 28 in food_data.feel:
            thirsty_text = f"{thirsty_text}{round(food_data.feel[28],2)}"
        else:
            thirsty_text = f"{thirsty_text}0.00"
        price = round(1 + sum(food_data.feel.values()) * food_data.quality / 100, 2)
        food_name = (
            food_name
            + f" {hunger_text} {thirsty_text} "
            + _("重量:")
            + str(round(food_data.weight, 2))
            + _("克")
            + " "
            + _("品质:")
            + quality_text_data[food_data.quality]
            + " "
            + _("售价:" + str(price))
        )
        index_text = text_handle.id_index(button_id)
        button_text = f"{index_text}{food_name}"
        name_draw = draw.LeftButton(
            button_text, self.button_return, self.width, cmd_func=self.buy_food
        )
        self.now_draw = name_draw
        """ 绘制的对象 """

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()

    def buy_food(self):
        """玩家购买食物"""
        cache.character_data[0].food_bag[self.text] = cache.restaurant_data[self.cid][self.text]
        del cache.restaurant_data[self.cid][self.text]
