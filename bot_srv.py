import telebot
from telebot import types
from peewee import SqliteDatabase, CharField, Model, Database, BooleanField
import peewee
import json
import os
import cv2
import numpy as np
import random

tg_db = SqliteDatabase('people.db')
vk_db = SqliteDatabase('vk_users.db')
tg_token = '1696391823:AAFlR_NOBSWGVy5MG4gkB2UBE3jNAcJZw0s'

bot = telebot.TeleBot(tg_token)

class Person(Model):
    tg_id = CharField(null=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    nick = CharField(null=True)
    info = CharField(null=True)
    sex = CharField(null=True)
    payed = BooleanField(null=True)
    shown = CharField(null=True)
    fuck = CharField(null=True)
    merry = CharField(null=True)
    kill = CharField(null=True)
    choice = CharField(null=True)
    actual_answers = CharField(null=True)
    class Meta:
        database = tg_db

class vk_person (Model):
    vk_id = CharField(null=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    nick = CharField(null=True)
    info = CharField(null=True)
    sex = CharField(null=True)
    payed = BooleanField(null=True)
    shown = CharField(null=True)
    fuck = CharField(null=True)
    merry = CharField(null=True)
    kill = CharField(null=True)
    photo = CharField(null=True)
    photo_link = CharField(null=True)
    class Meta:
        database = vk_db

def make_vs_image(vk_ids, directory, photo_file_name):
    print("generating")
    img = cv2.imread(directory + str(vk_ids[0]) + ".jpg")
    img = cv2.resize(img, (400, 400))
    for i in vk_ids[1:]:
        frame = cv2.imread(directory + str(i) + ".jpg")
        frame = cv2.resize(frame, (400, 400))
        img = np.vstack((img, frame))
    cv2.imwrite(photo_file_name, img)

def send_versus(message):
    tg_id = str(message.chat.id)
    try:
        p = Person.get(Person.tg_id == str(tg_id))
    except:
        start(message)
        return
    if p.sex == None:
        keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        keyboard.row('Парни', 'Девушки')
        bot.send_message(tg_id, "Кто тебе интересен?)", reply_markup=keyboard)
        return
    print("Request: ", p.tg_id, p.sex, p.nick)
    if p.choice == None:
        choice_list = []
        for vk_p in vk_person.select().where(vk_person.sex != p.sex):
            if (vk_p.fuck == None or str(vk_p.fuck).find(tg_id) == -1) and (vk_p.merry == None or str(vk_p.merry).find(tg_id) == -1) and (vk_p.kill == None or str(vk_p.kill).find(tg_id) == -1):
                choice_list.append(vk_p)
        try:
            candidates = random.sample(choice_list, 3)
        except:
            print("No more!")
            bot.send_message(message.chat.id, "На этом пока всё!)")
            return
    else:
        candidates = []
        vk_ids = list(p.choice.split())
        for vk_id in vk_ids:
            for vk_p in vk_person.select().where(vk_person.vk_id == vk_id):
                candidates.append(vk_p)
    vk_ids = []
    text_field_choice = ""
    choice_text = ""
    n = 0
    photo_file_name = "avatars/"
    for vk_p in candidates:
        n += 1
        vk_ids.append(vk_p.vk_id)
        text_field_choice += vk_p.vk_id + " "
        choice_text += "{0}. {1} {2}\n".format(n, vk_p.first_name, vk_p.last_name)
        photo_file_name += vk_p.vk_id
    photo_file_name += ".jpg"
    p.choice = text_field_choice[:-1]
    p.save()
    print(photo_file_name)
    try:
        img = open(photo_file_name, 'rb')
        bot.send_photo(tg_id, img, choice_text)
        img.close()
    except:
        make_vs_image(vk_ids, "avatars/", photo_file_name)
        img = open(photo_file_name, 'rb')
        bot.send_photo(tg_id, img, choice_text)
        img.close()
    fmk_keypad(message)
# actual_answers format is str(F1 F2 F3)
def fmk_keypad(message):
    tg_id = str(message.chat.id)
    try:
        p = Person.get(Person.tg_id == str(tg_id))
    except:
        start(message)
        return
    if p.choice == None:
        send_versus(message)
        return
    if len(list(str(p.choice).split())) != 3:
        send_versus(message)
        return
    if p.actual_answers == None:
        p.actual_answers = ""
        p.save()
    answers = list(str(p.actual_answers).split())
    '''
    for i in answers:
        if i
    '''
    msg = message.text
    if msg[1].isdigit() and (msg[0] == "F" or msg[0] == "M" or msg[0] == "K"):
        command = message.text.upper()
        num = int(''.join(filter(str.isdigit, command)))
        if 0 < num < 4:
            p.actual_answers += command[0]
            print(num, command[0])
        else:
            return
    answers = list(str(p.actual_answers).split())
    keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    for i in range(3):
        keyboard.row('F' + str(i + 1), 'M' + str(i + 1), 'K' + str(i + 1))
    bot.send_message(message.chat.id, "Тебе решать: fuck, merry, kill", reply_markup=keyboard)

@bot.message_handler(commands=['start'])
def start(message):
    try:
        p = Person.get(Person.tg_id == str(message.chat.id))
        print(p.tg_id, p.sex, p.nick)
    except:
        print("New person: ", message.chat.username, message.chat.id)
        p = Person.create(tg_id = str(message.chat.id), first_name = message.chat.first_name, last_name = message.chat.last_name, nick = message.chat.username)
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.row('Парни', 'Девушки')
    bot.send_message(message.chat.id, "Кто тебе интересен?)", reply_markup=keyboard)

@bot.message_handler(content_types=['text'])
def text(message):
    try:
        p = Person.get(Person.tg_id == str(message.chat.id))
    except:
        print("New person: ", message.chat.username, message.chat.id)   
        p = Person.create(tg_id = str(message.chat.id), first_name = message.chat.first_name, last_name = message.chat.last_name, nick = message.chat.username)
        p = Person.get(Person.tg_id == str(message.chat.id))
    if message.text.lower() == 'девушки':
        p.sex = "male"
        p.save()
        bot.send_message(message.chat.id, 'Добро пожаловать в мужское братство, развлекайся')
        send_versus(message)
    elif message.text.lower() == 'парни':
        p.sex = "female"
        p.save()
        directory = r'/Users/sav/Desktop/FuckMK/Males/'
        bot.send_message(message.chat.id, 'Тьфу на тебя')
        send_versus(message)
    msg = message.text
    if msg[1].isdigit() and (msg[0] == "F" or msg[0] == "M" or msg[0] == "K"):
        fmk_keypad(message)

Person.create_table()
vk_person.create_table()
bot.polling()
