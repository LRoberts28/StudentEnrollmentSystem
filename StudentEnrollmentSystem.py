import sqlite3
import bcrypt
from tkinter import *
from tkinter import messagebox

def create_db():
    conn = sqlite3.connect('university.db')
    c = conn.cursor()
    
    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS students (
                    student_id INTEGER PRIMARY KEY,
                    first_name TEXT,
                    last_name TEXT,
                    email TEXT,
                    password TEXT
                  )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS courses (
                    course_id INTEGER PRIMARY KEY,
                    course_name TEXT,
                    department TEXT,
                    instructor_id INTEGER
                  )''')

    c.execute('''CREATE TABLE IF NOT EXISTS instructors (
                    instructor_id INTEGER PRIMARY KEY,
                    first_name TEXT,
                    last_name TEXT,
                    email TEXT,
                    password TEXT
                  )''')

    c.execute('''CREATE TABLE IF NOT EXISTS departments (
                    department_id INTEGER PRIMARY KEY,
                    department_name TEXT
                  )''')

    c.execute('''CREATE TABLE IF NOT EXISTS enrollments (
                    enrollment_id INTEGER PRIMARY KEY,
                    student_id INTEGER,
                    course_id INTEGER,
                    FOREIGN KEY(student_id) REFERENCES students(student_id),
                    FOREIGN KEY(course_id) REFERENCES courses(course_id)
                  )''')

    c.execute('''CREATE TABLE IF NOT EXISTS grades (
                    grade_id INTEGER PRIMARY KEY,
                    enrollment_id INTEGER,
                    grade TEXT,
                    FOREIGN KEY(enrollment_id) REFERENCES enrollments(enrollment_id)
                  )''')
    
    conn.commit()
    conn.close()

create_db()  # Call this function to create the database

class StudentEnrollmentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Enrollment System")
        self.root.geometry("600x400")

        Label(root, text="Welcome to the Student Enrollment System", font=("Arial", 18)).pack(pady=20)

        Button(root, text="Login as Student", command=self.student_login, width=20).pack(pady=10)
        Button(root, text="Login as Instructor", command=self.instructor_login, width=20).pack(pady=10)
        Button(root, text="Admin Login", command=self.admin_login, width=20).pack(pady=10)

    def student_login(self):
        self.login_screen("Student")

    def instructor_login(self):
        self.login_screen("Instructor")

    def admin_login(self):
        self.login_screen("Admin")

    def login_screen(self, user_type):
        login_window = Toplevel(self.root)
        login_window.title(f"{user_type} Login")
        login_window.geometry("300x200")

        Label(login_window, text="Email:").pack(pady=5)
        email_entry = Entry(login_window)
        email_entry.pack(pady=5)

        Label(login_window, text="Password:").pack(pady=5)
        password_entry = Entry(login_window, show="*")
        password_entry.pack(pady=5)

        Button(login_window, text="Login", command=lambda: self.authenticate(user_type, email_entry.get(), password_entry.get())).pack(pady=10)
        Button(login_window, text="Create Account", command=lambda: self.create_account_window(user_type), width=20).pack(pady=5)

    def authenticate(self, user_type, email, password):
        conn = sqlite3.connect("university.db")
        c = conn.cursor()

        if user_type == "Student":
            c.execute("SELECT * FROM students WHERE email = ?", (email,))
        elif user_type == "Instructor":
            c.execute("SELECT * FROM instructors WHERE email = ?", (email,))
        else:  # Admin
            c.execute("SELECT * FROM instructors WHERE email = ?", (email,))

        user = c.fetchone()
        conn.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[4].encode('utf-8')):  # user[4] is password column
            messagebox.showinfo("Login Success", f"Welcome, {user_type}!")
            if user_type == "Student":
                self.student_dashboard()
            elif user_type == "Instructor":
                self.instructor_dashboard()
            else:
                self.admin_dashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials. Try again.")

    def create_account_window(self, user_type):
        create_window = Toplevel(self.root)
        create_window.title(f"Create {user_type} Account")
        create_window.geometry("300x300")

        Label(create_window, text="First Name:").pack(pady=5)
        first_name_entry = Entry(create_window)
        first_name_entry.pack(pady=5)

        Label(create_window, text="Last Name:").pack(pady=5)
        last_name_entry = Entry(create_window)
        last_name_entry.pack(pady=5)

        Label(create_window, text="Email:").pack(pady=5)
        email_entry = Entry(create_window)
        email_entry.pack(pady=5)

        Label(create_window, text="Password:").pack(pady=5)
        password_entry = Entry(create_window, show="*")
        password_entry.pack(pady=5)

        Label(create_window, text="Confirm Password:").pack(pady=5)
        confirm_password_entry = Entry(create_window, show="*")
        confirm_password_entry.pack(pady=5)

        Button(create_window, text="Create Account", 
               command=lambda: self.create_account(user_type, first_name_entry.get(), last_name_entry.get(), 
                                                    email_entry.get(), password_entry.get(), confirm_password_entry.get(), create_window)).pack(pady=10)

    def create_account(self, user_type, first_name, last_name, email, password, confirm_password, window):
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        conn = sqlite3.connect("university.db")
        c = conn.cursor()

        try:
            if user_type == "Student":
                c.execute("INSERT INTO students (first_name, last_name, email, password) VALUES (?, ?, ?, ?)", 
                          (first_name, last_name, email, hashed_password))
            elif user_type == "Instructor":
                c.execute("INSERT INTO instructors (first_name, last_name, email, password) VALUES (?, ?, ?, ?)", 
                          (first_name, last_name, email, hashed_password))
            conn.commit()
            messagebox.showinfo("Account Created", f"{user_type} account created successfully!")
            window.destroy()  # Close the create account window
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error: {e}")
        finally:
            conn.close()

    def student_dashboard(self):
        student_window = Toplevel(self.root)
        student_window.title("Student Dashboard")
        student_window.geometry("400x300")
        Label(student_window, text="Student Dashboard", font=("Arial", 16)).pack(pady=20)

        Button(student_window, text="View Courses", command=self.view_courses).pack(pady=10)
        Button(student_window, text="Register for Course", command=self.register_course).pack(pady=10)

    def instructor_dashboard(self):
        instructor_window = Toplevel(self.root)
        instructor_window.title("Instructor Dashboard")
        instructor_window.geometry("400x300")
        Label(instructor_window, text="Instructor Dashboard", font=("Arial", 16)).pack(pady=20)

        Button(instructor_window, text="Manage Enrollments", command=self.view_enrollments).pack(pady=10)
        Button(instructor_window, text="Submit Grades", command=self.submit_grades).pack(pady=10)

    def admin_dashboard(self):
        admin_window = Toplevel(self.root)
        admin_window.title("Admin Dashboard")
        admin_window.geometry("400x300")
        Label(admin_window, text="Admin Dashboard", font=("Arial", 16)).pack(pady=20)

        Button(admin_window, text="Manage Courses", command=self.manage_courses).pack(pady=10)
        Button(admin_window, text="Manage Instructors", command=self.manage_instructors).pack(pady=10)
        Button(admin_window, text="Manage Departments", command=self.manage_departments).pack(pady=10)
    
    # (Other methods such as view_courses, register_course, etc. remain unchanged)
        
root = Tk()
app = StudentEnrollmentApp(root)
root.mainloop()
