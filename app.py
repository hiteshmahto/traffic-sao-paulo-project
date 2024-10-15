import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

# Load and preprocess traffic data
traffic_df = pd.read_csv('traffic_sao_paulo.csv', sep=";")
traffic_df['Slowness in traffic (%)'] = traffic_df['Slowness in traffic (%)'].str.replace(',', '.').astype('float')
traffic_df.rename(columns={'Slowness in traffic (%)': 'Slowness'}, inplace=True)

# Generate time slots
time_slots = []
start_time = 7 * 60

for i in range(27):
    hour = start_time + i * 30
    hours = hour // 60
    minutes = hour % 60
    time_slots.append(f"{hours:02d}:{minutes:02d}")

traffic_df["Time"] = time_slots * 5

# Group data by day
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
traffic_per_day = {}

for i, day in zip(range(0, 135, 27), days):
    each_day_traffic_df = traffic_df.iloc[i: i + 27]
    traffic_per_day[day] = each_day_traffic_df


def plot_graph(day):
    # Convert day to lowercase for case insensitivity
    day = day.lower()

    # Use a dark theme for the plot
    plt.style.use('dark_background')
    plt.figure(figsize=(10, 6))

    day_capitalized = day.capitalize()  # Capitalize for title and labels

    if day == "all":
        # Plot the data for all days
        for day_name, data in traffic_per_day.items():
            plt.plot(data["Time"], data["Slowness"], label=day_name)  # Use label for each day

        # Set titles and labels
        plt.title("Traffic Analysis for All Days", color='white')
        plt.xlabel("Hour of the day", color='white')
        plt.ylabel("Slowness in Traffic %age", color='white')
        plt.legend()
    else:
        # Check if the day is valid before trying to plot
        if day_capitalized in traffic_per_day:
            plt.plot(traffic_per_day[day_capitalized]["Time"], traffic_per_day[day_capitalized]["Slowness"],
                     label=day_capitalized, color='yellow')
            plt.title(f"{day_capitalized} Analysis", color='white')
            plt.xlabel("Hour of the day", color='white')
            plt.ylabel("Slowness in Traffic %age", color='white')
        else:
            return None  # If the day is invalid, return None

    plt.grid(color='gray', linestyle='--', linewidth=0.5)
    plt.xticks(rotation=45, color='white')
    plt.yticks(color='white')

    # Save the plot as an image file in the static folder
    graph_filename = f"static/{day_capitalized}_traffic_analysis.png"  # Save in the static folder
    plt.savefig(graph_filename, bbox_inches='tight', facecolor='black')  # Save with black background
    plt.close()  # Close the plot to free memory
    return graph_filename


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/plot', methods=['POST'])
def plot():
    day = request.form.get('day')
    graph_filename = plot_graph(day)

    if graph_filename:
        return jsonify({'graph': graph_filename})
    else:
        return jsonify({'error': 'Invalid day name. Please try again.'}), 400


if __name__ == '__main__':
    app.run(debug=True)
