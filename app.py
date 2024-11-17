import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd
from make_pizza_plot import make_pizza_plot
import matplotlib.pyplot as plt

# Load environment variables from .env file
load_dotenv()

# Retrieve the variables
username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
database = os.getenv("DB_NAME")

# Create the engine
engine = create_engine(f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}')

# Define available stats for selection
stats_display_to_column = {
    "Points per Game": "avg_points",
    "Assists per Game": "avg_assists",
    "Rebounds per Game": "avg_rebounds",
    "Field Goals Made per Game": "avg_field_goals",
    "Total Three Pointers Made": "total_three_pointers",
    "FT Attempted per Game": "avg_free_throw_attempts",
    "Three-Point %": "three_point_percentage",
    "Free Throw %": "free_throw_percentage",
}

# Define the color scheme
base_colors = ["blue"] * 3 + ["green"] * 3 + ["red"] * 2

# Define available stats for selection (display names)
stats_list = list(stats_display_to_column.keys())



def get_team_names_and_ids():
    """Query the database for a list of all team names and IDs."""
    query = "SELECT DISTINCT name, id AS team_id FROM teams ORDER BY name"
    try:
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.write("Error querying the database for team names:", e)
        return pd.DataFrame()

def get_players_for_team(team_id):
    """Query the database for players in the selected team, ordered by total minutes played."""
    query = f"""
        SELECT p1.name AS player_name, p1.id AS player_id
        FROM players p1
        LEFT JOIN player_stats_with_percentiles p2 ON p1.id = p2.player_id
        WHERE p1.team_id = {team_id} AND p2.total_minutes_played IS NOT NULL
        ORDER BY p2.total_minutes_played DESC
    """
    try:
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.write("Error querying the database for players:", e)
        return pd.DataFrame()


def get_player_data(player_id):
    """Query the database for a specific player's stats using player_id."""
    query = f"""
        SELECT * FROM player_stats_with_percentiles
        WHERE player_id = {player_id}
    """
    try:
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.write("Error querying the database:", e)
        return None



# Streamlit application layout
st.title("Interactive Basketball Pizza Plot")

# Dropdown for team selection
teams_df = get_team_names_and_ids()
if not teams_df.empty:
    team_name = st.selectbox("Team Name", teams_df["name"])
    # Get the corresponding team_id for the selected team
    team_id = teams_df[teams_df["name"] == team_name]["team_id"].values[0]
else:
    st.write("Could not load team names.")
    team_id = None

# Dropdown for player selection based on selected team
if team_id is not None:
    players_df = get_players_for_team(team_id)
    if not players_df.empty:
        # Display player names in the dropdown, and get the corresponding player_id
        player_name = st.selectbox("Player Name", players_df["player_name"])
        player_id = players_df[players_df["player_name"] == player_name]["player_id"].values[0]
    else:
        st.write("No players found for the selected team.")
        player_id = None
else:
    player_id = None

# Load player data from the database if both team and player are selected
player_data = get_player_data(player_id) if player_id else None

# Display error if no data is found
if player_data is None or player_data.empty:
    st.write("No data found for the specified player.")
else:
    # Display player stats for selection
    selected_stats = st.multiselect(
        "Select Stats to Display",
        options=stats_list,
        default=stats_list  # By default, all stats are selected
    )

    # Slice colors according to selected stats length, keeping the desired order
    slice_colors = base_colors[:len(selected_stats)]

    
    # Retrieve percentiles for the selected stats from the database data
    percentiles = []
    values = []
    # Additional list to track if the player is top-ranked for each selected stat
    player_ranks = []
    for display_name in selected_stats:
        column_name = stats_display_to_column[display_name]  # Map display name to actual column name
        rank_column = f"{column_name}_rank"  # Assuming rank columns have '_rank' suffix
        value_column = column_name
        
        # Fetch the rank and value
        rank = player_data[rank_column].values[0]
        value = player_data[value_column].values[0]
        
        percentiles.append(player_data[f"{column_name}_percentile"].values[0] * 100)  # Convert percentile to 0-100 scale
        values.append(value)
        player_ranks.append(rank)  # Collect the rank for dynamic coloring

    # Display plot if at least one stat is selected
    if selected_stats:
        fig = make_pizza_plot(player_name, team_name, selected_stats, percentiles, values, slice_colors, player_ranks)
        st.pyplot(fig)
    else:
        st.write("Please select at least one stat to display the plot.")
