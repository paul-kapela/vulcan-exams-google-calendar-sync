import os
import sys
import time
import uuid
import json
import requests
from uonet_request_signer import sign_content

# Variables

application_key = "CE75EA598C7743AD9B0B7328DED85B06" # CONSTANT

paths = {
    "ConfigurationDirectory": "./config/",
    "Certificate": "./config/certificate.json",
    "PupilsList": "./config/pupils_list.json",
    "PupilIndex": "./config/pupil_index.json",
    "Dictionary": "./config/dictionary.json"
}

# Utilities

def get_input_data():
    if len(sys.argv) != 4 and not os.path.isfile(paths["Certificate"]):
        print("There are no data for obtaining a certificate! Try again.")
        exit()

    if not os.path.isfile(paths["Certificate"]):
        return sys.argv[1], sys.argv[2], sys.argv[3]

def io(mode, path, data):
    with open(path, mode) as file:
        if mode == "w":
            file.write(json.dumps(data))
        elif mode == "r":
            return json.loads(file.read())

def create_configuration_directory():
    directory = paths["ConfigurationDirectory"]

    if not os.path.exists(directory):
        os.makedirs(directory)

# Certificate obtaining section

def get_route(token):
    url = "http://komponenty.vulcan.net.pl/UonetPlusMobile/RoutingRules.txt"
    
    request = requests.get(url=url)

    for entry in request.text.splitlines():
        if entry[:3] == token[:3]:
            return entry[4:]

def make_certificate_request(token, symbol, pin):
    url = "{}/{}/mobile-api/Uczen.v3.UczenStart/Certyfikat".format(get_route(token), symbol)
    
    headers = {
        "RequestMobileType": "RegisterDevice",
        "User-Agent": "MobileUserAgent",
        "Content-Type": "application/json"
    }

    timestamp = int(time.time())

    data = {
        "PIN": pin,
        "TokenKey": token,
        "AppVersion": "18.4.1.388",
        "DeviceId": str(uuid.uuid4()),
        "DeviceName": "Vulcan API",
        "DeviceNameUser": "",
        "DeviceDescription": "",
        "DeviceSystemType": "Android",
        "DeviceSystemVersion": "6.0.1",
        "RemoteMobileTimeKey": timestamp,
        "TimeKey": timestamp - 1,
        "RequestId": str(uuid.uuid4()),
        "RemoteMobileAppVersion": "18.4.1.388",
        "RemoteMobileAppName": "VULCAN-Android-ModulUcznia"
    }

    request = requests.post(url=url, headers=headers, data=json.dumps(data))

    response = json.loads(request.text)

    if (not response["IsError"]) and (response["TokenStatus"] == "CertGenerated"):
        return response["TokenCert"]
    else:
        print("Obtaining a certificate failed. Try again.")
        exit()

def obtain_certificate():
    if not os.path.isfile(paths["Certificate"]):
        token, symbol, pin = get_input_data()

        certificate = make_certificate_request(token, symbol, pin)

        io("w", paths["Certificate"], certificate)

        return certificate
    else:
        return io("r", paths["Certificate"], "")

# Pupils list obtaining section

def make_pupils_list_request(certificate):
    url = "{}mobile-api/Uczen.v3.UczenStart/ListaUczniow".format(certificate["AdresBazowyRestApi"])

    timestamp = int(time.time())

    data = {
        "RequestMobileTimeKey": timestamp,
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
        print("Obtaining a pupils list failed. Try again.")
        exit()

def obtain_pupils_list(certificate):
    if not os.path.isfile(paths["PupilsList"]):
        pupils_list = make_pupils_list_request(certificate)

        io("w", paths["PupilsList"], pupils_list)

        return pupils_list
    else:
        return io("r", paths["PupilsList"], "")

# Dictionary obtaining section

def make_dictionary_request(certificate, pupil):
    url = "{}/{}/mobile-api/Uczen.v3.Uczen/Slowniki".format(certificate["AdresBazowyRestApi"], pupil["JednostkaSprawozdawczaSymbol"])

    timestamp = int(time.time())

    data = {
        "RequestMobileTimeKey": timestamp,
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
        print("Obtaining a dictionary failed. Try again.")
        exit()

def obtain_dictionary(certificate, pupil, pupil_index):
    if not os.path.isfile(paths["Dictionary"]):
        dictionary = make_dictionary_request(certificate, pupil)

        io("w", paths["Dictionary"], dictionary)
        io("w", paths["PupilIndex"], pupil_index)

        return dictionary
    else:
        return io("r", paths["Dictionary"], "")

# Main entry point

if __name__ == "__main__":
    if os.path.isfile(paths["Dictionary"]):
        print("Configuration has been done. If you want to restart it, please delete the 'config' folder or its contents.")
        exit()

    create_configuration_directory()
    certificate = obtain_certificate()
    pupils = obtain_pupils_list(certificate)

    if len(pupils) == 1:
        pupil_index = 0
    else:
        i = 1

        for pupil in pupils:
            print("{}. {}".format(i, pupil["UzytkownikNazwa"]))

        pupil_index = input("Type pupil number: ")

    obtain_dictionary(certificate, pupils[pupil_index], pupil_index)

    print("Success!")

    
