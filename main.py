#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   main.py
@Time    :   2021/10/25 14:05:57
@Author  :   YuFanWenShu 
@Contact :   1365240381@qq.com

'''

# here put the import lib

from mymusic import Music, Staff, Converter

def main():
    music = Music("Python演奏国际歌")
    music.load_staff("国际歌.txt")
    music.save_music("Python演奏国际歌")
    music.draw_wave()

if __name__ == "__main__":
    main()