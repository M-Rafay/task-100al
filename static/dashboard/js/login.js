const validate = (email, password, errorText, showErrorMessage) => {
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
    else if (password.trim() === '') {
        showErrorMessage('Please enter password');
        return false
    }
    else if (password.length < 6) {
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

const loginFormHandler = (e) => {
    const errorText = getElement('errorText');
    const email = getElement('username');
    const password = getElement('password');
    const emailValue = email.value;
    const passwordValue = password.value;

    if (validate(emailValue, passwordValue, errorText, showErrorMessage)) {
    } else {
        e.preventDefault();
    }
}
const loginForm = getElement('loginForm');
loginForm.addEventListener('submit', loginFormHandler);

const showErrorMessage = (errorMessage = 'Invalid email or password') => {
    const errorText = getElement('errorText');
    errorText.innerHTML = `<div class="alert alert-danger alert-dismissible fade show" role="alert" id="errorText">
                                    ${errorMessage}
                                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                            </div>`;
}


