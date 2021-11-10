const comment_div = document.querySelector('#comment-div');
const comment_div_inner = document.querySelector('#comment-div-inner');
const comment_field = document.querySelector('#comment-field');
const comment_form = document.querySelector('#comment-form');
const comment_delete_modal_e = document.querySelector('#comment-delete-modal');
let comment_delete_modal;
if (comment_delete_modal_e) {
    comment_delete_modal = new bootstrap.Modal(comment_delete_modal_e);
}

async function addComment(comment) {
    let content = `<div class="card col-md-8" id="comment-${comment.id}"><div class="card-header">`;
    content += `<a href="/users/${userid}/">${username}</a> &mdash; Just now `;
    let time = '';
    if (comment.song_time) {
        let song_time = parseInt(comment.song_time);
        let minutes = Math.floor(song_time / 60);
        let seconds = song_time % 60;
        time = `<a role="button" class="timecode-link" onclick="wavesurfer.play(${comment.song_time});"><h5>${minutes}:${pad(seconds)}</h5></a>`;
    }
    content += `</div><div class="card-body">${time}<p class="card-text">${comment.text}</p></div>`;
    content += `<div class="card-footer text-muted">
<button class="btn btn-link btn-sm text-muted comment-edit">Edit</button>
<button id="comment-delete-btn-${comment.id}" class="btn btn-link btn-sm text-muted comment-delete">Delete</button>
0<button class="btn btn-link btn-sm text-muted comment-assign">Assign</button>
<button id="comment-unresolve-btn-${comment.id}" class="btn btn-link btn-sm text-muted comment-resolve">Mark as needing resolution</button>
</div></div>`;
    if (comment.parent) {
        let parent = document.getElementById("comment-" + comment.parent);
        parent.parentElement.innerHTML += '<div style="padding-left:10px;">' + content + '</div>';
    } else {
        comment_div_inner.innerHTML = content + comment_div_inner.innerHTML;
    }
    bindEventToSelector('.comment-delete', deleteComment);
    bindEventToSelector('.comment-resolve', resolveComment);
    fadeIn(document.querySelector('#comment-' + comment.id));
    window.location = "#comment-" + comment.id;
}

function getCommentId(id) {
    return id.split('-')[3];
}

async function likeComment(event) {
    let comment = getCommentId(event.currentTarget.id);
    let result = await commentLike(comment);
    let likeBtn = document.getElementById("comment-like-btn-" + comment);
    document.getElementById("comment-likes-" + comment).innerText = result.likes;
    if (result.liked) {
        likeBtn.className = "btn btn-link btn-sm btn-primary text-muted comment-like";
        showToast("Comments", "Comment liked");
    } else {
        likeBtn.className = "btn btn-link btn-sm text-muted comment-like";
        showToast("Comments", "Comment unliked");
    }
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

const cdc = document.querySelector('#confirm-comment-delete');
if (cdc) {
    cdc.addEventListener('click', doDeleteComment);
}

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
        song: context.song,
        parent: elements.parent.value ? parseInt(elements.parent.value) : "",
    };
    if (!data.text.length) {
        showToast("Comments", "Can't add comment. You must enter text.", "danger");
        return;
    }
    if (elements.song_time) {
        data.song_time = parseInt(elements.song_time.value);
    }
    let resp = await comment(data);
    data.id = resp.id;
    await addComment(data);
    await clearComment();
    showToast("Comments", "Comment posted successfully!", "success");
    try {
        await setUpMarkers();
    } catch (e) {
    }
}

async function resolveComment(event) {
    let comment = getCommentId(event.target.id);
    console.log(comment);
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
    if (playerActive) {
        await setUpMarkers();
    }
}

let lastReply;
async function replyComment(event) {
    let comment = getCommentId(event.target.id);
    if (lastReply) {
        lastReply.className = "btn btn-link btn-sm text-muted comment-reply";
    }
    lastReply = event.target;
    lastReply.className = "btn btn-link btn-sm btn-primary comment-reply"
    console.log(comment);
    document.getElementById("comment-parent").value = comment;
    document.getElementById("comment-field").setAttribute("placeholder", "Reply to comment...");
    window.location = "#comment-div";
}

bindEventToSelector('.comment-delete', deleteComment);
bindEventToSelector('.comment-resolve', resolveComment);
bindEventToSelector('.comment-like', likeComment);
bindEventToSelector('.comment-reply', replyComment);

if (comment_form) {
    comment_form.addEventListener('submit', commentFormSubmit);
}

if (comment_field != null) {
    comment_field.addEventListener('keyup', k => {

    });
}
