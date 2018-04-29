
import sqlite3
import sys

def init_db():
    conn = sqlite3.connect('teachingassignments.sqlite')
    cur = conn.cursor()

    # Drop tables
    statement = '''
        DROP TABLE IF EXISTS 'Instructors';
    '''
    cur.execute(statement)
    statement = '''
        DROP TABLE IF EXISTS 'Classes';
    '''
    cur.execute(statement)

    conn.commit()

    statement = '''
        CREATE TABLE 'Instructors' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'LastName' TEXT NOT NULL,
            'FirstName' TEXT NOT NULL,
            'Uniqname' TEXT NOT NULL,
            'Office' TEXT
        );
    '''
    cur.execute(statement)
    statement = '''
        CREATE TABLE 'Classes' (
                'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
                'CourseDept' TEXT NOT NULL,
                'CourseNum' TEXT NOT NULL,
                'TeacherId' INTEGER
        );
    '''
    cur.execute(statement)
    conn.commit()
    conn.close()

if len(sys.argv) > 1 and sys.argv[1] == '--init':
    print('Deleting db and starting over from scratch.')
    init_db()
else:
    print('Leaving the DB alone.')