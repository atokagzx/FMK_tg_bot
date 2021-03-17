import vk  # Импортируем модуль vk
import cv2 as cv
from PIL import Image
import urllib
import requests
import json
from peewee import SqliteDatabase, CharField, Model, Database, BooleanField
import peewee
import threading
import os
sql_db = SqliteDatabase('vk_users.db')


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
        database = sql_db
        
def get_members(groupid):
    first = vk_api.groups.getMembers(group_id=groupid, v=5.92)  # Первое выполнение метода
    data = first["items"]  # Присваиваем переменной первую тысячу id'шников
    count = first["count"] // 1000  # Присваиваем переменной количество тысяч участников
    # С каждым проходом цикла смещение offset увеличивается на тысячу
    # и еще тысяча id'шников добавляется к нашему списку.
    for i in range(1, count+1):  
        data = data + vk_api.groups.getMembers(group_id=groupid, v=5.92, offset=i*1000)["items"]
    return data
def get_user_data(userid, update = False):
    if not update:
        try:
            f = vk_person.get(vk_person.vk_id == str(userid))
            return
        except:
            pass
    while True:
        try:
            info = vk_api.users.get(user_id=userid, fields="sex, photo_max_orig, screen_name, maiden_name", v=5.92)[0]
            break
        except:
            pass
    try:
        p = vk_person.get(vk_person.vk_id == str(userid))
        p.first_name = info['first_name']
        p.last_name = info['last_name']
        p.nick = info['screen_name']
        p.photo_link = info['photo_max_orig']
        if info['sex'] == 2:
            p.sex = "male"
        elif info['sex'] == 1:
            p.sex = "female"
        p.save()
        print("Old person: ", p.first_name, p.last_name, p.nick, p.sex, p.vk_id)
    except:
        try:
            p = vk_person.create(vk_id = str(userid), first_name = info['first_name'], last_name = info['last_name'], nick = info['screen_name'], photo_link = info['photo_max_orig'])
        except:
            print("ERROR: ", info)
            return
        if info['sex'] == 2:
            p.sex = "male"
        elif info['sex'] == 1:
            p.sex = "female"
        p.save()
        print("New person: ", p.first_name, p.last_name, p.nick, p.sex, p.vk_id)
        '''
        p = requests.get(info['photo_max_orig'])
        if info['sex'] == 1:
            data_file = open("Females.json", "r")
            data = json.load(data_file)
            data_file.close()
            data.update({userid:{'first_name': info['first_name'], 'last_name': info['last_name'], 'nick': info['screen_name'], 'val': '0', 'shown': []}})
            data_file = open("Females.json", "w")
            json.dump(data, data_file)
            data_file.close()
            out = open("Females/" + str(userid) + ".jpg", "wb")
        elif info['sex'] == 2:
            data_file = open("Males.json", "r")
            data = json.load(data_file)
            data_file.close()
            data.update({userid:{'first_name': info['first_name'], 'last_name': info['last_name'], 'nick': info['screen_name'], 'val': '0', 'shown': []}})
            data_file = open("Males.json", "w")
            json.dump(data, data_file)
            data_file.close()
            out = open("Males/" + str(userid) + ".jpg", "wb")
        out.write(p.content)
        out.close()
        '''

vk_person.create_table()

def read_vk_profiles(x):
    for user_id in x:
        get_user_data(user_id)
def save_photos(link, vk_id, person):
    while True:
        try:
            p = requests.get(link)
            directory = "avatars/" + str(vk_id) + ".jpg"
            #person.photo = directory
            #person.save()
            out = open(directory, "wb")
            out.write(p.content)
            out.close()
        except:
            print("err")
        else:
            break

if __name__ == "__main__":
    token = "b26803c5b26803c5b26803c58bb21ee4f2bb268b26803c5d227f32126b1852312ca415f"
    session = vk.Session(access_token=token)
    vk_api = vk.API(session)
    '''
    members = get_members("nust_misis")
    m1 = list(members[:len(members) // 2])
    m2 = list(members[len(members) // 2 : ])
    e1 = threading.Event()
    e2 = threading.Event()
    t1 = threading.Thread(target=read_vk_profiles, args=(m1, ))
    t2 = threading.Thread(target=read_vk_profiles, args=(m2, ))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    '''
    '''
    for person in vk_person.select():
        link = person.photo_link
        vk_id = person.vk_id
        #print(link)
        while(True):
            try:
                t = threading.Thread(target=save_photos, args=(link, vk_id, person))
                t.start()
            except:
                pass
            else:
                break
    '''
    '''
    for entry in os.scandir("avatars"):
        if (entry.path.endswith(".jpg") or entry.path.endswith(".png")) and entry.is_file():
            #print(entry.path)
            img_id = entry.path.split(".")[0].split("/")[1]
            #print(img_id)
            p = vk_person.get(vk_person.vk_id == str(img_id))
            p.photo = entry.path
            p.save()
    '''
    for p in vk_person.select().where(vk_person.photo == None):
        p.delete_instance()
        #print(p.vk_id)
    #m1 = threading.Thread(target=save_photos, args=())
    #m1.start()
    #m1.join()