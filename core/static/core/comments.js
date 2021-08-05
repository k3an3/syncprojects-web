const comment_div = document.querySelector('#comment-div');
const comment_div_inner = document.querySelector('#comment-div-inner');
const comment_field = document.querySelector('#comment-field');
const comment_form = document.querySelector('#comment-form');
const comment_delete_modal = new bootstrap.Modal(document.querySelector('#comment-delete-modal'));

async function addComment(comment) {
    let content = `<div class="card col-md-8" id="comment-${comment.id}"><div class="card-header">`;
    content += `<a href="/users/${userid}/">${username}</a> &mdash; Just now `;
    let time = '';
    if (comment.song_time) {
        let song_time = parseInt(comment.song_time);
        let minutes = Math.floor(song_time / 60);
        let seconds = song_time % 60;
        time = `<a role="button" class="timecode-link" onclick="awp_player.seek(${comment.song_time});"><h5>${minutes}:${pad(seconds)}</h5></a>`;
    }
    content += `</div><div class="card-body">${time}<p class="card-text">${comment.text}</p></div>`;
    content += `<div class="card-footer text-muted">
<button class="btn btn-link btn-sm text-muted">Edit</button>
<button id="comment-delete-btn-${comment.id}" class="btn btn-link btn-sm text-muted">Delete</button>
0<button class="btn btn-link btn-sm text-muted">Assign</button>
<button id="comment-unresolve-btn-${comment.id}" class="btn btn-link btn-sm text-muted">Mark as needing resolution</button>
</div></div>`;
    comment_div_inner.innerHTML = content + comment_div_inner.innerHTML;
    document.querySelector('#comment-delete-btn-' + comment.id).addEventListener('click', deleteComment);
    document.querySelector('#comment-unresolve-btn-' + comment.id).addEventListener('click', resolveComment);
    fadeIn(document.querySelector('#comment-' + comment.id));
}

function getCommentId(id) {
    return id.split('-')[3];
}

let comment_to_delete = '';

async function deleteComment(event) {
    comment_to_delete = getCommentId(event.target.id);
    comment_delete_modal.show();
}

async function doDeleteComment() {
    await commentDelete(comment_to_delete);
    showToast("Comments", "Comment deleted successfully.", "success");
    fadeOut(document.querySelector("#comment-" + comment_to_delete));
    comment_to_delete = '';
    comment_delete_modal.hide()
}

document.querySelector('#confirm-comment-delete').addEventListener('click', doDeleteComment);

async function clearComment() {
    comment_field.value = "";
    if (clicked) {
        handleCommentTimeClick();
    }
}

async function commentFormSubmit(event) {
    event.preventDefault();
    let context = getContext();
    let elements = comment_form.elements;
    let data = {
        text: elements.text.value,
        project: context.project,
        song: context.song
    };
    if (elements.song_time) {
        data.song_time = parseInt(elements.song_time.value);
    }
    let resp = await comment(data);
    data.id = resp.id;
    await addComment(data);
    await clearComment();
    showToast("Comments", "Comment posted successfully!", "success");
}

async function resolveComment(event) {
    let comment = getCommentId(event.target.id);
    if (event.target.id.split('-')[1] === "unresolve") {
        await commentUnresolve(comment);
        showToast("Comments", "Comment marked as needing resolution", "success");
        event.target.innerHTML = "Mark as resolved";
        event.target.id = event.target.id.replace('unresolve', 'resolve');
        event.target.parentElement.parentElement.firstElementChild.innerHTML += '<span class="badge bg-warning">Unresolved</span>';
    } else {
        await commentResolve(comment);
        showToast("Comments", "Comment resolved successfully!", "success");
        fadeOut(document.querySelector("#comment-" + comment));
    }
}

bindEventToClass('.comment-delete', deleteComment);
bindEventToClass('.comment-resolve', resolveComment);

if (comment_form) {
    comment_form.addEventListener('submit', commentFormSubmit);
}

if (comment_field != null) {
    comment_field.addEventListener('keyup', k => {

    });
}
