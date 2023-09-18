# rmb to change after

from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

# db_conn = connections.Connection(
#     host=customhost,
#     port=3306,
#     user=customuser,
#     password=custompass,
#     db=customdb

# )
# output = {}
# table = 'employee'


# Main
@app.route("/")
def index():
    return render_template('index.html')

# Student
@app.route("/student/login")
def studentLogin():
    return render_template('student/login.html')

@app.route("/student/register")
def studentRegister():
    return render_template('student/register.html')

@app.route("/student/registerSuccess")
def studentRegisterSuccess():
    return render_template('student/registerSuccess.html')

@app.route("/student/home")
def studentHome():
    return render_template('student/home.html')

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
@app.route("/lecturer/login")
def lecturerLogin():
    return render_template('lecturer/login.html')

@app.route("/lecturer/home")
def lecturerHome():
    return render_template('lecturer/home.html')

@app.route("/lecturer/studentDetail")
def lecturerDetail():
    return render_template('lecturer/studentDetail.html')

# Company
@app.route("/company/login")
def companyLogin():
    return render_template('company/login.html')

@app.route("/company/register")
def companyRegister():
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
@app.route("/admin/login")
def adminLogin():
    return render_template('admin/login.html')

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

