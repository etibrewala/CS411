#main.py
from flask import Flask, jsonify, request, render_template, redirect, url_for, session, flash
from db import *

app = Flask(__name__)
app.secret_key = 'temp_key'

cur_user = "Not Logged In"

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['password']
        user_info = check_credentials(username, password)
        if user_info and user_info != "error":
            session['user_info'] = user_info  # Storing user information in session
            pharmacy_info = get_pharmacy_info(user_info[5])
            session['pharmacy_info'] = pharmacy_info
            if user_info[3] == "doctor@kunjeshmd.org":
                prescription_info = get_user_prescriptions()
                print(prescription_info)
                session['prescription_info'] = prescription_info
            return redirect(url_for('welcome'))
        else:
            error = 'Invalid Login Credentials'
    return render_template('home.html', error=error)

@app.route('/new_user')
def new_user():
    return render_template('new_user.html')

@app.route('/create_user', methods=['POST'])
def create_user():
    # Fetch the form data
    email = request.form['email']
    password = request.form['password']
    first_name = request.form['fname']
    last_name = request.form['lname']
    hp_id = request.form['hp_id']
    user_id = add_user_db(first_name, last_name, email, password, hp_id)
    session['user_info'] = [user_id, first_name, last_name, email, password, hp_id]
    session['pharmacy_info'] = get_pharmacy_info(hp_id)
    return redirect(url_for('welcome'))

@app.route('/welcome')
def welcome():
    if 'user_info' in session:
        if(session['user_info'][3] == "doctor@kunjeshmd.org"):
            return redirect(url_for('admin_welcome'))
        user_info = session['user_info']
        return render_template('shubh.html', user_info=user_info, pharmacy_info = session['pharmacy_info'])
    return redirect(url_for('login'))

@app.route('/admin_welcome')
def admin_welcome():
    if 'user_info' in session:
        user_info = session['user_info']
        return render_template('admin.html', user_info=user_info, pharmacy_info = session['pharmacy_info'],prescription_info = session['prescription_info'])
    return redirect(url_for('login'))

@app.route('/userinfo', methods=['GET', 'POST'])
def userinfo():
    if 'user_info' in session:
        user_info = session['user_info']
        if request.method == 'POST':
            state = request.form['state']
            session['state'] = state
            result1, result2 = get_procedure("%"+state+"%")
            print(result1)
            print(result2)
            session['user_pharmacies'] = result1
            session['user_conditions'] = result2
            return redirect(url_for('procedure'))
        return render_template('selectstate.html', user_info=user_info, pharmacy_info = session['pharmacy_info'])
    return redirect(url_for('login'))

@app.route('/procedure')
def procedure():
    if 'user_info' in session:
        return render_template('procedure.html', user_pharmacies = session['user_pharmacies'], user_conditions = session['user_conditions'])
    return redirect(url_for('login'))

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_info', None)  # Remove data from session
    session.pop('pharmacy_info', None)
    session.pop('state', None)
    session.pop('prescription_info', None)
    return redirect(url_for('login'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    if 'user_info' in session:
        error = None
        session.pop('pharmacies', None)
        popular_pharmacies = get_popular_pharmacies()
        if request.method == 'POST':
            query = request.form['search']
            pharmacies = search_pharm(query)
            if pharmacies and pharmacies != "error":
                session['pharmacies'] = pharmacies
                return redirect(url_for('pharmacies'))
            else:
                error = 'No Pharmacies Found'
        return render_template('search.html', error=error, popular_pharmacies = popular_pharmacies)
    return redirect(url_for('login'))

@app.route('/pharmacies')
def pharmacies():
    if 'pharmacies' in session:
        pharmacies = session['pharmacies']
        return render_template('pharmacies.html', pharmacies=pharmacies)
    return redirect(url_for('search'))

@app.route('/delete', methods=['POST'])
def delete():
    if 'user_info' in session:
        user_info = session['user_info']
        delete_user(user_info[0])
        session.pop('user_info', None)
        return redirect(url_for('login'))
    return redirect(url_for('login'))

@app.route('/settings')
def settings():
    if 'user_info' in session:
        return render_template('user.html', user_info=session['user_info'])
    return redirect(url_for('login'))

@app.route('/update_user', methods=['POST'])
def update_user():
    if 'user_info' in session:
        user_info = session['user_info']
        new_fname = request.form['fname']
        new_lname = request.form['lname']
        new_email = request.form['email']
        new_password = request.form['password']
        
        update_user_db(user_info[0], new_fname, new_lname, new_email, new_password, user_info[5])

        # Update session info
        session['user_info'] = [user_info[0], new_fname, new_lname, new_email, new_password, user_info[5]]

        flash('Your information has been updated.')
        return redirect(url_for('welcome'))
    return redirect(url_for('login'))

@app.route('/update_home_pharmacy', methods=['POST'])
def update_home_pharmacy():
    if 'user_info' in session:
        user_info = session['user_info']
        new_fname = user_info[1]
        new_lname = user_info[2]
        new_email = user_info[3]
        new_password = user_info[4]
        new_hp_id = request.form['hp_id']
        
        update_user_db(user_info[0], new_fname, new_lname, new_email, new_password, new_hp_id)

        session['user_info'] = [user_info[0], new_fname, new_lname, new_email, new_password, new_hp_id]
        session['pharmacy_info'] = get_pharmacy_info(new_hp_id)
        # flash('Your information has been updated.')
        return redirect(url_for('pharmacies'))
    return redirect(url_for('login'))

# @app.route('/search='{user_query}, methods=['GET', 'POST'])
if __name__ == '__main__':
    app.run(host = '0.0.0.0', port=5000)