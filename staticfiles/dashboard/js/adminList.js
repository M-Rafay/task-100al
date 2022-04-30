const validate = (email, password, checkPassword, errorText, showErrorMessage) => {
    const emailReg =
        /^(([^<>()[\]\.,;:\s@\"]+(\.[^<>()[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$/i;
    if (email.trim() === '') {
        showErrorMessage('Please enter Email');
        return false
    }
    else if (!email.match(emailReg)) {
        showErrorMessage('please input valid email');
        return false
    }
    else if (checkPassword && password.trim() === '') {
        showErrorMessage('Please enter password');
        return false
    }
    else if (checkPassword && password.length < 6) {
        showErrorMessage('Password must be at least 6 characters');
        return false
    }
    errorText.innerHTML = '';
    return true
}

const getElement = (id) => {
    const element = document.querySelector(`#${id}`);
    return element;
}

const addUserFormHandler = (e, IseditForm) => {
    const errorText = getElement('errorText');
    const email = getElement('id_email');
    const emailValue = email.value;
    if (IseditForm) {
        const password = getElement('id_password');
        const passwordValue = password.value;
        if (validate(emailValue, passwordValue,true, errorText, showErrorMessage)) {
        } else {
            e.preventDefault()
        }
    }  else {
        if (validate(emailValue, false, errorText,false, showErrorMessage)) {
        } else {
            e.preventDefault();
        }
    }
}

const addUserForm = getElement('addUserForm');

if (addUserForm) {
    addUserForm.addEventListener('submit', () => addUserFormHandler(this.event, true));
}
const editUserForm = getElement('editUserForm');
if (editUserForm) {
    editUserForm.addEventListener('submit', () => addUserFormHandler(this.event, false));
}

const showErrorMessage = (errorMessage = 'Invalid email or password') => {
    const errorText = getElement('errorText');
    errorText.innerHTML = `<div class="alert alert-danger alert-dismissible fade show" role="alert" id="errorText">
                                    ${errorMessage}
                                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                            </div>`;
}