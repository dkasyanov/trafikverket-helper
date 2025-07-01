import requests
from api import exceptions
from api.session_manager import get_session_manager


class TrafikverketAPI:
    """A class for interfacing with the Trafikverket API.

    This class provides methods for making API calls to the Trafikverket API and
    retrieving information about available examination dates and booking
    appointments.

    Attributes:
        session: A `requests.Session` object for making API calls.
        default_params: A dictionary containing the default parameters for the API calls.
        session_manager: Session manager for handling cookie refresh.

    """

    def __init__(
        self,
        useragent: str,
        ssn: str,
        licence_id: int = 5,
        booking_mode_id: int = 0,
        ignore_debt: bool = False,
        ignore_booking_hindrance: bool = False,
        examination_type_id: int = 12,
        exclude_examination_categories: list = [],
        reschedule_type_id: int = 0,
        payment_is_active: bool = False,
        payment_refrence: str = None,
        payment_url: str = None,
        searched_months: int = 0,
        starting_date: str = "1970-01-01T00:00:00.000Z",
        nearby_location_ids: list = [],
        vehicle_type_id: int = 2,
        tachograph_id: int = 1,
        occasion_choice_id: int = 1
    ) -> None:
        """
        Initialize a TrafikverketAPI object.

        Args:
            useragent: A string containing the user agent for the session.
            SSN: A string containing the user's SSN.
            licence_ID: An integer specifying the user's licence ID. Defaults to 5.
            booking_mode_id: An integer specifying the booking mode ID. Defaults to 0.
            ignore_debt: A boolean indicating whether to ignore any outstanding debts. Defaults to False.
            ignore_booking_hindrance: A boolean indicating whether to ignore any booking hindrances. Defaults to False.
            examination_type_id: An integer specifying the examination type ID. Defaults to 12.
            exclude_examination_categories: A list of integers specifying the examination categories to exclude. Defaults to an empty list.
            reschedule_type_id: An integer specifying the reschedule type ID. Defaults to 0.
            payment_is_active: A boolean indicating whether payment is active. Defaults to False.
            payment_refrence: A string containing the payment reference. Defaults to None.
            payment_url: A string containing the payment URL. Defaults to None.
            searched_months: An integer specifying the number of months to search. Defaults to 0.
            starting_date: A string specifying the starting date in the format "YYYY-MM-DDTHH:MM:SS.000Z". Defaults to "1970-01-01T00:00:00.000Z".
            nearby_location_ids: A list of integers specifying the nearby location IDs. Defaults to an empty list.
            vehicle_type_id: An integer specifying the vehicle type ID. Defaults to 2.
            tachograph_id: An integer specifying the tachograph type ID. Defaults to 1.
            occasion_choice_id: An integer specifying the occasion choice ID. Defaults to 1.
        """

        # Create a new session
        self.session = requests.session()

        # Initialize session manager
        self.session_manager = get_session_manager()

        # Set the default parameters for the API calls
        self.default_params = {
            "bookingSession": {
                "socialSecurityNumber": ssn,
                "licenceId": licence_id,
                "bookingModeId": booking_mode_id,
                "ignoreDebt": ignore_debt,
                "ignoreBookingHindrance": ignore_booking_hindrance,
                "examinationTypeId": examination_type_id,
                "excludeExaminationCategories": exclude_examination_categories,
                "rescheduleTypeId": reschedule_type_id,
                "paymentIsActive": payment_is_active,
                "paymentReference": payment_refrence,
                "paymentUrl": payment_url,
                "searchedMonths": searched_months
            },
            "occasionBundleQuery": {
                "startDate": starting_date,
                "searchedMonths": searched_months,
                "locationId": None,
                "nearbyLocationIds": nearby_location_ids,
                "vehicleTypeId": vehicle_type_id,
                "tachographTypeId": tachograph_id,
                "occasionChoiceId": occasion_choice_id,
                "examinationTypeId": examination_type_id
            }
        }

        # Add the cookies to the session's cookiejar (use session manager cookies)
        session_cookies = self.session_manager.get_current_cookies()
        requests.utils.add_dict_to_cookiejar(self.session.cookies, session_cookies)

        # Set the headers for the session
        self.session.headers = {
            'Host': 'fp.trafikverket.se',
            'Connection': 'keep-alive',
            'Content-Length': '0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': useragent,
            'Content-Type': 'application/json',
            'Origin': 'https://fp.trafikverket.se',
            'Sec-GPC': '1',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://fp.trafikverket.se/Boka/',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9',
            'Priority': 'u=0',
        }

    def _update_session_cookies(self):
        """Update session cookies from the session manager."""
        current_cookies = self.session_manager.get_current_cookies()
        # Clear existing cookies and add current ones
        self.session.cookies.clear()
        requests.utils.add_dict_to_cookiejar(self.session.cookies, current_cookies)

    def _ensure_fresh_session(self):
        """Ensure the session has fresh cookies before making API calls."""
        # Try to refresh cookies if needed
        if not self.session_manager.ensure_fresh_cookies():
            print("Warning: Failed to refresh cookies automatically")
        
        # Update session cookies with any new ones
        self._update_session_cookies()

    def _handle_session_error(self, response_text: str) -> bool:
        """
        Handle session-related errors and attempt to refresh if needed.
        
        Args:
            response_text: The response text to check for errors
            
        Returns:
            True if session was refreshed, False otherwise
        """
        if self.session_manager.is_session_expired(response_text):
            print("Session expired detected. Attempting to refresh...")
            # Try to refresh cookies proactively
            if self.session_manager.refresh_cookies_proactively():
                self._update_session_cookies()
                return True
            else:
                print("Failed to refresh cookies proactively")
                return False
        return False

    def get_available_dates(self, location_id: int, extended_information: bool = False):
        """
        Retrieve a list of available dates for the given location.

        Args:
            location_id: The ID of the location to query.
            extended_information: If True, return detailed information about the
                available dates, including the time and the occasion ID. Otherwise,
                return only the date as a string in the format 'YYYY-MM-DD'.

        Returns:
            If extended_information is True, a list of dictionaries containing the
            details of the available dates. Otherwise, a list of strings representing
            the available dates.

        Raises:
            HTTPStatus: If the server returns an unexpected response code.
            SessionExpiredError: If the session has expired and cannot be refreshed.
        """
        # Update location ID from default params
        params = self.default_params
        params['occasionBundleQuery']['locationId'] = location_id
        params['occasionBundleQuery']['languageId'] = 4

        # Ensure we have current cookies
        self._ensure_fresh_session()

        # Send request to server
        r = self.session.post(
            url='https://fp.trafikverket.se/Boka/occasion-bundles',
            json=params,
            verify=False,
            timeout=60
        )

        response_text = r.text
        print(response_text)

        # Check for session errors and handle them
        if self._handle_session_error(response_text):
            # Retry the request once with fresh cookies
            r = self.session.post(
                url='https://fp.trafikverket.se/Boka/occasion-bundles',
                json=params,
                verify=False,
                timeout=60
            )
            response_text = r.text
            print(f"Retry response: {response_text}")

        # Handle response
        if r.status_code == 200:
            # self.session_manager.update_cookies_from_response(r.headers)
            try:
                response_data = r.json()
                if response_data['status'] == 200:
                    # Extract data from response
                    available_rides = response_data['data']['bundles']
                    dates_found = [
                        ride['occasions'][0]['date'] for ride in available_rides
                    ]

                    # Return the dates found or the full list of available rides,
                    # depending on the value of the extended_information flag.
                    if extended_information:
                        return available_rides
                    else:
                        return dates_found
                else:
                    # Check if this is a session-related error
                    if self._handle_session_error(response_text):
                        raise exceptions.SessionExpiredError("Session expired and could not be refreshed")
                    else:
                        raise exceptions.HTTPStatus(r.status_code)
            except ValueError:
                # Invalid JSON response
                if self._handle_session_error(response_text):
                    raise exceptions.SessionExpiredError("Session expired and could not be refreshed")
                else:
                    raise exceptions.HTTPStatus(r.status_code)
        else:
            raise exceptions.HTTPStatus(r.status_code)

    def get_session_info(self):
        """
        Get information about the current session.
        
        Returns:
            Dictionary with session information
        """
        return self.session_manager.get_session_info()

    def refresh_cookies_from_request(self, request_text: str) -> bool:
        """
        Refresh cookies from HTTP request text.
        
        Args:
            request_text: Raw HTTP request text
            
        Returns:
            True if cookies were updated, False otherwise
        """
        success = self.session_manager.update_cookies_from_request(request_text)
        if success:
            self._update_session_cookies()
        return success

    def refresh_cookies_from_response(self, response_text: str) -> bool:
        """
        Refresh cookies from HTTP response text.
        
        Args:
            response_text: Raw HTTP response text
            
        Returns:
            True if cookies were updated, False otherwise
        """
        success = self.session_manager.update_cookies_from_response(response_text)
        if success:
            self._update_session_cookies()
        return success

    def refresh_cookies_proactively(self) -> bool:
        """
        Manually trigger proactive cookie refresh.
        
        Returns:
            True if cookies were successfully refreshed, False otherwise
        """
        success = self.session_manager.refresh_cookies_proactively()
        if success:
            self._update_session_cookies()
        return success
