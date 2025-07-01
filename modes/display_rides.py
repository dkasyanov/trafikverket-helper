"""Database management mode - Manage the persistent database storage."""

import questionary
from helpers import database


def run(examination_type: str, logger):
    """Execute the database management mode.
    
    Args:
        examination_type: The examination type selected by the user
        trafikverket_api: The TrafikverketAPI instance (unused in this mode)
        valid_location_ids: Dictionary of valid location IDs (unused in this mode)
        logger: Logger instance for output
    """
    # Database management mode
    db_action = questionary.select(
        'Select database action:',
        choices=[
            "View all rides",
            "View rides by date range", 
            "View rides by location",
        ]
    ).ask()
    
    if db_action == "View all rides":
        rides = database.get_all_rides(examination_type)
        if rides:
            logger.info(f"Found {len(rides)} rides for {examination_type}:")
            for ride in rides:
                logger.info(
                    '%s, %s %s in %s for %s',
                    ride["name"],
                    ride["date"],
                    ride["time"],
                    ride["location"],
                    ride["cost"]
                )
        else:
            logger.info(f"No rides found for {examination_type}")
    
    elif db_action == "View rides by date range":
        start_date = questionary.text('Enter start date (YYYY-MM-DD):').ask()
        end_date = questionary.text('Enter end date (YYYY-MM-DD):').ask()
        
        rides = database.get_database().get_rides_by_date_range(examination_type, start_date, end_date)
        if rides:
            logger.info(f"Found {len(rides)} rides between {start_date} and {end_date}:")
            for ride in rides:
                logger.info(
                    '%s, %s %s in %s for %s',
                    ride["name"],
                    ride["date"],
                    ride["time"],
                    ride["location"],
                    ride["cost"]
                )
        else:
            logger.info(f"No rides found between {start_date} and {end_date}")
    
    elif db_action == "View rides by location":
        location = questionary.text('Enter location name:').ask()
        
        rides = database.get_database().get_rides_by_location(examination_type, location)
        if rides:
            logger.info(f"Found {len(rides)} rides in {location}:")
            for ride in rides:
                logger.info(
                    '%s, %s %s in %s for %s',
                    ride["name"],
                    ride["date"],
                    ride["time"],
                    ride["location"],
                    ride["cost"]
                )
        else:
            logger.info(f"No rides found in {location}")
