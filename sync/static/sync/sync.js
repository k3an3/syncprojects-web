const proj_re = /projects\/(?<project>[0-9]+)\/(songs\/(?<song>[0-9]+)\/)?/;
const sync_button = document.querySelector('#sync_button');

function localRequest(path, method = 'POST') {
    const response = fetch("http://localhost:5000/api/" + path, {
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

function APIRequest(path) {
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

function getContext() {
    let matches = window.location.path.match(proj_re);
    console.log({'proj': matches.groups.project, 'song': matches.groups.song});
    return matches;
}

sync_button.addEventListener('click', event => {
    button.textContent = `Click count: ${event.detail}`;
});