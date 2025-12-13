from db_config import get_connection
from datetime import date, timedelta

class Habit:
    def __init__(self, habit_id, name, daily_goal, xp=0, created_at=None):
        self.habit_id = habit_id
        self.name = name
        self.daily_goal = daily_goal
        self.xp = xp
        self.created_at = created_at if created_at else date.today()

    def add_xp(self, amount):
        self.xp += amount
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE habits SET xp=%s WHERE habit_id=%s", (self.xp, self.habit_id))
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def get_all():
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM habits")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [Habit(**row) for row in rows]

    @staticmethod
    def add(name, daily_goal=1):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO habits (name, daily_goal) VALUES (%s, %s)", (name, daily_goal))
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def delete(habit_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM habit_logs WHERE habit_id=%s", (habit_id,))
        cursor.execute("DELETE FROM habits WHERE habit_id=%s", (habit_id,))
        conn.commit()
        cursor.close()
        conn.close()

    def log_today(self):
        today = date.today()
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM habit_logs WHERE habit_id=%s AND log_date=%s", (self.habit_id, today))
        exists = cursor.fetchone()

        logged_successfully = False

        if not exists:
            cursor.execute(
                "INSERT INTO habit_logs (habit_id, log_date, completed) VALUES (%s, %s, %s)",
                (self.habit_id, today, True)
            )
            self.xp += 50
            cursor.execute("UPDATE habits SET xp=%s WHERE habit_id=%s", (self.xp, self.habit_id))
            logged_successfully = True

        conn.commit()
        cursor.close()
        conn.close()

        return logged_successfully

    def get_streak(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT log_date FROM habit_logs WHERE habit_id=%s AND completed=1 ORDER BY log_date DESC",
            (self.habit_id,)
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        if not rows:
            return 0

        today = date.today()
        last_log_date = rows[0][0]

        if (today - last_log_date).days > 1:
            return 0

        streak = 0
        current_check = last_log_date

        for r in rows:
            if r[0] == current_check:
                streak += 1
                current_check -= timedelta(days=1)
            else:
                break

        return streak