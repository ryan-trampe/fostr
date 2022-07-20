# Imports ######################################################################
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required

from fostr import app
from fostr.models import User
from fostr.forms import (
    LoginForm, 
    UserCreateForm,
    UserUpdateForm
) 
from fostr.utils import (
    hashPassword, 
    checkPassword,
    str2list,
    str2int,
    savePicture,
    deletePicture,
    dprint,
    addUserDB,
    deleteUserDB,
    commitDB,
    fillUserForm
)
from fostr.config import (
    Roles,
    DEFAULT_PROFILE_PIC
)

# Globals ######################################################################

# flash messages
# https://getbootstrap.com/docs/4.0/components/alerts/
# categories = {success, danger, info, warning}
# flash('<message here>', '<category type>')
#     flash('A success flash', 'success')
#     flash('A danger flash', 'danger')
#     flash('A info flash', 'info')
#     flash('A warning flash', 'warning')
#     return redirect(url_for('home'))

# methods
# request.method == 'GET'

# parameterized routes
# @app.route('/user/<string:username>')

# Library ######################################################################

# Error Routes #################################################################
@app.errorhandler(404)
def pageNotFound_404(error):
    return render_template('pageNotFound_404.html'), 404

@app.errorhandler(403)
def forbidden_403(error):
    return render_template('forbidden_403.html'), 403

# Session Routes ###############################################################
@app.route('/login', methods=['GET', 'POST'])
def login():
    # check if already logged in
    if (current_user.is_authenticated):
        flash('You are already logged in!', 'info')
        return redirect(url_for('home'))
    # not logged in
    form = LoginForm()
    if (form.validate_on_submit()):
        # check if user is in database
        user = User.query.filter_by(username=form.username.data).first()
        # validate their password
        if (user and checkPassword(user.password, form.password.data)):
            login_user(user, remember=form.remember.data)
            nextPage = request.args.get('next')
            # flash('Logged in!', 'success')
            return redirect(nextPage) if nextPage else redirect(url_for('home'))
        else:
            flash('Invalid login credentials!', 'danger')
    content = {
        'app_name': app.name.capitalize(),
        'title': 'Login',
        'form': form
    }
    return render_template('login.html', **content)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

# General Routes ###############################################################
@app.route('/')
@login_required
def home():
    # get the right users for the current_user's view permissions
    users = None
    if (current_user.checkRole(Roles.ADMIN)):
        # admin can see all users
        users = User.query.all()
    elif (current_user.checkRole(Roles.PARENT)):
        # parent can see all children
        users = User.query.filter_by(role=Roles.CHILD).all()
    elif (current_user.checkRole(Roles.CHILD)):
        # child can see themselves
        users = User.query.filter_by(username=current_user.username).all()
    # render home with a set of children based on curren_user's permissions
    content = {
        'app_name': app.name.capitalize(),
        'title': 'Home',
        'users': users
    }
    return render_template('home.html', **content)

@app.route('/about')
@login_required
def about():
    content = {
        'app_name': app.name.capitalize(),
        'title': 'About'
    }
    return render_template('about.html', **content)

@app.route('/user/<string:role>/<string:username>')
@login_required
def userInfo(role, username):
    # check if required role
    if (current_user.checkRole(Roles.ADMIN)):
        # admin can see everyone
        pass 
    elif (current_user.checkRole(Roles.PARENT) and (role != Roles.CHILD)):
        flash('You can only view children!', 'danger')
        return abort(403, description='Parent can only see children!')
    elif (current_user.checkRole(Roles.CHILD) and (username != current_user.username)):
        flash('You can only view yourself!', 'danger')
        return abort(403, description='Child can only see themselves!')
    # current_user is permitted to see the requested user
    user = User.query.filter_by(username=username).first()
    if (not user):
        flash(f'{role} user {username} does not exist!', 'warning')
        return abort(404, description='User does not exist')
    content = {
        'app_name': app.name.capitalize(),
        'title': 'User',
        'user': user
    }
    return render_template('user_info.html', **content)

