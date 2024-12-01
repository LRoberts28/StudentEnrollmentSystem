import sqlite3
from tkinter import *
from tkinter import messagebox
from argon2 import PasswordHasher

# Initialize Argon2 password hasher
ph = PasswordHasher()

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
    
    c.execute('''CREATE TABLE IF NOT EXISTS admin_users (
                    admin_id INTEGER PRIMARY KEY,
                    first_name TEXT,
                    last_name TEXT,
                    email TEXT UNIQUE,
                    password TEXT
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
            c.execute("SELECT * FROM admin_users WHERE email = ?", (email,))

        user = c.fetchone()
        conn.close()

        if user:
            try:
                # Verify password using Argon2
                ph.verify(user[4], password)  # user[4] is the password column
                messagebox.showinfo("Login Success", f"Welcome, {user_type}!")
                if user_type == "Student":
                    self.student_dashboard()
                elif user_type == "Instructor":
                    self.instructor_dashboard()
                else:
                    self.admin_dashboard()
            except Exception:
                messagebox.showerror("Login Failed", "Invalid credentials. Try again.")
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

        # Hash password with Argon2
        hashed_password = ph.hash(password)

        conn = sqlite3.connect("university.db")
        c = conn.cursor()

        try:
            if user_type == "Student":
                c.execute("INSERT INTO students (first_name, last_name, email, password) VALUES (?, ?, ?, ?)", 
                        (first_name, last_name, email, hashed_password))
            elif user_type == "Instructor":
                c.execute("INSERT INTO instructors (first_name, last_name, email, password) VALUES (?, ?, ?, ?)", 
                        (first_name, last_name, email, hashed_password))
            elif user_type == "Admin":
                c.execute("INSERT INTO admin_users (first_name, last_name, email, password) VALUES (?, ?, ?, ?)",
                        (first_name, last_name, email, hashed_password))
            
            conn.commit()
            messagebox.showinfo("Account Created", f"{user_type} account created successfully!")
            window.destroy()  # Close the create account window
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Email already exists.")
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
        admin_window.geometry("500x400")
        
        Label(admin_window, text="Admin Dashboard", font=("Arial", 16)).pack(pady=20)
        
        Button(admin_window, text="Manage Courses", command=self.manage_courses).pack(pady=10)
        Button(admin_window, text="Manage Instructors", command=self.manage_instructors).pack(pady=10)
        Button(admin_window, text="Manage Departments", command=self.manage_departments).pack(pady=10)
        Button(admin_window, text="Logout", command=admin_window.destroy).pack(pady=10)

    def manage_courses(self):
        course_window = Toplevel(self.root)
        course_window.title("Manage Courses")
        course_window.geometry("400x300")
        
        Label(course_window, text="Manage Courses", font=("Arial", 14)).pack(pady=10)
        
        Button(course_window, text="Add Course", command=self.add_course).pack(pady=5)
        Button(course_window, text="Update Course", command=self.update_course).pack(pady=5)
        Button(course_window, text="Delete Course", command=self.delete_course).pack(pady=5)

    def manage_instructors(self):
        instructor_window = Toplevel(self.root)
        instructor_window.title("Manage Instructors")
        instructor_window.geometry("400x300")
        
        Label(instructor_window, text="Manage Instructors", font=("Arial", 14)).pack(pady=10)
        
        Button(instructor_window, text="Add Instructor", command=self.add_instructor).pack(pady=5)
        Button(instructor_window, text="Update Instructor", command=self.update_instructor).pack(pady=5)
        Button(instructor_window, text="Delete Instructor", command=self.delete_instructor).pack(pady=5)

    def manage_departments(self):
        department_window = Toplevel(self.root)
        department_window.title("Manage Departments")
        department_window.geometry("400x300")
        
        Label(department_window, text="Manage Departments", font=("Arial", 14)).pack(pady=10)
        
        Button(department_window, text="Add Department", command=self.add_department).pack(pady=5)
        Button(department_window, text="Update Department", command=self.update_department).pack(pady=5)
        Button(department_window, text="Delete Department", command=self.delete_department).pack(pady=5)

    def add_course(self):
        add_window = Toplevel(self.root)
        add_window.title("Add Course")
        add_window.geometry("300x200")
        
        Label(add_window, text="Course Name:").pack(pady=5)
        course_name_entry = Entry(add_window)
        course_name_entry.pack(pady=5)
        
        Label(add_window, text="Department:").pack(pady=5)
        department_entry = Entry(add_window)
        department_entry.pack(pady=5)
        
        Label(add_window, text="Instructor ID:").pack(pady=5)
        instructor_entry = Entry(add_window)
        instructor_entry.pack(pady=5)
        
        Button(add_window, text="Submit", command=lambda: self.save_course(
            course_name_entry.get(), department_entry.get(), instructor_entry.get(), add_window)).pack(pady=10)

    def save_course(self, course_name, department, instructor_id, window):
        if not course_name or not department or not instructor_id:
            messagebox.showerror("Error", "All fields are required.")
            return
        
        try:
            conn = sqlite3.connect("university.db")
            c = conn.cursor()
            c.execute("INSERT INTO courses (course_name, department, instructor_id) VALUES (?, ?, ?)",
                    (course_name, department, int(instructor_id)))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Course added successfully!")
            window.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")

    def update_course(self):
        update_window = Toplevel(self.root)
        update_window.title("Update Course")
        update_window.geometry("300x250")
        
        Label(update_window, text="Course ID:").pack(pady=5)
        course_id_entry = Entry(update_window)
        course_id_entry.pack(pady=5)
        
        Label(update_window, text="New Course Name:").pack(pady=5)
        course_name_entry = Entry(update_window)
        course_name_entry.pack(pady=5)
        
        Label(update_window, text="New Department:").pack(pady=5)
        department_entry = Entry(update_window)
        department_entry.pack(pady=5)
        
        Label(update_window, text="New Instructor ID:").pack(pady=5)
        instructor_entry = Entry(update_window)
        instructor_entry.pack(pady=5)
        
        Button(update_window, text="Update", command=lambda: self.save_updated_course(
            course_id_entry.get(), course_name_entry.get(), department_entry.get(), instructor_entry.get(), update_window)).pack(pady=10)

    def save_updated_course(self, course_id, course_name, department, instructor_id, window):
        if not course_id or not course_name or not department or not instructor_id:
            messagebox.showerror("Error", "All fields are required.")
            return
        
        try:
            conn = sqlite3.connect("university.db")
            c = conn.cursor()
            c.execute("UPDATE courses SET course_name = ?, department = ?, instructor_id = ? WHERE course_id = ?",
                    (course_name, department, int(instructor_id), int(course_id)))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Course updated successfully!")
            window.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")

    def delete_course(self):
        delete_window = Toplevel(self.root)
        delete_window.title("Delete Course")
        delete_window.geometry("300x150")
        
        Label(delete_window, text="Course ID to delete:").pack(pady=5)
        course_id_entry = Entry(delete_window)
        course_id_entry.pack(pady=5)
        
        Button(delete_window, text="Delete", command=lambda: self.remove_course(course_id_entry.get(), delete_window)).pack(pady=10)

    def remove_course(self, course_id, window):
        if not course_id:
            messagebox.showerror("Error", "Course ID is required.")
            return
        
        try:
            conn = sqlite3.connect("university.db")
            c = conn.cursor()
            c.execute("DELETE FROM courses WHERE course_id = ?", (int(course_id),))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Course deleted successfully!")
            window.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")

    def add_instructor(self):
        add_window = Toplevel(self.root)
        add_window.title("Add Instructor")
        add_window.geometry("300x200")
        
        Label(add_window, text="First Name:").pack(pady=5)
        first_name_entry = Entry(add_window)
        first_name_entry.pack(pady=5)
        
        Label(add_window, text="Last Name:").pack(pady=5)
        last_name_entry = Entry(add_window)
        last_name_entry.pack(pady=5)
        
        Label(add_window, text="Email:").pack(pady=5)
        email_entry = Entry(add_window)
        email_entry.pack(pady=5)
        
        Label(add_window, text="Password:").pack(pady=5)
        password_entry = Entry(add_window, show="*")
        password_entry.pack(pady=5)
        
        Button(add_window, text="Submit", command=lambda: self.save_instructor(
            first_name_entry.get(), last_name_entry.get(), email_entry.get(), password_entry.get(), add_window)).pack(pady=10)

    def save_instructor(self, first_name, last_name, email, password, window):
        if not first_name or not last_name or not email or not password:
            messagebox.showerror("Error", "All fields are required.")
            return
        
        try:
            # Hash the password before storing
            hashed_password = ph.hash(password)
            
            conn = sqlite3.connect("university.db")
            c = conn.cursor()
            c.execute("INSERT INTO instructors (first_name, last_name, email, password) VALUES (?, ?, ?, ?)",
                    (first_name, last_name, email, hashed_password))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Instructor added successfully!")
            window.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")



        
root = Tk()
app = StudentEnrollmentApp(root)
root.mainloop()

import sqlite3
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
                    email TEXT
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
                    email TEXT
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

    def authenticate(self, user_type, email, password):
        conn = sqlite3.connect("university.db")
        c = conn.cursor()

        if user_type == "Student":
            c.execute("SELECT * FROM students WHERE email = ? AND password = ?", (email, password))
        elif user_type == "Instructor":
            c.execute("SELECT * FROM instructors WHERE email = ? AND password = ?", (email, password))
        else:  # Admin
            c.execute("SELECT * FROM instructors WHERE email = ? AND password = ?", (email, password))

        user = c.fetchone()
        conn.close()

        if user:
            messagebox.showinfo("Login Success", f"Welcome, {user_type}!")
            if user_type == "Student":
                self.student_dashboard()
            elif user_type == "Instructor":
                self.instructor_dashboard()
            else:
                self.admin_dashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials. Try again.")

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
        
    def view_courses(self):
        conn = sqlite3.connect("university.db")
        c = conn.cursor()
        c.execute("SELECT course_id, course_name FROM courses")
        courses = c.fetchall()
        conn.close()
    
        course_window = Toplevel(self.root)
        course_window.title("Available Courses")
        course_window.geometry("300x300")
    
        Label(course_window, text="Available Courses", font=("Arial", 14)).pack(pady=10)
        for course in courses:
            Label(course_window, text=f"{course[0]}: {course[1]}").pack(pady=5)
            
    def register_course(self):
        register_window = Toplevel(self.root)
        register_window.title("Register for a Course")
        register_window.geometry("300x200")
    
        Label(register_window, text="Course ID:").grid(row=0, column=0, padx=10, pady=10)
        course_id_entry = Entry(register_window)
        course_id_entry.grid(row=0, column=1, padx=10, pady=10)
    
        Button(
            register_window, 
            text="Register", 
            command=lambda: self.save_registration(course_id_entry.get(), register_window)
        ).grid(row=1, column=0, columnspan=2, pady=10)

    def save_registration(self, course_id, window):
        conn = sqlite3.connect("university.db")
        c = conn.cursor()
        try:
            # Assuming a logged-in student with `student_id = 1`
            student_id = 1  # Replace with dynamic logic
            c.execute("INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)", (student_id, course_id))
            conn.commit()
            messagebox.showinfo("Success", "Successfully registered for the course.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error: {e}")
        finally:
            conn.close()
            window.destroy()
    
    def view_enrollments(self):
        enroll_window = Toplevel(self.root)
        enroll_window.title("Enrollments")
        enroll_window.geometry("400x300")
    
        conn = sqlite3.connect("university.db")
        c = conn.cursor()
    
        # Assuming a logged-in instructor with `instructor_id = 1`
        instructor_id = 1  # Replace with dynamic logic
        c.execute('''
            SELECT e.enrollment_id, s.first_name || ' ' || s.last_name AS student_name, c.course_name 
            FROM enrollments e
            JOIN students s ON e.student_id = s.student_id
            JOIN courses c ON e.course_id = c.course_id
            WHERE c.instructor_id = ?
        ''', (instructor_id,))
        enrollments = c.fetchall()
        conn.close()
    
        Label(enroll_window, text="Enrollments", font=("Arial", 14)).pack(pady=10)
        for enrollment in enrollments:
            Label(enroll_window, text=f"{enrollment[1]} - {enrollment[2]}").pack(pady=5)
    
    def submit_grades(self):
        grade_window = Toplevel(self.root)
        grade_window.title("Submit Grades")
        grade_window.geometry("300x300")
    
        Label(grade_window, text="Enrollment ID:").grid(row=0, column=0, padx=10, pady=10)
        enroll_id_entry = Entry(grade_window)
        enroll_id_entry.grid(row=0, column=1, padx=10, pady=10)
    
        Label(grade_window, text="Grade:").grid(row=1, column=0, padx=10, pady=10)
        grade_entry = Entry(grade_window)
        grade_entry.grid(row=1, column=1, padx=10, pady=10)
    
        Button(
            grade_window, 
            text="Submit", 
            command=lambda: self.save_grade(enroll_id_entry.get(), grade_entry.get(), grade_window)
        ).grid(row=2, column=0, columnspan=2, pady=10)

    def save_grade(self, enrollment_id, grade, window):
        conn = sqlite3.connect("university.db")
        c = conn.cursor()
        try:
            c.execute("INSERT INTO grades (enrollment_id, grade) VALUES (?, ?)", (enrollment_id, grade))
            conn.commit()
            messagebox.showinfo("Success", "Grade submitted successfully.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error: {e}")
        finally:
            conn.close()
            window.destroy()
            
    def manage_courses(self):
        manage_window = Toplevel(self.root)
        manage_window.title("Manage Courses")
        manage_window.geometry("400x300")
    
        Label(manage_window, text="Add Course", font=("Arial", 14)).pack(pady=10)
    
        Label(manage_window, text="Course Name:").pack()
        course_name_entry = Entry(manage_window)
        course_name_entry.pack(pady=5)
    
        Label(manage_window, text="Department ID:").pack()
        dept_id_entry = Entry(manage_window)
        dept_id_entry.pack(pady=5)
    
        Label(manage_window, text="Instructor ID:").pack()
        instructor_id_entry = Entry(manage_window)
        instructor_id_entry.pack(pady=5)
    
        Button(
            manage_window, 
            text="Add Course", 
            command=lambda: self.add_course(course_name_entry.get(), dept_id_entry.get(), instructor_id_entry.get(), manage_window)
        ).pack(pady=10)

    def add_course(self, course_name, department_id, instructor_id, window):
        conn = sqlite3.connect("university.db")
        c = conn.cursor()
        try:
            c.execute("INSERT INTO courses (course_name, department_id, instructor_id) VALUES (?, ?, ?)", 
                      (course_name, department_id, instructor_id))
            conn.commit()
            messagebox.showinfo("Success", "Course added successfully.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error: {e}")
        finally:
            conn.close()
            window.destroy()

root = Tk()
app = StudentEnrollmentApp(root)
root.mainloop()

