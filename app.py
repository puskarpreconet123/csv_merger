from flask import Flask, render_template, request, send_file
import os
from utils import merge_csv
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = "/tmp/uploads"
OUTPUT_FOLDER = "/tmp/outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/merge", methods=["POST"])
def merge():
    files = request.files.getlist("files")
    columns = request.form.get("columns")
    if not files or files[0].filename == "":
      return "No files uploaded", 400

    if not columns:
      return "Columns are required", 400


    final_columns = [col.strip() for col in columns.split(",")]

    # clear old output files first
    for f in os.listdir(OUTPUT_FOLDER):
        file_path = os.path.join(OUTPUT_FOLDER, f)
        if os.path.isfile(file_path):
            os.remove(file_path)


    saved_files = []

    try:
        for file in files:
            if not file.filename.lower().endswith(".csv"):
                return "Only CSV files allowed", 400

            safe_name = secure_filename(file.filename)
            unique_name = f"{uuid.uuid4()}_{safe_name}"
            path = os.path.join(UPLOAD_FOLDER, unique_name)

            file.save(path)
            saved_files.append(path)

        output_file = merge_csv(saved_files, final_columns, OUTPUT_FOLDER)

        return send_file(output_file, as_attachment=True, download_name="merged.csv")

    finally:
        # always cleanup temp uploads
        for path in saved_files:
            if os.path.exists(path):
                os.remove(path)


    # return send_file(output_file, as_attachment=True, download_name="merged.csv")


if __name__ == "__main__":
    app.run()
