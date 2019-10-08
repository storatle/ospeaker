#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import xml.etree.ElementTree as ET
import tkinter as tk
import tkinter.ttk as TTK
from functools import partial
from brikkesys import Database
import pdfgen
from PIL import ImageTk, Image
from oRace import Race

class Window(tk.Tk):
    def __init__(self,*args,**kwargs):
        tk.Tk.__init__(self,*args,**kwargs)
        self.notebook = TTK.Notebook()
        self.os = 'linux'
        global page_break
        global one_active_class
        global for_start
        page_break = tk.BooleanVar()
        one_active_class = tk. BooleanVar()
        for_start = tk.BooleanVar()
        global race_number
        self.win_width = self.winfo_screenwidth()
        self.win_height = self.winfo_screenheight()
        res= str(self.win_width)+'x'+str(self.win_height)
        self.geometry(res)
        self.configure(background='black')
        race_number = 0

    def add_tab(self, db, os):
        # Legger inn administrasjonsfane som har 2 vinduer. En for de som er ute og en for de som er imål
        adm_tab= Tab(self.notebook, width=str(self.win_width), height=str(int((self.win_height-260)/2)), tab_type='adm', database=db, os=os)
        self.notebook.add(adm_tab,text='Administrasjon')
        res_tab= Tab(self.notebook, width=str(self.win_width), height=str(int(self.win_height-250)), tab_type='results', database=db, os=os)
        self.notebook.add(res_tab,text='Resultater')
        pre_tab = Tab(self.notebook, width=str(self.winfo_screenwidth()), height=str(self.winfo_screenheight()), tab_type='prewarn', database=db, os=os)
        self.notebook.add(pre_tab,text='Forvarsel')
        self.notebook.grid(row=0)

    def add_menu(self, db, os):
        self.db = Database(db, os)
        self.os = os
        # Fil-Meny
        menubar = tk.Menu(self, bg="white")
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
      
        #  PDF-meny
        pdf_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="PDF", menu=pdf_menu)
        # Lager PDF meny
        pdf_menu.add_command(label="Lag startliste", command=lambda: self.pdf_list(False)) 
        pdf_menu.add_separator()
        pdf_menu.add_command(label="Lag resultatliste", command=lambda: self.pdf_list(True))

        try:
            self.config(menu=menubar)
        except AttributeError:
            print('Error')

    # Denne laget jeg for å få til å bruke meny, men kanskje jeg kan bruke følgende funksjon i stedet
    # pdf_menu.add_command(label="Lag startliste", command=self.pdf_start_list, self.race, False, self.one_active_class, self.class_name, self.page_break)
    # Det vil i så fall kunne fjerne disse tre funksjonen under 
    def pdf_list(self, results):#, one_active_class, class_name, page_break):
        pdf = pdfgen.Pdf(self.os)
        race = Race(self.db, race_number, self.os)
        if results:
            pdf.result_list(race, one_active_class.get(), active_class, page_break.get())
        else:
            pdf.start_list(race, for_start.get(), one_active_class.get(), active_class, page_break.get())

