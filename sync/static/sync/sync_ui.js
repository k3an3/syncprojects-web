const proj_re = /projects\/(?<project>[0-9]+)\/(songs\/(?<song>[0-9]+)\/)?/;
const sync_button = document.querySelector('#sync_button');
const daw_button = document.querySelector('#daw_button');
const sync_modal = new bootstrap.Modal(document.querySelector("#sync_modal"), {});
const sync_modal_body = document.querySelector("#sync-modal-body");
const progress = document.querySelector("#sync_progress");
const alert = document.querySelector('#alert');
let ping_failed = true;

function getContext() {
    let matches = window.location.pathname.match(proj_re);
    if (matches == null)
        return {'project': null, 'song': null};
    return {'project': parseInt(matches.groups.project), 'song': parseInt(matches.groups.song) || null};
}


function pushTask(task_id, data) {
    let tasks = taskStore.getObj('tasks');
    if (tasks == null) {
        tasks = {}
    }
    tasks[task_id] = data;
    taskStore.setObj('tasks', tasks);
}

function clearTasks() {
    taskStore.setObj('tasks', {});
}

function popTask(task_id) {
    let tasks = taskStore.getObj('tasks');
    let result = tasks[task_id];
    delete tasks[task_id];
    taskStore.setObj('tasks', tasks);
    return result;
}

function getTask(task_id) {
    return taskStore.getObj('tasks')[task_id];
}

if (daw_button != null)
    daw_button.addEventListener('click', async _ => {
        daw_button.textContent = "Opening..."
        sync_button.disabled = true;
        let context = getContext();
        console.log("Got context");
        console.log(context);
        let result;
        taskStore.setObj('sync_in_progress', true);
        let msg = {'song': {'song': context.song, 'project': context.project}};
        console.log("Working on song")
        console.log(msg);
        let signed = await signData(msg);
        console.log("Signed data");
        console.log(signed);
        result = await workOn(signed);
        console.log("Got initial response");
        console.log(result);
        if (result.result === "started") {
            pushTask(result.task_id, 'workon');
            showToast("Sync", "Syncing and opening song in DAW...");
        } else {
            console.warn("Unknown response.");
        }
    });

sync_button.addEventListener('click', async _ => {
    showToast("Sync", "Starting sync...");
    sync_button.textContent = "Syncing..."
    sync_button.disabled = true;
    let context = getContext();
    console.log("Got context");
    console.log(context);
    let result;
    taskStore.setObj('sync_in_progress', true);
    if (context.project == null) {
        // Sync all projects
        let projects = await getProjects();
        let msg = {'projects': projects}
        console.log("Syncing projects");
        console.log(msg);
        let signed = await signData(msg);
        console.log("Signed data");
        console.log(signed);
        result = await startSync(signed);
    } else if (context.song == null) {
        // Sync single project
        let msg = {'projects': [context.project]};
        console.log("Syncing project");
        console.log(msg);
        let signed = await signData(msg);
        console.log("Signed data");
        console.log(signed);
        result = await startSync(signed);
    } else {
        // Sync single song
        let msg = {'songs': [{'song': context.song, 'project': context.project}]};
        console.log("Syncing song")
        console.log(msg);
        let signed = await signData(msg);
        console.log("Signed data");
        console.log(signed);
        result = await startSync(signed);
    }
    console.log("Got initial response");
    console.log(result);
    if (result.result === "started") {
        showToast("Sync", "Sync started");
        pushTask(result.task_id, 'sync');
    } else {
        showToast("Sync", "Something went wrong! Contact support.", "danger");
        console.warn("Unknown response.");
    }
});

function disableDawButton(status = true) {
    if (daw_button != null)
        daw_button.disabled = status;
}

function enableSyncButton() {
    sync_button.className = "btn btn-sm btn-primary";
    sync_button.textContent = "Sync";
    sync_button.disabled = false;
    disableDawButton(false);
}

async function checkConnection() {
    const result = await ping().catch(_ => {
        ping_failed = true;
        //console.error("Failed to connect to syncprojects client: " + error);
        sync_button.disabled = true;
        disableDawButton();
        sync_button.className = "btn btn-sm btn-outline-danger";
        sync_button.textContent = "Sync: Not Connected";
    });
    if (result != null && result.result == "pong") {
        ping_failed = false;
        console.debug("Got PONG from server: " + result.task_id);
        if (taskStore.getObj('sync_in_progress')) {
            sync_button.className = "btn btn-sm btn-primary";
            sync_button.textContent = "Syncing...";
            sync_button.disabled = true;
            disableDawButton();
        } else {
            enableSyncButton();
        }
    }
}

