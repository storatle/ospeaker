#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import xml.etree.ElementTree as ET
import tkinter as tk
import tkinter.ttk as TTK
from functools import partial
from brikkesys import Database
import pdfgen
import xmlgen
import csv
from PIL import ImageTk, Image
import heading as hdn
from orace import Race
import sys
import screeninfo

class Window(tk.Tk):
    def __init__(self,*args,**kwargs):
        tk.Tk.__init__(self,*args,**kwargs)
        self.notebook = TTK.Notebook()
        global page_break
        global one_active_class
        global for_start
        global with_points
        global active_class 
        global race_number
        active_class = 0
        page_break = tk.BooleanVar()
        one_active_class = tk. BooleanVar()
        for_start = tk.BooleanVar()
        with_points = tk.BooleanVar()
        # Get the monitor's size
        # Get the screen which contains top
        current_screen = self.get_monitor_from_coord(self.winfo_x(), self.winfo_y())
        self.win_width = current_screen.width
        self.win_height = current_screen.height
        res= str(self.win_width)+'x'+str(self.win_height)
        #print('resolution: {}'.format(res))
        self.geometry(res)
        self.configure(background='black')
        race_number = 0

    def get_monitor_from_coord(self, x, y):
        monitors = screeninfo.get_monitors()

        for m in reversed(monitors):
            if m.x <= x <= m.width + m.x and m.y <= y <= m.height + m.y:
                return m
        return monitors[0]


    def add_tab(self, args):
        # Legger inn administrasjonsfane som har 2 vinduer. En for de som er ute og en for de som er imål
        adm_tab = Tab(self.notebook, width=str(self.win_width), height=str(int((self.win_height-250)/2)), tab_type='adm', database=args.server )
        self.notebook.add(adm_tab,text='Administrasjon')
        res_tab = Tab(self.notebook, width=str(self.win_width), height=str(int(self.win_height-250)), tab_type='results', database=args.server)
        self.notebook.add(res_tab,text='Resultater')
        if args.prewarn:
            pre_tab = Tab(self.notebook, width=str(self.win_width), height=str(int(self.win_height-250)), tab_type='prewarn', database=args.server)
            self.notebook.add(pre_tab,text='forvarsel')
        if args.poengo:
            poengo_tab = Tab(self.notebook, width=str(self.win_width), height=str(int(self.win_height-250)), tab_type='poengo', database=args.server)
            self.notebook.add(poengo_tab,text='Poeng-O')
        if args.finish:
            finish_tab = Tab(self.notebook, width=str(self.win_width), height=str(int(self.win_height - 250)), tab_type='finish', database=args.server)
            self.notebook.add(finish_tab, text='Målliste')
       # if args.prewarn_2:
       #     pre_tab = Tab(self.notebook, width=str(self.win_width), height=str(int(self.win_height-250)), tab_type='prewarn', database=args.server, pre_database=args.prewarn)
       #     self.notebook.add(pre_tab,text='forvarsel')
 
        self.notebook.grid(row=0)

    def add_menu(self, args):
        self.db = Database(args.server)
        # Fil-Meny
        menubar = tk.Menu(self, bg="white")
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_separator()
        file_menu.add_command(label="Status", command=self.find_99ers)
        file_menu.add_command(label="Exit", command=self.quit)
      
        #  PDF-meny
        pdf_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="PDF", menu=pdf_menu)
        # Lager PDF meny
        pdf_menu.add_command(label="Lag startliste", command=lambda: self.pdf_list(False)) 
        pdf_menu.add_separator()
        pdf_menu.add_command(label="Lag resultatliste", command=lambda: self.pdf_list(True))
        
        # XML-meny
        xml_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="XML", menu=xml_menu)
        #lager XML meny
        xml_menu.add_command(label="Lag resultatliste", command=lambda: self.xml_list()) 

        try:
            self.config(menu=menubar)
        except AttributeError:
            print('Error')

    # Denne laget jeg for å få til å bruke meny, men kanskje jeg kan bruke følgende funksjon i stedet
    # pdf_menu.add_command(label="Lag startliste", command=self.pdf_start_list, self.race, False, self.one_active_class, self.class_name, self.page_break)
    # Det vil i så fall kunne fjerne disse tre funksjonen under 
    def pdf_list(self, results):#, one_active_class, class_name, page_break):
        pdf = pdfgen.Pdf()
        race = Race(self.db, race_number)
        if results:
            pdf.result_list(race, one_active_class.get(), active_class, page_break.get(), with_points.get() )
        else:
            pdf.start_list(race, for_start.get(), one_active_class.get(), active_class, page_break.get())

    def xml_list(self):
        xml = xmlgen.xml()
        race = Race(self.db, race_number)
        xml.result_list(race)

    def find_99ers(self):
        race = Race(self.db, race_number)
        race.make_99_list()

