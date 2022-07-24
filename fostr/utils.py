# Imports ######################################################################
from fostr import app, db, bcrypt
from fostr.models import User
from fostr.forms import UserForm
from fostr.config import (
    Roles, 
    Gender,
    DEFAULT_PROFILE_PIC
)
import os
from secrets import token_hex
from PIL import Image
from flask import current_app
from datetime import date

# Globals ######################################################################
ADMIN_PIC='admin.png'
PUSER_PIC='puser.png'
CUSER_PIC='cuser.png'
CUSER2_PIC='cuser2.png'
DEV_USER_PICS=[
    DEFAULT_PROFILE_PIC,
    ADMIN_PIC,
    PUSER_PIC,
    CUSER_PIC, 
    CUSER2_PIC
]

# Library ######################################################################
 
# Other ########################################################################
def dprint(message):
    print(f'[{app.name}]: {message}')

def str2list(strList:str, delim:str):
    return [item.strip() for item in strList.split(delim)]

def list2str(alist, delim:str):
    return delim.join(alist)

def str2int(aNum:str):
    return int(aNum)

def hashPicture(profile_pic) -> str:
    """
    Hash a profile picture filename
    """
    # get file and extension
    _, ext = os.path.splitext(profile_pic)
    # create a hex filename
    pic_file = token_hex(8) + ext
    return pic_file

def savePicture(form_pic) -> str:
    """
    Save a form picture in the database and return the encoded 
    filename
    """
    pic_file = hashPicture(form_pic.filename)
    PROFILE_PICS_DIR=os.path.join(current_app.root_path, 'static/profile_pics')
    pic_path = os.path.join(PROFILE_PICS_DIR, pic_file)
    # resize the form picture
    i = Image.open(form_pic)
    i.thumbnail((125,125)) # scale size
    # save the pic
    i.save(pic_path)
    return pic_file

def deletePicture(profile_pic):
    """
    Delete profile_pic from the server
    """
    if (profile_pic in DEV_USER_PICS): return
    PROFILE_PICS_DIR=os.path.join(current_app.root_path, 'static/profile_pics')
    profile_pic_path = os.path.join(PROFILE_PICS_DIR, profile_pic)
    os.remove(profile_pic_path)

def fillUserForm(form:UserForm, user:User):
    """
    Prefill the UserForm with a user
    """
    # user state
    form.username.data     = user.username
    form.roles.data        = user.role
    # user info
    form.name.data         = user.name
    form.age.data          = user.age
    form.genders.data      = user.gender
    form.interests.data    = list2str(user.interests, ';')
    form.hobbies.data      = list2str(user.hobbies, ';')
    form.date_entered.data = user.date_entered

# Password #####################################################################
def hashPassword(password:str):
    """
    Hash a password
    """
    return bcrypt.generate_password_hash(password).decode('utf-8')

def checkPassword(db_password, form_password) -> bool:
    return bcrypt.check_password_hash(db_password, form_password)

# Database #####################################################################
def initDB():
    """
    Drop and create all tables
    """
    # drop all tables
    db.drop_all()
    db.create_all()
    addChildren()
    addParents()
    addAdmin()
    dprint(f'Inititalized {app.name} Database!')

def addChildren():
    """
    Add some test children
    """
    child = User(
            username='cuser',
            password=hashPassword('cuser'),
            role=Roles.CHILD,
            name='Miles',
            age=12,
            gender=Gender.MALE,
            interests=['Sports', 'Video Games'],
            hobbies=["Messing up databases", "Soccer"],
            date_entered=date(2021, 11, 22),
            profile_pic=CUSER_PIC
    )
    addUserDB(child)
    dprint(f'Added user {child.name}!')
    print(child)
    child = User(
            username='cuser2',
            password=hashPassword('cuser2'),
            role=Roles.CHILD,
            name='Valkyria',
            age=11,
            gender=Gender.FEMALE,
            interests=['Movies', 'TV Shows'],
            hobbies=['collecting popcans', 'Painting Gundams'],
            date_entered=date(2021, 11, 22),
            profile_pic=CUSER2_PIC
    )
    addUserDB(child)
    dprint(f'Added user {child.name}!')
    print(child)

def addParents():
    """
    Add some test parents
    """
    parent = User(
            username='puser',
            password=hashPassword('puser'),
            role=Roles.PARENT,
            name='Ricardo',
            age=35,
            gender=Gender.FEMALE,
            interests=['Gaming','Video game design'],
            hobbies=['Managing gamers'],
            date_entered=date(2021, 11, 22),
            profile_pic=PUSER_PIC
    )
    addUserDB(parent)
    dprint(f'Added user {parent.name}!')
    print(parent)

def addAdmin():
    """
    Add the superuser
    """
    user = User(
        username='admin',
        password=hashPassword('nimda'),
        role=Roles.ADMIN,
        name='Superuser',
        age=45,
        gender=Gender.MALE,
        interests=['administrative'],
        hobbies=['Managing databases'],
        date_entered=date(2021, 11, 19),
        profile_pic=ADMIN_PIC
    )
    
    addUserDB(user)
    dprint(f'Added admin {user.name}!')
    print(user)

def commitDB():
    """
    Commit changes to DB
    """
    db.session.commit()

def addUserDB(user:User):
    """
    Add a user to the database
    """
    db.session.add(user)
    commitDB()

def deleteUserDB(user:User):
    """
    Delete a user from the database
    """
    deletePicture(user.profile_pic)
    db.session.delete(user)
    commitDB()

# Main #########################################################################
def main():
    pass

if __name__ == '__main__':
    main()