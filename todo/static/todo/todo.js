const csrf_token = "";

async function handleCheck(e) {
    let todo = e.currentTarget.id.split('-')[1];
    let checkbox = document.getElementById('todo-' + todo);
    let text = document.getElementById('todo-text-' + todo);
    let result = await APIRequest('todo/check/', 'POST', {'id': todo});
    if (result.checked) {
        checkbox.setAttribute('checked', 'checked');
        text.className = "text-muted text-decoration-line-through";
    } else {
        checkbox.removeAttribute('checked');
        text.className = "";
    }
}

bindEventToSelector('.todo-checkbox', handleCheck);