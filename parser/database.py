import sqlite3

def create_database():
    connection = sqlite3.connect('solutions.db')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accepted_solutions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER,
            problem_id INTEGER
        )
    ''')
    connection.commit()
    connection.close()

def save_solution_to_db(team_id, problem_id):
    connection = sqlite3.connect('solutions.db')
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO accepted_solutions (team_id, problem_id) 
        VALUES (?, ?)
    ''', (team_id, problem_id))
    connection.commit()
    connection.close()

def check_solution_exists(team_id, problem_id):
    connection = sqlite3.connect('solutions.db')
    cursor = connection.cursor()
    cursor.execute('''
        SELECT COUNT(*) FROM accepted_solutions 
        WHERE team_id = ? AND problem_id = ?
    ''', (team_id, problem_id))
    count = cursor.fetchone()[0]
    connection.close()
    return count > 0
