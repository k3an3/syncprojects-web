async function do_login() {
    await localRequest('auth', 'POST', {'data': "{{ auth_data }}"}).then(_ => {
        window.location.href = "{% url 'sync:client-login-success' %}";
    }).catch(error => {
        alert(error);
    });
}

do_login();
