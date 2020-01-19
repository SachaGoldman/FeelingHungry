from typing import List, Optional
from fuzzywuzzy import fuzz, process
from epicurcrawler import Crawler
import json
from mitLoader import MitLoader


import os.path
from food import Food
from foodAI import FoodAi

banned = ["dough", "spice", "sauce", "seasoning", "my", "season", "crust", "rub"]


class FoodProducer:
    def __init__(self):
        self.foods = []
        self.load()
        # self.word_model = api.load('glove-wiki-gigaword-50')
        self.cached_foods = {}
        self.crawler = Crawler()
        self.ai = FoodAi(self)

    def get_food(self, food_id: str) -> Optional[Food]:
        for food in self.foods:
            if food.id == food_id:
                return food
        return None

    def search_food(self, food_name: str) -> List[int]:
        if food_name in self.cached_foods:
            return self.cached_foods[food_name]

        ids = self.ai.search_index(food_name)
        ids = [(id, self.foods[id].num_leaves) for id in ids]
        ids.sort(key=lambda x: x[1])
        ids = [str(_id[0]) for _id in ids][::-1][:5]
        found_foods = [self.foods[id] for id in ids]
        for food in found_foods:
            if food.image_url is None:
                food.findImage(food_name)
        self.cached_foods[food_name] = ids
        # self.save()
        return self.cached_foods[food_name]

    def add_food(self, food_name: str) -> None:
        for new_food in self.crawler.get_food(food_name):
            if new_food.name not in [x.name for x in self.foods]:
                print("Added food: " + new_food.name)
                self.foods.append(new_food)

    def food_exists(self, food_name: str) -> bool:
        for food in self.foods:
            if food.name == food_name:
                return True
        return False

    def save(self):
        with open('foods.json', 'w') as fp:
            str_food = []
            for food in self.foods:
                str_food.append(food.toJson())
            json.dump(str_food, fp)

    def load(self):
        """Either loads the self.foods array from the self created foods.json save or recreates it using the MIT dataset"""
        if not os.path.isfile("foods.json"):
            loader = MitLoader()
            self.foods = loader.load()
            print("Loaded: " + str(len(self.foods)) + " foods from MIT data source")
            self.save()
            return

        with open('foods.json', 'r') as fp:
            x = json.load(fp)
            for i in x:
                r = json.loads(i)
                allow = True
                for namew in r["name"].split(" "):
                    if namew.strip().lower() in banned:
                        allow = False
                        break
                if allow:
                    self.foods.append(Food(r["name"], r["image_url"], r["recipe_url"], r["recipe_html"], r["fat_level"], r["salt_level"], r["saturates_level"], r["sugars_level"]))
        print("Loaded: " + str(len(self.foods)))