class Tab(tk.Frame):
    def __init__(self,name,*args,**kwargs):
        width = int(kwargs['width'])
        height = int(kwargs['height'])
        left_w = int(width*0.07)
        mid_w = int(width - 2 * left_w)
        self.table_w = mid_w
        ##self.idx=0
        self.runners=[]
        tab_type = kwargs['tab_type']
        self.db = Database(kwargs['database'])
        if 'pre_database'in kwargs:
            self.pre_db = Database(kwargs['pre_database'])
        self.race_number = None
        self.class_name = None
        self.name = None
        self.print_results = False
        self.race = None
        self.break_result_list = False
        self.break_loop_list = False
        self.break_last_list = False
        break_adm = True
        break_res = True
        break_pre = True
        if sys.platform == "win32":
            self.log_file = open("ospeaker.log", "w")
        else:
            self.log_file = open("/var/log/ospeaker.log", "w")

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
        if sys.platform == "win32":
            img = ImageTk.PhotoImage(Image.open("C:\Program Files (x86)\Brikkespy\images\\black_MILO_banner.png").resize((pixels_x, pixels_y)))
        else:
            img = ImageTk.PhotoImage(Image.open("/etc/black_MILO_banner.png").resize((pixels_x, pixels_y)))

        label = tk.Label(btm_frame,bg="black", image = img)
        label.image = img 
        label.pack(side = "bottom", fill = "both", expand = "yes")
        head = hdn.get_heading('resultater')
        heading = list(head.keys())
        columnwidth = [item[0] for item in head.values()]
        anchor = [item[1] for item in head.values()]

        # Spesifiser for de forskjellige vinduene
 
        if tab_type == 'adm':
            # Tabell for de som er i mål
            self.finish =  Table(ctr_mid, width=mid_w, height=height, row_height=30, heading=heading, columnwidth=columnwidth, anchor=anchor)
            # inne.tree.bind("<Double-1>", self.onclick_out)
            # Tabell for de som er ute i skogen
            self.out =  Table(ctr_mid, width=mid_w, height=height, row_height=30,  heading=heading, columnwidth=columnwidth, anchor=anchor)
            # ute.tree.bind("<Double-1>", self.onclick_out)
            tk.Label(self.top_frame, text="Løp:").grid(row=0, column=1, sticky='w')
            # Combobox med alle løp i databasen
            self.combo_races = TTK.Combobox(self.top_frame, width=30, values=list(zip(*self.db.races))[1])
            self.combo_races.grid(row=0, column=2, sticky='w')
            self.combo_races.bind("<<ComboboxSelected>>", self.set_class_buttons)
            # Checkboxes
            # Setter om det skal være sideskift for printing
            self.check = tk.Checkbutton(self.top_frame, text="Print med sideskift", variable=page_break).grid(row=0, column=3, sticky='w')
            self.check2 = tk.Checkbutton(self.top_frame, text="Print aktiv_klasse", variable=one_active_class).grid(row=0, column=4, sticky='w')
            self.check3 = tk.Checkbutton(self.top_frame, text="Print lister for start", variable=for_start).grid(row=0, column=5, sticky='w')
            self.check4 = tk.Checkbutton(self.top_frame, text="Print lister med poeng", variable=with_points).grid(row=0, column=6, sticky='w')

        elif tab_type == 'results':
            self.board = Table(ctr_mid, width=mid_w, height=height, row_height=30, heading=heading, columnwidth=columnwidth, anchor=anchor)
            # self.res.tree.bind("<Double-1>", self.onclick_res)
            # Buttons
            class_button = tk.Button(self.top_frame, text='Klassevis', bg='white', command=partial(self.write_to_board))
            loop_button = tk.Button(self.top_frame, text='Loop', bg='white', command=partial(self.write_to_loop))
            last_button = tk.Button(self.top_frame, text='Siste', bg='white', command=partial(self.write_to_last))
            class_button.grid(row=0, column=0)
            loop_button.grid(row=0, column=1)
            last_button.grid(row=0, column=2)

        elif tab_type == 'finish':
            self.finish = Table(ctr_mid, width=mid_w, height=height, row_height=30, heading=heading, columnwidth=columnwidth, anchor=anchor)
            # self.res.tree.bind("<Double-1>", self.onclick_res)
            # Buttons
            class_button = tk.Button(self.top_frame, text='Klassevis', bg='white', command=partial(self.write_to_finish))
            class_button.grid(row=0, column=0)

        elif tab_type == 'prewarn':
            self.pre = Table(ctr_mid, width=mid_w, height=height, row_height=30, heading=heading, columnwidth=columnwidth, anchor=anchor)
            # Buttons
            self.button = tk.Button(self.top_frame, text='Forvarsel', command=partial(self.write_to_prewarn))
            self.button.grid(row=0, column=0)

        elif tab_type == 'poengo':

            head = hdn.get_heading('poengo')
            heading = list(head.keys())
            columnwidth = [item[0] for item in head.values()]
            anchor = [item[1] for item in head.values()]
            self.poengo = Table(ctr_mid, width=mid_w, height=height, row_height=30, heading=heading, columnwidth=columnwidth, anchor=anchor)
            # Buttons
            self.button = tk.Button(self.top_frame, text='PoengO', command=partial(self.write_poengo))
            self.button.grid(row=0, column=0)
            self.button = tk.Button(self.top_frame, text='csv', command=partial(self.write_poengo_csv))
            self.button.grid(row=0, column=1)

    def write_to_admin(self, class_name):
        global break_res
        break_res = True
        global break_pre
        break_pre = True
        global break_adm
        break_adm = False
        self.write_admin_list(class_name)


