const auth_token = document.querySelector("#auth_token");
const redirect_url = document.querySelector("#redirect_url");

async function do_login() {
    await localRequest('auth', 'POST', {'data': auth_token.value}, false, false).then(_ => {
        window.location.href = redirect_url.value;
    }).catch(error => {
        alert("Oops! Something went wrong. Try again, or contact support.");
        console.log(error);
    });
}

do_login();
