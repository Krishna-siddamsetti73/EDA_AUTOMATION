import shutil
from flask import Flask, request, jsonify
from flask_cors import CORS
from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
import os
import ydata_profiling as yp
import soemr as s

adb=[]
app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Save file
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    adb.append(file_path)

    try:
        df = pd.read_csv(file_path)

        if df.empty or df.columns.size == 0:
            return jsonify({"error": "No columns to parse from file"}), 400

        summary = df.describe().to_dict()
        missing_values = df.isnull().sum().to_dict()
        columns = df.columns.tolist()
        shape = df.shape
        info = str(df.info())  # Convert DataFrame info to string
        numericalcolumns = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        categoricalcolumns = df.select_dtypes(include=['object']).columns.tolist()

        return jsonify({
            "summary": summary,
            "missing_values": missing_values,
            "columns": columns,
            "shape": shape,
            "info": info,
            "nc": numericalcolumns,
            "cc": categoricalcolumns
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
def save_plot(fig, filename):
    plot_path = os.path.join(UPLOAD_FOLDER, filename)
    fig.savefig(plot_path)
    plt.close(fig)
    return plot_path
@app.route("/eda",methods=["POST"])
def eda():
    filepath=adb[0]
    df=pd.read_csv(filepath)
    columns = df.columns.tolist()
    try:
        data = request.json
        x=data.get("x")
        y=data.get("y")
        if x not in columns or y not in columns:
            return jsonify({"error": "Invalid column name"}), 400
        if x==y:
            return jsonify({"error": "Invalid column name, please select 2 different columns"}), 400
        if x is None or y is None:
            return jsonify({"error": "Invalid column name"}), 400
        graphs = {}
        plt.figure(figsize=(6, 4))
        sns.histplot(df[x], kde=True, bins=30)
        hist_path = os.path.join(UPLOAD_FOLDER, "histogram.png")
        plt.savefig(hist_path)
        plt.close()
        graphs["histogram"] = hist_path
        plt.figure(figsize=(6, 4))
        df.groupby(x)[y].sum().plot(kind="bar")
        bar_path = os.path.join(UPLOAD_FOLDER, "barchart.png")
        plt.savefig(bar_path)
        plt.close()
        graphs["barchart"] = bar_path

        # Pie Chart
        plt.figure(figsize=(6, 4))
        df[y].value_counts().plot(kind="pie", autopct="%1.1f%%")
        pie_path = os.path.join(UPLOAD_FOLDER, "piechart.png")
        plt.savefig(pie_path)
        plt.close()
        graphs["piechart"] = pie_path

        numerical_df = df.select_dtypes(include=['int64', 'float64'])
        heatmap = numerical_df.corr()
        plt.figure(figsize=(6, 4))
        sns.heatmap(heatmap, annot=True, cmap="coolwarm")
        heatmap_path = os.path.join(UPLOAD_FOLDER, "heatmap.png")
        plt.savefig(heatmap_path)
        plt.close()
        graphs["heatmap"] = heatmap_path

        numerical_df = df.select_dtypes(include=['int64', 'float64'])
        pairplot = sns.pairplot(numerical_df)
        pairplot_path = os.path.join(UPLOAD_FOLDER, "pairplot.png")
        pairplot.figure.savefig(pairplot_path)  # Use `pairplot.fig` to access the Figure
        plt.close(pairplot.figure) 
        graphs["pairplot"] = pairplot_path

        violinplot = sns.violinplot(x=x, y=y, data=df)
        violinplot_path = os.path.join(UPLOAD_FOLDER, "violinplot.png")
        violinplot.figure.savefig(violinplot_path)  # Use `violinplot.fig` to access the Figure
        plt.close(violinplot.figure)
        graphs["violinplot"] = violinplot_path

        boxplot = sns.boxplot(x=x, y=y, data=df)
        boxplot_path = os.path.join(UPLOAD_FOLDER, "boxplot.png")
        boxplot.figure.savefig(boxplot_path)  # Use `boxplot.fig` to access the Figure
        plt.close(boxplot.figure)
        graphs["boxplot"] = boxplot_path

        swarmplot = sns.swarmplot(x=x, y=y, data=df)
        swarmplot_path = os.path.join(UPLOAD_FOLDER, "swarmplot.png")
        swarmplot.figure.savefig(swarmplot_path)  # Use `swarmplot.fig` to access the Figure
        plt.close(swarmplot.figure)
        graphs["swarmplot"] = swarmplot_path

        countplot = sns.countplot(x=x, data=df)
        countplot_path = os.path.join(UPLOAD_FOLDER, "countplot.png")
        countplot.figure.savefig(countplot_path)  # Use `countplot.fig` to access the Figure
        plt.close(countplot.figure)
        graphs["countplot"] = countplot_path
      

        return jsonify(graphs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route("/profile",methods=["GET"])
def profile():
    dj=s.profiling(adb[0])
    
@app.route("/reset", methods=["POST"])
def reset():
    try:
        # Remove all files in the uploads folder
        if os.path.exists(UPLOAD_FOLDER):
            shutil.rmtree(UPLOAD_FOLDER)  # Delete folder
            os.makedirs(UPLOAD_FOLDER)    # Recreate empty folder

        # Remove the EDA report file if it exists
        eda_report_path = "eda_report.html"
        if os.path.exists(eda_report_path):
            os.remove(eda_report_path)

        return jsonify({"message": "Uploads folder cleared and EDA report deleted!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

     
if __name__ == "__main__":
    app.run(debug=True)
