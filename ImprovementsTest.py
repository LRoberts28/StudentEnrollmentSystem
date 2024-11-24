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
                self.student_dashboard(user[0])  # Pass student_id
            elif user_type == "Instructor":
                self.instructor_dashboard(user[0])  # Pass instructor_id
            else:
                self.admin_dashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials. Try again.")

    def student_dashboard(self, student_id):
        student_window = Toplevel(self.root)
        student_window.title("Student Dashboard")
        student_window.geometry("400x300")
        Label(student_window, text="Student Dashboard", font=("Arial", 16)).pack(pady=20)

        Button(student_window, text="View Courses", command=lambda: self.view_courses(student_window)).pack(pady=10)
        Button(student_window, text="Register for Course", command=lambda: self.register_course(student_window, student_id)).pack(pady=10)

    def instructor_dashboard(self, instructor_id):
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

    def manage_courses(self):
        manage_window = Toplevel(self.root)
        manage_window.title("Manage Courses")
        manage_window.geometry("400x300")

        Label(manage_window, text="Manage Courses", font=("Arial", 16)).pack(pady=10)

        Button(manage_window, text="Add Course", command=self.add_course).pack(pady=10)
        Button(manage_window, text="Update Course", command=self.update_course).pack(pady=10)
        Button(manage_window, text="Delete Course", command=self.delete_course).pack(pady=10)

    def add_course(self):
        course_window = Toplevel(self.root)
        course_window.title("Add Course")
        course_window.geometry("400x300")

        Label(course_window, text="Course Name:").pack(pady=5)
        course_name_entry = Entry(course_window)
        course_name_entry.pack(pady=5)

        Label(course_window, text="Department:").pack(pady=5)
        department_entry = Entry(course_window)
        department_entry.pack(pady=5)

        Label(course_window, text="Instructor ID:").pack(pady=5)
        instructor_id_entry = Entry(course_window)
        instructor_id_entry.pack(pady=5)

        Button(course_window, text="Add Course", 
               command=lambda: self.insert_course(course_name_entry.get(), department_entry.get(), instructor_id_entry.get(), course_window)).pack(pady=10)

    def insert_course(self, course_name, department, instructor_id, window):
        conn = sqlite3.connect("university.db")
        c = conn.cursor()

        try:
            c.execute("INSERT INTO courses (course_name, department, instructor_id) VALUES (?, ?, ?)", 
                      (course_name, department, instructor_id))
            conn.commit()
            messagebox.showinfo("Success", "Course added successfully!")
            window.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error: {e}")
        finally:
            conn.close()

    def update_course(self):
        update_window = Toplevel(self.root)
        update_window.title("Update Course")
        update_window.geometry("400x300")

        Label(update_window, text="Select Course to Update").pack(pady=10)

        conn = sqlite3.connect("university.db")
        c = conn.cursor()
        c.execute("SELECT * FROM courses")
        courses = c.fetchall()
        conn.close()

        course_var = StringVar(update_window)
        course_var.set(courses[0][0])  # Default to first course

        course_menu = OptionMenu(update_window, course_var, *[course[1] for course in courses])
        course_menu.pack(pady=10)

        Label(update_window, text="New Course Name:").pack(pady=5)
        new_course_name_entry = Entry(update_window)
        new_course_name_entry.pack(pady=5)

        Label(update_window, text="New Department:").pack(pady=5)
        new_department_entry = Entry(update_window)
        new_department_entry.pack(pady=5)

        Label(update_window, text="New Instructor ID:").pack(pady=5)
        new_instructor_id_entry = Entry(update_window)
        new_instructor_id_entry.pack(pady=5)

        Button(update_window, text="Update Course", 
               command=lambda: self.apply_course_update(course_var.get(), new_course_name_entry.get(), new_department_entry.get(), new_instructor_id_entry.get(), update_window)).pack(pady=10)

    def apply_course_update(self, course_name, new_course_name, new_department, new_instructor_id, window):
        conn = sqlite3.connect("university.db")
        c = conn.cursor()

        c.execute("UPDATE courses SET course_name = ?, department = ?, instructor_id = ? WHERE course_name = ?", 
                  (new_course_name, new_department, new_instructor_id, course_name))
        conn.commit()
        messagebox.showinfo("Success", "Course updated successfully!")
        window.destroy()
        conn.close()

    def delete_course(self):
        delete_window = Toplevel(self.root)
        delete_window.title("Delete Course")
        delete_window.geometry("400x300")

        Label(delete_window, text="Select Course to Delete").pack(pady=10)

        conn = sqlite3.connect("university.db")
        c = conn.cursor()
        c.execute("SELECT * FROM courses")
        courses = c.fetchall()
        conn.close()

        course_var = StringVar(delete_window)
        course_var.set(courses[0][0])  # Default to first course

        course_menu = OptionMenu(delete_window, course_var, *[course[1] for course in courses])
        course_menu.pack(pady=10)

        Button(delete_window, text="Delete Course", 
               command=lambda: self.apply_course_delete(course_var.get(), delete_window)).pack(pady=10)

    def apply_course_delete(self, course_name, window):
        conn = sqlite3.connect("university.db")
        c = conn.cursor()

        c.execute("DELETE FROM courses WHERE course_name = ?", (course_name,))
        conn.commit()
        messagebox.showinfo("Success", "Course deleted successfully!")
        window.destroy()
        conn.close()

    def manage_instructors(self):
        # You would implement similar CRUD operations for instructors here.
        pass

    def manage_departments(self):
        # You would implement similar CRUD operations for departments here.
        pass

root = Tk()
app = StudentEnrollmentApp(root)
root.mainloop()