function syncResultHandler(data) {
    console.log("displaying sync results, fetched from storage");
    let html = `<p class="text-muted"><small>(${data.task_id})</small></p>`;
    let results = taskStore.getObj('sync-' + data.task_id);
    results.forEach(project_result => {
        console.log(project_result);
        html += `<h3>${project_result.project}</h3>`;
        if (project_result.songs != null && project_result.songs.length) {
            html += '<span class="badge bg-success">Success</span>';
            html += '<ul class="list-group">'
            let bg = "primary";
            project_result.songs.forEach(song_result => {
                html += '<li class="list-group-item d-flex justify-content-between align-items-start">';
                html += `<div class="ms-2 me-auto"><div class="fw-bold">${song_result.name}</div>${song_result.action}</div>`;
                html += `<span class="badge bg-${bg} rounded-pill>${song_result.result}</span>`;
            });
            html += '</ul>';
        } else if (project_result.lock) {
            html += '<span class="badge bg-danger">Failed</span>';
            let since = "";
            let reason = "";
            let unlock = "";
            if (project_result.lock.since != null)
                since = " since " + project_result.lock.since;
            if (project_result.lock.reason != null)
                reason = " Reason: " + project_result.lock.reason + ".";
            if (project_result.lock.locked_by === "self")
                unlock = " Soon, you will be able to work around this yourself... In the meantime, contact support.";
            html += `<p class="text-danger">Locked by ${project_result.lock.locked_by}${since}.${reason}${unlock}</p>`;
        } else {
            html += '<span class="badge bg-warning">None</span>';
            html += '<p class="text-muted">No results.</p>';
        }
    });
    taskStore.removeItem('sync-' + data.task_id);
    console.log(results);
    sync_modal_body.innerHTML = html;
    sync_modal.show();
}

function saveSyncProgress(task_id, data) {
    console.log("Ok... saving progress...");
    console.log(data);
    let stored = taskStore.getObj('sync-' + task_id);
    if (stored == null || stored.isEmpty()) {
        stored = [];
    }
    stored.push(data);
    taskStore.setObj('sync-' + task_id, stored);
}

function handleResults(data) {
    if (!data.results.length) {
        return;
    }
    console.log("Got results");
    console.log(data.results);
    data.results.forEach(result => {
        console.log("processing");
        console.log(result);
        let task = getTask(result.task_id);
        if (task == null) {
            console.warn("Task was null, bailing...");
            return;
        }
        console.log("Got task");
        console.log(task);
        switch (result.status) {
            case "complete":
                console.log("Handle sync completion");
                showToast("Sync", task[0].toUpperCase() + task.substr(1) + " complete", "success");
                popTask(result.task_id);
                switch (task) {
                    case 'sync':
                        taskStore.setObj('sync_in_progress', false);
                        enableSyncButton();
                        syncResultHandler(result);
                        break;
                    default:
                        console.warn("Unexpected task handler " + task);
                        break;
                }
                break;
            case "progress":
                saveSyncProgress(result.task_id, result.completed);
                break;
            case "error":
                task = popTask(result.task_id);
                showToast("Sync", "Oops! " + result.msg, "danger");
                taskStore.setObj('sync_in_progress', false);
                break;
            case "warn":
                showToast("Sync", "Note: " + result.msg, "warning");
                saveSyncProgress(result.task_id, result.failed)
                break;
            default:
                console.warn("Unhandled task status " + result.status);
                break;
        }
    });
}

async function checkTasks(force_check = false) {
    if (force_check || (!isMobile() && (!ping_failed) && taskStore.getObj('tasks') != null && !taskStore.getObj('tasks').isEmpty())) {
        let results = await getResults().catch(_ => {
        });
        if (results != null)
            handleResults(results);
    }
}

// noinspection JSIgnoredPromiseFromCall
if (!isMobile()) {
    if (daw_button != null)
        daw_button.removeAttribute('hidden');
    sync_button.removeAttribute('hidden');
    if (!taskStore.getObj('sync_in_progress'))
        sync_button.removeAttribute('disabled');
    checkConnection();
    setInterval(checkConnection, 15000);
}
// noinspection JSIgnoredPromiseFromCall
checkTasks(true);
setInterval(checkTasks, 3000);
