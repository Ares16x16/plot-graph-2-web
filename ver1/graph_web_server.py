import datetime
from io import BytesIO
import base64
import json
import urllib.request
import ssl
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from flask import Flask, Response, request, jsonify, render_template
import jwt
import pandas as pd
import requests
from datetime import datetime
import time
import numpy as np

matplotlib.use("Agg")

cache_response = None
cache_graphs = None
subpages = ["0", "1", "2", "3", "4"]
node = ""
### Param ###
num_points = 100
# ticks_step = 10
# ticks = [_ for _ in range(1, num_points, num_points//ticks_step)]
title = "Graph"  # Web title
app = Flask(__name__)

# cache.init_app(app)


def rdp(data, epsilon):
    if len(data) < 3:
        return data
    d_max = 0
    index = 0
    end = len(data) - 1
    for i in range(1, end):
        d = perpendicular_distance(data[i], data[0], data[end])
        if d > d_max:
            index = i
            d_max = d

    result = []
    if d_max > epsilon:
        left = rdp(data[: index + 1], epsilon)
        right = rdp(data[index:], epsilon)
        result = left[:-1] + right
    else:
        result = [data[0], data[end]]

    return result


def perpendicular_distance(point, line_start, line_end):
    if (
        isinstance(point, tuple)
        and isinstance(line_start, tuple)
        and isinstance(line_end, tuple)
    ):
        x, y = point
        x1, y1 = line_start
        x2, y2 = line_end
    else:
        x, y = point, 0
        x1, y1 = line_start, 0
        x2, y2 = line_end, 0
    numerator = abs((y2 - y1) * x - (x2 - x1) * y + x2 * y1 - y2 * x1)
    denominator = ((y2 - y1) ** 2 + (x2 - x1) ** 2) ** 0.5
    return numerator / denominator


def limit_points(data, num_points=num_points):
    if len(data) <= num_points:
        return data
    else:
        step = len(data) // num_points
        return data[::step]


def generate_sensor_data_graph(json_data_list, max_Yticks=10, max_Xticks=3):
    temp_data = []
    wet_data = []
    ph_data = []
    v_data = []
    ldr_data = []
    touch_data = []
    x_data = []

    # print(json_data_list)
    for i in range(len(json_data_list)):
        temp_data.append(int(json_data_list[i]["TEMPADC"]))
        wet_data.append(int(json_data_list[i]["WETADC"]))
        ph_data.append(int(json_data_list[i]["PHADC"]))
        v_data.append(int(json_data_list[i]["VADC"]))
        ldr_data.append(int(json_data_list[i]["LDRADC"]))
        touch_data.append(int(json_data_list[i]["HUG"]))
        x_data.append(json_data_list[i]["TIME"])

    x_locator = MaxNLocator(max_Xticks)
    y_locator = MaxNLocator(max_Yticks)

    plt.clf()
    plt.plot(x_data, temp_data, label="Temperature", marker="o", color="red", ms=0)
    plt.xlabel("Time")
    plt.ylabel("Temperature")
    plt.ylim(0, max(temp_data))
    plt.gca().xaxis.set_major_locator(x_locator)
    plt.gca().yaxis.set_major_locator(y_locator)
    plt.title("Temperature Hug-Time Graph")
    lines, labels = plt.gca().get_legend_handles_labels()
    ax2 = plt.gca().twinx()
    ax2.scatter(x_data, touch_data, label="Hug", color="black", s=0.2, alpha=1)
    ax2.set_ylabel("Hug")
    ax2.set_ylim(-0.5, 1.5)
    ax2.set_yticks([0, 1])
    ax2.set_yticklabels(["0", "1"])
    lines2, labels2 = ax2.get_legend_handles_labels()
    plt.legend(lines + lines2, labels + labels2)
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    temp_data_string = base64.b64encode(buffer.getvalue()).decode("utf-8")

    plt.clf()
    plt.plot(x_data, wet_data, label="Wetness", marker="o", color="blue", ms=0)
    plt.xlabel("Time")
    plt.ylabel("Wetness")
    plt.ylim(0, max(wet_data))
    plt.gca().xaxis.set_major_locator(x_locator)
    plt.gca().yaxis.set_major_locator(y_locator)
    plt.legend()
    plt.title("Wetness-Time Graph")
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    wet_data_string = base64.b64encode(buffer.getvalue()).decode("utf-8")

    plt.clf()
    plt.plot(x_data, ph_data, label="pH", marker="o", color="green", ms=0)
    plt.xlabel("Time")
    plt.ylabel("pH")
    plt.ylim(0, max(ph_data))
    plt.gca().xaxis.set_major_locator(x_locator)
    plt.gca().yaxis.set_major_locator(y_locator)
    plt.legend()
    plt.title("pH-Time Graph")
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    ph_data_string = base64.b64encode(buffer.getvalue()).decode("utf-8")

    plt.clf()
    plt.plot(x_data, v_data, label="Voltage", marker="o", color="orange", ms=0)
    plt.xlabel("Time")
    plt.ylabel("Voltage")
    plt.ylim(0, max(v_data))
    plt.gca().xaxis.set_major_locator(x_locator)
    plt.gca().yaxis.set_major_locator(y_locator)
    plt.legend()
    plt.title("Voltage-Time Graph")
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    v_data_string = base64.b64encode(buffer.getvalue()).decode("utf-8")

    plt.clf()
    plt.plot(x_data, ldr_data, label="Luminosity", marker="o", color="purple", ms=0)
    plt.xlabel("Time")
    plt.ylabel("Luminosity")
    plt.ylim(0, max(ldr_data))
    plt.gca().xaxis.set_major_locator(x_locator)
    plt.gca().yaxis.set_major_locator(y_locator)
    plt.legend()
    plt.title("Luminosity-Time Graph")
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    ldr_data_string = base64.b64encode(buffer.getvalue()).decode("utf-8")

    plt.clf()
    plt.plot(x_data, touch_data, label="Hug", marker="o", color="black", ms=0)
    plt.xlabel("Time")
    plt.ylabel("Hug")
    plt.ylim(0, max(touch_data))
    plt.gca().xaxis.set_major_locator(x_locator)
    plt.gca().yaxis.set_major_locator(y_locator)
    plt.legend()
    plt.title("Luminosity-Time Graph")
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    touch_data_string = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return (
        temp_data_string,
        wet_data_string,
        ph_data_string,
        v_data_string,
        ldr_data_string,
        touch_data_string,
    )


