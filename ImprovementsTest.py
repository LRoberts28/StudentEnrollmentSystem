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
            except Exception as e:
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
            conn.commit()
            messagebox.showinfo("Account Created", f"{user_type} account created successfully!")
            window.destroy()  # Close the create account window
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error: {e}")
        finally:
            conn.close()
    
    #-------------------------------------------------------------------------------------------------

    #Student View
    def student_dashboard(self, student_id):
        student_window = Toplevel(self.root)
        student_window.title("Student Dashboard")
        student_window.geometry("400x300")
        Label(student_window, text="Student Dashboard", font=("Arial", 16)).pack(pady=20)

        Button(student_window, text="View Courses", command=lambda: view_all_courses()).pack(pady=10)
        Button(student_window, text="Register for Course", command=lambda: register_course()).pack(pady=10)

        #View Course
        def view_all_courses():
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

        # Register Course
        def register_course():
            # Create new window for registration
            register_window = Toplevel(self.root)
            register_window.title("Register for a Course")
            register_window.geometry("300x300")

            # Input field for course name
            Label(register_window, text="Course ID:").grid(row=0, column=0, padx=10, pady=10)
            course_name_entry = Entry(register_window)
            course_name_entry.grid(row=0, column=1, padx=10, pady=10)

            # Register button
            Button(
                register_window, 
                text="Register", 
                command=lambda: save_registration(course_name_entry.get(), register_window)
            ).grid(row=1, column=0, columnspan=2, pady=10)

            # Drop button
            Button(
                register_window, 
                text="Drop", 
                command=lambda: drop_course(course_name_entry.get(), register_window)
            ).grid(row=1, column=1, columnspan=2, pady=10)

            # Function to reload the course list after registration
            def reload_courses():
                try:
                    conn = sqlite3.connect("university.db")
                    c = conn.cursor()
                    c.execute('''
                            SELECT c.course_name, i.first_name || ' ' || i.last_name AS instructor_name
                            FROM courses c
                            JOIN enrollments e ON e.course_id = c.course_id
                            JOIN students s ON s.student_id = e.student_id
                            JOIN instructors i ON c.instructor_id = i.instructor_id
                            WHERE s.student_id = ?
                            ''', (student_id,))
                    courses = c.fetchall()
                    conn.close()
                except sqlite3.Error as e:
                    print("Error fetching data from the database:", e)
                    return []

                # Clear the current Listbox content and add new data
                listbox.delete(0, 'end')  # Clear the Listbox before updating
                for course in courses:
                    listbox.insert('end', f"{course[0]} - Instructor: {course[1]}")

            # Display the courses in a Listbox
            listbox = Listbox(register_window, width=40, height=10)
            listbox.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

            # Initial course list load
            reload_courses()

            # Function to check if the course is valid
            def is_valid_course(name):
                conn = sqlite3.connect("university.db")
                c = conn.cursor()
                c.execute("SELECT course_name FROM courses WHERE course_name = ?", (name,))
                isCourseValid = c.fetchone()
                conn.close()

                if(isCourseValid and not repeated(name)):
                    return "VALID"
                elif isCourseValid:
                    messagebox.showerror("Error", "Cannot Register for the same Course")
                    return "INVALID"
                else:
                    messagebox.showerror("Error", "Course not found")
                    return "INVALID"
            def repeated(name):
                conn = sqlite3.connect("university.db")
                c = conn.cursor()
                c.execute('''
                        SELECT c.course_id 
                        FROM courses c 
                        JOIN enrollments e ON e.course_id = c.course_id
                        JOIN students s on e.student_id = s.student_id
                        WHERE e.student_id = ? AND c.course_name = ?''', (student_id, name,))
                repeated = c.fetchone()
                conn.close()
                return repeated

            # Function to save registration
            def save_registration(course_name, window):
                conn = sqlite3.connect("university.db")
                c = conn.cursor()
                if(is_valid_course(course_name) == "VALID"):
                    c.execute("SELECT * FROM courses WHERE course_name = ?", (course_name,))
                    course = c.fetchone()
                    course_id = course[0]
                    try:
                        c.execute("INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)", (student_id, course_id))
                        c.execute("SELECT enrollment_id FROM enrollments WHERE student_id = ? AND course_id = ?", (student_id, course_id))
                        enrollment_id = c.fetchone()
                        c.execute("INSERT INTO grades (enrollment_id, grade) VALUES (?, ?)", (enrollment_id[0], 0))
                        conn.commit()
                        messagebox.showinfo("Success", "Successfully registered for the course.")
                        reload_courses()  # Reload the course list to show the newly added course
                        window.destroy()  # Close the registration window
                    except sqlite3.Error as e:
                        messagebox.showerror("Error", f"Error: {e}")
                    finally:
                        conn.close()
            def drop_course(course_name, window):
                conn = sqlite3.connect("university.db")
                c = conn.cursor()
                if(repeated(course_name)):
                    try:
                        c.execute('''
                                  DELETE FROM enrollments
                                  WHERE course_id = (SELECT course_id FROM courses WHERE course_name = ?)
                                  AND student_id = ?;''', (course_name, student_id,))
                        conn.commit()
                        messagebox.showinfo("Success", "Successfully dropped the course.")
                        reload_courses()  # Reload the course list to show the newly added course
                        window.destroy()  # Close the registration window
                    except sqlite3.Error as e:
                        messagebox.showerror("Error", f"Error: {e}")
                    finally:
                        conn.close()
                else:
                    messagebox.showerror("Error", "Cannot find class")

    #-------------------------------------------------------------------------------------------------

    #Instructor View
    def instructor_dashboard(self, instructor_id):
    # Function to create the instructor dashboard window
        def create_instructor_window():
            # Create a new window (recreates every time the function is called)
            instructor_window = Toplevel(self.root)
            instructor_window.title("Instructor Dashboard")
            instructor_window.geometry("400x600")
            Label(instructor_window, text="Instructor Dashboard", font=("Arial", 16)).pack(pady=20)

            # Connect to the database and fetch the enrollment data
            conn = sqlite3.connect("university.db")
            c = conn.cursor()

            c.execute('''SELECT c.course_name, s.first_name || ' ' || s.last_name AS student_name, g.grade, e.enrollment_id
                        FROM students s
                        JOIN enrollments e ON s.student_id = e.student_id
                        JOIN courses c ON e.course_id = c.course_id
                        JOIN grades g ON e.enrollment_id = g.enrollment_id
                        WHERE c.instructor_id = ?''', (instructor_id,))
            enrollments = c.fetchall()
            conn.close()

            # Create a Label for the title of the window
            Label(instructor_window, text="Enrollments", font=("Arial", 14)).pack(pady=10)

            # Create a Listbox to display enrollments
            listbox = Listbox(instructor_window, width=50, height=10, selectmode=SINGLE)
            listbox.pack(padx=10, pady=10)

            # Add a scrollbar for the listbox if the list is long
            scrollbar = Scrollbar(instructor_window, orient=VERTICAL, command=listbox.yview)
            scrollbar.pack(side=RIGHT, fill=Y)
            listbox.config(yscrollcommand=scrollbar.set)

            # Insert the enrollments into the Listbox
            for enrollment in enrollments:
                listbox.insert('end', f"{enrollment[0]} - {enrollment[1]} - {enrollment[2]}")

            # Create a Label and Entry widget to edit grades
            grade_label = Label(instructor_window, text="Grade:")
            grade_label.pack(pady=5)
            grade_entry = Entry(instructor_window, width=20)
            grade_entry.pack(pady=5)

            # Update grade function
            def update_grade():
                selected_index = listbox.curselection()
                if not selected_index:
                    return

                selected_enrollment = enrollments[selected_index[0]]
                enrollment_id = selected_enrollment[3]
                new_grade = grade_entry.get()

                # Update the grade in the database
                conn = sqlite3.connect("university.db")
                c = conn.cursor()
                c.execute('''UPDATE grades
                            SET grade = ?
                            WHERE enrollment_id = ?''', (new_grade, enrollment_id))
                conn.commit()
                conn.close()

                # Refresh the list of enrollments
                refresh_enrollments()

            # Refresh the listbox with updated enrollment data
            def refresh_enrollments():
                # Clear the listbox
                listbox.delete(0, 'end')

                # Re-fetch the updated enrollment data
                conn = sqlite3.connect("university.db")
                c = conn.cursor()
                c.execute('''SELECT c.course_name, s.first_name || ' ' || s.last_name AS student_name, g.grade, e.enrollment_id
                            FROM students s
                            JOIN enrollments e ON s.student_id = e.student_id
                            JOIN courses c ON e.course_id = c.course_id
                            JOIN grades g ON e.enrollment_id = g.enrollment_id
                            WHERE c.instructor_id = ?''', (instructor_id,))
                enrollments = c.fetchall()
                conn.close()

                # Insert updated enrollments into the Listbox
                for enrollment in enrollments:
                    listbox.insert('end', f"{enrollment[0]} - {enrollment[1]}")

            # Create a Submit button to submit the updated grade
            submit_button = Button(instructor_window, text="Submit Grade", command=update_grade)
            submit_button.pack(pady=10)

            # Allow deletion of a grade if needed
            def delete_grade():
                selected_index = listbox.curselection()
                if not selected_index:
                    return

                selected_enrollment = enrollments[selected_index[0]]
                enrollment_id = selected_enrollment[3]

                # Delete the grade from the database
                conn = sqlite3.connect("university.db")
                c = conn.cursor()
                c.execute('''DELETE FROM grades
                            WHERE enrollment_id = ?''', (enrollment_id,))
                conn.commit()
                conn.close()

                # Refresh the list of enrollments
                refresh_enrollments()

            # Create a Delete button to delete the grade
            delete_button = Button(instructor_window, text="Delete Grade", command=delete_grade)
            delete_button.pack(pady=5)

            # Create a Refresh button to close and reopen the instructor window
            def refresh_button_click():
                instructor_window.destroy()  # Close the current window
                create_instructor_window()  # Recreate the window to refresh content

            # Create a Refresh button
            refresh_button = Button(instructor_window, text="Refresh", command=refresh_button_click)
            refresh_button.pack(pady=10)

        # Initially create the instructor window
        create_instructor_window()

    #-------------------------------------------------------------------------------------------------

    #Admin View
    def admin_dashboard(self):
        admin_window = Toplevel(self.root)
        admin_window.title("Admin Dashboard")
        admin_window.geometry("400x300")
        Label(admin_window, text="Admin Dashboard", font=("Arial", 16)).pack(pady=20)

        Button(admin_window, text="Manage Courses", command=lambda: manage_courses()).pack(pady=10)
        Button(admin_window, text="Manage Instructors", command=lambda: manage_instructors()).pack(pady=10)
        Button(admin_window, text="Manage Departments", command=lambda: manage_departments()).pack(pady=10)

        #Manage Courses

        def manage_courses():
            manage_window = Toplevel(self.root)
            manage_window.title("Manage Courses")
            manage_window.geometry("400x300")
            conn = sqlite3.connect("university.db")
            c = conn.cursor()

            c.execute('''
                      SELECT c.course_name, c.department, i.first_name || ' ' || i.last_name AS instructor_name, i.instructor_id
                      FROM courses c
                      JOIN instructors i on c.instructor_id = i.instructor_id  
            ''')
            courses = c.fetchall()
            conn.close()

            Label(manage_window, text="Manage Courses", font=("Arial", 16)).pack(pady=10)

            Label(manage_window, text="Courses", font=("Arial", 14)).pack(pady=10)
            for course in courses:
                Label(manage_window, text=f"{course[1]} - {course[2]}").pack(pady=5)
            
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
                command=lambda: add_course(course_name_entry.get(), dept_id_entry.get(), instructor_id_entry.get(), manage_window)
            ).pack(pady=10)

            Button(manage_window, text="Update Course", command=lambda: update_course()).pack(pady=10)
            Button(manage_window, text="Delete Course", command=lambda: delete_course()).pack(pady=10)

        
            def add_course(course_name, department, instructor_id, window):
                conn = sqlite3.connect("university.db")
                c = conn.cursor()
                try:
                    c.execute("INSERT INTO courses (course_name, department, instructor_id) VALUES (?, ?, ?)", 
                            (course_name, department, instructor_id))
                    conn.commit()
                    messagebox.showinfo("Success", "Course added successfully.")
                except sqlite3.Error as e:
                    messagebox.showerror("Error", f"Error: {e}")
                finally:
                    conn.close()
                    window.destroy()
        
            #Update Course
            def update_course():
                pass

            #Delete Course
            def delete_course():
                pass

        

        #Manage Instructors
        def manage_instructors():
            # You would implement similar CRUD operations for instructors here.
            pass


        #Manage Departments
        def manage_departments():
            # You would implement similar CRUD operations for departments here.
            pass

    #-------------------------------------------------------------------------------------------------

root = Tk()
app = StudentEnrollmentApp(root)
root.mainloop()
