import os
import psycopg2
from collections import Counter
from contextlib import contextmanager
import matplotlib.pyplot as plt
import io
import base64
import urllib.parse as urlparse


def get_db_connection():
    DATABASE_URL = os.environ.get("DATABASE_URL")
    urlparse.uses_netloc.append("postgres")
    url = urlparse.urlparse(DATABASE_URL)

    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port,
        sslmode='require'
    )

    cur = conn.cursor()
    return cur, conn

@contextmanager
def get_db_connection_cm():
    cur, conn = get_db_connection()
    try:
        yield cur, conn
    except:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.commit()
        conn.close()

def is_numeric(value) -> bool:
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def create_match_db(cursor, conn) -> None:
    sql_path = os.path.join(os.path.dirname(__file__), "sql", "create_match_db.sql")
    with open(sql_path, "r") as f:
        sql = f.read()
    cursor.execute(sql)
    conn.commit()


def create_pit_db(cursor, conn) -> None:
    sql_path = os.path.join(os.path.dirname(__file__), "sql", "create_pit_db.sql")
    with open(sql_path, "r") as f:
        sql = f.read()
    cursor.execute(sql)
    conn.commit()


def insert_match_data(cursor, conn, data) -> None:
    sql_path = os.path.join(os.path.dirname(__file__), "sql", "insert_match_data.sql")
    with open(sql_path, "r") as f:
        sql = f.read()
    cursor.execute(sql, data)
    conn.commit()


def insert_pit_data(cursor, conn, data) -> None:
    print(f"{data}")
    sql_path = os.path.join(os.path.dirname(__file__), "sql", "insert_pit_data.sql")
    with open(sql_path, "r") as f:
        sql = f.read()
    print(f"got data")
    cursor.execute(sql, (data,))
    conn.commit()


def clear_match_data(cursor, conn) -> None:
    sql_path = os.path.join(os.path.dirname(__file__), "sql", "clear_match_db.sql")
    with open(sql_path, "r") as f:
        sql = f.read()
    cursor.execute(sql)
    conn.commit()


def clear_pit_data(cursor, conn) -> None:
    sql_path = os.path.join(os.path.dirname(__file__), "sql", "clear_pit_db.sql")
    with open(sql_path, "r") as f:
        sql = f.read()
    cursor.execute(sql)
    conn.commit()

def summarize_scouting_data(team_number: int, cur, datatable) -> dict:
    cur.execute(f"""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = '{datatable}'
    """)
    columns = [row[0] for row in cur.fetchall()]

    summary = {}
    for col in columns:
        query = f"""
            SELECT {col} FROM {datatable} 
            WHERE team_number = %s AND {col} IS NOT NULL
        """
        cur.execute(query, (team_number,))
        values = [row[0] for row in cur.fetchall()]

        if not values:
            summary[col] = 0
            continue

        numeric_values = [float(v) for v in values if is_numeric(v)]

        if len(numeric_values) == len(values):
            summary[col] = round(sum(numeric_values) / len(numeric_values), 2)
        else:
            summary[col] = Counter(values).most_common(1)[0][0]

    return summary

def create_pie_graph(data: dict, title: str) -> str:
    fig, axis = plt.subplots()

    wedges, texts, autotexts = axis.pie(
        data.values(),
        labels=list(data.keys()),
        autopct='%1.1f%%',
        startangle=140,
        textprops=dict(color="w")
    )

    axis.legend(wedges, list(data.keys()), title="Drivetrain Types", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    axis.axis('equal')
    plt.title(title)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)

    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    return f'<img src="data:image/png;base64,{img_base64}" alt="{title}">'


def create_box_plot(data, title: str, team_number) -> str:
    fig, axis = plt.subplots()
    axis.boxplot(data)
    plt.title(title)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)

    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    return f'<img src="data:image/png;base64,{img_base64}"/>'

def full_data(cur, datatable: str) -> list[dict]:
    cur.execute(f"SELECT * FROM {datatable}")
    rows = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]

    data_list = [dict(zip(colnames, row)) for row in rows]
    return data_list

def match_missed_made(cur, team_number):
    columns = ['l1', 'l2', 'l3', 'l4', 'algae', 'intake_missed', 'scorer_missed']

    summary = {}
    for col in columns:
        query = f"""
            SELECT {col} FROM match_scouting 
            WHERE team_number = %s AND {col} IS NOT NULL
        """
        cur.execute(query, (team_number,))
        values = [row[0] for row in cur.fetchall()]

        if not values:
            summary[col] = 0
            continue

        numeric_values = [float(v) for v in values if is_numeric(v)]

        if len(numeric_values) == len(values):
            summary[col] = round(sum(numeric_values) / len(numeric_values), 2)
        else:
            summary[col] = Counter(values).most_common(1)[0][0]

    match_pie_source = create_pie_graph(summary, f"Made vs Missed for team {str(team_number)}")
    return match_pie_source
