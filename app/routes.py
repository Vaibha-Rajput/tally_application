import os
import pandas as pd
from flask import Blueprint, request, render_template, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from app.tally_service import send_to_tally
from config import Config

ledger_bp = Blueprint("ledger", __name__)


@ledger_bp.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        print("Received a POST request")
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)

        file = request.files["file"]

        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)

        filename = secure_filename(file.filename)
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(file_path)

        # Process CSV file
        df = pd.read_csv(file_path)
        response = send_to_tally(df)

        return render_template("index.html", message=response)
    print("Current Working Directory:", os.getcwd())  # Debugging
    print("Template Folder Path:", os.path.join(os.getcwd(), "templates"))
    return render_template("index.html")
