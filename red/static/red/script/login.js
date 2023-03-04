let agreed = false;
const blue3 = "#3E4E8E";
const gray = "#515164";
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
    let attempts = 0;

    function alert_issue(issue) {
        $("#wrongdoing").text(issue);
        $("#wrongdiv").removeClass("hidden")
    }

    function handleRequestError(error) {
        if (error.name == "TypeError") {
            alert_issue("Servers are unreachable. Check your connection and try again later.");
        } else {
            alert_issue("An unexpected error occured.")
        }
    }

    $("#agreefield").change(function() {
        if (this.checked) {
            $("#checkbox").addClass("selected");
            agreed = true;
            if ($("#email").val() != "" && $("#password").val() != "") {
                $("#createaccount").addClass("accentshould");
                $("#login").removeClass("accentshould");
            }
        } else {
            $("#checkbox").removeClass("selected");
            agreed = false;
            $("#createaccount").removeClass("accentshould");
        }
    });

    $("#login").click(function() {
        sha256(SALT + $("#password").val()).then((hashed) => {
            fetch("/login/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify({
                    username: $("#username").val().trim(),
                    email: $("#email").val(),
                    password: hashed
                })
            }).then((output) => {
                switch (output.status) {
                    case 204: // success
                        const params = new URLSearchParams(location.search)
                        window.location.replace(
                            params.get("next") ? params.get("next") : "/"
                        );
                        break;
                    case 403:
                        alert("Incorrect username or password.")
                        break;
                    default:
                        alert("Something went wrong!")
                        break;
                }
            }).catch(handleRequestError)
        })
    });

    $("#createaccount").click(function() {
        let email = $("#email").val()
        if (attempts == 0) { // first click
            $("#emaildiv,#confirmdiv,#agreediv").removeClass("hidden");
        } else if (!(/^[\w-]{3,16}$/.test($("#username").val()))) {
            alert_issue("Usernames must contain 3 to 16 alphanumeric characters, underscores, and dashes.")
        } else if (
            email.length < 7 ||
            !(/^[a-zA-Z0-9]([\.-]?[a-zA-Z0-9]+)*@[a-zA-Z0-9][a-zA-Z0-9-\.]{0,62}[a-zA-Z0-9](\.[a-zA-Z]{2,63})$/.test(email))
        ) {
            alert_issue("Enter a valid email.");
        } else if (!agreed) {
            alert_issue("You must agree to create your account.");
        } else if ($("#confirm").val() != $("#password").val()) {
            alert_issue("The passwords you entered do not match.");
        } else if ($("#password").val().length < 8) {
            alert_issue("Passwords must be eight characters or more.")
        } else {
            sha256(SALT + $("#password").val()).then((hashed) => {
                fetch('/createaccount/', {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCookie("csrftoken")
                    },
                    body: JSON.stringify({
                        username: $("#username").val().trim(),
                        email: $("#email").val(),
                        password: hashed
                    })
                }).then((output) => {
                    switch (output.status) {
                        case 204: // success
                            const params = new URLSearchParams(location.search)
                            window.location.replace(
                                params.get("next") ? params.get("next") : "/"
                            );
                            break;
                        case 400:
                            alert_issue("Bad request!")
                            break;
                        case 403:
                            alert_issue("This username or email is taken!")
                            break;
                        default:
                            alert_issue("Something went wrong!")
                            break;
                    }
                }).catch(handleRequestError)
            })
        }
        attempts++;
    });

    $("label").hover(
        function() {
            $("#checkbox").addClass("hovered");
        },
        function() {
            $("#checkbox").removeClass("hovered");
        }
    );

    $("#tos").hover(
        function() {
            $("#checkbox").removeClass("hovered");
        },
        function() {
            $("#checkbox").addClass("hovered");
        }
    )

    $("input").on("keypress", function(e) {
        if (e.which == 13 && !$("#createaccount").is(":focus")) { // on enter
            $(".accentshould").click();
        }
    });
});