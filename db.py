#db.py
import os
import pymysql
from flask import jsonify
from google.cloud.sql.connector import Connector, IPTypes
import sqlalchemy
import pymysql

# db_user = os.environ.get('CLOUD_SQL_USERNAME')
# db_password = os.environ.get('CLOUD_SQL_PASSWORD')
# db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
# db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')


# connector = Connector()
# def open_connection() -> pymysql.connections.Connection:
#     # unix_socket = '/cloudsql/{}'.format(db_connection_name)
#     try:
#         conn = pymysql.connections.Connection = connector.connect(
#             "kunjeshdb:us-central1:kunjesh-sql",
#             "pymysql",
#             user=db_user,
#             password=db_password,
#             db=db_name
#             # cloud_config={
#             #     'project': db_connection_name.split(':')[0]
#             # }
#         )
#         return conn
#     except Exception as e:
#         print(e)
#     return None

def connect_with_connector() -> sqlalchemy.engine.base.Engine:
    instance_connection_name = "kunjeshdb:us-central1:kunjesh-sql"
    # db_user = os.environ.get('CLOUD_SQL_USERNAME')
    # db_pass = os.environ.get('CLOUD_SQL_PASSWORD') 
    # db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
    db_user = "eshaant2"
    db_pass = "C1rcusMax1mus"
    db_name = "Drugs"
    connector = Connector(IPTypes.PUBLIC)

    def getconn() -> pymysql.connections.Connection:
        conn: pymysql.connections.Connection = connector.connect(
            instance_connection_name,
            "pymysql",
            user=db_user,
            password=db_pass,
            db=db_name,
        )
        return conn
    
    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn,
        # ...
    )

    return pool


def get_songs():
    engine = connect_with_connector()
    with engine.connect() as connection:
        cursor = connection
        result = cursor.execute(sqlalchemy.text("SELECT * FROM User_Accounts LIMIT 15;"))
        songs = result.fetchall()
        cursor.commit()
        if result:
            rows = [row[:] for row in songs]
            print(rows)
            got_songs = str(rows)
        else:
            got_songs = 'No people in DB'
    return got_songs

def search_users(name):
    engine = connect_with_connector()
    with engine.connect() as connection:
        cursor = connection
        result = cursor.execute(sqlalchemy.text("SELECT * FROM User_Accounts WHERE FirstName = " + name + ";"))
        name = result.fetchall()
        cursor.commit()
        if result:
            rows = [row[:] for row in name]
            names = str(rows)
        else:
            names = 'No people in DB'
    return names

def check_credentials(email, password):
    engine = connect_with_connector()
    with engine.connect() as connection:
        cursor = connection
        result = cursor.execute(sqlalchemy.text(f"SELECT * FROM User_Accounts WHERE email=\"{email}\" AND user_password=\"{password}\""))
        out = result.fetchall()
        if out:
            user_info = list(out[0])
        else:
            user_info = "error"
        cursor.commit()
        return user_info
    
def search_pharm(query):
    engine = connect_with_connector()
    with engine.connect() as connection:
        cursor = connection
        result = cursor.execute(sqlalchemy.text(f"SELECT * FROM Pharmacies WHERE pharmacy_address LIKE '%{query}%' LIMIT 40"))
        out = result.fetchall()
        if out:
            out = [list(ele) for ele in out]
            pharmacy_info = list(out[:])
        else:
            pharmacy_info = "error"
        return pharmacy_info
    
def delete_user(user_id):
    engine = connect_with_connector()
    with engine.connect() as connection:
        cursor = connection
        cursor.execute(sqlalchemy.text(f"DELETE FROM User_Accounts WHERE user_id={user_id}"))
        cursor.commit() 
        return
    
def add_user_db(first_name, last_name, email, password, hp_id):
    # Insert the new user into the database
    engine = connect_with_connector()
    with engine.connect() as connection:
        cursor = connection
        result = cursor.execute(sqlalchemy.text(f"SELECT COUNT(*) FROM User_Accounts"))
        num = int(list(result.fetchall()[0])[0])
        num += 1 #increment to next id
        cursor.execute(sqlalchemy.text(f"INSERT INTO User_Accounts (user_id, first_name, last_name, email, user_password, home_pharmacy_id) VALUES ({num}, '{first_name}', '{last_name}', '{email}', '{password}', {hp_id})"))
        #cursor.execute(sqlalchemy.text(f"SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED; START TRANSACTION READ WRITE; INSERT INTO User_Accounts (user_id, first_name, last_name, email, user_password, home_pharmacy_id)  VALUES ({num}, '{first_name}', '{last_name}', '{email}', '{password}', {hp_id});COMMIT;"))
        cursor.commit()
        return num
    
def update_user_db(user_id, new_fname, new_lname, new_email, new_password, new_hp_id):
    engine = connect_with_connector()
    with engine.connect() as connection:
        cursor = connection
        cursor.execute(sqlalchemy.text(f"CALL UpdateUserInfo({user_id}, '{new_fname}', '{new_lname}', '{new_email}', '{new_password}', {new_hp_id})"))
        cursor.commit() 
        return
    
def get_pharmacy_info(pharmacy_id):
    engine = connect_with_connector()
    with engine.connect() as connection:
        cursor = connection
        result = cursor.execute(sqlalchemy.text("SELECT * FROM Pharmacies WHERE pharmacy_id = " + str(pharmacy_id) + ";"))
        out = result.fetchall()
        if out:
            info = list(out[0])
        else:
            info = 'No home pharmacy assigned.'
    return info

def get_popular_pharmacies():
    engine = connect_with_connector()
    with engine.connect() as connection:
        cursor = connection
        result = cursor.execute(sqlalchemy.text(f"CALL GetPopularPharmacies();"))
        out = result.fetchall()
        cursor.commit()
        if out:
            out = [list(ele) for ele in out]
            info = list(out[:])
        else:
            info = 'Pharmacy data not available'
    return info

def get_procedure(state):
    engine = connect_with_connector()
    with engine.connect() as connection:
        # connection.callproc('GetDoctorInfo',[state])
        # connection.execute(sqlalchemy.text(f"CALL GetDoctorInfo"), parameters = [dict({"state_":state})])
        result1 = connection.execute(sqlalchemy.text(f"CALL GetUserPharmacies(:state_)"), {"state_":state})
        result2 = connection.execute(sqlalchemy.text(f"CALL GetUserMedConditions()"))
        out1 = result1.fetchall()
        out2 = result2.fetchall()
        if out1:
            out1 = [list(ele) for ele in out1]
            info1 = out1[:]
            out2 = [list(ele) for ele in out2]
            info2 = out2[:]
            return info1, info2
        else:
            info = 'No Users Found'
    return info, None



def get_user_prescriptions():
    engine = connect_with_connector()
    with engine.connect() as connection:
        cursor = connection
        result = cursor.execute(sqlalchemy.text("CALL GetUserPrescriptions();"))
        out = result.fetchall()
        if out:
            out = [list(ele) for ele in out]
            info = list(out[:])
        else:
            info = 'Pharmacy data not available'
    return info