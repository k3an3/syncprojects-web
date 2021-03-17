async function localRequest(path, method = 'GET', data) {
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

async function APIRequest(path, method = 'GET', data) {
    const response = await fetch("/api/v1/" + path, {
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

async function ping() {
    return await localRequest('ping');
}

async function signData(data) {
    return await APIRequest('sign/', 'POST', data);
}

async function getProjects() {
    const response = await APIRequest('projects/');
    return response.results;
}

async function startSync(data) {
    return await localRequest('sync', 'POST', data);
}

async function workOn(data) {
    return await localRequest('workon', 'POST', data);
}

async function getResults() {
    return await localRequest('results');
}

Storage.prototype.setObj = function (key, obj) {
    return this.setItem(key, JSON.stringify(obj))
}
Storage.prototype.getObj = function (key) {
    return JSON.parse(this.getItem(key))
}
let taskStore = window.localStorage;
