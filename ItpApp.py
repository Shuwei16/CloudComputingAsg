# rmb to change after

from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymysql import connections
import os
import boto3
from config import *

import secrets




app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
# output = {}
# table = 'employee'


# Main
@app.route("/")
def index():
    return render_template('index.html')

# Student
@app.route("/student/login", methods=['GET', 'POST'])
def studentLogin():
    error_message = None  # Define error_message with a default value
    
    if request.method == 'POST':
        email = request.form['email']
        nric = request.form['nric']
        
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM student WHERE studEmail = %s AND studIC = %s;", (email, nric))
        user = cursor.fetchone()
        cursor.close()
        
        if user:
            session['studID'] = user[0]
            return render_template('student/home.html', session=user[0])
        else:
            error_message = 'Login failed. Please check your email and nric.'
    
    return render_template('student/login.html', error_message=error_message)

@app.route("/student/register", methods=['GET', 'POST'])
def studentRegister():
    if request.method == 'POST':
        # Retrieve registration data from the form
        name = request.form['name']
        nric = request.form['nric']
        gender = request.form['gender']
        studentID = request.form['studentID']
        email = request.form['email']
        contactNo = request.form['contactNo']
        programme = request.form['programme']
        cohort = request.form['cohort']
        lecturerName = request.form['lecturerName']
        cgpa = request.form['cgpa']
        resume = request.form['resume']
        
        # Search for lecturer email
        cursor = db_conn.cursor()
        cursor.execute("SELECT email FROM lecturers WHERE name = %s", (lecturerName))
        lecturerEmail = cursor.fetchone()
        cursor.close()

        # Insert the new user into the database (Assuming you have a 'students' table)
        cursor = db_conn.cursor()
        cursor.execute("INSERT INTO students (studID, studEmail, studIC, gender, studName, course, studPhone, cgpa, lectEmail) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                       (studentID, email, nric, name, programme, contactNo, cgpa, lecturerEmail))
        db_conn.commit()
        cursor.close()
        
        return redirect(url_for('studentRegisterSuccess'))
    
    return render_template('student/register.html')

@app.route("/student/registerSuccess")
def studentRegisterSuccess():
    return render_template('student/registerSuccess.html')

@app.route("/student/home", methods=['GET', 'POST'])
def studentHome():
    print(session['studID'])
    if 'studID' in session:
        studID = session['studID']
        
        # Fetch the user's information from the database based on studID
        cursor = db_conn.cursor()
        cursor.execute("""
                       SELECT students.*, cohorts.startDate AS startDate, cohorts.endDate AS endDate, lecturers.name AS lectName
                       FROM students
                       JOIN cohorts ON students.cohortID = cohorts.cohortID
                       JOIN lecturers ON students.lectEmail = lecturers.email
                       WHERE studID = %s
                       """, (studID))
        user = cursor.fetchone()
        cursor.close()
        
        if user:
            # Pass the user's information to the template
            return render_template('student/home.html', user=session,)
    
    return render_template('student/home.html')
def editStudentInfo():
    if request.method == 'POST':
        contactNo = request.form['contactNo']
        cgpa = request.form['cgpa']

@app.route("/student/companyList")
def studentCompanyList():
    return render_template('student/companyList.html')

@app.route("/student/companyDetail")
def studentCompanyDetail():
    return render_template('student/companyDetail.html')

@app.route("/student/applicationHistory")
def studentApplicationHistory():
    return render_template('student/applicationHistory.html')

# Lecturer
@app.route("/lecturer/login", methods=['GET', 'POST'])
def lecturerLogin():
    error_message = None  # Define error_message with a default value

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM lecturers WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()
        cursor.close()
        
        if user:
            session['user'] = user
            return render_template('lecturer/home.html')
        else:
            error_message = 'Login failed. Please check your email and password.'
    
    return render_template('lecturer/login.html', error_message=error_message)

@app.route("/lecturer/home")
def lecturerHome():
    return render_template('lecturer/home.html')

@app.route("/lecturer/studentDetail")
def lecturerDetail():
    return render_template('lecturer/studentDetail.html')

# Company
@app.route("/company/login", methods=['GET', 'POST'])
def companyLogin():
    error_message = None  # Define error_message with a default value
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM companies WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()
        cursor.close()
        
        if user:
            session['email'] = user['email']
            return render_template('company/home.html')
        else:
            error_message = 'Login failed. Please check your email and password.'
    
    return render_template('company/login.html', error_message=error_message)

@app.route("/company/register", methods=['GET', 'POST'])
def companyRegister():
    if request.method == 'POST':
        # Retrieve registration data from the form
        companyName = request.form['companyName']
        companyDescription = request.form['companyDescription']
        category = request.form['category']
        contactNo = request.form['contactNo']
        email = request.form['email']
        address = request.form['line1'] + ', ' + request.form['line2'] + ', ' + request.form['city'] + ', ' + request.form['postcode'] + ', ' + request.form['state'] + '.'
        companyLogo = request.form['companyLogo']
        password = request.form['password']

        # Insert the new user into the database (Assuming you have a 'students' table)
        cursor = db_conn.cursor()
        cursor.execute("INSERT INTO companies (compEmail, compPassword, compName, compDesc, category, compLocation, compPhone) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                       (email, password, companyName, companyDescription, category, address, contactNo))
        db_conn.commit()
        cursor.close()
        
        return redirect(url_for('studentRegisterSuccess'))
    
    return render_template('company/register.html')

@app.route("/company/registerSuccess")
def companyRegisterSuccess():
    return render_template('company/registerSuccess.html')

@app.route("/company/home")
def companyHome():
    return render_template('company/home.html')

@app.route("/company/studentApplication")
def companyStudentApplication():
    return render_template('company/studentApplication.html')

# Admin
@app.route("/admin/login", methods=['GET', 'POST'])
def adminLogin():
    error_message = None  # Define error_message with a default value
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()
        cursor.close()
        
        if user:
            session['email'] = user['email']
            return render_template('admin/home.html')
        else:
            error_message = 'Login failed. Please check your email and password.'
    
    return render_template('admin/login.html', error_message=error_message)

@app.route("/admin/home")
def adminHome():
    return render_template('admin/home.html')

@app.route("/admin/companyList")
def adminCompanyList():
    return render_template('admin/companyList.html')

@app.route("/admin/companyDetail")
def adminCompanyDetail():
    return render_template('admin/companyDetail.html')

@app.route("/admin/lecturerList")
def adminLecturerList():
    return render_template('admin/lecturerList.html')

# logout
@app.route("/logout")
def logout():
    # Clear the session to log out the user
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

# @app.route("/about", methods=['POST'])
# def about():
#     return render_template('www.tarc.edu.my')


# @app.route("/addemp", methods=['POST'])
# def AddEmp():
#     emp_id = request.form['emp_id']
#     first_name = request.form['first_name']
#     last_name = request.form['last_name']
#     pri_skill = request.form['pri_skill']
#     location = request.form['location']
#     emp_image_file = request.files['emp_image_file']

#     insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
#     cursor = db_conn.cursor()

#     if emp_image_file.filename == "":
#         return "Please select a file"

#     try:

#         cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
#         db_conn.commit()
#         emp_name = "" + first_name + " " + last_name
#         # Uplaod image file in S3 #
#         emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
#         s3 = boto3.resource('s3')

#         try:
#             print("Data inserted in MySQL RDS... uploading image to S3...")
#             s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
#             bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
#             s3_location = (bucket_location['LocationConstraint'])

#             if s3_location is None:
#                 s3_location = ''
#             else:
#                 s3_location = '-' + s3_location

#             object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
#                 s3_location,
#                 custombucket,
#                 emp_image_file_name_in_s3)

#         except Exception as e:
#             return str(e)

#     finally:
#         cursor.close()

#     print("all modification done...")
#     return render_template('AddEmpOutput.html', name=emp_name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