# Result lists
    def write_to_board(self):
        global break_res
        break_res = False
        global break_adm
        break_adm = True
        global break_pre
        break_pre = True
        self.board.tree.delete(*self.board.tree.get_children())
        self.race = Race(self.db, race_number)
        self.class_names = iter(self.race.class_names)
        self.break_pre_list = True
        self.break_board_list = False
        self.break_loop_list = True
        self.break_last_list = True
        self.write_board_list()

    def write_to_loop(self):
        # Alle de boolske variablene settes for å stoppe innlesing fra databasen nå man endre bilde
        global break_res
        break_res = False
        global break_adm
        break_adm = True
        global break_pre
        break_pre = True
        #print("write_to_loop - {}".format(break_res))
        self.break_pre_list = True
        self.break_board_list = True
        self.break_loop_list = False
        self.break_last_list = True
        self.board.tree.delete(*self.board.tree.get_children())
        self.race = Race(self.db, race_number)
        self.write_loop_list(0)

    def write_to_last(self):
        # Alle de boolske variablene settes for å stoppe innlesing fra databasen nå man endre bilde
        global break_res
        break_res = False
        global break_adm
        break_adm = True   
        global break_pre
        break_pre = True
        self.break_pre_list = True
        self.break_board_list = True
        self.break_loop_list = True 
        self.break_last_list = False
        self.board.tree.delete(*self.board.tree.get_children())
        self.race = Race(self.db, race_number)
        self.write_last_list()

    def write_to_prewarn(self):
        # Alle de boolske variablene settes for å stoppe innlesing fra databasen nå man endre bilde
        global break_res
        break_res = True
        global break_adm
        break_adm = True   
        global break_pre
        break_pre = False
        self.write_prewarn_list()

    def write_to_finish(self):
       # self.finish.tree.delete(*self.finish.tree.get_children())
        self.race = Race(self.db, race_number)
       #self.class_names = iter(self.class_names)
        self.write_finish_list()

    def write_admin_list(self, class_name):
        #print("write_to_admin_list - break_adm =  {}".format(break_adm))
        if not break_adm:
            active_class = class_name
            # denne kjøres kontinuerlig så og derfor må jeg sette flagg som ikke endrer urangerte listeri/
            # kontinuerlig. Her setter jeg randomize lik False
            self.randomized = False
            if self.class_name:
                self.finish.after_cancel(self.finish_tree_alarm)
                self.out.after_cancel(self.out_tree_alarm)

            # Her legger jeg inn en resultatliste som bare inneholde de som er i mål, DNS og DSQ
            self.finish.tree.delete(*self.finish.tree.get_children())
            result_list = self.race.make_result_list(class_name)
            self.write_table(result_list,'res')
            self.finish_tree_alarm = self.finish.after(5000, self.write_admin_list, class_name)
            self.class_name = class_name

            # Her legger jeg inn en resultatliste som bare inneholder de som er ute
            self.out.tree.delete(*self.out.tree.get_children())
            out_list = self.race.make_result_list(class_name, 'out')
            self.write_table(out_list,'out')
            self.out_tree_alarm = self.out.after(5000, self.write_admin_list, class_name)

    def write_finish_list(self):
        self.finish.tree.delete(*self.finish.tree.get_children())
        all_lists = []
        for class_name in self.race.class_names:
            # Henter resultatliste for klassen
            result_list = self.race.make_result_list(class_name)
            if result_list:  # Sjekker om det er deltaker i klassen
                all_lists.extend(result_list)
        finish_list = [i for i in all_lists if not ((i['tag'] == 'arr') or i['tag'] == 'dns')]
        finish_list = (sorted(finish_list, key=lambda i: str(i['Innkomst'])))
        # Her må jeg sjekke om det er noen i klassen
        if finish_list:
            for name in (finish_list):
                self.finish.LoadinTable(name)
        self.finish_tree_alarm = self.finish.after(500, self.write_finish_list)

    def write_board_list(self):  # Skriver resultat liste per klasse
        #print("write_to_board_list - break_res =  {}".format(break_res))
        if not self.break_board_list and not break_res:
            class_list = []
            class_name = self.get_next_element(self.class_names)
            print('Klasse {}'.format(class_name))
            if class_name is None:
                self.class_names = iter(self.race.class_names)
                class_name = self.get_next_element(self.class_names)
            self.board.tree.delete(*self.board.tree.get_children())
            result_list = self.race.make_result_list(class_name)
            # Her må jeg sjekke om det er noen i klassen
            if result_list:
                class_list.extend([hdn.line_shift()])
                class_list.extend([hdn.class_heading(class_name)])
                class_list.extend(result_list)
                for name in reversed(class_list):
                    self.board.LoadinTable(name)
            else:
                self.write_board_list()
            self.board_tree_alarm = self.board.after(5000, self.write_board_list)

    def write_loop_list(self, loop):
        #print("write_to_loop_list - break_res =  {}".format(break_res))
        if not self.break_loop_list and not break_res:
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

    def write_last_list(self):
        #print("write_to_last_list - break_res =  {}".format(break_res))
        if not self.break_last_list and not break_res:
            last_list = []
            last_list = self.make_last_list()
            self.board.tree.delete(*self.board.tree.get_children())
            if last_list:
                for name in reversed(last_list):
                    self.board.LoadinTable(name)
            else:
                self.write_board_list()
            self.board_tree_alarm = self.board.after(5000, self.write_last_list)

    def write_prewarn_list(self):
        #print("write_to_last_list - break_pre =  {}".format(break_pre))
        if not break_pre:
            self.race = Race(self.db, race_number)
            prewarn_list= []
            self.pre.tree.delete(*self.pre.tree.get_children())
            prewarn_list = self.race.make_prewarn_list()
            for name in reversed(prewarn_list):
                self.pre.LoadinTable(name)
            self.pre_tree_alarm = self.pre.after(5000, self.write_prewarn_list)

    def write_poengo(self):
        self.poengo.tree.delete(*self.poengo.tree.get_children())
        self.poeng = Race(self.db, race_number)
        self.write_poengo_list()

    def write_poengo_list(self):  # Skriver resultat liste per klasse
        self.poengo.tree.delete(*self.poengo.tree.get_children())
        results_list = self.make_treeview_list(self.poeng.make_point_list())
        for name in reversed(results_list):
            self.poengo.LoadinTable(name)
        self.poengo_tree_alarm = self.poengo.after(5000, self.write_poengo_list)

    def write_poengo_csv(self):
        poeng = Race(self.db, race_number)
        results = poeng.make_point_list()
        self.write_csv_list(results, poeng.heading)
   
    def write_csv_list(self, results, heading):
        result_writer = csv.writer(open("resultater.csv", "w"))
        if 'klatresek' in heading: 
            heading.remove('klatresek')
        if 'sprintsek' in heading:
            heading.remove('sprintsek')
        csv_list = []
        csv_list.append(heading)
        for result in results:
            res = []
            for key in heading:
                if key in result.keys():
                    res.append(result[key])
                else:
                    res.append('')
            csv_list.append(res)
        result_writer.writerows(csv_list)
    
    def make_treeview_list(self, results):
        tree_results=[]
        for result in results:
            tree_results.append(self.poeng.set_poengo_text(result))
        return tree_results

    def write_table(self, data, table):
        for name in reversed(data):
            if table == 'res':
                self.finish.LoadinTable(name)
            else:
                self.out.LoadinTable(name)

    def make_loop_list(self):
        loop_list = []
        result_list = []
        for class_name in self.race.class_names:
            # Henter resultatliste for klassen
            result_list = self.race.make_result_list(class_name)
            if result_list:  # Sjekker om det er deltaker i klassen
                loop_list.extend([hdn.line_shift()])
                loop_list.extend([hdn.class_heading(class_name)])
                loop_list.extend(result_list)
        return loop_list

    def make_last_list(self):
        last_list = []
        last_list = self.race.make_last_list()
        return last_list


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
    def get_next_element(self, my_itr):
        try:
            return next(my_itr)
        except StopIteration:
            return None

    # Henter løpene og lager knapper for hver eneste klasse i løpet.
    def set_class_buttons(self, races):
        # Henter ønsket løp fra Combobox
        global race_number
        race_number = self.combo_races.current()
        self.race = Race(self.db, race_number)
