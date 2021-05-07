const proj_re = /projects\/(?<project>[0-9]+)\/(songs\/(?<song>[0-9]+)\/)?/;
const sync_button = document.querySelector('#sync_button');
const daw_button = document.querySelector('#daw_button');
const sync_modal = new bootstrap.Modal(document.querySelector("#sync_modal"), {});
const sync_modal_body = document.querySelector("#sync-modal-body");
const progress = document.querySelector("#sync_progress");
const alert = document.querySelector('#alert');
let ping_failed = true;

if (taskStore.getObj('changelog_todo') == null)
    taskStore.setObj('changelog_todo', []);

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
        if (!isSongCheckedOut()) {
            showToast("Sync", "Syncing and opening song in DAW... <span class=\"fas fa-hourglass-start\"></span>");
            progress.removeAttribute('hidden');
            daw_button.innerHTML = "Opening... <span class=\"fas fa-hourglass-start\"></span>";
            daw_button.disabled = true;
            sync_button.disabled = true;
            let context = getContext();
            console.log("Got context");
            console.log(context);
            let result;
            taskStore.setObj('sync_in_progress', true);
            let msg = {'song': {'song': context.song, 'project': context.project}};
            console.log("Working on song")
            console.log(msg);
            result = await workOn(msg);
            console.log("Got initial response");
            console.log(result);
            if (result.result === "started") {
                showToast("Sync", "Sync started <span class=\"fas fa-check\"></span>");
                pushTask(result.task_id, 'workon');
            } else {
                console.warn("Unknown response.");
            }
        } else {
            showToast("Sync", "Syncing and checking song back in... <span class=\"fas fa-hourglass-start\"></span>");
            progress.removeAttribute('hidden');
            daw_button.innerHTML = "Checking in... <span class=\"fas fa-hourglass-start\"></span>";
            daw_button.disabled = true;
            sync_button.disabled = true;
            let context = getContext();
            taskStore.setObj('sync_in_progress', true);
            let msg = {'song': {'song': context.song, 'project': context.project}};
            console.log("Work done on song")
            console.log(msg);
            let result = await workDone(msg);
            console.log("Got initial response");
            console.log(result);
            if (result.result === "started") {
                showToast("Sync", "Sync started <span class=\"fas fa-check\"></span>");
                pushTask(result.task_id, 'workdone');
            } else {
                console.warn("Unknown response.");
            }
        }
    });

sync_button.addEventListener('click', async _ => {
    showToast("Sync", "Starting sync... <span class=\"fas fa-hourglass-start\"></span>");
    progress.removeAttribute('hidden');
    sync_button.innerHTML = "Syncing... <span class=\"fas fa-hourglass-start\"></span>";
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
        result = await startSync(msg);
    } else if (context.song == null) {
        // Sync single project
        let msg = {'projects': [context.project]};
        console.log("Syncing project");
        console.log(msg);
        result = await startSync(msg);
    } else {
        // Sync single song
        let msg = {'songs': [{'song': context.song, 'project': context.project}]};
        console.log("Syncing song")
        console.log(msg);
        result = await startSync(msg);
    }
    console.log("Got initial response");
    console.log(result);
    if (result.result === "started") {
        showToast("Sync", "Sync started <span class=\"fas fa-check\"></span>");
        pushTask(result.task_id, 'sync');
    } else {
        showToast("Sync", "Something went wrong! Contact support.", "danger");
        console.warn("Unknown response.");
    }
});

function disableDawButton(status = true) {
    if (daw_button != null) {
        daw_button.disabled = status;
        if (!status) {
            daw_button.innerHTML = "Open in DAW";
            daw_button.className = "btn btn-sm btn-secondary";
        }
    }
}

