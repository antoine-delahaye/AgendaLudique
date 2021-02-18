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
    user.set_profile_picture(form.profile_picture.data, form.use_gravatar.data)
    db.session.commit()