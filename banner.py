#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import xml.etree.ElementTree as ET
import tkinter as tk  # Import tKinter
import tkinter.ttk as TTK
from PIL import ImageTk, Image
#sudo apt-get install python3-pil.imagetk

class Window(tk.Tk):
    def __init__(self,*args,**kwargs):
       tk.Tk.__init__(self,*args,**kwargs)
       self.notebook = TTK.Notebook()
       self.add_tab()
       self.notebook.grid(row=0)
  
    def add_tab(self):
        tab = Results(self.notebook)
        #tab2 = Prewarn(self.notebook) 
        self.notebook.add(tab,text="Resultater")
        #self.notebook.add(tab2,text="Forvarsel")
  
  
class Results(tk.Frame):
    def __init__(self,name,*args,**kwargs):
        tk.Frame.__init__(self,*args,**kwargs)
        self.class_name = None
        self.name = None
        self.print_results = False
        self.race = None
        global page_break
        global one_active_class
        global for_start
        page_break = tk.BooleanVar()
        one_active_class = tk. BooleanVar()
        for_start = tk.BooleanVar()

        # create all of the main containers
        top_frame = tk.Frame(self, bg='white')#, width=1700, height=50)  # , pady=3)
        center = tk.Frame(self,  bg='black', width=50, height=40)  # , padx=3, pady=3)
        btm_frame = tk.Frame(self,  bg='black', width=450, height=45)  # , pady=3)
        #btm_frame2 = tk.Frame(self, width=450, height=60)  # , pady=3)

        # layout all of the main containers
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        top_frame.grid(row=0, sticky="ew")
        center.grid(row=1, sticky="nsew")
        btm_frame.grid(row=2, sticky="ew")
        #btm_frame2.grid(row=4, sticky="ew")
#        # Label til Combobox
#        tk.Label(top_frame, text="Løp:").grid(row=0, column=1, sticky='w')
#        # Combobox med alle løp i databasen
#        self.combo_races = TTK.Combobox(top_frame, width=30, values=list(zip(*self.db.races))[1])
#        self.combo_races.grid(row=0, column=2, sticky='w')
#        self.combo_races.bind("<<ComboboxSelected>>", self.get_race, "+")
        # Checkboxes
        # Setter om det skal være sideskift for printing
        self.check = tk.Checkbutton(top_frame,  bg='white', text="Print med sideskift", variable=page_break).grid(row=0, column=3, sticky='w')
        self.check2 = tk.Checkbutton(top_frame,  bg='white', text="Print aktiv_klasse", variable=one_active_class).grid(row=0, column=4, sticky='w')
        self.check3 = tk.Checkbutton(top_frame,  bg='white', text="Print lister for start", variable=for_start).grid(row=0, column=5, sticky='w')

        # create the center widgets
        center.grid_rowconfigure(1, weight=1)
        center.grid_columnconfigure(1, weight=1)

        self.ctr_left = tk.Frame(center,  bg='black', width=100, height=290)
        self.ctr_mid = tk.Frame(center, width=1250, height=290)  # , padx=3, pady=3)
        self.ctr_right = tk.Frame(center,  bg='black', width=100, height=190)  # , padx=3, pady=3)
        
        self.ctr_left.grid(row=0, column=0, sticky="ns")
        self.ctr_mid.grid(row=0, column=1, sticky="nsew")
        self.ctr_right.grid(row=0, column=2, sticky="nsew")
        pixels_x = 1700
        pixels_y = int(pixels_x * 0.144)
        img = ImageTk.PhotoImage(Image.open("banner.png").resize((pixels_x, pixels_y)))
        label = tk.Label(btm_frame, image = img)
        label.image = img 
        label.pack(side = "bottom", fill = "both", expand = "yes")
#        # Tabell i øverste vindu
        self.res = Table(self.ctr_mid, 220)
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

    def __init__(self, parent, rows):
        TTK.Frame.__init__(self, parent)
        self.rows = rows
        self.rowheight = 40
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
        vsb.place(x=30+1556, y=20, height=self.rowheight*self.rows)

        tv.configure(yscrollcommand=vsb.set)
        tv['columns'] = ('plass', 'navn', 'klubb', 'klasse', 'starttid', 'tid', 'diff')
        tv.heading("#0", text='Startnum', anchor='w')
        tv.column("#0", anchor="center", width=100)
        tv.heading('plass', text='Plass')
        tv.column('plass', anchor='w', width=100)
        tv.heading('navn', text='Navn')
        tv.column('navn', anchor='w', width=400)
        tv.heading('klubb', text='Klubb')
        tv.column('klubb', anchor='center', width=300)
        tv.heading('klasse', text='Klasse')
        tv.column('klasse', anchor='center', width=200)
        tv.heading('starttid', text='Starttid')
        tv.column('starttid', anchor='center', width=150)
        tv.heading('tid', text='Tid')
        tv.column('tid', anchor='center', width=150)
        tv.heading('diff', text='Differanse')
        tv.column('diff', anchor='center', width=200)
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

 

def main():
    my_app = Window()
    my_app.geometry('1700x1000')
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