function enableSyncButton() {
    sync_button.className = "btn btn-sm btn-primary";
    sync_button.innerHTML = "Sync <span class=\"fas fa-sync\"></span>";
    sync_button.disabled = false;
    disableDawButton(false);
    handleSongCheckedOut();
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
            sync_button.innerHTML = "Syncing... <span class=\"fas fa-hourglass-start\"></span>";
            sync_button.disabled = true;
            disableDawButton();
        } else {
            enableSyncButton();
        }
    }
}

const sync_action_mapping = {
    local: "Your changes were sent to the server.",
    remote: "New changes were received from the server:",
    null: "No actions were taken.",
    error: "An error occured during sync.",
    disabled: "Sync is disabled for this song.",
    locked: "The song is locked by another sync.",
}

const action_icon_mapping = {
    local: 'cloud-upload-alt',
    remote: 'cloud-download-alt',
    null: '',
    disabled: '',
    locked: 'lock',
    error: 'exclamation-triangle',
}

function appendChangelogTodo(name) {
    let td = taskStore.getObj('changelog_todo');
    td.push(name);
    taskStore.setObj(td);
}


function syncResultHandler(data) {
    console.log("displaying sync results, fetched from storage");
    let html = `<p class="text-muted"><small>(${data.task_id})</small></p>`;
    let results = taskStore.getObj('sync-' + data.task_id);
    if (results == null) {
        console.warn("Results were null. Skipping...");
        return;
    }
    results.forEach(project_result => {
        console.log(project_result);
        html += `<h3>${project_result.project}</h3>`;
        if (project_result.songs != null && project_result.songs.length) {
            html += '<span class="badge bg-success">Success</span>';
            html += '<ul class="list-group">'
            project_result.songs.forEach(song_result => {
                let after_action = "";
                if (song_result.action == "remote") {
                    after_action = ` <a data-bs-toggle="collapse" href="#collapse-${song_result.id}" role="button" aria-expanded="false" aria-controls="collapse-${song_result.id}">View Changes</a>`;
                    after_action += `<div class="collapse" id="collapse-${song_result.id}">
  <div class="card card-body">
    ${song_result.changes || 'No changes found.'} 
  </div>
</div>`;
                } else if (song_result.action == "local") {
                    // TODO
                    // appendChangelogTodo(song_result.song);
                    after_action = `<textarea class="form-control" id="changelog-${song_result.id}" placeholder="What did you change..."></textarea>
   <button class="btn btn-primary btn-sm" class="changelog-submit" id="changelog-btn-${song_result.id}">Submit</button>
</div>`;
                    document.querySelector(`#changelog-btn-${song_result.id}`).addEventListener('click', element => {
                        submitChangelog(getContext().project, song_result.id, document.querySelector(`changelog-${song_result.id}`).textContent);
                    });
                }
                let bg = "success";
                if (song_result.result == "error") {
                    bg = "danger";
                }
                html += '<li class="list-group-item d-flex justify-content-between align-items-start">';
                html += `<div class="ms-2 me-auto"><div class="fw-bold">${song_result.song}&nbsp;<span class="fas fa-${action_icon_mapping[song_result.action]}"></span></div>${sync_action_mapping[song_result.action]}${after_action}</div>`;
                if (song_result.action != null && song_result.action != 'disabled') {
                    console.log(song_result)
                    html += `<span class="badge bg-${bg} rounded-pill">${song_result.result}</span>`;
                }
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
    showToast("Sync", `Sync for project "${data.project}" complete <span class=\"fas fa-check\"></span>`);
    console.log("Ok... saving progress...");
    console.log(data);
    let stored = taskStore.getObj('sync-' + task_id);
    if (stored == null || isEmpty(stored)) {
        stored = [];
    }
    stored.push(data);
    taskStore.setObj('sync-' + task_id, stored);
}

function setSongCheckedOut() {
    let context = getContext();
    let checked_out = taskStore.getObj('checked_out');
    if (checked_out == null || isEmpty(checked_out))
        checked_out = [];
    checked_out.push(context.song);
    taskStore.setObj('checked_out', checked_out);
}

function setSongCheckedIn() {
    let context = getContext();
    let checked_out = taskStore.getObj('checked_out');
    checked_out.splice(checked_out.indexOf(context.song, 1));
    taskStore.setObj('checked_out', checked_out);
}

function isSongCheckedOut() {
    let context = getContext();
    if (context.song != null) {
        let checked_out = taskStore.getObj('checked_out');
        if (checked_out == null)
            return false;
        return checked_out.includes(context.song);
    }
    return false;
}

function handleSongCheckedOut() {
    if (isSongCheckedOut()) {
        sync_button.disabled = true;
        daw_button.innerHTML = "Check in <span class=\"fas fa-clipboard-check\"></span>";
        daw_button.className = "btn btn-sm btn-primary";
    }
}

const task_name_map = {
    'workon': "Check out",
    'workdone': "Check in"
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
        // TODO gross
        if (task == null) {
            console.warn("Task was null, bailing...");
            return;
        }
        console.log("Got task");
        console.log(task);
        // TODO: this switch seems backwards... Check task type first, then handle level
        switch (result.status) {
            case "complete":
                console.log("Handle sync completion");
                progress.setAttribute("hidden", "hidden");
                let name = task_name_map[task];
                if (name == null)
                    name = task[0].toUpperCase() + task.substr(1);
                showToast("Sync", name + " complete <span class=\"fas fa-check\"></span>", "success");
                popTask(result.task_id);
                switch (task) {
                    case 'sync':
                        taskStore.setObj('sync_in_progress', false);
                        enableSyncButton();
                        disableDawButton(false);
                        syncResultHandler(result);
                        break;
                    case 'workon':
                        taskStore.setObj('sync_in_progress', false);
                        setSongCheckedOut();
                        break;
                    case 'workdone':
                        taskStore.setObj('sync_in_progress', false);
                        setSongCheckedIn();
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
                progress.setAttribute("hidden", "hidden");
                enableSyncButton();
                disableDawButton(false);
                if (result.msg == null) {
                    result.msg = "An unhandled error occurred in the client. Contact support";
                }
                showToast("Sync", "Oops! " + result.msg, "danger");
                taskStore.setObj('sync_in_progress', false);
                break;
            case "warn":
                showToast("Sync", "Note: " + result.msg + " <span class=\"fas fa-exclamation-triangle\"></span>", "warning");
                saveSyncProgress(result.task_id, result.failed)
                break;
            case "tasks":
                if (result.tasks == null || result.tasks.length == 0) {
                    console.log("Clearing out tasks...");
                    enableSyncButton();
                    clearTasks();
                    progress.setAttribute("hidden", "hidden");
                    taskStore.setObj('sync_in_progress', false);
                }
                break;
            default:
                console.warn("Unhandled task status " + result.status);
                break;
        }
    });
}

async function checkTasks(force_check = false) {
    if (force_check || (!isMobile() && (!ping_failed) && taskStore.getObj('tasks') != null && !isEmpty(taskStore.getObj('tasks')))) {
        let results = await getResults().catch(_ => {
        });
        if (results != null)
            handleResults(results);
    }
}

async function handleSyncInProgress() {
    if (taskStore.getObj('sync_in_progress')) {
        // noinspection JSIgnoredPromiseFromCall
        progress.removeAttribute('hidden');
        let result = await getTasks();
        pushTask(result.task_id, 'tasks');
    }
}

if (!isMobile()) {
    if (daw_button != null)
        daw_button.removeAttribute('hidden');
    sync_button.removeAttribute('hidden');
    if (!taskStore.getObj('sync_in_progress')) {
        sync_button.removeAttribute('disabled');
        disableDawButton(false);
    }
    checkConnection();
    setInterval(checkConnection, 15000);
}

handleSyncInProgress();
checkTasks(true);
setInterval(checkTasks, 1000);
