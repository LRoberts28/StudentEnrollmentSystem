import sqlite3
import bcrypt
from tkinter import *
from tkinter import messagebox

conn = sqlite3.connect('university.db')
c = conn.cursor()

c.execute('''UPDATE instructors SET isAdmin = 1 WHERE email = "arhea2@murraystate.edu"''')

conn.commit()
conn.close()