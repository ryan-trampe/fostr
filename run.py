# Imports ######################################################################
from fostr import app
from fostr.config import HOST, PORT, DEBUG
from fostr.utils import initDB

# Globals ######################################################################


# Library ######################################################################


# Main #########################################################################
def main():
    initDB()
    app.run(host=HOST, port=PORT, debug=DEBUG)

if __name__ == '__main__':
    main()