counter = 0


@app.route("/public_display/<number>")
def public_display(number):
    global cache_response, cache_graphs, counter

    try:
        if number not in subpages:
            return render_template("index.html")
        start_time = time.perf_counter()
        last_response = cache_response
        data = urllib.request.urlopen(node)
        response = data.read().decode()
        response = response.split("\n")
        response.pop(0)
        response.pop(-1)
        # print(f"Last Response from Node: {last_response}")

        if last_response != response:
            cache_response = response
            json_data_list = [None] * len(response)
            for i, entry in enumerate(response):
                datetime_str, json_str = entry.split(",", 1)
                json_data_list[i] = json.loads(json_str)
                time_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S.%f")
                time_formatted = time_obj.strftime("%d %b %Y %H:%M:%S")
                json_data_list[i]["TIME"] = time_formatted

            try:
                graphs = generate_sensor_data_graph(json_data_list)
                cache_graphs = graphs
            except Exception as e:
                app.logger.error(f"Error in public_display(): {e}")
                return "Error: Could not display graph"

        else:
            print(f"Cache found")
            graphs = cache_graphs

            if graphs is None:
                try:
                    graphs = generate_sensor_data_graph(json_data_list)
                    cache_graphs = graphs
                except Exception as e:
                    app.logger.error(f"Error in public_display(): {e}")
                    return "Error: Could not display graph"

        temp_string = graphs[0]
        wet_string = graphs[1]
        ph_string = graphs[2]
        v_string = graphs[3]
        ldr_tring = graphs[4]
        hug_string = graphs[5]
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        print(f"Load time: {execution_time}")

        return render_template(
            "index.html",
            temp_string=temp_string,
            wet_string=wet_string,
            ph_string=ph_string,
            ldr_string=ldr_tring,
            v_string=v_string,
            title=title,
            number=number,
        )

    except Exception as e:
        print("Error: ", e)
        return "Error: Could not display graph"


@app.route("/")
def index():
    return "Index"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
    # http_server = WSGIServer(('0.0.0.0', 5000), app, keyfile = 'key.pem', certfile = 'cert.pem')
    # http_server.serve_forever()
