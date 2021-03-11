async function localRequest(path, method = 'POST', data) {
    const response = await fetch("http://localhost:5000/api/" + path, {
        method: method,
        mode: 'cors',
        cache: 'no-cache',
        credentials: 'omit',
        headers: {
            'Content-Type': 'application/json'
        },
        redirect: 'error',
        referrerPolicy: 'origin',
        body: JSON.stringify(data)
    });
    return response.json();
}

function APIRequest(path, method = 'POST', data) {
    const response = fetch("/api/v1/" + path, {
        method: method,
        mode: 'same-origin',
        credentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json'
        },
        redirect: 'error',
        body: JSON.stringify(data)
    });
    return response.json();
}