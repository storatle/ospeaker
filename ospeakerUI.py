#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import xml.etree.ElementTree as ET
import tkinter as tk  # Import tKinter
import tkinter.ttk as TTK
from PIL import ImageTk, Image

class Window(tk.Tk):
    def __init__(self,*args,**kwargs):
       tk.Tk.__init__(self,*args,**kwargs)
       self.notebook = TTK.Notebook()
       self.add_tab()
       self.notebook.grid(row=0)
  
    def add_tab(self):
        res= str(self.winfo_screenwidth())+'x'+str(self.winfo_screenheight())
        print(res)
        tab = Results(self.notebook,width=str(self.winfo_screenwidth()),height=str(self.winfo_screenheight()))
        #tab = Results(self.notebook)
        #tab2 = Prewarn(self.notebook) 
        self.notebook.add(tab,text="Resultater")
        #self.notebook.add(tab2,text="Forvarsel")
  
  
class Results(tk.Frame):
    def __init__(self,name,*args,**kwargs):
        #print(name)
        for key, value in kwargs.items():
            print("%s == %s" %(key, value))
        #args = None
        width = int(kwargs['width'])
        height = int(kwargs['height'])
        left_w = int(width*0.1)
        mid_w = int(width - 2 * left_w)
        self. table_w = mid_w

        self.class_name = None
        self.name = None
        self.print_results = False
        self.race = None
        # Flytt disse til menyen
       # global page_break
       # global one_active_class
       # global for_start
       # page_break = tk.BooleanVar()
       # one_active_class = tk. BooleanVar()
       # for_start = tk.BooleanVar()

        tk.Frame.__init__(self,*args,**kwargs)
        # create all of the main containers
        top_frame = tk.Frame(self, bg='white')#, width=1700, height=50)  # , pady=3)
        center = tk.Frame(self,  bg='black')#, width=50, height=40)  # , padx=3, pady=3)
        btm_frame = tk.Frame(self,  bg='black')#, width=450, height=45)  # , pady=3)
        #btm_frame2 = tk.Frame(self, width=450, height=60)  # , pady=3)

        # layout all of the main containers
        #self.grid_rowconfigure(1, weight=1)
        #self.grid_columnconfigure(0, weight=1)

        top_frame.grid(row=0, sticky="ew")
        center.grid(row=1, sticky="nsew")
        btm_frame.grid(row=2, sticky="ew")

        # create the center widgets
        center.grid_rowconfigure(1, weight=1)
        center.grid_columnconfigure(1, weight=1)

        ctr_left = tk.Frame(center, bg='black',width=left_w, height=100)  # , padx=3, pady=3)
        ctr_mid = tk.Frame(center, width=mid_w, height=100)  # , padx=3, pady=3)
        ctr_right = tk.Frame(center,  bg='black', width=left_w, height=100)  # , padx=3, pady=3)
        
        ctr_left.grid(row=0, column=0, sticky="ns")
        ctr_mid.grid(row=0, column=1, sticky="nsew")
        ctr_right.grid(row=0, column=2, sticky="nsew")

        #Logo Banner
        pixels_x = 700
        pixels_y = int(pixels_x * 0.144)
        img = ImageTk.PhotoImage(Image.open("banner.png").resize((pixels_x, pixels_y)))
        label = tk.Label(btm_frame,bg="black", image = img)
        label.image = img 
        label.pack(side = "bottom", fill = "both", expand = "yes")


#        # Tabell i øverste vindu
        res = Table(ctr_mid, width=mid_w, height=height,num_rows=40, row_height=20)
