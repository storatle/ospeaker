#!/usr/bin/env python3
# -*- coding: utf-8 -*- 
import ospeakerUI as gui
import tkinter as tk  # Import tKinter
#sudo apt-get install python3-pil.imagetk


def main():
    my_app = gui.Window()
    res= str(my_app.winfo_screenwidth())+'x'+str(my_app.winfo_screenheight())
    my_app.geometry(res)
    my_app.configure(background='black')
    menubar = tk.Menu(my_app, bg = "white")

    # file-Meny 
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Open...", command=dummy_func)#,'Open file....')
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=my_app.quit)
    #my_app.notebook.tab(0).page_break
    try:
        my_app.config(menu=menubar)
    except AttributeError:
        print('Error')
    my_app.mainloop()   
    #gui()

def dummy_func(self, name):
    print(name)

if __name__=="__main__":
    main()  # Create GUI


