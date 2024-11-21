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

