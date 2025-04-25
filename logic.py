import sqlite3
from config import DATABASE

""""
************************************************
Proje adı: "Ödev"
Proje açıklaması: "Harika detaylı bi tablo"
Projenin GitHub deposuna bir bağlantı: "https://github.com/ahmetsenocak23/Tablo.git"
Proje durumu: "Gelişiyor" 
Projede kullanılan beceri: "sqlite3 + python"
************************************************
"""

class DB_Manager:
    def __init__(self, database):
        self.database = database # veri tabanının adı

    def create_tables(self):
        con = sqlite3.connect(self.database)
        with con:
            con.execute("""CREATE TABLE status(
                                    status_id INTEGER PRIMARY KEY,
                                    status_name TEXT) """)

            con.execute("""CREATE TABLE projects (
                                    project_id INTEGER PRIMARY KEY,
                                    user_id INTEGER,
                                    project_name TEXT,
                                    description TEXT,
                                    url TEXT,
                                    status_id INTEGER,
                                    FOREIGN KEY (status_id) REFERENCES status (status_id)) """)

            con.execute("""CREATE TABLE skills (
                                    skill_id INTEGER PRIMARY KEY,
                                    skill_name TEXT) """)

            con.execute("""CREATE TABLE project_skills (
                    
                                    project_id INTEGER,
                                    skill_id INTEGER,
                                    FOREIGN KEY (project_id) REFERENCES projects (project_id),
                                    FOREIGN KEY (skill_id) REFERENCES skills (skill_id)) """)
            
            con.execute("""INSERT INTO project_skills (skill_id) VALUES (?) """, ("Python",))
            con.execute("""INSERT INTO project_skills (skill_id) VALUES (?) """, ("Sqlite3",))
            con.execute("""INSERT INTO status (status_name) VALUES (?) """, ("Geliştirme Aşamasında",))
            con.execute("""INSERT INTO skills (skill_name) VALUES (?) """, ("Python",))
            con.execute("""INSERT INTO skills (skill_name) VALUES (?) """, ("Discord bot geliştirme",))
            con.execute("""INSERT INTO skills (skill_name) VALUES (?) """, ("SQL / sqlite3",))
            con.execute("""INSERT INTO skills (skill_name) VALUES (?) """, ("API",))
            con.execute("""INSERT INTO skills (skill_name) VALUES (?) """, ("HTML",))
            con.execute("""INSERT INTO skills (skill_name) VALUES (?) """, ("CSS",))
            con.execute("""INSERT INTO skills (skill_name) VALUES (?) """, ("FLASK",))
            con.execute("""INSERT INTO skills (skill_name) VALUES (?) """, ("AI",))
            
        con.commit()
        con.close()

if __name__ == '__main__':
    dbmanager = DB_Manager(DATABASE)
    dbmanager.create_tables()
