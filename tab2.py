#!/usr/bin/env python3
import tkinter as tk
import tkinter.ttk as TTK
class gui:
    def __init__(self):
        my_app = App()
        my_app.geometry('1700x1000')
        my_app.mainloop()




class App(tk.Tk):
    def __init__(self,*args,**kwargs):
       tk.Tk.__init__(self,*args,**kwargs)
       self.notebook = TTK.Notebook()
       self.add_tab()
       self.notebook.grid(row=0)
  
    def add_tab(self):
        tab = Results(self.notebook)
        tab2 = Prewarn(self.notebook) 
        self.notebook.add(tab,text="Resultater")
        self.notebook.add(tab2,text="Forvarsel")
  
  
class Results(tk.Frame):
   def __init__(self,name,*args,**kwargs):
       tk.Frame.__init__(self,*args,**kwargs)
       top_frame = tk.Frame(self, width=450, height = 50)
       self.label = tk.Label(self, text="Hi This is Tab1")

       self.label.grid(row=1,column=0,padx=10,pady=10)
       self.name = name
  
class Prewarn(tk.Frame):
   def __init__(self,name,*args,**kwargs):
       tk.Frame.__init__(self,*args,**kwargs)
       self.label = tk.Label(self, text="Hi This is Tab2")
       self.label.grid(row=1,column=0,padx=10,pady=10)
       self.name = name

def dummy():
    print('Hallo')

if __name__ == "__main__":
    my_app = App()
    my_app.geometry('1700x1000')
    menubar = tk.Menu(my_app)
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='File',menu=dummy)
    my_app.config(menu=menubar)
    my_app.mainloop()
