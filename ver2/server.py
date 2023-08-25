from flask import Flask, render_template, jsonify
import plotly.graph_objects as go
import requests
import urllib
import json

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/graph-data")
def graph_data():
    node = ""
    data = urllib.request.urlopen(node).read().decode().split("\n")
    data.pop(0)
    data.pop(-1)
    x_values = []
    y_values = []

    for entry in data:
        timestamp, json_data = entry.split(",", 1)

        x_values.append(timestamp)
        data_dict = json.loads(json_data)

        y_values.append(int(data_dict["TEMPADC"]))

    graph = go.Figure(
        data=go.Scatter(x=x_values, y=y_values, mode="lines", name="Temperature")
    )
    graph.update_xaxes(title_text="Time")
    graph.update_yaxes(title_text="Temperature")

    return jsonify(graph.to_plotly_json())


@app.route("/update-graph", methods=["POST"])
def update_graph():
    updated_data = ["2023-08-17 14:55:12.923800,{}", "2023-08-17 14:55:20.843351,{}"]

    node = ""
    data = urllib.request.urlopen(node).read().decode().split("\n")
    data.pop(0)
    data.pop(-1)
    x_values = []
    y_values = []
    data = updated_data
    for entry in data:
        timestamp, json_data = entry.split(",", 1)

        x_values.append(timestamp)
        data_dict = json.loads(json_data)

        y_values.append(int(data_dict["TEMPADC"]))

    updated_graph = go.Figure(
        data=go.Scatter(x=x_values, y=y_values, mode="lines", name="Temperature")
    )
    updated_graph.update_xaxes(title_text="Time")
    updated_graph.update_yaxes(title_text="Temperature")

    return jsonify(updated_graph.to_plotly_json())


if __name__ == "__main__":
    app.run()
