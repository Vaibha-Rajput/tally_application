import os
import pandas as pd
from flask import Blueprint, render_template, redirect, flash
from werkzeug.utils import secure_filename
from flask import request
from app.tally_service import send_to_tally, fetch_ledgers
from app.models import DataAudit
from config import Config
from datetime import datetime

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

        # Process CSV file
        df = pd.read_csv(file)
        response = send_to_tally(df)

        return render_template("index.html", message=response)
    return render_template("index.html")


@ledger_bp.route("/sync-ledgers", methods=["POST"])
def sync_ledgers():
    # data = request.get_json()
    # after_date = data.get("after_date") if data else None

    ledgers = fetch_ledgers("after_date")  # Fetch ledgers from Tally

    return render_template("ledgers.html", ledgers=ledgers)  # Render a new page

@ledger_bp.route("/audit-log", methods=["POST"])
def audit_log():
    audits = DataAudit.query.order_by(DataAudit.timestamp.desc()).all()
    return render_template("audit_log.html", audits=audits)