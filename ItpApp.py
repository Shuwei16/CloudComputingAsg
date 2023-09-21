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
    if session:
        session.clear()
    return render_template('index.html')

# Student
@app.route("/student/login", methods=['GET', 'POST'])
def studentLogin():
    error_message = None  # Define error_message with a default value

    if request.method == 'POST':
        email = request.form['email']
        nric = request.form['nric']

        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM student WHERE studEmail = %s AND studIC = %s", (email, nric))
        user = cursor.fetchone()
        cursor.close()

        if user:
            # Access the 'studID' from the tuple using integer index
            studID = user[0]  # Assuming 'studID' is the first column in your SELECT statement
            # Store 'studID' in the session
            session['studID'] = studID
            return redirect(url_for('studentHome'))
        else:
            error_message = 'Login failed. Please check your email and nric.'
            return render_template('student/login.html', error_message=error_message)

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
        cursor.execute("SELECT lecEmail FROM lecturer WHERE lecName = %s", (lecturerName))
        lecturerEmail = cursor.fetchone()
        cursor.close()

        # Insert the new user into the database (Assuming you have a 'students' table)
        cursor = db_conn.cursor()
        cursor.execute("INSERT INTO student (studID, studEmail, studIC, gender, studName, course, studPhone, cgpa, lectEmail) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                       (studentID, email, nric, gender, name, programme, contactNo, cgpa, lecturerEmail))
        db_conn.commit()
        cursor.close()
        
        return redirect(url_for('studentRegisterSuccess'))
    
    cursor = db_conn.cursor()
    # Execute a SQL query to fetch data from the database
    cursor.execute("SELECT cohortID FROM cohort")
    cohort = cursor.fetchall()  # Fetch all rows
    cursor.close()
    
    cursor = db_conn.cursor()
    # Execute a SQL query to fetch data from the database
    cursor.execute("SELECT lecEmail, lecName FROM lecturer")
    lecturer = cursor.fetchall()  # Fetch all rows
    cursor.close()
    
    return render_template('student/register.html', cohort=cohort, lecturer=lecturer)

@app.route("/student/registerSuccess")
def studentRegisterSuccess():
    return render_template('student/registerSuccess.html')

@app.route("/student/home", methods=['GET', 'POST'])
def studentHome():
    if 'studID' in session:
        
        if request.method == 'POST':
            action = request.form.get('action')
            
            # Edit student info
            if action == 'editInfo':
                contactNo = request.form['contactNo']
                cgpa = request.form['cgpa']
                
                # Update data in student table
                cursor = db_conn.cursor()
                cursor.execute("""
                            UPDATE student
                            SET studPhone = %s, cgpa = %s
                            WHERE studID = %s
                            """, 
                            (contactNo, cgpa, session['studID']),)
                db_conn.commit()
                cursor.close()
            
            # Edit company info
            if action == 'editCompany':
                companyName = request.form['companyName']
                companyAddress = request.form['companyAddress']
                allowance = request.form['allowance']
                compSupervisorName = request.form['compSupervisorName']
                compSupervisorEmail = request.form['compSupervisorEmail']
                compSupervisorContact = request.form['compSupervisorContact']
                compAcceptanceForm = request.files['compAcceptanceForm']
                parrentAckForm = request.files['parrentAckForm']
                letterOfIndemnity = request.files['letterOfIndemnity']
                hiredEvidence = request.files['hiredEvidence']

                # Update data in student table
                cursor = db_conn.cursor()
                
                # Uplaod image file in S3
                compAcceptanceForm_in_s3 = "studID-" + str(session['studID']) + "_compAcceptanceForm"
                parrentAckForm_in_s3 = "studID-" + str(session['studID']) + "_parrentAckForm"
                letterOfIndemnity_in_s3 = "studID-" + str(session['studID']) + "_letterOfIndemnity"
                hiredEvidence_in_s3 = "studID-" + str(session['studID']) + "_hiredEvidence"
                s3 = boto3.resource('s3')
                
                cursor.execute("""
                            UPDATE student
                            SET compName = %s, compAddr = %s, monthlyAllowance = %s, compSupervisorName = %s, compSupervisorEmail = %s, compSupervisorPhone = %s
                            WHERE studID = %s
                            """, 
                            (companyName, companyAddress, allowance, compSupervisorName, compSupervisorEmail, compSupervisorContact, session['studID']),)
                db_conn.commit()
                
                try:
                    s3.Bucket(custombucket).put_object(Key=compAcceptanceForm_in_s3, Body=compAcceptanceForm)
                    s3.Bucket(custombucket).put_object(Key=parrentAckForm_in_s3, Body=parrentAckForm)
                    s3.Bucket(custombucket).put_object(Key=letterOfIndemnity_in_s3, Body=letterOfIndemnity)
                    s3.Bucket(custombucket).put_object(Key=hiredEvidence_in_s3, Body=hiredEvidence)
                    bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
                    s3_location = (bucket_location['LocationConstraint'])

                    if s3_location is None:
                        s3_location = ''
                    else:
                        s3_location = '-' + s3_location
                    
                except Exception as e:
                    return str(e)

                cursor.close()
        
        # Fetch the user's information from the database based on studID
        cursor = db_conn.cursor()
        
        cursor.execute("""
                    SELECT student.*, lecturer.lecName, cohort.internStartDate, cohort.internEndDate
                    FROM student 
                    JOIN lecturer ON student.lectEmail = lecturer.lecEmail
                    JOIN cohort ON student.cohort = cohort.cohortID
                    WHERE studID = %s
                    """, (session['studID']),)
        user_data = cursor.fetchone()
        cursor.close()
        
        if user_data:
            # Convert the user record to a dictionary
            user = {
                'studID': user_data[0],
                'studEmail': user_data[1],
                'studIC': user_data[2],
                'gender': user_data[3],
                'studName': user_data[4],
                'course': user_data[5],
                'studPhone': user_data[6],
                'cgpa': user_data[7],
                'lecEmail': user_data[8],
                'cohort': user_data[9],
                'compName': user_data[10],
                'compAddr': user_data[11],
                'monthlyAllowance': user_data[12],
                'compSupervisorName': user_data[13],
                'compSupervisorEmail': user_data[14],
                'compSupervisorPhone': user_data[15],
                'lecName': user_data[16],
                'internStartDate': user_data[17],
                'internEndDate': user_data[18],
                # Add other fields as needed
            }
            
            # Get the s3 bucket location
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])
            
            # Initialize files url 
            compAcceptanceForm_url = None
            parrentAckForm_url = None
            letterOfIndemnity_url = None
            hiredEvidence_url = None
            
            # Retrieve files from s3 bucket
            compAcceptanceForm_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                compAcceptanceForm_in_s3)
            
            parrentAckForm_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                parrentAckForm_in_s3)
            
            letterOfIndemnity_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                letterOfIndemnity_in_s3)
            
            hiredEvidence_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                hiredEvidence_in_s3)
            
            # Pass the user's information to the template
            return render_template('student/home.html', user=user, 
                                   compAcceptanceForm_url=compAcceptanceForm_url,
                                   parrentAckForm_url=parrentAckForm_url,
                                   letterOfIndemnity_url=letterOfIndemnity_url,
                                   hiredEvidence_url=hiredEvidence_url)
    
    return render_template('student/home.html')