class Tab(tk.Frame):
    def __init__(self,name,*args,**kwargs):
        self.os = kwargs['os']
        width = int(kwargs['width'])
        height = int(kwargs['height'])
        left_w = int(width*0.07)
        mid_w = int(width - 2 * left_w)
        self.table_w = mid_w
        tab_type = kwargs['tab_type']
        self.db = Database(kwargs['database'],kwargs['os'])
        self.race_number = None
        self.class_name = None
        self.name = None
        self.print_results = False
        self.race = None
        self.break_result_list = False
        self.break_loop_list = False
        if self.os == 'linux':
            self.log_file = open("/var/log/ospeaker.log", "w")
        else:
            self.log_file = open("ospeaker.log", "w")

       #Standard frame for alle tabs
        tk.Frame.__init__(self)
        # create all of the main containers
        self.top_frame = tk.Frame(self, bg='white')#, width=100, height=50)  # , pady=3)
        center = tk.Frame(self,  bg='black')#, width=50, height=40)  # , padx=3, pady=3)
        btm_frame = tk.Frame(self,  bg='black')#, width=450, height=45)  # , pady=3)

        # layout all of the main containers
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.top_frame.grid(row=0, sticky="ew")
        center.grid(row=1, sticky="nsew")
        btm_frame.grid(row=2, sticky="ew")

        # create the center widgets
        center.grid_rowconfigure(0, weight=1)
        center.grid_columnconfigure(0, weight=0)

        self.ctr_left = tk.Frame(center, bg='black',width=left_w, height=100)  # , padx=3, pady=3)
        ctr_mid = tk.Frame(center, width=mid_w, height=100)  # , padx=3, pady=3)
        ctr_right = tk.Frame(center,  bg='black', width=left_w, height=100)  # , padx=3, pady=3)
        
        self.ctr_left.grid(row=0, column=0, sticky="ns")
        ctr_mid.grid(row=0, column=1, sticky="nsew")
        ctr_right.grid(row=0, column=2, sticky="nsew")

    #   Logo Banner
        pixels_x = 700
        pixels_y = int(pixels_x * 0.144)
        if self.os == 'linux':
            img = ImageTk.PhotoImage(Image.open("/etc/black_MILO_banner.png").resize((pixels_x, pixels_y)))
        else:
            img = ImageTk.PhotoImage(Image.open("black_MILO_banner.png").resize((pixels_x, pixels_y)))

        label = tk.Label(btm_frame,bg="black", image = img)
        label.image = img 
        label.pack(side = "bottom", fill = "both", expand = "yes")

        # Spesifiser for de forskjellige vinduene
        if tab_type == 'results':
            self.board = Table(ctr_mid, width=mid_w, height=height, row_height=30)
        #    self.res.tree.bind("<Double-1>", self.onclick_res)
        # Buttons
            class_button = tk.Button(self.top_frame, text='Klassevis', bg='white', command=partial(self.write_to_board))
            loop_button = tk.Button(self.top_frame, text='Loop', bg='white', command=partial(self.write_to_loop))
            class_button.grid(row=0, column=0)
            loop_button.grid(row=0, column=1)

        elif tab_type == 'prewarn':
            self.pre = Table(ctr_mid, width=mid_w, height=height, row_height=30)
            # Buttons
            self.button = tk.Button(self.top_frame, text='start forvarsel', command=partial(self.write_prewarn_list))
            self.button.grid(row=0, column=0)

        elif tab_type == 'adm':
            # Tabell for de som er i mål
            self.finish =  Table(ctr_mid, width=mid_w, height=height, row_height=30)
    #        inne.tree.bind("<Double-1>", self.onclick_out)
            # Tabell for de som er ute i skogen
            self.out =  Table(ctr_mid, width=mid_w, height=height, row_height=30)
    #        ute.tree.bind("<Double-1>", self.onclick_out)
            tk.Label(self.top_frame, text="Løp:").grid(row=0, column=1, sticky='w')
            # Combobox med alle løp i databasen
            self.combo_races = TTK.Combobox(self.top_frame, width=30, values=list(zip(*self.db.races))[1])
            self.combo_races.grid(row=0, column=2, sticky='w')
            self.combo_races.bind("<<ComboboxSelected>>", self.set_class_buttons)
    #        Checkboxes
            # Setter om det skal være sideskift for printing
            self.check = tk.Checkbutton(self.top_frame, text="Print med sideskift", variable=page_break).grid(row=0, column=3, sticky='w')
            self.check2 = tk.Checkbutton(self.top_frame, text="Print aktiv_klasse", variable=one_active_class).grid(row=0, column=4, sticky='w')
            self.check3 = tk.Checkbutton(self.top_frame, text="Print lister for start", variable=for_start).grid(row=0, column=5, sticky='w')

# Henter løpene og lager knapper for hver eneste klasse i løpet.
    def set_class_buttons(self, races):
        # Henter ønsket løp fra Combobox
        global race_number
        race_number = self.combo_races.current()
        self.race = Race(self.db, race_number, self.os)
