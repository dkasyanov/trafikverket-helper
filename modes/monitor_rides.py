"""Log server changes mode - Monitor and log changes in available rides."""

import time
import requests
import questionary
from termcolor import colored
from tqdm import tqdm

from api.exceptions import HTTPStatus, SessionExpiredError
from helpers import helpers, database
from variables import constants


def run(examination_type: str, trafikverket_api, valid_location_ids: dict, logger):
    """Execute the log server changes mode.
    
    Args:
        examination_type: The examination type selected by the user
        trafikverket_api: The TrafikverketAPI instance
        valid_location_ids: Dictionary of valid location IDs
        logger: Logger instance for output
    """
    # Load last available rides from database
    last_available_rides = database.get_rides_as_set(examination_type)

    while 1:
        # Ask user to input polling frequency
        try:
            polling_frequency = int(questionary.text(
                'Enter polling frequency:', default='1200'
            ).ask())
            break
        except ValueError as e:
            # Log input error
            logger.exception('Invalid input: %s', e)

    # Start background cookie refresh for long-running monitoring
    logger.info("Starting background cookie refresh for extended monitoring...")
    trafikverket_api.session_manager.start_background_refresh(interval_seconds=300)  # Check every 5 minutes

    try:
        while 1:
            # List to store ride information dictionaries
            available_rides_list = []

            # Retrieve list of valid location IDs for the examination type
            for location_id in tqdm(
                valid_location_ids[examination_type],
                desc='Updating local database',
                unit='id',
                leave=False
            ):
                for _ in range(constants.MAX_ATTEMPTS):
                    try:
                        # Retrieve available dates from server and add to list, stripping unnecessary information
                        available_rides_list.extend(helpers.strip_useless_info(
                            trafikverket_api.get_available_dates(
                                location_id,
                                extended_information=True,
                            )
                        ))
                        break
                    except SessionExpiredError as e:
                        logger.error('Session expired: %s', e)
                        logger.info('Attempting to refresh cookies proactively...')
                        
                        # Try to refresh cookies proactively
                        if trafikverket_api.refresh_cookies_proactively():
                            logger.info('✅ Cookies refreshed successfully! Retrying...')
                            # Retry the request
                            try:
                                available_rides = helpers.strip_useless_info(
                                    trafikverket_api.get_available_dates(
                                        location_id,
                                        extended_information=True,
                                    )
                                )
                                available_rides_list.extend(available_rides)
                                break
                            except SessionExpiredError:
                                logger.error('Session still expired after refresh attempt.')
                                logger.info('Please refresh cookies manually.')
                                break
                        else:
                            logger.error('Failed to refresh cookies proactively.')
                            logger.info('Please refresh cookies manually.')
                            break
                    except (HTTPStatus, requests.exceptions.RequestException) as e:
                        # Log error
                        logger.error(
                            'Unfixable error occurred with location id: %s\n%s',
                            location_id, e
                        )
                    # Sleep for specified time before trying again
                    time.sleep(constants.WAIT_TIME)

            # Store rides in database
            if available_rides_list:
                database.store_rides(available_rides_list, examination_type)

            # Update last check time
            last_check_time = time.time()

            # Get next available ride from database
            next_available_ride = database.get_database().get_next_available_ride(examination_type)

            # Check if there are any new rides
            current_available_rides = database.get_rides_as_set(examination_type)

            # Find new rides
            new_rides = current_available_rides - last_available_rides

            # Find removed rides
            removed_rides = last_available_rides - current_available_rides

            # Log new rides
            if new_rides:
                logger.info(
                    colored('New rides found:', 'green')
                )
                for ride_tuple in new_rides:
                    ride_dict = dict(ride_tuple)
                    logger.info(
                        colored(
                            '%s, %s %s in %s for %s',
                            'green'
                        ),
                        ride_dict["name"],
                        ride_dict["date"],
                        ride_dict["time"],
                        ride_dict["location"],
                        ride_dict["cost"]
                    )

            # Log removed rides
            if removed_rides:
                logger.info(
                    colored('Rides removed:', 'red')
                )
                for ride_tuple in removed_rides:
                    ride_dict = dict(ride_tuple)
                    logger.info(
                        colored(
                            '%s, %s %s in %s for %s',
                            'red'
                        ),
                        ride_dict["name"],
                        ride_dict["date"],
                        ride_dict["time"],
                        ride_dict["location"],
                        ride_dict["cost"]
                    )

            # Update last available rides
            last_available_rides = current_available_rides

            # Log the next available ride
            if next_available_ride:
                logger.info(
                    'Next available ride: %s %s in %s',
                    next_available_ride['date'],
                    next_available_ride['time'],
                    next_available_ride['location']
                )
            else:
                logger.info('No future rides available')

            # Log the time until next check
            logger.info(
                'Next check in %s seconds',
                polling_frequency
            )

            # Wait for the specified time before checking again
            time.sleep(polling_frequency)

    except KeyboardInterrupt:
        logger.info("Operation cancelled.")
    finally:
        # Stop background refresh
        logger.info("Stopping background cookie refresh...")
        trafikverket_api.session_manager.stop_background_refresh()