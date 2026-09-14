# College Complaint Management System

This is a faithful, runnable Django implementation based on the uploaded project report and its sample UI screenshots.

## Stack
- Python 3.8+
- Django 3.2
- Bootstrap 5.3
- SQLite for easiest local development
- MySQL 5.7 supported through environment variables
- HTML/CSS/JavaScript
- Pillow for image uploads

## Main modules
1. Student/Staff registration
2. Email activation (console email by default during local development)
3. Login/logout with role-based redirection
4. Student profile
5. Complaint submission with optional proof image
6. Student complaint tracking
7. Staff department-based complaint dashboard
8. Staff reply/resolution
9. Django admin
10. Password reset

## Run on Windows
```text
cd college_complaints
py -3.8 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open:
- http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

## Local email activation
The default email backend is the Django console backend. After registration, the activation link is printed in the terminal where `runserver` is running. Copy the activation URL into the browser.

## MySQL
The report specifies MySQL 5.7. To use it, create a database named `college_complaints`, then set:
```text
DB_ENGINE=mysql
DB_NAME=college_complaints
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_PORT=3306
```
before running migrations.

## Important note about the source report
The report's model uses `ImageField` for complaint proof, while its validation section also mentions PDF/DOCX. This implementation follows the model and screenshots and therefore accepts JPG/JPEG/PNG proof images. The report also describes Admin as a role, but the provided registration code only creates Student/Staff profiles; Admin is implemented through Django's `/admin/` interface and `createsuperuser`.
