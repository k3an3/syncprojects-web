let console_ = console;
if (!document.location.host.startsWith("localhost"))
    console = new Proxy({}, {
        get(target, name) {
            return function () {
            };
        }
    })

