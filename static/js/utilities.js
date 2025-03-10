// Utility functions for formatting currencies, handling dates, and making API requests. 

// Utility function to format currency values. 
function formatCurrency(value) {
    // create new instance of number format, specifyingg usd as the currency. 
    return new Intl.NumberFormat('en-US', {style: 'currency', currency: 'USD'}).format(value); 
    // return will be string formatted as currency ($1235.34)
}


// Utility function to formate dates into a readable format
function formatDate(date) {
    // defin iotiuons for formatting data, and convert input in js date object and format/ Return as string. 
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(date).toLocaleDateString(undefined, options); 
}

// Utility function ot handle API errors
function handleAPIError(response) {
    if(!response.ok) {
        throw Error('API request failed: ' + response.statusText);
    }
    return response;
}


// Utility function to make GET requests
function fetchData(url) {
    // make fetch request to spceified URL 
    return fetch(url)
    // pass response to handleAPIError toc check for errors
    .then(handleAPIError)
    // parse response and return it as js object. Return value is promise that resolves with the parsed JSON data. 
    .then(response => response.json()); 
}