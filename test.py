#!/usr/bin/env python3
# -*- coding: utf-8 -*- 
import ospeakerUI as gui
import tkinter as tk  # Import tKinter
import tkinter.ttk as TTK
#sudo apt-get install python3-pil.imagetk

my_app = gui.Window()
res = '700x400'
my_app.geometry(res)
my_app.configure(background='black')

# create all of the main containers
top_frame = tk.Frame(my_app, bg='white', width=700, height=50)  # , pady=3)
center = tk.Frame(my_app,  bg='black')#, width=50, height=140)  # , padx=3, pady=3)
btm_frame = tk.Frame(my_app,  bg='red')#, width=450, height=145)  # , pady=3)
#btm_frame2 = tk.Frame(self, width=450, height=60)  # , pady=3)
# layout all of the main containers
#self.grid_rowconfigure(1, weight=1)
#self.grid_columnconfigure(0, weight=1)

top_frame.grid(row=0, sticky="ew")
center.grid(row=1, sticky="nsew")
btm_frame.grid(row=2, sticky="ew")

# create the center widgets
center.grid_rowconfigure(0, weight=1)
center.grid_columnconfigure(0, weight=1)


ctr_left = tk.Frame(center, bg='black',width=500, height=100)  # , padx=3, pady=3)
ctr_mid = tk.Frame(center, width=100, height=100)  # , padx=3, pady=3)
ctr_right = tk.Frame(center,  bg='black', width=50, height=100)  # , padx=3, pady=3)

ctr_left.grid(row=0, column=0, sticky="nsew")
ctr_mid.grid(row=0, column=1, sticky="nsew")
ctr_right.grid(row=0, column=2, sticky="nsew")

## create the center widgets
#ctr_left.grid_rowconfigure(1, weight=1)
#ctr_left.grid_columnconfigure(1, weight=1)
#
button=tk.Button(ctr_left, text='Test').grid(row=0,column=0)

my_app.mainloop()   

