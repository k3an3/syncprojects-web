const comment_div = document.querySelector('#comment-div');
const comment_div_inner = document.querySelector('#comment-div-inner');
const comment_field = document.querySelector('#comment-field');
const comment_form = document.querySelector('#comment-form');

async function addComment(comment) {
    let content = '<div class="card col-md-8"><div class="card-header">';
    content += `<a href="/users/${userid}/">${username}</a> &mdash; Just now`;
    let time = '';
    if (comment.song_time) {
        let song_time = parseInt(comment.song_time);
        let minutes = Math.floor(song_time / 60);
        let seconds = song_time % 60;
        time = `<a role="button" class="timecode-link" onclick="awp_player.seek(${comment.song_time});"><h5>${minutes}:${pad(seconds)}</h5></a>`;
    }
    content += `</div><div class="card-body">${time}<p class="card-text">${comment.text}</p></div>`;
    content += '<div class="card-footer text-muted"><button class="btn btn-link btn-sm text-muted">Edit</button><button class="btn btn-link btn-sm text-muted">Delete</button>0<button class="btn btn-link btn-sm text-muted">Assign</button><button class="btn btn-link btn-sm text-muted">Mark as needing resolution</button></div></div>'
    comment_div_inner.innerHTML = content + comment_div_inner.innerHTML;
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
        song: context.song
    };
    if (elements.song_time) {
        data.song_time = parseInt(elements.song_time.value);
    }
    await comment(data);
    await addComment(data);
    await clearComment();
    showToast("Comments", "Comment posted successfully!", "success");
}

if (comment_form) {
    comment_form.addEventListener('submit', commentFormSubmit);
}

if (comment_field != null) {
    comment_field.addEventListener('keyup', k => {

    });
}
