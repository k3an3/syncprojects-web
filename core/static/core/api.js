async function APIRequest(path, method = 'GET', data) {
    const response = await fetch("/api/v1/" + path, {
        method: method,
        mode: 'same-origin',
        credentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf_token,
        },
        redirect: 'error',
        body: JSON.stringify(data)
    });
    return response.json();
}

async function comment(comment) {
    const response = await APIRequest('comments/', 'POST', comment);
    return response.results;
}
