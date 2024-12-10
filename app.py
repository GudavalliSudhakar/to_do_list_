from flask import Flask, render_template, request, redirect, url_for, session
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__, template_folder='.')  # Telling Flask to look in the current directory

app.secret_key = "your_secret_key"  # Required for session management
tasks = []

# Simulate an OTP verification process
def send_otp(email):
    otp = random.randint(100000, 999999)
    session['otp'] = otp  # Store OTP in session for verification
    session['email'] = email

    # Simulating an email sending process
    sender_email = "20bec016@iiitdwd.ac.in"
    receiver_email = email
    password = "klni qbip xops nxki"  # Use app password or OAuth2 for better security

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Your OTP Verification Code"

    body = f"Your OTP is {otp}"
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            text = message.as_string()
            server.sendmail(sender_email, receiver_email, text)
    except Exception as e:
        print(f"Error sending email: {e}")

@app.route("/")
def index():
    if 'email_verified' in session and session['email_verified']:
        username = session.get('name')  # Get the username from session
        return render_template("index.html", tasks=tasks, username=username)
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    name = request.form.get("name")
    email = request.form.get("email")

    if name and email:
        send_otp(email)
        session['name'] = name
        session['email'] = email
        return redirect(url_for("verify"))
    return redirect(url_for("index"))

@app.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        entered_otp = request.form.get("otp")
        if entered_otp == str(session.get("otp")):
            session['email_verified'] = True
            return redirect(url_for("index"))
        else:
            return render_template("verify.html", error="Invalid OTP. Please try again.")
    return render_template("verify.html")

@app.route("/add", methods=["POST"])
def add_task():
    task = request.form.get("task")
    if task:
        tasks.append({"id": len(tasks) + 1, "name": task})
    return redirect(url_for("index"))

@app.route("/update/<int:task_id>", methods=["POST"])
def update_task(task_id):
    task_name = request.form.get("task")
    for task in tasks:
        if task["id"] == task_id:
            task["name"] = task_name
    return redirect(url_for("index"))

@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    global tasks
    tasks = [task for task in tasks if task["id"] != task_id]
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
