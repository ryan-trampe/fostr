# Imports ######################################################################
from dotenv import load_dotenv
import os

# Globals ######################################################################
load_dotenv()

# Library ######################################################################
DEBUG = os.getenv('DEBUG')
HOST = os.getenv('HOST')
PORT = os.getenv('PORT')

SECRET_KEY = os.getenv('SECRET_KEY')
SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')

DEFAULT_PROFILE_PIC = 'default.png'

# roles
class Roles:
    """
    User roles (Parent, Child, Admin)
    """
    PARENT = 'Parent'
    CHILD  = 'Child'
    ADMIN  = 'Admin'

class Gender:
    MALE   = 'Male'
    FEMALE = 'Female'

# Main #########################################################################
def main():
    print(f'{DEBUG} http://{HOST}:{PORT}')
    print(f'{SECRET_KEY}')

if __name__ == '__main__':
    main()