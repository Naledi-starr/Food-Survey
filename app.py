from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
import os


app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')

def get_db_connection():
    conn = sqlite3.connect('survey.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/survey', methods=['GET', 'POST'])
def survey():
    if request.method == 'POST':
        # Get form data
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        date_of_birth = request.form.get('date_of_birth')
        contact_number = request.form.get('contact_number')
        favorite_foods = ','.join(request.form.getlist('favorite_foods'))  # Handle multiple checkboxes
        movies_rating = request.form.get('movies_rating')
        radio_rating = request.form.get('radio_rating')
        eating_out_rating = request.form.get('eating_out_rating')
        tv_rating = request.form.get('tv_rating')

        # Server-side validation
        errors = []
        if not all([full_name, email, date_of_birth, contact_number]):
            errors.append('All personal details fields are required.')
        
        # Validate age
        try:
            dob = datetime.strptime(date_of_birth, '%Y-%m-%d')
            age = (datetime.now() - dob).days / 365.25
            if age < 5 or age > 120:
                errors.append('Age must be between 5 and 120 years.')
        except ValueError:
            errors.append('Invalid date of birth format.')

        # Validate ratings
        if not all([movies_rating, radio_rating, eating_out_rating, tv_rating]):
            errors.append('All rating questions must be answered.')
        else:
            try:
                ratings = [int(movies_rating), int(radio_rating), int(eating_out_rating), int(tv_rating)]
                if not all(1 <= r <= 5 for r in ratings):
                    errors.append('Ratings must be between 1 and 5.')
            except ValueError:
                errors.append('Ratings must be valid numbers.')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('survey.html')  # Stay on survey page for errors

        # Save to database
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO surveys (full_name, email, date_of_birth, contact_number, favorite_foods,
                                movies_rating, radio_rating, eating_out_rating, tv_rating)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (full_name, email, date_of_birth, contact_number, favorite_foods,
              movies_rating, radio_rating, eating_out_rating, tv_rating))
        conn.commit()
        conn.close()
        flash('Survey submitted successfully!', 'success')
        return redirect(url_for('home'))  # Redirect to home page on success

    return render_template('survey.html')

@app.route('/results')
def results():
    conn = get_db_connection()
    surveys = conn.execute('SELECT * FROM surveys').fetchall()
    total_surveys = len(surveys)
    
    if total_surveys == 0:
        conn.close()
        return render_template('results.html', no_data=True)
    
    # Calculate ages
    ages = []
    for survey in surveys:
        dob = datetime.strptime(survey['date_of_birth'], '%Y-%m-%d')
        age = (datetime.now() - dob).days // 365  # Integer division for whole number age
        ages.append(age)
    
    avg_age = int(sum(ages) // len(ages)) if ages else 0  # Whole number average
    oldest_age = int(max(ages)) if ages else 0
    youngest_age = int(min(ages)) if ages else 0
    
    # Calculate food percentages
    food_counts = {'Pizza': 0, 'Pasta': 0, 'Pap and Wors': 0, 'Other': 0}
    for survey in surveys:
        foods = survey['favorite_foods'].split(',') if survey['favorite_foods'] else []
        for food in foods:
            if food in food_counts:
                food_counts[food] += 1
    
    food_percentages = {
        food: round((count / total_surveys) * 100, 1) for food, count in food_counts.items()
    }
    
    # Calculate average ratings
    avg_ratings = {
        'movies': round(sum(survey['movies_rating'] for survey in surveys) / total_surveys, 1),
        'radio': round(sum(survey['radio_rating'] for survey in surveys) / total_surveys, 1),
        'eating_out': round(sum(survey['eating_out_rating'] for survey in surveys) / total_surveys, 1),
        'tv': round(sum(survey['tv_rating'] for survey in surveys) / total_surveys, 1)
    }
    
    conn.close()
    return render_template('results.html', no_data=False, total_surveys=total_surveys,
                       avg_age=avg_age, oldest_age=oldest_age, youngest_age=youngest_age,
                       food_percentages=food_percentages, avg_ratings=avg_ratings)

if __name__ == '__main__':
    app.run(debug=True)