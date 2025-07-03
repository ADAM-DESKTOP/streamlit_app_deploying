import sqlite3
import threading
import os
# The DataBase Class
class DataBase():
    def __init__(self):
        self.con = sqlite3.connect("tasks_database.db")
        self.cursor = self.con.cursor()
        self.create_task_table()

    def create_task_table(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS tasks(id integer PRIMARY KEY AUTOINCREMENT, task varchar(50) NOT NULL, \
        due_date varchar(50), completed BOOLEAN NOT NULL CHECK (completed IN (0, 1)) )")
        self.con.commit()

    # Creating a Task
    def create_task(self, task, due_date):
        self.cursor.execute("INSERT INTO tasks(task, due_date, completed) VALUES(?,?,?)", (task, due_date, 0))
        self.con.commit()


        # Getting The Last Entered Item to add it to The Database
        created_task = self.cursor.execute("SELECT id, task, due_date FROM tasks WHERE task=? and completed=0", (task,)).fetchall()
        return created_task
    def get_tasks(self):
        """Getting all The Tasks"""
        incompleted_tasks = self.cursor.execute("SELECT id, task, due_date FROM tasks WHERE completed=0").fetchall()
        completed_tasks = self.cursor.execute("SELECT id, task, due_date FROM tasks WHERE completed=1").fetchall()
        return completed_tasks, incompleted_tasks

    # Marking The Tasks as Completed
    def mark_task_completed(self, task_id,):
        """Updating The Task's Status"""
        self.cursor.execute("UPDATE tasks SET completed=1 WHERE id=?", (task_id,))
        self.con.commit()
    # Marking The Tasks as Incompleted
    def mark_task_incompleted(self, task_id):
        """Updating The Task's Status"""
        self.cursor.execute("UPDATE tasks SET completed=0 WHERE id=?", (task_id,))
        self.con.commit()

        # Return The Task in Strings
        task_text = self.cursor.execute("SELECT task FROM tasks WHERE id=?", (task_id,)).fetchall()

        return task_text[0][0]

    def delete_task(self, tasks_id):
        self.cursor.execute("DELETE FROM tasks WHERE id=?", (tasks_id,))
        self.con.commit()

    def close_connection(self):
        self.con.close()

class PrayerDB:
    def __init__(self, username):
        self.db_file = f"prayers_{username.lower().strip().replace(' ', '_')}.db"
        self.lock = threading.Lock()
        self._connect()
        self._create_table()

    def _connect(self):
        self.con = sqlite3.connect(self.db_file, check_same_thread=False)
        self.cursor = self.con.cursor()

    def _create_table(self):
        with self.lock:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS prayers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    prayer TEXT NOT NULL,
                    completed INTEGER NOT NULL CHECK (completed IN (0,1)),
                    UNIQUE(date, prayer)
                )
            """)
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_prayer_date ON prayers(date)")
            self.con.commit()

    def get_status_for_date(self, date):
        with self.lock:
            self.cursor.execute("SELECT prayer, completed FROM prayers WHERE date=?", (date,))
            rows = self.cursor.fetchall()
            return {prayer: bool(completed) for prayer, completed in rows}

    def set_status_for_date(self, date, status_dict):
        with self.lock:
            for prayer, completed in status_dict.items():
                self.cursor.execute("""
                    INSERT INTO prayers (date, prayer, completed)
                    VALUES (?, ?, ?)
                    ON CONFLICT(date, prayer) DO UPDATE SET completed=excluded.completed
                """, (date, prayer, int(bool(completed))))
            self.con.commit()

    def close(self):
        self.con.close()