#        self.res.tree.bind("<Double-1>", self.onclick_res)
#
#        # Tabell i nederste vindu
#        self.out = Table(self.ctr_mid, 10)
#        self.out.tree.bind("<Double-1>", self.onclick_out)
#        self.name = name
#

    def get_race(self, race):
        # Henter ønsket løp fra Combobox
        self.race = Race(self.db, self.combo_races.current())
        global race_number
        race_number = self.combo_races.current()
        # Lager knapper for hver klasse
        try:
           if self.button:
                for knapp in self.button:
                    knapp.grid_remove()
        except:
            self.button = list()
        i = 1
        j = 0
        for class_name in self.race.class_names:
 
            self.button.append(tk.Button(self.ctr_left, text=class_name, command=partial(self.write_result_list, class_name)))
            self.button[-1].grid(row=i, column=j)
            i += 1
            if i >= 30:
                j = 1
                i = 1

    def write_result_list(self, class_name):
        global active_class
        active_class = class_name
        # denne kjøres kontinuerlig så og derfor må jeg sette flagg om ikke endrer urangerte listeri/
        # kontinuerlig. Her setter jeg randomize lik False
        self.randomized = False
        if self.class_name:
            self.res.after_cancel(self.res_tree_alarm)
            self.out.after_cancel(self.out_tree_alarm)

        # Her legger jeg inn en resultatliste som bare inneholde de som er i mål, DNS og DSQ
        self.res.tree.delete(*self.res.tree.get_children())
        result_list = self.race.make_result_list(class_name)
        self.write_table(result_list,'res')
        self.res_tree_alarm = self.res.after(200, self.write_result_list, class_name)
        self.class_name = class_name

        # Her legger jeg inn en resultatliste som bare inneholder de som er ute
        self.out.tree.delete(*self.out.tree.get_children())
        out_list = self.race.make_result_list(class_name, 'out')
        self.write_table(out_list,'out')
        self.out_tree_alarm = self.out.after(250, self.write_result_list, class_name)

    def write_table(self, data, table):
        for name in reversed(data):
            if table == 'res':
                self.res.LoadinTable(name)
            else:
                self.out.LoadinTable(name)

    # Denne brukes når det dobbelklikkes på navn i tabellen. Foreløpig så skjer det ingen ting. peker til update runners som er kommentert ut under.    
    def onclick_out(self, race):
        self.update_runner_table()
 
    # Denne brukes når det dobbelklikkes på navn i tabellen. Foreløpig så skjer det ingen ting. peker til update runners som er kommentert ut under.    
    def onclick_res(self, race):
        #self.res.after_cancel(self.res_tree_alarm)
        #item = str(self.res.tree.focus())
        #class_name = self.res.tree.item(item, "value")[2]
        #self.write_result_list(class_name)
        self.update_runner_table()
 
class Table(TTK.Frame):

    def __init__(self, parent, **kwargs): #width, heigth) #rows, row_height):
        TTK.Frame.__init__(self, parent)
        self.width = kwargs['width']
        self.height = kwargs['height']-250
        print(self.width)
        #self.rows = kwargs['num_rows']
        self.rowheight = kwargs['row_height']
        self.rows = int(self.height/self.rowheight)
        print(self.rows)
        self.tree = self.CreateUI()

        self.tree.tag_configure('ute', background='orange')
        self.tree.tag_configure('inne', background="white")
        self.tree.tag_configure('dsq', background='red')
        self.tree.tag_configure('dns', background='grey')

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid(sticky=('n')) #N, S, W, E))

    def CreateUI(self):
        style = TTK.Style()
        style.configure('Treeview', rowheight=self.rowheight, font="Helvetica 20 bold")  # SOLUTION
        tv = TTK.Treeview(self, height=self.rows, style='Treeview')

        vsb = TTK.Scrollbar(self, orient="vertical", command=tv.yview)
        vsb.place(x=30+self.width, y=20, height=self.rowheight*self.rows)

        tv.configure(yscrollcommand=vsb.set)
        tv['columns'] = ('plass', 'navn', 'klubb', 'klasse', 'starttid', 'tid', 'diff')
        tv.heading("#0", text='Startnum', anchor='w')
        tv.column("#0", anchor="center", width=int(self.width*0.07)) # 7%
        tv.heading('plass', text='Plass')
        tv.column('plass', anchor='w', width=int(self.width*0.07)) # 7%
        tv.heading('navn', text='Navn')
        tv.column('navn', anchor='w', width=int(self.width*0.26)) # 26 %
        tv.heading('klubb', text='Klubb')
        tv.column('klubb', anchor='center', width=int(self.width*0.20)) # 20%
        tv.heading('klasse', text='Klasse')
        tv.column('klasse', anchor='center', width=int(self.width*0.1)) # 10%
        tv.heading('starttid', text='Starttid')
        tv.column('starttid', anchor='center', width=int(self.width*0.1)) # 10%
        tv.heading('tid', text='Tid')
        tv.column('tid', anchor='center', width=int(self.width*0.1)) # 10%
        tv.heading('diff', text='Differanse')
        tv.column('diff', anchor='center', width=int(self.width*0.1)) # 10%
        tv.grid(sticky=('n'))#, 'S', 'W', 'E'))
        return tv

    def LoadTable(self):
        self.tree.insert('', 'end', text="First", values=('10:00', '10:10', 'Ok'))

    def LoadinTable(self, entry):
       # print(entry)
        # Sjekker om de har startnummer, dette trenger jeg vel ikke lenger?
        if not entry['Startnr']:
            entry['Startnr'] = ' '
        # self.tree.insert('', 0, text=entry[0], values=(entry[1], entry[2], entry[3], entry[4], entry[5], entry[6], entry[7]), tags = (entry[8],))
        self.tree.insert('', 0, text=entry['Startnr'], values=(entry['Plass'], entry['Navn'], entry['Klubb'], entry['Klasse'], entry['Starttid'], entry[str('Tid')], entry['Diff']), tags = (entry['tag'],))

 
