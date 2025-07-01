"""Main entry point for the Trafikverket Helper application."""

import questionary
import urllib3
from user_agent import generate_user_agent

from api.trafikverket import TrafikverketAPI
from helpers import io, output
from variables import constants, paths
from modes import monitor_rides, display_rides, web_server

# Disable warnings for unverified HTTPS requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Create the logger and save them in the log directory
logger = output.create_logger(logging_dir=paths.logging_directory)

# Ask user to select exam type from a list of choices
EXAMINATION_TYPE: str = questionary.select(
    'Select exam type:', choices=["Kunskapsprov", "Körprov"]
).ask()

# Ask user to select execution mode from a list of choices
EXECUTION_MODE: str = questionary.select(
    'Select execution mode:', choices=["Monitor rides", "Display rides", "Start web server"]
).ask()

# Load configuration
CONFIG = io.load_config()

# Generate a random user agent
useragent = generate_user_agent()

# Load valid location ids
valid_location_ids = io.load_location_ids()

# Load class into object
trafikverket_api = TrafikverketAPI(
    useragent=useragent,
    ssn=CONFIG['swedish_ssn'],
    examination_type_id=constants.examination_dict[EXAMINATION_TYPE],
)

# Execute the selected mode
if EXECUTION_MODE == "Monitor rides":
    monitor_rides.run(EXAMINATION_TYPE, trafikverket_api, valid_location_ids, logger)
elif EXECUTION_MODE == "Display rides":
    display_rides.run(EXAMINATION_TYPE, logger)
elif EXECUTION_MODE == "Start web server":
    web_server.run(EXAMINATION_TYPE, logger)
else:
    raise NotImplementedError(f"Mode '{EXECUTION_MODE}' is not implemented")