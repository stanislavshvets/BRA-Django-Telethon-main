const formBlock = document.querySelector('#formBlock');

function toggleVisibility() {
    if (formBlock.classList.contains('hidden')) {
        formBlock.classList.remove('hidden');
        formBlock.classList.add('block');
    } else {
        formBlock.classList.remove('block');
        formBlock.classList.add('hidden');
    }
}

function validateFilterForm(form) {
    const inputs = form.querySelectorAll("input");
    for (let input of inputs) {
        if (input.value.trim() !== "") {
            return true;
        }
    }
    alert("Будь ласка, заповніть хоча б одне поле для фільтрації!");
    return false;
}

function removeEmptyInputs(form) {
    for (const el of form.querySelectorAll("input")) {
        if (!el.value) el.removeAttribute("name");
    }
}