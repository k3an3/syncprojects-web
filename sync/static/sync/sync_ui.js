const sync_button = document.querySelector('#sync_button');
const daw_button = document.querySelector('#daw_button');
const undo_button = document.querySelector('#undo_button');
const final_undo_countdown = document.querySelector('#undo_countdown');
const final_undo_button = document.querySelector('#final_undo_button');
const sync_modal = new bootstrap.Modal(document.querySelector("#sync_modal"), {});
const undo_modal = new bootstrap.Modal(document.querySelector("#undo_modal"), {});
const sync_modal_body = document.querySelector("#sync-modal-body");
const progress = document.querySelector("#sync_progress");
const alert_div = document.querySelector('#alert');
let ping_failed = true;
let auth_attempt = false;
// maybe will use to remind the user to fill out changes if they haven't done any yet
let changelog_pending = false;

if (taskStore.getObj('changelog_todo') == null)
    taskStore.setObj('changelog_todo', []);


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
    if (ping_failed) {
        document.location = "/sync/download";
        return;
    }
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
        undo_button.setAttribute("hidden", "hidden");
        if (!status) {
            daw_button.innerHTML = "Sync & Open <span class=\"fas fa-arrow-up-right-from-square\"></span>";
            daw_button.className = "btn btn-sm btn-success";
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
        //sync_button.disabled = true;
        disableDawButton();
        sync_button.className = "btn btn-sm btn-success";
        sync_button.innerHTML = "Download Sync Client <span class=\"fas fa-download\"></span>";
    });
    if (result != null) {
        if (result.result == "pong") {
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
        if (!auth_attempt && !result.auth) {
            auth_attempt = true;
            console.log("Open client auth window");
            showToast("Sync Client Login", "<p>We're trying to log you in to syncprojects-client. If the popup is blocked, click <a href=\"/sync/client_login/\">here</a>.</p><p>This message will appear again after refresh.</p>", "info");
            window.open('/sync/client_login/');
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

function closeSyncModal() {
    if (changelog_pending) {
        if (!confirm("You haven't entered any changes. Are you sure you want to close?")) {
            return;
        }
    }
    sync_modal.hide();
}

const close_buttons = document.querySelectorAll('.close-sync-modal');
close_buttons.forEach(el => el.addEventListener('click', closeSyncModal));

document.addEventListener('click', e => {
    console.log(e);
    if (e.target && e.target.classList.contains("view-changes")) {
    } else if (e.target && e.target.classList.contains("changelog-submit")) {
        changelog_pending = false;
        let id = e.target.id.split('-')[2]
        submitChangelog(parseInt(id), document.querySelector(`#changelog-${id}`).value);
        showToast("Success", "Submitted your changes.", "success");
        e.target.setAttribute("hidden", "hidden");
        document.querySelector(`#changelog-${id}`).disabled = true;
    }
});

async function processChangelogs(id, revision) {
    let changelogs = await getChangelogs(id, revision)
    console.log(changelogs);
    let result = '';
    changelogs.forEach(c => {
        result += `<h5>${c.date_created} &mdash; ${c.user}</h5><p>${c.text}</p>`
    });
    return result;
}

async function syncResultHandler(data) {
    console.log("displaying sync results, fetched from storage");
    let html = `<p class="text-muted"><small>(${data.task_id})</small></p>`;
    let results = taskStore.getObj('sync-' + data.task_id);
    if (results == null) {
        console.warn("Results were null. Skipping...");
        return;
    }
    for (const project_result of results) {
        console.log(project_result);
        html += `<h3>${project_result.project}</h3>`;
        if (project_result.songs != null && project_result.songs.length) {
            html += '<span class="badge bg-success">Success</span>';
            html += '<ul class="list-group">'
            for (const song_result of project_result.songs) {
                let after_action = "";
                if (song_result.action == "remote") {
                    let revision = song_result.revision || 0;
                    let changelogs = await processChangelogs(song_result.id, revision - 1);
                    after_action = ` <a class="view-changes" data-bs-toggle="collapse" id="#collapse-${song_result.id}-rev-${revision}-btn" href="#collapse-${song_result.id}" role="button" aria-expanded="false" aria-controls="collapse-${song_result.id}">Show/Hide Changes</a>`;
                    after_action += `<div class="collapse" id="collapse-${song_result.id}">
  <div class="card card-body">
    ${changelogs || 'No changes found.'} 
  </div>
</div>`;
                    /*
                    document.querySelector(".view_changes").addEventListener('click', (e) => {
                        console.log(this);
                    });
                     */
                } else if (song_result.action == "local") {
                    // TODO
                    // appendChangelogTodo(song_result.song);
                    changelog_pending = true;
                    after_action = `<textarea class="form-control" id="changelog-${song_result.id}" placeholder="What did you change..."></textarea>
   <button class="btn btn-primary btn-sm changelog-submit" id="changelog-btn-${song_result.id}">Submit</button>
</div>`;
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
            }
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
                unlock = " Someday, you will be able to work around this yourself... In the meantime, contact support.";
            html += `<p class="text-danger">Locked by ${project_result.lock.locked_by}${since}.${reason}${unlock}</p>`;
        } else {
            html += '<span class="badge bg-warning">None</span>';
            html += '<p class="text-muted">No results.</p>';
        }
    }
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
        undo_button.removeAttribute("hidden");
    }
}

const task_name_map = {
    'workon': "Check out",
    'workdone': "Check in"
}

async function handleResults(data) {
    if (!data.results.length) {
        return;
    }
    console.log("Got results");
    console.log(data.results);
    for (const result of data.results) {
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
                        await syncResultHandler(result);
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
    }
}

let FINAL_UNDO_TIME = 3;
let final_undo_counter = FINAL_UNDO_TIME;

final_undo_button.addEventListener('click', async _ => {
    undo_button.setAttribute('hidden', 'hidden');
    showToast("Sync", "Undoing checkout... <span class=\"fas fa-hourglass-start\"></span>");
    progress.removeAttribute('hidden');
    daw_button.innerHTML = "Undoing checkout... <span class=\"fas fa-hourglass-start\"></span>";
    daw_button.disabled = true;
    sync_button.disabled = true;
    let context = getContext();
    taskStore.setObj('sync_in_progress', true);
    let msg = {'song': {'song': context.song, 'project': context.project}, 'undo': true};
    console.log("Undo song checkout")
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
});

function count_down() {
    final_undo_countdown.innerHTML = final_undo_counter;

    if (final_undo_counter) {
        setTimeout(count_down, 1000);
        final_undo_counter--;
    } else {
        final_undo_button.removeAttribute('disabled');
        final_undo_countdown.innerHTML = "";
    }
}

if (undo_button != null) {
    undo_button.addEventListener('click', _ => {
        final_undo_counter = FINAL_UNDO_TIME;
        final_undo_button.setAttribute('disabled', 'disabled');
        undo_modal.show();
        count_down();
    });
}

async function checkTasks(force_check = false) {
    if (force_check || (!isMobile() && (!ping_failed) && taskStore.getObj('tasks') != null && !isEmpty(taskStore.getObj('tasks')))) {
        let results = await getResults().catch(_ => {
        });
        if (results != null)
            await handleResults(results);
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

if (taskStore.getObj('sync-disabled')) {
    console.debug("Sync is disabled.")

} else {
    if (!isMobile()) {
        let isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
        if (isSafari) {
            // We don't support Safari
            document.querySelector('#safari').removeAttribute('hidden');
            if (taskStore.getItem('safari_warn') != '1') {
                alert("Safari does not properly follow web browser standards set by the World Wide Web Consortium (W3C) and therefore does not work with the syncprojects client. Please use another browser that properly follows the standards, such as Google Chrome or Mozilla Firefox.");
                taskStore.setItem('safari_warn', '1');
            }
        } else {
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
    }

    handleSyncInProgress();
    checkTasks(true);
    setInterval(checkTasks, 1000);
}