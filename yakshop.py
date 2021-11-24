#!/usr/bin/python

from os import name
import sys, getopt
import xml.etree.ElementTree as ET
import json

class Yak():
    def __init__(self, name, age, sex):
        self.name = name
        self.age = float(age)
        self.sex = sex

    def current_age(self, t):
        return (self.age*100.0 + float(t))/100.0

    def milk(self, start, end):
        if self.current_age(end) >= 10.0:
            return -1.0
        milk = 0
        for day in range(int(start), int(end)):
            d = self.age*100.0 + float(day)
            milk = milk + (50.0 - d*0.03)
        return milk

    def skins(self, start, end):
        if self.current_age(end) >= 10.0:
            return -1
        skins = 0
        if self.age == 1.0:
            skins = skins + 1
        elif self.age > 1.0:
            time = int(start)
            d = self.age*100.0 + float(time)
            f = 8 + d*0.01
            time += int(f) + 1
            while time < int(end):
                skins += 1
                d = self.age*100.0 + float(time)
                f = 8 + d*0.01
                time += int(f) + 1
        return skins

    def last_shaved(self, t):
        if self.age == 1.0:
            return self.age
        elif self.age > 1.0:
            skins = 0
            time = 0
            d = self.age*100.0 + float(time)
            f = 8 + d*0.01
            time += int(f) + 1
            while time < int(t):
                skins += 1
                d = self.age*100.0 + float(time)
                f = 8 + d*0.01
                time += int(f) + 1
            return time - (int(f) + 1) + self.age
        else:
            return 0.0



    def priint(self, t):
        print(self.name + " " + str(self.current_age(t)) + " years old")


class Herd():
    def __init__(self):
        self.herd = []
        self.milk = 0.0
        self.skins = 0
        self.t_milk = 0
        self.t_skins = 0

    def add_yak(self, yak):
        self.herd.append(yak)
        self.skins += 1

    def calc_milk(self,t):
        for yak in self.herd:
            milk =  yak.milk(self.t_milk, t)
            if milk < 0.0:
                self.herd.remove(yak)
                break
            self.milk = self.milk + milk
        self.t_milk = t
        return self.milk

    def calc_skins(self, t):
        for yak in self.herd:
            if t == self.t_skins:
                break
            skins = yak.skins(self.t_skins, t)
            if skins < 0:
                self.herd.remove(yak)
                break
            self.skins = self.skins + skins
        self.t_skins = t
        return self.skins

    def get_stock(self, t):
        stock = {}
        stock['milk'] = self.calc_milk(t)
        stock['skins'] = self.calc_skins(t)
        stock_j = json.dumps(stock, indent=2)
        print(stock_j)
        return stock_j

    def get_herd(self, t):
        herd_dict = []
        for yak in self.herd:
            yak_dict = {}
            yak_dict['name'] = yak.name
            yak_dict['age'] = yak.current_age(t)
            yak_dict['age_last_shaved'] = yak.last_shaved(t)
            herd_dict.append(yak_dict)
        herd_j = json.dumps(herd_dict, indent=2)
        print(herd_j)
        return herd_j

    def order(self, t, body):
        order = {}
        body_dict = json.loads(body)
        if 'milk' in body_dict['order']:
            milk = self.calc_milk(t)
            order_milk = float(body_dict['order']['milk'])
            if milk >= order_milk:
                self.milk -= order_milk
                order['milk'] = order_milk
        
        if 'skins' in body_dict['order']:
            skins = self.calc_skins(t)
            order_skins = int(body_dict['order']['skins'])
            if skins >= order_skins:
                self.skins -= order_skins
                order['skins'] = order_skins

        if 'skins' in order and 'milk' in order:
            print("Status = 201")
        elif order:
            print("Status = 206")
        else:
            return
        order = json.dumps(order, indent=2)
        print(order)        
        return order

def get(herd, req, t):
    if req == "herd":
        herd.get_herd(t)
    elif req == "stock":
        herd.get_stock(t)
    else:
        print("Invalid request!")

def post(herd, req, t, body):
    if req == "order":
        if not herd.order(t, body):
            print("Status = 404")
    else:
        print("Status = 404")

    
def read_input(filename, t, herd):
    root = ET.parse(filename).getroot()
    for yak in root:
        name = yak.get('name')
        age = yak.get('age')
        sex = yak.get('sex')
        new_yak = Yak(name, age, sex)
        herd.add_yak(new_yak)

    print("In Stock:")
    print(str(herd.calc_milk(t)) + " liters of milk")
    print(str(herd.calc_skins(t)) + " skins of wool")
    print("Herd:")
    for yak in herd.herd:
        yak.priint(t)
    

def main():
    herd = Herd()
    while(True):
        user_in = input().split()
        if 'exit' in user_in:
            return
        elif len(user_in) > 1:
            first = user_in[0]
            sec = user_in[1]
            if first == 'GET':
                req = sec.split('/')
                get(herd, req[2], req[3])
            elif first == 'POST':
                body = input()
                req = sec.split('/')
                post(herd, req[2],req[3],body)
            else:
                read_input(first, sec, herd)
        else:
            print("Invalid input please try again!")

if __name__ == "__main__":
    main()