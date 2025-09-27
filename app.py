from flask import Flask, render_template, request, redirect, url_for
from psycopg2._psycopg import cursor
from scouting_utils import *
from collections import Counter
import matplotlib

matplotlib.use('Agg')
app = Flask(__name__)


# Basic Routes *******************************************#
@app.route("/")
def start_up():
    """
    Renders the root page of the application.

    Returns:
        HTML template for the StartUp page.
    """
    return render_template("StartUp.html")


@app.route("/match-scouting/")
def match_scouting():
    """
    Render the match scouting page. Does not handle page submission

    Returns:
        HTML template for the MatchScouting page.
    """
    return render_template("MatchScouting.html")


@app.route("/pit-scouting/")
def pit_scouting():
    """
    Render the pit scouting page. Does not handle page submission

    Returns:
        HTML template for the PitScouting page.
    """
    return render_template("PitScouting.html")


@app.route("/data-analysis/")
def data_analysis():
    """
    Render the data analysis scouting page. Does not handle page submission

    Returns:
        HTML template for the Data analysisScouting page.
    """
    return render_template("DataAnalysis.html")


@app.route("/sys_admin/")
def sys_admin():
    """
    Render the system admin page. Does not handle page submission

    Returns:
        HTML template for the administration page.
    """

    return render_template("Administration.html")


# Submit data *******************************************#

@app.route("/submit-match-data/", methods=["POST"])
def sub_match_scouting():
    """
        Handles form submission for match scouting data.

        - Establishes a database connection.
        - Creates the match data table if it doesn't exist.
        - Converts submitted form data into a dictionary.
        - Inserts the match data into the database.

        Returns:
            HTML template for the StartUp page after submission.
    """
    with get_db_connection_cm() as (cur, conn):
        create_match_db(cur, conn)

        data_list_match = request.form
        match_dict = dict(data_list_match)
        insert_match_data(cur, conn, match_dict)
    return render_template("StartUp.html")


@app.route("/submit-pit-data/", methods=["POST"])
def sub_pit_scouting():
    """
    Handles form submission for pit scouting data.

    - Establishes a database connection.
    - Creates the pit data table if it doesn't already exist.
    - Converts submitted form data into a dictionary.
    - Inserts the pit scouting data into the database.

    Returns:
        HTML template for the StartUp page after data submission.
    """
    with get_db_connection_cm() as (cur, conn):
        create_pit_db(cur, conn)

        data_list_pit = request.form
        pit_dict = dict(data_list_pit)
        print("Submitted data:", pit_dict)
        insert_pit_data(cur, conn, pit_dict)
    return render_template("StartUp.html")


# Data Analysis/Administration *******************************************#

@app.route("/run_sql", methods=["POST"])
def run_sql() -> str:
    """
    Executes a raw SQL query submitted via an admin form.

    - Retrieves the SQL string from the POST form.
    - Connects to the database and attempts to execute the query.
    - Returns an error message if execution fails.

    Returns:
        str: Empty string on success or an error message if the query fails.
    """
    sql_query = request.form.get("sql")
    with get_db_connection_cm() as (cur, conn):
        cur.execute(sql_query)
    return redirect(url_for("start_up"))


@app.route("/clear_match")
def clear_match():
    """
    Clears all match scouting data from the database.

    - Establishes a database connection.
    - Deletes all records from the match data table.
    - Returns the StartUp page after clearing the data.

    Returns:
        HTML template for the StartUp page.
    """
    with get_db_connection_cm() as (cur, conn):
        clear_match_data(cur, conn)
    return render_template("StartUp.html")


@app.route("/clear_pit")
def clear_pit():
    """
    Clears all pit scouting data from the database.

    - Establishes a database connection.
    - Deletes all records from the match data table.
    - Returns the StartUp page after clearing the data.

    Returns:
        HTML template for the StartUp page.
    """
    with get_db_connection_cm() as (cur, conn):
        clear_pit_data(cur, conn)
    return render_template("StartUp.html")


@app.route('/match-summary', methods=['POST'])
def match_summary():
    """
    Processes a team number submitted via POST and display the match scouting summary.

    - Retrieves the team number from the submitted form.
    - Calls a utility function to generate a summary of scouting data for the team.
    - Handles exceptions and returns an error message if the summary generation fails.
    - Renders the DataAnalysis page with the team's summary data.

    Returns:
        Rendered HTML template with the team number and its scouting summary,
        or an error message if processing fails.
    """
    with get_db_connection_cm() as (cur, conn):
        team_number = int(request.form.get("team_number"))
        cur.execute(f"""SELECT l1_auto, l2_auto, l3_auto, l4_auto, algae_auto,
                   l1, l2, l3, l4, algae from match_scouting WHERE team_number={team_number}
        """)
        rows = cur.fetchall()
        all_values = []
        for row in rows:
            all_values.extend(row)
        boxplot_source = create_box_plot(all_values, f"Boxplot of {team_number}")

        try:
            match_summary_dict = summarize_scouting_data(team_number, cur, "match_scouting")
        except Exception as e:
            return render_template("DataAnalysis.html", team_number=team_number, match_summary=str(f"Error: {e}"))
    return render_template("DataAnalysis.html", team_number=team_number, match_summary=match_summary_dict, boxplot_source=boxplot_source)


@app.route('/pit-summary', methods=['POST'])
def pit_summary():
    """
    Processes a team number submitted via POST and display the pit scouting summary.

    - Retrieves the team number from the submitted form.
    - Calls a utility function to generate a summary of scouting data for the team.
    - Handles exceptions and returns an error message if the summary generation fails.
    - Renders the DataAnalysis page with the team's summary data.

    Returns:
        Rendered HTML template with the team number and its scouting summary,
        or an error message if processing fails.
    """
    team_number = request.form.get("team_number")
    with get_db_connection_cm() as (cur, conn):
        try:
            pit_summary_dict = summarize_scouting_data(str(team_number), cur, "pit_scouting")
        except Exception as e:
            return render_template("DataAnalysis.html", team_number=team_number, pit_summary={"Error": f"Error: {e}"})

        cur.execute("SELECT drivetrain FROM pit_scouting WHERE team_number = %s", (team_number,))
        rows = cur.fetchall()
        drivetrains = [row[0] for row in rows]
        drivetrains_dict = dict(Counter(drivetrains))
        print(drivetrains_dict)

        pie_source = create_pie_graph(drivetrains_dict, "Drivetrains Used In DDU")



    return render_template("DataAnalysis.html", team_number=team_number, pit_summary=pit_summary_dict, pie_source=pie_source)

@app.route('/full-pit', methods=['GET'])
def full_pit():
    with get_db_connection_cm() as (cur, conn):
        pit_data = full_data(cur, "pit_scouting")
    return render_template("DataAnalysis.html", full_pit_data=pit_data)


@app.route('/full-match', methods=['GET'])
def full_match():
    print(f"TEST 1")
    with get_db_connection_cm() as (cur, conn):
        print(f"TEST cur and conn")
        match_data = full_data(cur, "match_scouting")
        print(f"{match_data}")
    return render_template("DataAnalysis.html", full_match_data=match_data)

@app.route('/match-missed-made', methods=['POST'])
def match_missed_made_app():
    team_number = int(request.form.get("team_number"))
    with get_db_connection_cm() as (cur, conn):
        missed_made_source = match_missed_made(cur, team_number)
    return render_template("DataAnalysis.html", missed_made_source=missed_made_source)

# Only use when testing:
if __name__ == "__main__":
    app.run(debug=True)
