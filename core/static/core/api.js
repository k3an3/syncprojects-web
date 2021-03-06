const csrf_token_e = document.querySelector('[name=csrfmiddlewaretoken]');
const csrf_token = csrf_token_e != null ? csrf_token_e.value : "";

async function APIRequest(path, method = 'GET', data, jsonResponse = true) {
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
    if (jsonResponse) {
        return response.json();
    } else {
        return response;
    }
}

async function comment(comment) {
    const response = await APIRequest('comments/', 'POST', comment);
    return response;
}

async function commentDelete(comment) {
    const response = await APIRequest('comments/' + comment + '/', 'DELETE', {}, false);
    return response;
}

async function commentResolve(comment) {
    const response = await APIRequest('comments/' + comment + '/resolve/', 'POST', {}, false);
    return response;
}

async function commentUnresolve(comment) {
    const response = await APIRequest('comments/' + comment + '/unresolve/', 'POST', {}, false);
    return response;
}

async function commentLike(comment) {
    const response = await APIRequest('comments/' + comment + '/like/', 'POST', {});
    return response;
}

async function getComments(project = null, song = null) {
    let query = '';
    if (project) {
        query = 'project=' + project;
    } else {
        query = 'song=' + song;
    }
    const response = await APIRequest('comments/?' + query);
    return response;
}

async function getRegions(song) {
    const response = await APIRequest('player/regions/?song=' + song);
    return response
}

async function addRegion(data, id = null) {
    if (id) {
        return await APIRequest('player/regions/' + id + "/", 'PUT', data);
    } else {
        return await APIRequest('player/regions/', 'POST', data);
    }
}

async function deleteRegion(id) {
    return await APIRequest('player/regions/' + id + '/', 'DELETE');
}

async function addSnippet(data) {
    return await APIRequest('snippets/', 'POST', data);
}