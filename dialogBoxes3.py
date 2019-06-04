#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from  tkinter import *
from tkinter import filedialog

import os
#from tkFileDialog import askopenfilename, asksaveasfilename
import tkinter.simpledialog

#from ttk import *


class open_file:
    def __init__(self, parent):
        self.parent = parent
        self.fixpoints=[]
        self.name = filedialog.askopenfilename()
        self.file=open(self.name, 'r')
        self.mapfile = self.file.readline().strip()
        self.gpxfile = self.file.readline().strip()
        p1 = self.file.readline()
        p2 = self.file.readline()
        p1 = p1[:-2]
        p1 = p1.strip().split(',') 
        self.fixpoints.append([float(n) for n in p1])
        p2 = p2[:-2]
        p2 = p2.strip().split(',') 
        self.fixpoints.append([float(n) for n in p2])
       # self.alpha = calibrate(fixpoints[0],fixpoints[1]) # skal denne regnes ut her?
        #self.fixpoints = fixpoints    
        

    def apply(self):
        self.result = int(self.e1.get())
        #print first, second 
    

class set_spurttid(tkinter.simpledialog.Dialog):
    
    def body(self, master):
        Label(master, text="Spurttid").grid(row=0)
        #Label(master, text="Fixpoint 2 coordinate:").grid(row=1)
     
        string_e1=str(0)
        #string_e2=str(0)
        self.e1 = Entry(master)
        self. e1.insert(0, string_e1)
        #self.e2 = Entry(master)
        #self. e2.insert(0, string_e2)
        self.e1.grid(row=0, column=1)
        #self.e2.grid(row=1, column=1)
        #return self.e1 # initial focus

    def apply(self):
        self.result = int(self.e1.get())
        #print first, second 


        

#        tv = Treeview(self, height=self.num_lines, style='Treeview')
#        tv['columns'] = ('dato', 'navn', 'deltakere')
#        tv.heading("#0", text='Dato', anchor='w')
#        tv.column("#0", anchor="center")
#        tv.heading('navn', text='Navn')
#        tv.column('navn', anchor='w', width=400)
#        tv.heading('antall', text='Antall')
#        tv.column('antall', anchor='center', width=300)
#        tv.grid(sticky = (N,S,W,E))
#        tv.insert('', 0, text=entry[0], values=(entry[1], entry[2], entry[3], entry[4], entry[5]))
#        
#    def LoadTable(self):
#        tv.insert('', 'end', text="First", values=('10:00','10:10', 'Ok'))
##        self.treeview.insert('', 'end', text="First", values=('10:01','10:11', 'Ok'))
#        
#    def LoadinTable(self, entry):
#        
#        tv.insert('', 0, text=entry[0], values=(entry[1], entry[2], entry[3], entry[4], entry[5]))
#        
#        

    




class set_race():
    def __init__(self, parent, controller):
        self.root = parent;
        self.button = Button(parent, text="Treeview", command=self.ChildWindow)
        self.button.pack()


    def ChildWindow(self):

        #Create menu
        self.popup = Menu(self.root, tearoff=0)
        self.popup.add_command(label="Next", command=self.selection)
        self.popup.add_separator()

        def do_popup(event):
            # display the popup menu
            try:
                self.popup.selection = self.tree.set(self.tree.identify_row(event.y))
                self.popup.post(event.x_root, event.y_root)
            finally:
                # make sure to release the grab (Tk 8.0a1 only)
                self.popup.grab_release()

        #Create Treeview
        win2 = Toplevel(self.root)
        new_element_header=['1st']
        treeScroll = ttk.Scrollbar(win2)
        treeScroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree = ttk.Treeview(win2, columns=new_element_header, show="headings")
        self.tree.heading("1st", text="1st")
        self.tree.insert("" ,  0, text="Line 1", values=("1A"))
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH)

        self.tree.bind("<Button-3>", do_popup)

        win2.minsize(600,30)

    def selection(self):
        print (self.popup.selection)
#class setFixpoints:
#    def __init__(self, parent):
#        self.parent=parent
#        master = Tk()
#        
#        
#        
#    def body(master):    
#        
#        
#        Label(master, text="Fixpoint 1 coordinate:").grid(row=0)
#        Label(master, text="Fixpoint 2 coordinate:").grid(row=1)
#        
#        fixpoints=self.parent.fixpoints
#        lat, lon, px, py=fixpoints[0]
#
#        e1 = Entry(master)
#        e1.insert(0, str(lat)+","+str(lon))
#        e1.grid(row=0, column=1)
#        
#        
#        lat, lon, px, py=fixpoints[1]
#
#        e2 = Entry(master)
#        e2.grid(row=1, column=1)
#        e2.insert(0, str(lat)+","+str(lon))
#
#    def apply(self):
#                self.result = self.e1.get(), self.e2.get()
#        
#    def buttons(master):
#            Button(master, text='Quit', command=master.quit).grid(row=3, column=0, sticky=W, pady=4)
#            Button(master, text='Show', command=apply).grid(row=3, column=1, sticky=W, pady=4)
#            
#    
#    body(master)
#    mainloop( )
        
   
