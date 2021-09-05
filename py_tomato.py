#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import time
import json
from datetime import datetime

import pygame
from pygame import mixer

import PySimpleGUI as sg


PYTOMATO_CONF_FILE = "PyTomato.json"
# seconds
DEFAUT_CYCLE = 25 * 60
MAX_CYCLE = 60 * 60 - 1
DEFAULT_MUSIC = "RainyMood.ogg"
DEFAULT_RUN_TIMES = 0
DEFAULT_PAUSE_TIMES = 0

USE_MUSIC = True

def init_config(today):
    if not os.path.exists(PYTOMATO_CONF_FILE) or not os.path.isfile(PYTOMATO_CONF_FILE):
        return DEFAUT_CYCLE, DEFAULT_MUSIC, DEFAULT_RUN_TIMES, DEFAULT_PAUSE_TIMES

    with open(PYTOMATO_CONF_FILE, "r") as fp:
        content = json.load(fp)

    cycle = content.get("cycle", DEFAUT_CYCLE)
    cycle = MAX_CYCLE if cycle > MAX_CYCLE else cycle
    music_file = content.get("music", DEFAULT_MUSIC)
    run_times, pause_times = DEFAULT_RUN_TIMES, DEFAULT_PAUSE_TIMES
    if today in content:
        run_times = content[today].get("Run", DEFAULT_RUN_TIMES)
        pause_times = content[today].get("Pause", DEFAULT_PAUSE_TIMES)

    return cycle, music_file, run_times, pause_times


def save_times(today, run_times, pause_times):
    with open(PYTOMATO_CONF_FILE, "r") as fp:
        content = json.load(fp)

    if today not in content:
        content[today] = dict()

    today_times = content[today]
    today_times["Run"] = run_times
    today_times["Pause"] = pause_times

    with open(PYTOMATO_CONF_FILE, "w", newline="\n") as fp:
        json.dump(content, fp, indent=2)


def main():
    today = datetime.today().strftime("%Y-%m-%d %a")
    default_time, music_file, run_times, pause_times = init_config(today)
    init_music(music_file)

    window = init_window(default_time, run_times, pause_times)
    current_time, start_time = default_time, 0
    last_time = None
    while True:
        if window.find_element("Play").GetText() == "Pause":
            event, _ = window.Read(timeout=10)
            current_time = (start_time - end_time()) // 100
        else:
            event, _ = window.Read()

        if event == "text":
            if last_time and (datetime.now() - last_time).seconds < 1:
                pause_times += 1 if window.find_element("Play").GetText() == "Pause" else 0
                save_times(today, run_times, pause_times)
                break
            last_time = datetime.now()

        if event == 'Play':
            event = window.find_element(event).GetText()

        if event == 'Pause':
            music_pause()
            window.find_element('Play').Update(text='Run')

            pause_times += 1
            save_times(today, run_times, pause_times)
        elif event == 'Run':
            music_unpause()
            start_time = end_time() + default_time * 100
            window.find_element('Play').Update(text='Pause')

            run_times += 1
            save_times(today, run_times, pause_times)

        window.find_element("Times").Update(times_text(run_times, pause_times))

        current_text = countdown_time_text(current_time)
        window.find_element('text').Update(current_text)

        if current_text == "00:00":
            current_time = default_time
            music_pause()
            window['Play'].Update(text='Run')
            window['text'].Update(countdown_time_text(default_time))
    window.close()


def init_window(default_time, run_times=0, pause_times=0):
    sg.SetOptions(element_padding=(0, 0))
    sg.theme("DarkGrey")
    layout = init_layout(default_time, run_times, pause_times)
    return sg.Window('PyTomato',
        auto_size_buttons=False,
        no_titlebar=True,
        use_default_focus=False,
        grab_anywhere=True,
        keep_on_top=True,
        margins=(0,0),
        alpha_channel=0.7).Layout(layout)


def init_layout(default_time, run_times, pause_times):
    frame_layout = [[sg.Button('Run', font=("Consolas", 16), button_color=('#FFFFFF', '#404040'), border_width=0, key='Play')],
                    [sg.Text(times_text(run_times, pause_times), font=("Consolas", 9), auto_size_text=True, key="Times")]]
    return [[sg.Text(countdown_time_text(default_time),
                     size=(6, 1),
                     font=("Consolas", 27),
                     justification='center',
                     key='text',
                     enable_events=True),
             sg.Frame("", layout=frame_layout, element_justification="center", border_width=0)]]


def end_time():
    return int(round(time.time() * 100))

def times_text(run_times, pause_times):
    return "R/P: {:0>3}/{:0>3}".format(run_times, pause_times)

def countdown_time_text(countdown_time):
    return '{:02d}:{:02d}'.format(countdown_time // 60, countdown_time % 60)

def init_music(music_file):
    try:
        pygame.init()
        mixer.init()
        mixer.music.load(os.path.join(os.getcwd(), music_file))
        mixer.music.set_volume(1.0)
        mixer.music.play(-1)
        mixer.music.pause()
    except Exception as e:
        print("exception when init music", e)
        global USE_MUSIC
        USE_MUSIC = False

def music_pause():
    if not USE_MUSIC:
        return
    mixer.music.pause()

def music_unpause():
    if not USE_MUSIC:
        return
    mixer.music.unpause()

if __name__ == '__main__':
    main()
