# Rentify
# Rentify Web App

This is a web application called Rentify, built with Flask for managing properties.

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/jayachandranpm/Rentify.git
   ```

2. Navigate to the project directory:
   ```bash
   cd Rentify
   ```

3. Create a virtual environment and activate it:
   - For Windows:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   - For Unix/macOS:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

4. Install dependencies using pip:
   ```bash
   pip install -r requirements.txt
   ```

5. Set up the database:
   - Create a MySQL database named `rentify_db`.
   - Update the database URI in `app.py`:
     ```python
     app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/rentify_db'
     ```

6. Apply Flask Migrations for database setup:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

7. Set up SMTP mail server using your Gmail address and app password:
   - Update the SMTP configuration in `app.py`:
     ```python
     app.config['MAIL_SERVER'] = 'smtp.gmail.com'
     app.config['MAIL_PORT'] = 587
     app.config['MAIL_TIMEOUT'] = 30
     app.config['MAIL_USE_TLS'] = True
     app.config['MAIL_USERNAME'] = 'your@gmail.com'
     app.config['MAIL_PASSWORD'] = 'your_app_password'
     ```

## Running the App

1. Set the Flask app environment variable:
   - For Windows:
     ```bash
     set FLASK_APP=app.py
     ```
   - For Unix/macOS:
     ```bash
     export FLASK_APP=app.py
     ```

2. Run the Flask app:
   ```bash
   flask run
   ```

3. Open your web browser and navigate to http://localhost:5000 to access Rentify.

## Usage

- Register an account to post properties or view listings.
- Navigate to the dashboard to manage properties, like or express interest in listings.

## Technologies Used

- Flask
- SQLAlchemy
- Flask Migrate
- HTML/CSS (Bootstrap)

## Credits

This project was developed by [Jayachandran P M](https://github.com/jayachandranpm/Rentify).

For more details, contact: jayachandranpm2001@gmail.com

