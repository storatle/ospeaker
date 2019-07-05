import tkinter as tk
from tkinter import ttk

window = tk.Tk()

#style = ttk.Style(root)
#style.configure('lefttab.TNotebook', tabposition='ws')
window.title('O-speaker')
window.geometry('{}x{}'.format(1700,1000))
notebook = ttk.Notebook(window)#, style='lefttab.TNotebook')
f1 = tk.Frame(notebook, bg='red', width=1700, height=1000)
f2 = tk.Frame(notebook, bg='blue', width=1700, height=1000)
f1.
notebook.add(f1, text='Forvarsel')
notebook.add(f2, text='Resultater')

notebook.pack()

window.mainloop()
