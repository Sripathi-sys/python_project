import sqlite3

class Database:
    def __init__(self, db_name="app_data.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Create tables if they don't exist"""
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                completed INTEGER DEFAULT 0
            )"""
        )

        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT DEFAULT (datetime('now', 'localtime'))
            )"""
        )
        self.conn.commit()

    # To-Do List Methods
    def add_task(self, task):
        self.cursor.execute("INSERT INTO tasks (task) VALUES (?)", (task,))
        self.conn.commit()

    def get_tasks(self):
        self.cursor.execute("SELECT * FROM tasks")
        return self.cursor.fetchall()

    def delete_task(self, task_id):
        self.cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        self.conn.commit()

    def mark_task_complete(self, task_id, completed):
        self.cursor.execute("UPDATE tasks SET completed=? WHERE id=?", (completed, task_id))
        self.conn.commit()

    # Expense Tracker Methods
    def add_expense(self, amount, category):
        self.cursor.execute("INSERT INTO expenses (amount, category) VALUES (?, ?)", (amount, category))
        self.conn.commit()

    def get_expenses(self):
        self.cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
        return self.cursor.fetchall()

    def delete_expense(self, expense_id):
        self.cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
        self.conn.commit()

    def get_total_expenses(self):
        self.cursor.execute("SELECT SUM(amount) FROM expenses")
        return self.cursor.fetchone()[0] or 0  # Return 0 if no expenses

    def close(self):
        self.conn.close()
