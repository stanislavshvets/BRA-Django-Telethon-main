const formBlock = document.getElementById('formBlock');
const mobileMenu = document.getElementById('mobileMenu');
const mobileMenuBg = document.getElementById('mobileMenuBg');

function toggleVisibility() {
    if (formBlock.classList.contains('hidden')) {
        formBlock.classList.remove('hidden');
        formBlock.classList.add('block');
    } else {
        formBlock.classList.remove('block');
        formBlock.classList.add('hidden');
    }
}

function toggleMobMenuVisibility() {
    if (mobileMenu.classList.contains("translate-x-full")) {
        mobileMenuBg.classList.remove("opacity-0", "invisible");
        mobileMenuBg.classList.add("opacity-100", "visible");

        mobileMenu.classList.remove("translate-x-full");
        mobileMenu.classList.add("translate-x-0");
    } else {
        mobileMenuBg.classList.remove("opacity-100", "visible");
        mobileMenuBg.classList.add("opacity-0", "invisible");

        mobileMenu.classList.remove("translate-x-0");
        mobileMenu.classList.add("translate-x-full");
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