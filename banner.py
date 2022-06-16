#!/usr/bin/env python3
# -*- coding: utf-8 -*- 
import ospeakerUI as gui
import tkinter as tk  # Import tKinter
import tkinter.ttk as TTK
#sudo apt-get install python3-pil.imagetk

class Manager:
    def __init__(self,*args,**kwargs):
        my_app = gui.Window()
        win_width = my_app.winfo_screenwidth()
        win_height = my_app.winfo_screenheight()
        res= str(win_width)+'x'+str(win_height)
        print(res)
        my_app.geometry(res)
        my_app.configure(background='black')
        # Legger inn administrasjonsfane som har 2 vinduer. En for de som er ute og en for de som er imål

        self.adm_tab= gui.Tab(my_app.notebook, width=str(win_width), height=str(int((win_height-260)/2)), tab_type='adm')
        my_app.notebook.add(self.adm_tab,text='Administrasjon')

        self.res_tab= gui.Tab(my_app.notebook, width=str(win_width), height=str(int(win_height-250)), tab_type='results')
        my_app.notebook.add(self.res_tab,text='Resultater')


        my_app.notebook.grid(row=0)


        
        # Combobox med alle løpene i databasen
        tk.Label(self.adm_tab.top_frame, text="Løp:").grid(row=0, column=1, sticky='w')
        # Combobox med alle løp i databasen
    #    #self.combo_races = TTK.Combobox(top_frame, width=30, values=list(zip(*self.db.races))[1])
        combo_races = TTK.Combobox(self.adm_tab.top_frame, width=30, values=['1','2'])
        combo_races.grid(row=0, column=2, sticky='w')
        combo_races.bind("<<ComboboxSelected>>",self.get_race) 

       # file-Meny 
        menubar = tk.Menu(my_app, bg = "white")
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open...", command=self.dummy_func)#,'Open file....')
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=my_app.quit)
        #my_app.notebook.tab(0).page_break
        try:
            my_app.config(menu=menubar)
        except AttributeError:
            print('Error')
        my_app.mainloop()   
        #gui()

    def dummy_func(self,event):
        print(event.widget.get())

# Henter løpene og lager knapper for hver eneste klasse i løpet.
    def get_race(self, event):
        # Henter ønsket løp fra Combobox
#        self.race = Race(db, event.widget.current())
#        global race_number
#        race_number = self.combo_races.current()
#        # Lager knapper for hver klasse
        try:
           if buttons:
                for button in buttons:
                    button.grid_remove()
        except:
            buttons = list()
        i = 0
        j = 0
        class_names = ['H10','H12', 'D10', 'D12']

        for class_name in class_names:
 
            #buttons.append(tk.Button(self.adm_tab.ctr_left, text=class_name, command=partial(self.write_result_list, class_name)))
            buttons.append(tk.Button(self.adm_tab.ctr_left, text=class_name, command=self.dummy_func).grid(row=i,column=j, padx = 10))
            
            #buttons[-1].grid(row=i, column=j, padx=10)
            #buttons[-1].columnconfigure(0,weight=1)

            i += 1
            if i >= 30:
                j = 1
                i = 1


 


def main():
    coach = Manager()

if __name__=="__main__":
    main()  # Create GUI