@app.route("/student/companyList")
def studentCompanyList():
    
    cursor = db_conn.cursor()
    # Execute a SQL query to fetch data from the database
    cursor.execute("SELECT compName, category FROM company")
    companies_data = cursor.fetchall()  # Fetch all rows
    cursor.close()
    
    # Initialize an empty list to store dictionaries
    companies = []

    # Iterate through the fetched data and create dictionaries
    for row in companies_data:
        company_dict = {
            'compName': row[0],
            'category': row[1],
            # Add other fields as needed
        }
        companies.append(company_dict)
    
    return render_template('student/companyList.html', companies=companies)

@app.route("/student/companyDetail")
def studentCompanyDetail():
    # Retrieve the company query parameter from the URL
    companyName = request.args.get('company')
    
    # Fetch the user's information from the database based on studID
    cursor = db_conn.cursor()
        
    cursor.execute("""
                SELECT *
                FROM company 
                WHERE compName = %s
                """, (companyName),)
    company_data = cursor.fetchone()
    cursor.close()
    
    if company_data:
        # Convert the user record to a dictionary
        company = {
            'compEmail': company_data[0],
            'compName': company_data[2],
            'compDesc': company_data[3],
            'category': company_data[4],
            'compLocation': company_data[5],
            'workingStartDay': company_data[6],
            'workingEndDay': company_data[7],
            'workingStartTime': company_data[8],
            'workingEndTime': company_data[9],
            'compPhone': company_data[10],
            'accessories': company_data[11],
            'accomodation': company_data[12],
            # Add other fields as needed
        }
    
    # Pass the company's information to the template
    return render_template('student/companyDetail.html', company=company)

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
        cursor.execute("SELECT * FROM lecturer WHERE lecEmail = %s AND lecPassword = %s", (email, password))
        user = cursor.fetchone()
        cursor.close()
        
        if user:
            # Access the 'lecEmail' from the tuple using integer index
            lecEmail = user[0]  # Assuming 'lecEmail' is the first column in your SELECT statement
            # Store 'lecEmail' in the session
            session['lecEmail'] = lecEmail
            return redirect(url_for('lecturerHome'))
        else:
            error_message = 'Login failed. Please check your email and password.'
            return render_template('lecturer/login.html', error_message=error_message)
    
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
        cursor.execute("SELECT * FROM company WHERE compEmail = %s AND compPassword = %s", (email, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
             # Access the 'compEmail' from the tuple using integer index
            compEmail = user[0]  # Assuming 'compEmail' is the first column in your SELECT statement
            # Store 'studID' in the session
            session['compEmail'] = compEmail
            return redirect(url_for('companyHome'))
        else:
            error_message = 'Login failed. Please check your email and password.'
            return render_template('company/login.html', error_message=error_message)

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
        cursor.execute("INSERT INTO company (compEmail, compPassword, compName, compDesc, category, compLocation, compPhone) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                       (email, password, companyName, companyDescription, category, address, contactNo))
        db_conn.commit()
        cursor.close()
        
        return redirect(url_for('companyRegisterSuccess'))
    
    return render_template('company/register.html')

@app.route("/company/registerSuccess")
def companyRegisterSuccess():
    return render_template('company/registerSuccess.html')

@app.route("/company/home", methods=['GET', 'POST'])
def companyHome():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'addJob':
            jobTitle = request.form['jobTitle']
            minimum = request.form['minimum']
            maximum = request.form['maximum']
            open_for = request.form.getlist('open_for')
            jobDescription = request.form['jobDescription']
            jobRequirement = request.form['jobRequirement']
            compEmail = session['compEmail']

            allowance = f"{minimum} - {maximum}"

            # Automatically generate a new job ID by incrementing the maximum job ID
            cursor = db_conn.cursor()
            cursor.execute("SELECT MAX(jobID) FROM jobs")
            max_id = cursor.fetchone()[0]  # Get the maximum job ID

            if max_id is not None:
                # Extract the numeric part and increment it
                numeric_part = int(max_id[1:])  # Convert 'J001' to 1
                new_numeric_part = numeric_part + 1
    
                # Format the new jobID with the same pattern ('J' + 3-digit numeric part)
                new_job_id = 'J{:03d}'.format(new_numeric_part)
            else:
                # If there are no jobs, start with 'J001'
                new_job_id = 'J001'
            

            cursor = db_conn.cursor()
            cursor.execute("INSERT INTO jobs (jobID, jobTitle, allowance, level, jobDesc, jobReq, compEmail) VALUES (%s, %s, %s, %s, %s, %s, %s)", (new_job_id, jobTitle, allowance, ','.join(open_for), jobDescription, jobRequirement, compEmail))
            db_conn.commit()
            cursor.close()
        
        elif action == 'editJob':
    
            job_id = request.form['job_id']  # Get the job ID from the form
            jobTitle = request.form['jobTitle']
            minimum = request.form['minimum']
            maximum = request.form['maximum']
            open_for = request.form.getlist('open_for')
            jobDescription = request.form['jobDescription']
            jobRequirement = request.form['jobRequirement']

            allowance = f"{minimum} - {maximum}"

            print(f"Received data: job_id={job_id}, jobTitle={jobTitle}, allowance={allowance}, open_for={open_for}, jobDescription={jobDescription}, jobRequirement={jobRequirement}")

            cursor = db_conn.cursor()
            cursor.execute("UPDATE jobs SET jobTitle = %s, allowance = %s, level = %s, jobDesc = %s, jobReq = %s WHERE jobID = %s", (jobTitle, allowance, ','.join(open_for), jobDescription, jobRequirement, job_id))
            db_conn.commit()
            cursor.close()

            print("Data updated successfully")
            # return render_template('company/home.html', job=job, minimum=minimum, maximum=maximum)

        elif action == 'editInfo':
            
            compEmail = request.form['companyEmail']
            compName = request.form['companyName']
            compDesc = request.form['companyDescription']
            compLocation = request.form['companyLocation']
            workingStartDay = request.form['workingStartDay']
            workingEndDay = request.form['workingEndDay']
            workingStartTime = request.form['workingStartTime']
            workingEndTime = request.form['workingEndTime']
            compPhone = request.form['compPhone']
            accessories = request.form['accessories']
            accomodation = request.form['accomodation']

            # print(f"Received data: job_id={job_id}, jobTitle={jobTitle}, allowance={allowance}, open_for={open_for}, jobDescription={jobDescription}, jobRequirement={jobRequirement}")

            cursor = db_conn.cursor()
            cursor.execute("UPDATE company SET compName = %s, compDesc = %s, compLocation = %s, workingStartDay = %s, workingEndDay = %s, workingStartTime = %s, workingEndTime = %s, compPhone = %s, accessories = %s, accomodation = %s WHERE compEmail = %s", (compName, compDesc, compLocation, workingStartDay, workingEndDay, workingStartTime, workingEndTime, compPhone, accessories, accomodation, compEmail))
            db_conn.commit()
            cursor.close()

            # print("Data updated successfully")
        

        elif action == 'delete':
            # Handle the DELETE request (e.g., delete a job)
            # Extract the job ID from the request data
            job_id = request.form['job_id']
            print(f"Received job_id for deletion: {job_id}")
            cursor = db_conn.cursor()
            cursor.execute("DELETE FROM jobs WHERE jobID = %s", (job_id,))
            db_conn.commit()
            cursor.close()
            print("Record deleted successfully")
        
    cursor = db_conn.cursor()
    # cursor.execute('SELECT * FROM jobs')
    # jobs = cursor.fetchall()
    # cursor.execute('SELECT * FROM company')
    # companies = cursor.fetchall()
    cursor.execute("""
                SELECT company.*
                FROM company 
                JOIN jobs ON company.compEmail = jobs.compEmail
                WHERE company.compEmail = %s
                """, (session['compEmail']),)
    company_data = cursor.fetchone()
        

    if company_data:
        # Convert the user record to a dictionary
        company = {
            'compEmail': company_data[0],
            'compPassword': company_data[1],
            'compName': company_data[2],
            'compDesc': company_data[3],
            'category': company_data[4],
            'compLocation': company_data[5],
            'workingStartDay': company_data[6],
            'workingEndDay': company_data[7],
            'workingStartTime': company_data[8],
            'workingEndTime': company_data[9],
            'compPhone': company_data[10],
            'accessories': company_data[11],
            'accomodation': company_data[12],
            # Add other fields as needed
        }
    
    cursor.execute("""
            SELECT *
            FROM jobs 
            WHERE compEmail = %s
            """, (session['compEmail']),)
    job_data = cursor.fetchall()
    cursor.close()
    
    # Initialize an empty list to store job dictionaries
    jobs = []
    minimums = []  # Initialize an empty list for minimums
    maximums = []  # Initialize an empty list for maximums
    for row in job_data:
    # Convert each row to a dictionary
        job = {
            'jobID': row[0],
            'jobTitle': row[1],
            'allowance': row[2],  # Access the 'allowance' column
            'level': row[3],
            'jobDesc': row[4],
            'jobReq': row[5],
            'compEmail': row[6],
            # Add other fields as needed
        }    
        # Append the job dictionary to the list of jobs
        jobs.append(job)

        allowance = job['allowance']
        min_allowance, max_allowance = map(float, allowance.split(' - '))

    # Append a dictionary containing jobID and minimum allowance to the minimums list
        minimums.append({'jobID': job['jobID'], 'min_allowance': min_allowance})
        maximums.append({'jobID': job['jobID'], 'max_allowance': max_allowance})
        
    return render_template('company/home.html', company=company, jobs=jobs, minimums=minimums, maximums=maximums)

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
        cursor.execute("SELECT * FROM admin WHERE adminEmail = %s AND adminPassword = %s", (email, password))
        user = cursor.fetchone()
        cursor.close()
        
        if user:
            # Access the 'adminEmail' from the tuple using integer index
            adminEmail = user[0]  # Assuming 'adminEmail' is the first column in your SELECT statement
            # Store 'adminEmail' in the session
            session['adminEmail'] = adminEmail
            return redirect(url_for('adminHome'))
        else:
            error_message = 'Login failed. Please check your email and password.'
            return render_template('admin/login.html', error_message=error_message)
    
    return render_template('admin/login.html', error_message=error_message)

@app.route("/admin/home")
def adminHome():
    return render_template('admin/home.html')

@app.route("/admin/companyList")
def adminCompanyList():
    

    cursor = db_conn.cursor()
    cursor.execute("""
            SELECT company.status, company.category, company.compName
                    FROM company""")

    company_data = cursor.fetchall()
    cursor.close()
    
    # Initialize an empty list to store job dictionaries
    companies = []
    for row in company_data:
    # Convert each row to a dictionary
        company = {
            'status': row[0],
            'category': row[1],
            'compName': row[2],
    #         # Add other fields as needed
         }    
    #     # Append the job dictionary to the list of jobs
        companies.append(company)
    
        print("Companies:", companies)

    return render_template('admin/companyList.html', companies=companies)

@app.route("/admin/companyDetail", methods=['GET', 'POST'])
def adminCompanyDetail():

    company = {}  # Initialize with an empty dictionary as a default value

    if request.method == 'POST':
        action = request.form.get('action') 

        if action == 'approve':

            comp_name = request.form['comp_name']  # Get the job ID from the form
            print(comp_name)
            cursor = db_conn.cursor()
            cursor.execute("UPDATE company SET status = 'Approved' WHERE compName = %s", (comp_name))
            db_conn.commit()
            cursor.close()

            print("Data updated successfully")

            return redirect(url_for('adminCompanyList'))
        
        elif action == 'reject':

            comp_name = request.form['comp_name']  # Get the job ID from the form
            print(comp_name)
            cursor = db_conn.cursor()
            cursor.execute("UPDATE company SET status = 'Rejected' WHERE compName = %s", (comp_name))
            db_conn.commit()
            cursor.close()

            print("Data updated successfully")

            return redirect(url_for('adminCompanyList'))

    companyName = request.args.get('comp_name')

    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM company WHERE compName = %s", (companyName,))
    company_data = cursor.fetchone()
    print("Companies:", company_data)
    cursor.close()

    if company_data:
        # Convert the retrieved data to a dictionary or other suitable format
        company = {
            'compEmail': company_data[0],
            'compName': company_data[2],
            'compDesc': company_data[3],
            'category': company_data[4],
            'compLocation': company_data[5],
            'workingStartDay': company_data[6],
            'workingEndDay': company_data[7],
            'workingStartTime': company_data[8],
            'workingEndTime': company_data[9],
            'compPhone': company_data[10],
            'accessories': company_data[11],
            'accomodation': company_data[12],
            'status' : company_data[13],
            # Add other fields as needed
        }
        # print("Companies:", company)
    
    return render_template('admin/companyDetail.html', company=company)

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

