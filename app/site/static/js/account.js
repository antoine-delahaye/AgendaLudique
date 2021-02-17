function enableOrDisableProfilePictureField() {
    let field = document.getElementById("profile_picture");
    let checkbox = document.getElementById("use_gravatar");
    field.disabled = checkbox.checked ? true : false;
}