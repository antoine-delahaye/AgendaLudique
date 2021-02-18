from app import db


def update_user_with_form(form,user):
    """
    update user informations in db from UpdateInformationForm
    :param form: UpdateInformationForm
    """
    user.username = form.username.data
    user.first_name = form.first_name.data
    user.last_name = form.last_name.data
    user.password = form.password.data
    user.use_gravatar = form.use_gravatar.data
    user.profile_picture = user.get_profile_picture()
    db.session.commit()
