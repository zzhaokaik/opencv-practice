#!/usr/bin/python3

import datetime

print("hello 江南小炮王")

x = "a"
y = "b"

'''
 不换行输出
'''
print(x, end=" ")
print(y, end=" ")
print()

str = "Runoob"
print(str[0:-1])
print(str[2:5])


def printStr(str):
    print(str)
    return str


b = printStr("afterloe")
print(b)

print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))