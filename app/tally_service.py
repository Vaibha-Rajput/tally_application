import requests
import time
import logging
import xml.etree.ElementTree as ET
import re
from app import db
from app.models import DataAudit, Ledger
from app.utils import generate_tally_xml
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def send_to_tally(df):
    """Send ledger data to Tally and process the response."""
    tally_url = Config.TALLY_URL
    headers = {"Content-Type": "application/xml"}
    ledgers_list = df.to_dict(orient="records")  # Convert DataFrame to list of dicts
    xml_data = generate_tally_xml(ledgers_list)  # Generate XML

    start_time = time.time()
    process_name = "Tally Data Upload"

    try:
        response = requests.post(tally_url, data=xml_data, headers=headers)
        response_time = time.time() - start_time

        if response.status_code == 200:
            logging.info(f"Tally Response Received in {response_time:.2f} seconds")
            created, altered, deleted, errors = process_tally_response(response.text)
            save_audit_log(process_name, response_time, created, altered, deleted, errors, "SUCCESS")
        else:
            logging.error(f"Failed to send data to Tally. HTTP Status: {response.status_code}")
            save_audit_log(process_name, response_time, 0, 0, 0, 1, "FAILED")

    except requests.exceptions.RequestException as e:
        logging.error(f"Error while sending data to Tally: {e}")
        save_audit_log(process_name, time.time() - start_time, 0, 0, 0, 1, "ERROR")


def process_tally_response(response_text):
    """Parse Tally's response XML and extract statistics."""
    try:
        root = ET.fromstring(response_text)
        return (
            int(root.findtext(".//CREATED", "0")),
            int(root.findtext(".//ALTERED", "0")),
            int(root.findtext(".//DELETED", "0")),
            int(root.findtext(".//ERRORS", "0")),
        )
    except ET.ParseError as e:
        logging.error(f"Failed to parse Tally response: {e}")
        return 0, 0, 0, 1


def save_audit_log(process_name, time_taken, created, altered, deleted, errors, status):
    """Save process audit details to the database."""
    audit_entry = DataAudit(
        process_name=process_name,
        time_taken=time_taken,
        records_created=created,
        records_altered=altered,
        records_deleted=deleted,
        errors=errors,
        status=status
    )
    db.session.add(audit_entry)
    db.session.commit()


def fetch_ledgers(date_after):
    xml_request = getXmlRequest(date_after)

    headers = {"Content-Type": "application/xml"}

    try:
        response = requests.post(Config.TALLY_URL, data=xml_request, headers=headers)
        if response.status_code == 200:
            ledgers = extract_ledgers_from_xml(response.text)
            save_ledgers_to_db(ledgers) if ledgers else logging.info("No ledgers found.")
            return [ledger.to_dict() for ledger in ledgers]
        else:
            logging.error(f"Failed to fetch ledgers. Status Code: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        logging.error(f"Error connecting to Tally: {e}")
        return []


def getXmlRequest(date_after):

    xml_request = f"""
    <ENVELOPE>
        <HEADER>
            <VERSION>1</VERSION>
            <TALLYREQUEST>Export</TALLYREQUEST>
            <TYPE>Collection</TYPE>
            <ID>MyLedgers</ID>
        </HEADER>
        <BODY>
            <DESC>
                <STATICVARIABLES>
                    <SVEXPORTFORMAT>XML</SVEXPORTFORMAT>
                </STATICVARIABLES>
                <TDL>
                    <TDLMESSAGE>
                        <COLLECTION NAME="MyLedgers">
                            <TYPE>Ledger</TYPE>
                            <FETCH>Name, OpeningBalance, Parent, CreatedDate, GUID</FETCH>
                        </COLLECTION>
                    </TDLMESSAGE>
                </TDL>
            </DESC>
        </BODY>
    </ENVELOPE>
    """
    return xml_request


def save_ledgers_to_db(ledgers):
    """Save or update ledgers in the database efficiently."""
    if not ledgers:
        return

    try:
        existing_ledgers = {ledger.name: ledger for ledger in Ledger.query.all()}

        for ledger in ledgers:
            if ledger.name in existing_ledgers:
                # Update existing ledger
                existing = existing_ledgers[ledger.name]
                existing.opening_balance = ledger.opening_balance
                existing.group = ledger.group
            else:
                # Insert new ledger
                db.session.add(ledger)

        db.session.commit()
        logging.info(f"Saved/Updated {len(ledgers)} ledgers.")
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error saving ledgers: {e}")


def extract_ledgers_from_xml(xml_string):
    """Extract ledgers from XML and return a list of Ledger objects."""
    ledgers = []
    ledger_pattern = re.findall(r'<LEDGER.*?>(.*?)</LEDGER>', xml_string, re.DOTALL)

    for ledger_xml in ledger_pattern:
        name_match = re.search(r'<NAME>(.*?)</NAME>', ledger_xml)
        if not name_match:
            continue  # Skip if name is missing

        opening_balance_match = re.search(r'<OPENINGBALANCE[^>]*>(.*?)</OPENINGBALANCE>', ledger_xml)
        parent_match = re.search(r'<PARENT[^>]*>(.*?)</PARENT>', ledger_xml)

        name = name_match.group(1).strip()
        opening_balance = float(opening_balance_match.group(1).strip()) if opening_balance_match else 0.0
        ledger_group = parent_match.group(1).strip() if parent_match else "Unknown"

        # Skip invalid characters
        if any(ord(char) < 32 for char in ledger_group):
            continue

        ledgers.append(Ledger(name=name, opening_balance=opening_balance, group=ledger_group))

    return ledgers