#        # Lager knapper for hver klasse
        try:
           if self.buttons:
                for button in self.buttons:
                    button.destroy()
                self.button.clear()    
        except:
            self.buttons = []
        i = 0
        j = 0
        for class_name in self.race.class_names:
            if class_name:
                self.buttons.append(tk.Button(self.ctr_left, text=class_name, command=partial(self.write_to_admin, class_name)))
                self.buttons[i].grid(row=i,column=j, padx = 10)
                i += 1
                if i >= 30: # Her bør jeg regne ut hvor mange knapper man kan ha i høyden før man legger til ny knappekolonne
                    j += 1
                    i = 0

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
        self.heading = kwargs['heading']
        self.anchor = kwargs['anchor']
        self.columnwidth = kwargs['columnwidth']
#        self.heading=['Startnum','Plass','Navn','Klubb','Klasse','Starttid','Tid','Differanse']
#        self.columnwidth=[0.07,0.07,0.26,0.20,0.1,0.1,0.1,0.1]
        self.rows = int(self.height/self.rowheight)
        self.tree = self.CreateUI()
        self.tree.tag_configure('title', background='green')
        self.tree.tag_configure('ute', background='orange')
        self.tree.tag_configure('inne', background="white")
        self.tree.tag_configure('last', background="green")
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
        vsb.place(x=-17+self.width, y=20, height=int(self.rowheight*self.rows))
        i = 0
        tv.configure(yscrollcommand=vsb.set)
        tv['columns'] = tuple(self.heading)
        tv.heading("#0", text='Startnum', anchor='center')
        tv.column("#0", anchor="center", width=int(self.width*0.07)) # 7%
        for title in self.heading:
            tv.heading(title,text=title)
            tv.column(title, anchor=self.anchor[i], width=int(self.width*self.columnwidth[i]))
            i +=1

        tv.grid(sticky=('n'))#, 'S', 'W', 'E'))
        return tv

    def LoadTable(self):
        self.tree.insert('', 'end', text="First", values=('10:00', '10:10', 'Ok'))

    def LoadinTable(self, entry):
        # Sjekker om de har startnummer, dette trenger jeg vel ikke lenger?
        if not entry['Startnr']:
            entry['Startnr'] = ' '
        a = []
        for title in self.heading:
            a.append(entry[title])
        a = tuple(a)
        self.tree.insert('', 0, text=entry['Startnr'], values=(a), tags=entry['tag'])
        #self.tree.insert('', 0,  values=(entry['Plass'], entry['Navn'], entry['Klubb'], entry['Klasse'], entry['Starttid'], entry[str('Tid')], entry['Diff']), tags = (entry['t:wq
