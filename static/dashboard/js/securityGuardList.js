const validate = (city, nationality, birth_date, address, license_expiry_date, license_no, per_hour_rate, email, password, checkPassword, errorText, showErrorMessage) => {
    const emailReg =
        /^(([^<>()[\]\.,;:\s@\"]+(\.[^<>()[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$/i;
    if (email.trim() === '') {
        showErrorMessage('Please enter email');
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
    else if (city.trim() === '') {
        showErrorMessage('Please enter city');
        return false
    }
    else if (nationality.trim() === '') {
        showErrorMessage('Please enter nationality');
        return false
    }
    else if (birth_date.trim() === '') {
        showErrorMessage('Please enter birthdate');
        return false
    }
    else if (address.trim() === '') {
        showErrorMessage('Please enter address');
        return false
    }
    else if (license_expiry_date.trim() === '') {
        showErrorMessage('Please enter license expiry date');
        return false
    }
    else if (license_no.trim() === '') {
        showErrorMessage('Please enter license no');
        return false
    }
    else if (per_hour_rate.trim() === '') {
        showErrorMessage('Please enter per hour rate');
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
    const emailValue = getElement('id_email').value;
    const city = getElement('id_city').value;
    const nationality = getElement('id_nationality').value;
    const birth_date = getElement('id_birth_date').value;
    const address = getElement('id_address').value;
    const license_expiry_date = getElement('id_license_expiry_date').value;
    const license_no = getElement('id_license_no').value;
    const per_hour_rate = getElement('id_per_hour_rate').value;
    if (IseditForm) {
        const password = getElement('id_password');
        const passwordValue = password.value;
        if (validate(city, nationality, birth_date, address, license_expiry_date, license_no, per_hour_rate, emailValue, passwordValue, true, errorText, showErrorMessage)) {
        } else {
            e.preventDefault()
        }
    } else {
        if (validate(emailValue, false, errorText, false, showErrorMessage)) {
        } else {
            e.preventDefault();
        }
    }
}

const addGuardForm = getElement('addGuardForm');

if (addGuardForm) {
    addGuardForm.addEventListener('submit', () => addUserFormHandler(this.event, true));
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