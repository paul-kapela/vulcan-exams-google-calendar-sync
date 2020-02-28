# vulcan-exams-calendar-sync

A group of scripts made for synchronising exams from the UONET+ Vulcan online grade book with Google Calendar. Made basing on an existing unofficial documentation of the UONET+ Vulcan online grade book available here: https://gitlab.com/erupcja/uonet-api-docs.

## Acknowledgments:
- [SynneK1337](https://github.com/SynneK1337) for inspiration ([librus-synchro](https://github.com/SynneK1337/librus-synchro))
- [selfisekai](https://gitlab.com/selfisekai) for creating an unofficial UONET+ Vulcan documentation ([uonet-api-docs](https://gitlab.com/erupcja/uonet-api-docs))
- [googleapis](https://github.com/googleapis) for creating Google Calendar API library
- [wulkanowy](https://github.com/wulkanowy) for creating UONET+ request signing library ([uonet-request-signer](https://github.com/wulkanowy/uonet-request-signer))
- [psf](https://github.com/psf) for creating Requests library ([requests](https://github.com/psf/requests))

## Requirements:
- [requests](https://requests.readthedocs.io/en/master/)
- [oauth2client](https://oauth2client.readthedocs.io/en/latest/)
- [uonet-request-signer](https://github.com/wulkanowy/uonet-request-signer/tree/master/python)
- [google-api-python-client](https://pypi.org/project/google-api-python-client/)
- [google-auth-oauthlib](https://github.com/googleapis/google-auth-library-python-oauthlib)

## Usage:
### Dependencies installation:
```pip install -r requirements.txt```

### Creating a Google API project:
- Open the [Google API console](https://console.cloud.google.com/apis/dashboard)
- Click ```New project```
- Enter a name and click ```Create```

### Downloading API credentials
- Enter [here](https://console.cloud.google.com/apis/credentials)
- Click ```Create credentials```
- From a opened list box select ```OAuth client ID```
- Select ```Other```, give a custom name and then click ```Create``` 
- Close the dialog window which appeared a while before
- Download user login data file, change its file to ```credentials.json```, create a directory named ```config``` and put this file there

## Register the script
- Open the UONET+ Vulcan website, log in and choose ```Dostęp mobilny``` section
- *virtualenv*
- Click
- Run the ```configure.py``` script with proper parameters: ```python3 configure.py <token> <symbol> <PIN>```

## How to use the script
- Simply run the ```main.py``` script. At the first launch, you will be prompted to log in into your Google account - the link to authentication will appear in the console.
- After the first launch you can add it to scheduled tasks (ex. ```cron```)
