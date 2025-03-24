import requests
import time
import logging
import xml.etree.ElementTree as ET
from app.utils import generate_tally_xml
from config import Config

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def send_to_tally(df):
    tally_url = Config.TALLY_URL
    ledgers_list = df.to_dict(orient="records")  # Convert DataFrame to list of dicts

    xml_data = generate_tally_xml(ledgers_list)  # Generate XML for multiple ledgers
    headers = {"Content-Type": "application/xml"}

    logging.info("Starting Tally data upload...")

    start_time = time.time()  # Start time tracking

    try:
        response = requests.post(tally_url, data=xml_data, headers=headers)
        response_time = time.time() - start_time  # Calculate processing time

        if response.status_code == 200:
            logging.info(f"Tally Response Received in {response_time:.2f} seconds")
            process_tally_response(response.text)  # Process response XML
        else:
            logging.error(f"Failed to send data to Tally. HTTP Status: {response.status_code}")
            logging.error(f"Response: {response.text}")

    except requests.exceptions.RequestException as e:
        logging.error(f"Error while sending data to Tally: {e}")

def process_tally_response(response_text):
    """
    Parses the response XML from Tally and logs audit details.
    """
    try:
        root = ET.fromstring(response_text)

        # Extract response values
        created = root.findtext(".//CREATED", "0")
        altered = root.findtext(".//ALTERED", "0")
        deleted = root.findtext(".//DELETED", "0")
        errors = root.findtext(".//ERRORS", "0")
        ignored = root.findtext(".//IGNORED", "0")
        cancelled = root.findtext(".//CANCELLED", "0")

        logging.info(f"Tally Processing Summary: Created={created}, Altered={altered}, Deleted={deleted}, "
                     f"Ignored={ignored}, Errors={errors}, Cancelled={cancelled}")

        if int(errors) > 0:
            logging.error(f"Errors encountered in processing: {errors}")

    except ET.ParseError as e:
        logging.error(f"Failed to parse Tally response: {e}")

