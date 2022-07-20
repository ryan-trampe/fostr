# Imports ######################################################################
from flask_login import current_user
# Flask specific subclass of WTForms
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
# form validation and rendering
from wtforms import (
    StringField, 
    PasswordField, 
    SubmitField, 
    BooleanField,
    RadioField,
    TextAreaField,
    DateField
) 
from wtforms.validators import (
    DataRequired, 
    Length, 
    EqualTo, 
    ValidationError
) 

from fostr.models import User
from fostr.config import Roles, Gender

# Globals ######################################################################


# Library ######################################################################
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit   = SubmitField('Login')

class UserForm(FlaskForm):
    # User Credentials #########################################################
    # user state
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=1, max=256),
    ])
    password = PasswordField('Password', validators=[
        DataRequired()
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password')
    ])
    # role [admin, child, parent]
    roles = RadioField('Role', 
    validators=[
        DataRequired()
    ],
    choices=[
        (Roles.ADMIN,  Roles.ADMIN),
        (Roles.PARENT, Roles.PARENT),
        (Roles.CHILD,  Roles.CHILD)
    ]
    )
    # User Info ################################################################
    name = StringField('Full Name', validators=[
        DataRequired(),
        Length(min=1, max=128),
    ])
    age = StringField('Age', validators=[
        DataRequired(),
    ])
    genders = RadioField('Gender', 
    validators=[
        DataRequired()
    ],
    choices=[
        (Gender.MALE, Gender.MALE),
        (Gender.FEMALE, Gender.FEMALE)
    ]
    )
    interests = TextAreaField('Interests (separate by semicolons)', validators=[
        DataRequired()
    ])
    hobbies = TextAreaField('Hobbies (separate by semicolons)', validators=[
        DataRequired()
    ])
    date_entered = DateField("Date Entered (e.g. DD/MM/YYYY)", validators=[
        DataRequired()
    ],
    format='%d/%m/%Y'
    )
    profile_pic = FileField(f'Profile Picture', validators=[
        FileAllowed(['png'])
    ])
    # Other ####################################################################
    
    def validate_age(self, age):
        try: int(age.data)
        except Exception: raise ValidationError('Not an age!')
        if (int(age.data) < 0):
            raise ValidationError('Age is less than 0!')

    def validate_interests(self, interests):
        error = self.__checkList(interests, 'interest')
        if (error is not None):
            raise error
    
    def validate_hobbies(self, interests):
        error = self.__checkList(interests, 'hobby')
        if (error is not None):
            raise error

    def __checkList(self, strList:str, itemType:str):
        # make sure no semicolon on right
        if (strList.data[-1] == ';'):
            raise ValidationError('Remove last semicolon')
        # make list and make sure all cells have something
        alist = [item.strip() for item in strList.data.split(';')]
        for i, item in enumerate(alist):
            if (not item or item == ''):
                raise ValidationError(f'No data for {itemType} {i+1}')
        return None

class UserCreateForm(UserForm):
    submit = SubmitField('Create')
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if (user):
            raise ValidationError(f'Username {username.data} is taken.')
class UserUpdateForm(UserForm):
    submit = SubmitField('Update')

# Main #########################################################################
def main():
    pass

if __name__ == '__main__':
    main()