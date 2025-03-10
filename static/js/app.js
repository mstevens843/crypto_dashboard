// wait for DOM to load before running script.
document.addEventListener('DOMContentLoaded', function() {
    // initialize ui components(); 
    initializeUIComponents();


    // handle form submissions for adding crypto:
    const addCurrencyForm = document.querySelector('#addCurrencyForm');
    if(addCurrencyForm) {
        addCurrencyForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleFormSubmission(addCurrencyForm);
        });
    }

    // handle form submission to existing currency. 
    const editCurrencyForm = document.querySelector('#editCurrencyForm');
    if (editCurrencyForm) {
        editCurrencyForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleFormSubmission(editCurrencyForm); 
        });
    }

    // handle click event to update crypto price. 
    const updateButton = document.querySelector('#updatePriceButton');
    if (updateButton) {
        updateButton.addEventListener('click', function() {
            updateCryptoCurrencyPrices();
        })
    }
}); 


// Initialize bootstrap, components
function initializeUIComponents() {
    $('[data-toggle="tooltip"]').tooltip(); 
}


// handle form submissions and send data to the backend
function handleFormSubmission(form) {
    const formData = new FormData(form)


    // sending form data to the server via fetch API 
    fetch(form.action, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log('Form submission successful:', data)
        // Redirect or update UI as needed
        window.location.href = '/';
    })
    .catch(error => console.error('Error submitting form:', error)); 
}


// Update crypto prices by making request to backend 
function updateCryptoCurrencyPrices() {
    fetch('/update_prices')
        .then(response => response.json())
        .then(date => {
            console.log('Prices updated:', data); 
            // optionally, update the UI to reflect the new prices
            location.reload();
        })
        .catch(error => console.error('Error updating prices:', error)); 
}