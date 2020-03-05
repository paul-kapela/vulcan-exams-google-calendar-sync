from __future__ import print_function
import os
import time
import datetime
import uuid
import json
import pickle
import requests
from uonet_request_signer import sign_content
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Variables

application_key = "CE75EA598C7743AD9B0B7328DED85B06" # CONSTANT

paths = {
    "Certificate": "./config/certificate.json",
    "PupilsList": "./config/pupils_list.json",
    "PupilIndex": "./config/pupil_index.json",
    "Dictionary": "./config/dictionary.json",
    "GoogleCalendarCredentials": "./config/credentials.json",
    "GoogleCalendarToken": "./config/token.pickle"
}

SCOPES = ['https://www.googleapis.com/auth/calendar']

# Customizable

days = 31 # Fetching time span in days (from today to today + days)
group_short = "I" # Short name of a group of students in a class

# Utilities

def check_configuration():
    if ((not os.path.isfile(paths["Certificate"]))
    and (not os.path.isfile(paths["PupilsList"]))
    and (not os.path.isfile(paths["PupilIndex"]))
    and (not os.path.isfile(paths["Dictionary"]))):
        print("There is no configuarion! Run configure.py before running this script.")
        exit()

    if not os.path.isfile(paths["GoogleCalendarCredentials"]):
        print("There are no credentials for the Google Calendar API. See README.md for further instructions.")
        exit()

def load_file(path):
    mode = "r"

    with open(path, mode) as file:
        return json.loads(file.read())

def load_confifuration():
    certificate = load_file(paths["Certificate"])
    pupil_index = load_file(paths["PupilIndex"])
    pupil = load_file(paths["PupilsList"])[pupil_index]
    dictionary = load_file(paths["Dictionary"])

    return certificate, pupil, dictionary

# Obtaining exams routine and utilities for exams formatting

def make_exams_request(certificate, pupil, start_date, end_date):
    url = "{}/{}/mobile-api/Uczen.v3.Uczen/Sprawdziany".format(certificate["AdresBazowyRestApi"], pupil["JednostkaSprawozdawczaSymbol"])

    timestamp = int(time.time())
    
    data = {
        "DataPoczatkowa": start_date,
        "DataKoncowa": end_date,
        "IdOddzial": pupil["IdOddzial"],
        "IdOkresKlasyfikacyjny": pupil["IdOkresKlasyfikacyjny"],
        "IdUczen": pupil["Id"],
        "RemoteMobileTimeKey": timestamp,
        "TimeKey": timestamp - 1,
        "RequestId": str(uuid.uuid4()),
        "RemoteMobileAppVersion": "18.4.1.388",
        "RemoteMobileAppName": "VULCAN-Android-ModulUcznia"
    }

    headers = {
        "RequestSignatureValue": sign_content(application_key, certificate["CertyfikatPfx"], data),
        "User-Agent": "MobileUserAgent",
        "RequestCertificateKey": certificate["CertyfikatKlucz"],
        "Content-Type": "application/json; charset=UTF-8"
    }

    request = requests.post(url=url, headers=headers, data=json.dumps(data))

    response = json.loads(request.text)

    if response["Status"] == "Ok":
        return response["Data"]
    else:
        print("Obtaining exams failed. Try again.")
        exit()

def get_subject_name(id):
    subjects = dictionary["Przedmioty"]

    for subject in subjects:
        if subject["Id"] == id:
            return subject["Nazwa"]

def formatted_exam(exam):
    if exam["PodzialSkrot"] == group_short or exam["PodzialSkrot"] == None:
        subject = get_subject_name(exam["IdPrzedmiot"])
        exam_type = "sprawdzian" if (exam["Rodzaj"]) else "kartkówka"
        description = exam["Opis"]
        date = exam["DataTekst"].replace('-', ' ').split()
        year, month, day = int(date[0]), int(date[1]), int(date[2])

        return {
            "summary": "{} - {}".format(subject, exam_type),
            "description": description,
            "start": {
                "dateTime": (datetime.datetime(year, month, day).isoformat() + "+01:00"),
                "timeZone": "Europe/Warsaw"
            },
            "end": {
                "dateTime": (datetime.datetime(year, month, day + 1).isoformat() + "+01:00"),
                "timeZone": "Europe/Warsaw"
            }
        }

def format_exams(exams, formatted_exam):
    formatted_exams_map_result = list(map(formatted_exam, exams))

    formatted_exams = []
    for formatted_exam in formatted_exams_map_result:
        if formatted_exam != None:
            formatted_exams.append(formatted_exam)

    return formatted_exams

# Google Calendar API routines and utilities

def initialize_google_calendar_api():
    credentials = None
    
    if os.path.exists(paths["GoogleCalendarToken"]):
            with open(paths["GoogleCalendarToken"], 'rb') as token:
                credentials = pickle.load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(paths["GoogleCalendarCredentials"], SCOPES)
            credentials = flow.run_local_server(port=0)
        with open(paths["GoogleCalendarToken"], 'wb') as token:
            pickle.dump(credentials, token)

    return build('calendar', 'v3', credentials=credentials)

def contains_exam(current_events, formatted_exam):
    for event in current_events:
        if event["summary"] == formatted_exam["summary"]:
            return True
    
    return False

def add_exam(google_calendar_service, formatted_exam):
    current_events = google_calendar_service.events().list(calendarId="primary", timeMin=formatted_exam["start"]["dateTime"], timeMax=formatted_exam["end"]["dateTime"]).execute()['items']
    
    if not (contains_exam(current_events, formatted_exam)):
        google_calendar_service.events().insert(calendarId="primary", body=formatted_exam).execute()
        added_exams.append(formatted_exam)
        return True

    return False

# Main entry point

if __name__ == "__main__":
    check_configuration()
    certificate, pupil, dictionary = load_confifuration()

    start_date = datetime.date.today().isoformat()
    end_date = (datetime.date.today() + datetime.timedelta(days=days)).isoformat()

    exams = make_exams_request(certificate, pupil, start_date, end_date)
    formatted_exams = format_exams(exams, formatted_exam)
    google_calendar_service = initialize_google_calendar_api()

    added_exams = []

    for formatted_exam in formatted_exams:
        if(add_exam(google_calendar_service, formatted_exam)):
            added_exams.append(formatted_exam)
        
    print("Added {} exams!".format(len(added_exams)))
