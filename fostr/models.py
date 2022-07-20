# Imports ######################################################################
from datetime import datetime

from flask_login import UserMixin
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import PickleType

from fostr import db, login_manager
from fostr.config import DEFAULT_PROFILE_PIC

# Globals ######################################################################


# Library ######################################################################
@login_manager.user_loader
def load_user(userID):
    return User.query.get(int(userID))
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    # user state
    username     = db.Column(db.String(256), unique=True, nullable=False)
    password     = db.Column(db.String(128), nullable=False)
    # role [admin, child, parent]
    role         = db.Column(db.String(32), nullable=False)
    # user info
    name         = db.Column(db.String(128), nullable=False) # full name
    age          = db.Column(db.Integer, nullable=False)
    gender       = db.Column(db.String(6), nullable=False) # male/female
    interests    = db.Column(MutableList.as_mutable(PickleType), nullable=False)
    hobbies      = db.Column(MutableList.as_mutable(PickleType), nullable=False)
    date_entered = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    profile_pic  = db.Column(db.String(32), nullable=False, default=DEFAULT_PROFILE_PIC)

    def __repr__(self):
        return f'User({self.username}, {self.role}, {self.gender})'
    
    def __str__(self):
        pad = 40*'-'+'\n'
        user = pad
        user += f'{self.role} {self.gender} User {self.name} Age {self.age}\n'
        user += f"Username {self.username} Password {self.password}\n"
        user += f'Interests: {self.interests}\n'
        user += f'Hobbies: {self.hobbies}\n'
        user += f'Date Entered: {self.date_entered}\n'
        user += f'Profile Pic: {self.profile_pic}\n'
        user += pad
        return user
    
    def checkRole(self, role:str) -> bool:
        """
        Returns true if user has required role
        fostr.config -> PARENT, CHILD, ADMIN
        """
        return self.role == role


# Main #########################################################################
def main():
    pass

if __name__ == '__main__':
    main()