# Admin Routes #################################################################
@app.route('/admin/create-user', methods=['GET', 'POST'])
@login_required
def createUser():
    # check if required role
    if (not current_user.checkRole(Roles.ADMIN)):
        flash('Not an admin, cannot create!', 'danger')
        return abort(403, description='Not an Admin!')
    # admin is creating a user
    form = UserCreateForm()
    if (form.validate_on_submit()):
        hashedPassword = hashPassword(form.password.data)
        if (form.profile_pic.data): 
            # profile picture was uploaded
            profile_pic = savePicture(form.profile_pic.data)
        else: profile_pic = DEFAULT_PROFILE_PIC # no picture uploaded 
        user = User(
            # user state
            username=form.username.data,
            password=hashedPassword,
            # role [admin, child, parent]
            role=form.roles.data,
            # user info
            name=form.name.data,
            age=str2int(form.age.data),
            gender=form.genders.data,
            interests=str2list(form.interests.data, ';'),
            hobbies=str2list(form.hobbies.data, ';'),
            date_entered=form.date_entered.data,
            profile_pic=profile_pic
        )
        dprint(f'Created user {user.name}')
        print(user)
        addUserDB(user)
        flash(f'{user.role.capitalize()} user {user.name} created!', 'success')
        return redirect(url_for('createUser'))
    content = {
        'app_name': app.name.capitalize(),
        'title': 'Create User',
        'form': form,
        'form_title': 'Create User',
        'profile_pic_hint': ' (leave blank for default)',
        'password_hint': '',
        'show_username': True
    }
    return render_template('user_form.html', **content)

@app.route('/user/<string:role>/<string:username>/update', methods=['GET', 'POST'])
@login_required
def updateUser(role, username):
    # check if required role
    if (not current_user.checkRole(Roles.ADMIN)):
        flash('Not an admin, cannot update!', 'danger')
        return abort(403, description='Not an Admin!')
    # admin is updating a user
    form = UserUpdateForm()
    # user to update
    user = User.query.filter_by(username=username).first()
    if (not user):
        flash('Cannot update, user does not exist!', 'warning')
        return abort(404, description='User does not exist!')
    if (form.validate_on_submit()):
        if (user.username != form.username.data):
            flash('Cannot change username!', 'danger')
            return abort(403, 'Cannot change username!')
        # hash password 
        hashedPassword = hashPassword(form.password.data)
        # select profile_pic
        profile_pic = user.profile_pic
        if (form.profile_pic.data):
            # new picture uploaded (delete old picture)
            deletePicture(user.profile_pic)
            profile_pic = savePicture(form.profile_pic.data)
        # update user ##########################################################
        # user state
        user.username=form.username.data
        user.password=hashedPassword
        # role [admin, child, parent]
        user.role=form.roles.data
        # user info
        user.name=form.name.data
        user.age=str2int(form.age.data)
        user.gender=form.genders.data
        user.interests=str2list(form.interests.data, ';')
        user.hobbies=str2list(form.hobbies.data, ';')
        user.date_entered=form.date_entered.data
        user.profile_pic=profile_pic
        # inform of update #####################################################
        commitDB()
        dprint(f'Updated user {user.name}')
        print(user)
        flash(f'{user.role.capitalize()} user {user.name} updated!', 'success')
        # return redirect(url_for('updateUser'))
        return redirect(f'/user/{user.role}/{user.username}')
    elif (request.method == 'GET'):
        fillUserForm(form, user)
    content = {
        'app_name': app.name.capitalize(),
        'title': 'Create User',
        'form': form,
        'form_title': 'Update User',
        'profile_pic_hint': ' (leave blank if using old picture)',
        'password_hint': ' (enter new password or old password to keep)',
        'show_username': False
    }
    return render_template('user_form.html', **content)

@app.route('/user/<string:role>/<string:username>/delete', methods=['POST'])
@login_required
def deleteUser(role, username):
    # check if required role
    if (not current_user.checkRole(Roles.ADMIN)):
        flash('Not an admin, cannot delete!', 'danger')
        return abort(403, description='Not an Admin!')
    # check if user exists
    user = User.query.filter_by(username=username).first()
    if (not user):
        flash('User does not exist!', 'warning')
        return abort(404, description='User does not exist!')
    # delete the user
    name = user.name
    deleteUserDB(user)
    # inform and redirect
    flash(f'User {name} deleted!', 'success')
    return redirect(url_for('home'))

# Main #########################################################################
def main():
    pass

if __name__ == '__main__':
    main()