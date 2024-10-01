#This is a private project

If cloning the project for the first time don't forget to create directories in the project folder as follows:
 - ./Export Files/ELS
 - ./Export Files/Royal
 - ./Import files
 - ./Logs
 - configure virtual environment

When doing pull request on a different system don't forget to check the file locations and firefox drivers.

Added two more price conditions, one if the rc price is smaller than 50 and another if the price is greater than 50 but smaller than 100.

First few tests of the import file on the local website went well. Consult with M if we should import the file on live website.

Added .env file for more a more secure way of handling password and keys. 