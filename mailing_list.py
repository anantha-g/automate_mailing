import os
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, redirect, url_for, flash, render_template

app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY", "fallback_key_if_not_set")

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16*1024*1024

smtp_server = 'smtp.gmail.com'
smtp_port = 587

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_email', methods = ['POST'])
def send_email():
    username = request.form['username']
    password = request.form['password']
    subject = request.form['subject']
    body_template = request.form['body']

    if 'file' not in request.files['file'].filename == '':
        flash('No file Selected')
        return redirect(url_for('index'))

    file = request.files['file']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    try:
        mail_list = pd.read_excel(file_path)
    except Exception as e:
        flash(f"Error reading file: {e}")
        return redirect(url_for('index'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(username, password)

            for index, row in mail_list.iterrows():
                recipient_email = row['Email']

                body = body_template

                msg = MIMEMultipart()
                msg['From'] = username
                msg['To'] = recipient_email
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))

                server.sendmail(username, recipient_email, msg.as_string())

        flash("Emails sent successfully")
    except Exception as e:
        flash(f"Failed to send message: {e}")

    os.remove(file_path)
    return redirect(url_for('index'))

if __name__ == "__main__":
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
