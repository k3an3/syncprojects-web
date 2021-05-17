const csrf_token = document.querySelector('[name=csrfmiddlewaretoken]').value;

async function localRequest(path, method = 'GET', data = {}, sign = true) {
    let body = null;
    if (method === 'POST') {
        if (sign)
            data = await signData(data);
        body = JSON.stringify(data);
    }
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
        body: body,
    });
    return response.json();
}

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

async function ping() {
    return await localRequest('ping');
}

async function signData(data, sign_user) {
    data.sign_user = sign_user;
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

async function workDone(data) {
    return await localRequest('workdone', 'POST', data);
}

async function getResults() {
    return await localRequest('results');
}

async function getTasks() {
    return await localRequest('tasks', 'POST', {});
}

async function submitChangelog(song, text) {
    if (text === "") {
        showToast("Error", "Changelog must not be blank.", "danger");
        return;
    }
    return await APIRequest('syncs/' + song + '/changelog/', 'PUT', {
        text: text
    });
}

Storage.prototype.setObj = function (key, obj) {
    return this.setItem(key, JSON.stringify(obj))
}
Storage.prototype.getObj = function (key) {
    try {
        return JSON.parse(this.getItem(key))
    } catch (e) {
        return {};
    }
}

function isEmpty(obj) {
    for (let prop in obj) if (obj.hasOwnProperty(prop)) return false;
    return true;
}

let taskStore = window.localStorage;
