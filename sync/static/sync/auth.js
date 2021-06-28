const auth_token = document.querySelector("#auth_token");
const redirect_url = document.querySelector("#redirect_url");

function timeout(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

const do_login = async (n = 3) => {
    try {
        return await localRequest('auth', 'POST', {'data': auth_token.value}, false, false);
    } catch (err) {
        if (n === 1) throw err;
        await timeout(1000);
        return await do_login(n - 1);
    }
};

do_login().then(_ => {
    window.location.href = redirect_url.value;
}).catch(e => {
    alert("Oops! Something went wrong. Try again, or contact support.");
    console.log(e);
})
