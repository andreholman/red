const SALT = "J33chivedMDjKs0bx65"

async function sha256(string) {
    const utf8 = new TextEncoder().encode(string);
    const hashBuffer = await crypto.subtle.digest('SHA-256', utf8);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray
        .map((bytes) => bytes.toString(16).padStart(2, '0'))
        .join('');
    return hashHex;
}

$(document).ready(function() {
    function successOptions() {
        $(".inputfield").addClass("hidden")
        $("#nextdiv, #successdiv").removeClass("hidden")
    }

    function displayLoader() {
        $("#loading").attr("style", "opacity: 1")
        $("#send, #change").attr("value", "")
    }

    function hideLoader(submitLabel) {
        $("#loading").attr("style", "opacity: 0")
        $("#send").attr("value", submitLabel)
    }

    function alert_issue(issue) {
        $("#wrongdoing").text(issue);
        $("#wrongdiv").removeClass("hidden")
    }

    $("#change").click(function() {
        if ($("#password").val() == $("#confirm").val()) {
            displayLoader();
            sha256(SALT + $("#password").val()).then((hashed) => {
                fetch(location.pathname, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCookie("csrftoken")
                    },
                    body: JSON.stringify({
                        password: hashed
                    })
                }).then((output) => {
                    switch (output.status) {
                        case 204: // success
                            successOptions();
                            break;
                        case 410:
                            alert_issue("This request has expired.")
                            break;
                    }
                }).catch((error) => {
                    if (error.name == "TypeError") {
                        alert_issue("Servers are unreachable. Check your connection and try again later.");
                    } else {
                        alert_issue("An unexpected error occured.")
                    }
                    hideLoader("CHANGE");
                })
            })
            $("#change").blur()
        } else {
            alert_issue("The passwords you entered do not match.")
        }
    });

    $("#send").click(function() {
        let email = $("#email").val()
        if (/^[a-zA-Z0-9]([\.-]?[a-zA-Z0-9]+)*@[a-zA-Z0-9][a-zA-Z0-9-\.]{0,62}[a-zA-Z0-9](\.[a-zA-Z]{2,63})$/.test(email)) {
            displayLoader();

            fetch("/createlinkverifiedrequest/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify({
                    email: email,
                    purpose: "P"
                })
            }).then((output) => {
                switch (output.status) {
                    case 204: // success
                        successOptions();
                        break;
                    case 404:
                        alert_issue("Could not find an account matching that email address.");
                        hideLoader("EMAIL ME");
                        break;
                    case 429:
                        alert_issue("You already have a pending request. Open the link that was sent to your email.")
                        $("#submitdiv").addClass("hidden")
                        break;
                    case 503:
                        alert_issue("Email failed to send.")
                        hideLoader("EMAIL ME");
                        break;
                }
            }).catch((error) => {
                if (error.name == "TypeError") {
                    alert_issue("Servers are unreachable. Check your connection and try again later.");
                    hideLoader("EMAIL ME");
                } else {
                    alert_issue("An unexpected error occured.")
                    hideLoader("EMAIL ME");
                }
            })
            $("#send").blur()
        } else {
            alert_issue("Enter a valid email.");
        }
    })

    $("#back").click(function() {
        window.location.replace("/resetpassword/");
    })

    $("#home").click(function() {
        window.location.replace("/");
    })

    $("#login").click(function() {
        window.location.replace("/login/")
    })

    $("input").on("keypress", function(e) {
        if (e.which == 13) {
            $(".accentshould").click();
            e.preventDefault();
        }
    });
});