#        # Lager knapper for hver klasse
        try:
           if self.buttons:
                for button in self.buttons:
                    button.destroy()
        except:
            self.buttons = list()
        i = 0
        j = 0
        for class_name in self.race.class_names:
            self.buttons.append(tk.Button(self.ctr_left, text=class_name, command=partial(self.write_admin_list, class_name)).grid(row=i,column=j, padx = 10))
            i += 1
            if i >= 30: # Her bør vi regne ut hvor mane knappe man kan ha i høyden før man legger til ny knappekolonne
                j += 1
                i = 0

    def write_admin_list(self, class_name):
        global active_class
        active_class = class_name
        # denne kjøres kontinuerlig så og derfor må jeg sette flagg om ikke endrer urangerte listeri/
        # kontinuerlig. Her setter jeg randomize lik False
        self.randomized = False
        if self.class_name:
            self.finish.after_cancel(self.finish_tree_alarm)
            self.out.after_cancel(self.out_tree_alarm)

        # Her legger jeg inn en resultatliste som bare inneholde de som er i mål, DNS og DSQ
        self.finish.tree.delete(*self.finish.tree.get_children())
        result_list = self.race.make_result_list(class_name)
        self.write_table(result_list,'res')
        self.finish_tree_alarm = self.finish.after(200, self.write_admin_list, class_name)
        self.class_name = class_name

        # Her legger jeg inn en resultatliste som bare inneholder de som er ute
        self.out.tree.delete(*self.out.tree.get_children())
        out_list = self.race.make_result_list(class_name, 'out')
        self.write_table(out_list,'out')
        self.out_tree_alarm = self.out.after(250, self.write_admin_list, class_name)

    def write_prewarn_list(self):
        prewarn_list= []
        self.race = Race(self.res_db, race_number, self.os)
        #Her legger jeg inn en resultatliste som bare inneholde de som er i mål, DNS og DSQ
        self.pre.tree.delete(*self.pre.tree.get_children())
        self.find_runner()
        for runner in self.runners:
            runner = list(runner)
            runner[10] = self.race.set_tag(runner[10])
            # sjekker om løperen ikke er kommet i mål.
            if runner[10] =='ute':
                #Regner ut tiden som skal vises i Vindu. Ikke på resultatlister
                try:
                    runner[8] = self.race.get_time(runner[14])
                except:
                    if runner[10] == 'dns':
                        runner[8] = 'DNS'
            if not runner[8]:
                runner[8] = runner[10]
            prewarn_list.insert(0,self.race.set_runner_details(runner))
        for name in reversed(prewarn_list):
            self.pre.LoadinTable(name)
        self.pre_tree_alarm = self.pre.after(200, self.write_prewarn_list)

    def find_runner(self):
        nums = self.pre_db.read_start_numbers()
        for num in nums:
            if self.idx < num[0]:
                self.idx = num[0]
                try:
                    start_num = int(num[1])
                    runner = self.race.find_runner(start_num)
                    if runner:
                        self.runners.append(runner)
                except:
                    str_num = num
                    self.log_file.write("No startnumbers {0}: \n".format(str(num)))
                    self.log_file.flush()

    def write_table(self, data, table):
        for name in reversed(data):
            if table == 'res':
                self.finish.LoadinTable(name)
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

    def write_to_board(self):
        self.board.tree.delete(*self.board.tree.get_children())
        self.race = Race(self.db, race_number, self.os)
        self.class_names = iter(self.race.class_names)
        self.break_result_list = False
        self.break_loop_list = True
        self.write_result_list()

    def write_to_loop(self):
        self.board.tree.delete(*self.board.tree.get_children())
        self.break_result_list = True
        self.break_loop_list = False
        self.write_loop_list(0)

    def write_result_list(self):  # Skriver resultat liste per klasse
        if not self.break_result_list:
            class_list = []
            class_name = self.get_next_element(self.class_names)
            self.race = Race(self.db, race_number, self.os)
            if class_name is None:
                self.class_names = iter(self.race.class_names)
                class_name = self.get_next_element(self.class_names)
            self.board.tree.delete(*self.board.tree.get_children())
            result_list = self.race.make_result_list(class_name)
            # Her må jeg sjekke om det er noen i klassen
            if result_list:
                class_list.extend([self.line_shift()])
                class_list.extend([self.class_heading(class_name)])
                class_list.extend(result_list)
                for name in reversed(class_list):
                    self.board.LoadinTable(name)
            else:
                self.write_result_list()
            self.board_tree_alarm = self.board.after(5000, self.write_result_list)

    def get_next_element(self, my_itr):
        try:
            return next(my_itr)
        except StopIteration:
            return None

    def make_loop_list(self):
        loop_list = []
        result_list = []
        race = Race(self.db, race_number, self.os)
        for class_name in race.class_names:
            # Henter resultatliste for klassen
            result_list = race.make_result_list(class_name)
            if result_list:  # Sjekker om det er deltaker i klassen
                loop_list.extend([self.line_shift()])
                loop_list.extend([self.class_heading(class_name)])
                loop_list.extend(result_list)
        return loop_list

    def write_loop_list(self, loop):
        if not self.break_loop_list:
            loop_list = self.make_loop_list()
            loop_list = loop_list[loop:] + loop_list[:loop]
            loop_length = len(loop_list)
            if loop >= loop_length:
                loop = 0
            self.board.tree.delete(*self.board.tree.get_children())
            for name in reversed(loop_list):
                self.board.LoadinTable(name)
            loop += 1
            self.board_tree_alarm = self.board.after(1000, self.write_loop_list, loop)

    def line_shift(self):
        text = {
            'Startnr': None,
            'Plass': str(''),
            'Navn': str(''),
            'Klubb': str(''),
            'Tid': str(''),
            'Diff': str(''),
            'Klasse': str(''),
            'Starttid': str(''),
            'tag': str(''),
            'Brikkenr': str(''),
            'Poeng': str('')
        }
        return text

    def class_heading(self, class_name):
        text = {
            'Startnr': None,
            'Plass': str(''),
            'Navn': str('Klasse: ') + class_name,
            'Klubb': str(''),
            'Tid': str(''),
            'Diff': str(''),
            'Klasse': str(''),
            'Starttid': str(''),
            'tag': str('title'),
            'Brikkenr': str(''),
            'Poeng': str('')
        }
        return text

