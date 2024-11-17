from matplotlib import pyplot as plt
from mplsoccer import PyPizza
from matplotlib.offsetbox import AnnotationBbox, OffsetImage

def make_pizza_plot(player, team_name, selected_stats, percentiles, values, slice_colors, player_ranks):
    # Define text colors for each slice (optional)
    text_colors = ["white"] * len(selected_stats)
    
    # Initialize PyPizza for the basketball plot
    baker = PyPizza(
        params=selected_stats,
        min_range=None,
        max_range=None,
        straight_line_color="#000000",
        straight_line_lw=1,
        last_circle_lw=1,
        other_circle_lw=1,
        other_circle_ls="-."
    )
    
    # Create the pizza plot
    fig, ax = baker.make_pizza(
        percentiles,
        figsize=(8, 8),
        param_location=110,
        slice_colors=slice_colors,  # Use the color scheme based on slice positions
        value_colors=text_colors,
        value_bck_colors=slice_colors,
        kwargs_slices=dict(facecolor="cornflowerblue", edgecolor="#000000", zorder=2, linewidth=1),
        kwargs_params=dict(color="#000000", fontsize=12, va="center"),
        kwargs_values=dict(color="#000000", fontsize=12,
                           bbox=dict(edgecolor="#000000", facecolor="cornflowerblue", boxstyle="round,pad=0.2", lw=1))
    )

    # Update the parameter values text with the actual values
    texts = baker.get_value_texts()
    

    # Load medal icons
    gold_medal_img = plt.imread("images/gold_medal.jpg")  # Provide path to your gold medal image
    silver_medal_img = plt.imread("images/gold_medal.jpg")  # Path to silver medal
    bronze_medal_img = plt.imread("images/gold_medal.jpg")  # Path to bronze medal

    # Create a dictionary of rank to image
    medal_images = {1: gold_medal_img, 2: silver_medal_img, 3: bronze_medal_img}

    # Update plot with medals
    for i, text in enumerate(baker.get_value_texts()):
        rank = player_ranks[i]
        if rank in medal_images:
            # Get image for this rank
            medal_img = medal_images[rank]
            # Create OffsetImage and AnnotationBbox
            image_box = OffsetImage(medal_img, zoom=0.1)  # Adjust zoom to size medals
            ab = AnnotationBbox(image_box, text.get_position(), frameon=False, box_alignment=(0.5, -0.5))
            ax.add_artist(ab)  # Add medal image to the plot
        # Update the text to avoid overlap
        text.set_text(f"{values[i]}")  # Just the value, no emoji


    # Add title and subtitle for the basketball player
    fig.text(0.515, 0.97, f"{player} per Game - {team_name}", size=18, ha="center", color="#000000")
    fig.text(0.515, 0.942, "NBA Season | 2023-24", size=15, ha="center", color="#000000")

    return fig
