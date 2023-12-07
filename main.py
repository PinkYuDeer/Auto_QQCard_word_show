import sys
import tkinter as tk
from PIL import Image, ImageTk
import requests
from io import BytesIO
import os

file_path = "data/words.txt"
bg_image = None
word_image = None


class Card:
    def __init__(self, line):
        data = line.split()
        self.id = data[0]
        self.name = data[1]
        self.description = data[2]
        self.image_url = data[3]
        self.first_obtain_time = data[4]
        self.latest_obtain_time = data[5]
        self.obtain_count = data[6]
        self.first_qq = data[7]
        self.last_qq = data[8]
        self.total_qq_count = data[9]

    def __str__(self):
        return f"ID: {self.id}\n" \
               f"名称: {self.name}\n" \
               f"描述: {self.description}\n" \
               f"图片链接: {self.image_url}\n" \
               f"首次获得时间: {self.first_obtain_time}\n" \
               f"最近获得时间: {self.latest_obtain_time}\n" \
               f"获得次数: {self.obtain_count}\n" \
               f"首次获得QQ: {self.first_qq}\n" \
               f"最近获得QQ: {self.last_qq}\n" \
               f"总获得QQ次数: {self.total_qq_count}\n"


class CardList:
    def __init__(self):
        self.file_path = file_path
        self.cards = []

    def load(self):
        with open(self.file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
        for line in lines:
            card = Card(line)
            self.cards.append(card)

    def search_by_id(self, card_id):
        for card in self.cards:
            if card.id == card_id:
                return card
        return None

    def search_by_name(self, card_name):
        for card in self.cards:
            if card.name == card_name:
                return card
        return None


class MyTk(tk.Tk):
    def __init__(self):
        super().__init__()

        # 加载卡片数据
        self.card_list = CardList()
        self.card_list.load()
        self.current_card = self.card_list.cards[0]

        # 配置窗口
        self.title("卡片显示")

        self.card = tk.Canvas(self, width=514, height=393, bg="white")
        self.card.pack()
        # 初始化显示第一张卡片的信息
        self.display_card_info(self.current_card)

        # 创建一个 Frame 作为按钮容器
        btn_s = tk.Frame(self)
        btn_s.pack()

        previous_button = tk.Button(btn_s, text="上一个", command=self.previous_card)
        previous_button.pack(side=tk.LEFT)

        self.search_entry = tk.Entry(btn_s)
        self.search_entry.pack(side=tk.LEFT)

        search_button = tk.Button(btn_s, text="搜索", command=self.search)
        search_button.pack(side=tk.LEFT)

        next_button = tk.Button(btn_s, text="下一个", command=self.next_card)
        next_button.pack(side=tk.LEFT)

    @staticmethod
    def findXCenter(canvas, item):
        coords = canvas.bbox(item)
        xOffset = (514 / 2) - ((coords[2] - coords[0]) / 2)
        return xOffset

    @staticmethod
    def get_resource_path(relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    def display_card_info(self, card):
        global bg_image, word_image
        bg_image = Image.open(self.get_resource_path("img/img.png"))  # 背景图片路径
        bg_image = bg_image.resize((514, 393))  # 调整背景图片大小
        bg_image = ImageTk.PhotoImage(bg_image)
        self.card.create_image(0, 0, anchor=tk.NW, image=bg_image)

        # 尝试读取word_image文件夹中的图片
        try:
            word_image = Image.open("word_image/" + (card.id + '【' + card.name + '】' + card.description) + ".png")
        except FileNotFoundError:
            # 下载图片并显示
            card_image_url = card.image_url
            response = requests.get(card_image_url)
            word_image = Image.open(BytesIO(response.content))
            # 判断文件夹是否存在，不存在则创建
            if not os.path.exists("word_image"):
                os.mkdir("word_image")
            # 将图片保存在word_image文件夹中
            word_image.save("word_image/" + (card.id + '【' + card.name + '】' + card.description) + ".png")
        # 调整图片大小，等比例调整图片的宽度为400
        word_image = word_image.resize((400, int(word_image.height * 400 / word_image.width)))
        height = word_image.height
        word_image = ImageTk.PhotoImage(word_image)
        self.card.create_image(57, int((360 - height) / 2), anchor=tk.NW, image=word_image)

        # 显示卡片信息
        id_name = self.card.create_text(0, 17, anchor=tk.NW, text=(card.id + ' : ' + card.name), font=("none", 20), fill="brown")
        card.description = card.description.replace('-', ' ')
        card.description = card.description.replace('，', ', ')
        top = height + int((360 - height) / 2)
        description = self.card.create_text(0, top, anchor=tk.NW, text=card.description, font=("none", 12), fill="brown", width=300)
        id_name_xOFFSET = self.findXCenter(self.card, id_name)
        description_xOFFSET = self.findXCenter(self.card, description)
        self.card.move(id_name, id_name_xOFFSET, 0)
        self.card.move(description, description_xOFFSET, 0)

    def previous_card(self):
        current_index = self.card_list.cards.index(self.current_card)
        current_index = (current_index - 1) % len(self.card_list.cards)
        self.current_card = self.card_list.cards[current_index]
        self.display_card_info(self.current_card)

    def next_card(self):
        current_index = self.card_list.cards.index(self.current_card)
        current_index = (current_index + 1) % len(self.card_list.cards)
        self.current_card = self.card_list.cards[current_index]
        self.display_card_info(self.current_card)

    def search(self):
        search_text = self.search_entry.get().strip()

        # 判断输入内容类型
        if search_text.isdigit():  # 如果是纯数字则按ID检索
            self.search_by_id(search_text)
        else:  # 否则按字符名检索
            self.search_by_name(search_text)

    def search_by_id(self, search_text):
        # 按ID检索的逻辑
        card = self.card_list.search_by_id(search_text)
        if card:
            self.current_card = card
            self.display_card_info(self.current_card)
        else:
            print("未找到卡片")

    def search_by_name(self, search_text):
        # 按字符名检索的逻辑
        card = self.card_list.search_by_name(search_text)
        if card:
            self.current_card = card
            self.display_card_info(self.current_card)
        else:
            print("未找到卡片")


if __name__ == "__main__":
    app = MyTk()
    app.mainloop()
