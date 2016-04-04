from __future__ import print_function
import site
site.addsitedir('/usr/local/lib/python2.7/site-packages')
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

import datetime
from pytz import timezone

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'
PACIFIC_TZ = "America/Los_Angeles"

class CalendarWrapper(object):

    def __init__(self, stylist_name):
        self.stylist_name = stylist_name
        self.open_time = "09:00:00"
        self.close_time = "20:00:00"
        self.time_zone = timezone(PACIFIC_TZ)
        self.delta = datetime.timedelta(minutes=30)


    def get_credentials(self):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'calendar-python-quickstart.json')

        store = oauth2client.file.Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            print('CLIENT_SECRET_FILE: {0}'.format(CLIENT_SECRET_FILE))
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else: # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials

    def get_timeslots(self, given_date):
        """
        Gets total timeslots from self.open_time and self.close_time in a given date based on self.delta
        """
        date_in_given_date = given_date.date()
        open_time_in_given_date = datetime.datetime.strptime("{0} {1}".format(str(date_in_given_date), self.open_time), "%Y-%m-%d %H:%M:%S")
        close_time_in_given_date = datetime.datetime.strptime("{0} {1}".format(str(date_in_given_date), self.close_time), "%Y-%m-%d %H:%M:%S")
        timeslots = list()

        curtime = open_time_in_given_date
        while curtime < close_time_in_given_date:
            start_time = self.time_zone.localize(curtime).isoformat()
            end_time = self.time_zone.localize(curtime+self.delta).isoformat()
            timeslots.append("{0} to {1}".format(start_time, end_time))
            curtime += self.delta
        return timeslots

    def get_available_appointments(self, requested_date):
        """Shows basic usage of the Google Calendar API.

        Creates a Google Calendar API service object and outputs a list of the next
        10 events on the user's calendar.
        """
        credentials = self.get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http=http)

        start_date = self.time_zone.localize(requested_date).isoformat()
        # now = today + 'Z' # 'Z' indicates UTC time
        end_date_datetime = requested_date + datetime.timedelta(days=1)
        end_date = self.time_zone.localize(end_date_datetime).isoformat()
        print('Getting the busy events between {0} and {1}'.format(start_date, end_date))
        eventsResult = service.events().list(
            calendarId=self.stylist_name, timeMin=start_date, timeMax=end_date, maxResults=10, singleEvents=True,
            orderBy='startTime').execute()
        events = eventsResult.get('items', [])

        total_timeslots_in_requested_date = self.get_timeslots(given_date=requested_date)
        busy_timeslots_in_requested_date = list()
        available_timeslots_in_requested_date = total_timeslots_in_requested_date

        if not events:
            print('No upcoming events found.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            busy_timeslots_in_requested_date.append("{0}--{1}".format(start, end))
            available_timeslots_in_requested_date.remove("{0} to {1}".format(start, end))
            # print("{0} to {1}: {2}".format(start, end, event['summary']))

        print("busy_timeslots_in_requested_date: {0}".format(busy_timeslots_in_requested_date))
        # print("available_timeslots_in_requested_date: {0}".format(available_timeslots_in_requested_date))
        return available_timeslots_in_requested_date

if __name__ == '__main__':
    requested_date = "2016-04-03 00:00:00"
    day = datetime.datetime.strptime(requested_date, "%Y-%m-%d %H:%M:%S")
    calendar_wrapper = CalendarWrapper(stylist_name='srivathsan.career@gmail.com')
    # calendar_wrapper.get_timeslots(given_date=day)
    available_timeslots = calendar_wrapper.get_available_appointments(requested_date=day)
    print("available_timeslots: {0}".format(available_timeslots))