#   Denne brukes når det dobbelklikkes på navn i tabellen. Foreløpig så skjer detingen ting. peker til update runners som er kommentert ut under.
    def onclick_pre(self, race):
        self.write_loop_list()

    def dummy_func(self, name):
        print(name)

class Table(TTK.Frame):
    def __init__(self, parent, **kwargs): #width, heigth) #rows, row_height):
        TTK.Frame.__init__(self, parent)
        self.width = kwargs['width']
        self.height = kwargs['height']
        self.rowheight = kwargs['row_height']
        self.rows = int(self.height/self.rowheight)
        self.tree = self.CreateUI()
        self.tree.tag_configure('title', background='green')
        self.tree.tag_configure('ute', background='orange')
        self.tree.tag_configure('inne', background="white")
        self.tree.tag_configure('dsq', background='red')
        self.tree.tag_configure('dns', background='grey')
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid(sticky=('n')) #N, S, W, E))

    def CreateUI(self):
        style = TTK.Style()
        style.configure('Treeview', rowheight=self.rowheight, font="Helvetica 16 bold")  # SOLUTION
        tv = TTK.Treeview(self, height=self.rows, style='Treeview')

        vsb = TTK.Scrollbar(self, orient="vertical", command=tv.yview)
        vsb.place(x=-25+self.width, y=20, height=int(self.rowheight*self.rows))

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
        # Sjekker om de har startnummer, dette trenger jeg vel ikke lenger?
        if not entry['Startnr']:
            entry['Startnr'] = ' '
        self.tree.insert('', 0, text=entry['Startnr'], values=(entry['Plass'], entry['Navn'], entry['Klubb'], entry['Klasse'], entry['Starttid'], entry[str('Tid')], entry['Diff']), tags = (entry['tag'],))
