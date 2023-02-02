let agreed = false;
const blue = "#3E4E8E";
const gunmetal = "#5b6d77";
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

    $("#agreefield").change(function() {
        if (this.checked) {
            $("#checkbox").addClass("selected");
            agreed = true;
            if ($("#email").val() != "" && $("#password").val() != "") {
                $("#createaccount").addClass("accentshould");
            }
        } else {
            $("#checkbox").removeClass("selected");
            agreed = false;
            $("#createaccount").removeClass("accentshould");
        }
    });

    $("input").on("keypress", function() {
        if (agreed && $("#email").val() != "" && $("#password").val() != "") {
            $("#createaccount").addClass("accentshould");
        } else {
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
                    case 400:
                        alert("Bad request!")
                        break;
                    case 403:
                        alert("Invalid Credentials!")
                    default:
                        alert("Something went wrong!")
                        break;
                }
            })
        })
    });

    $("#createaccount").click(function() {
        $("#emaildiv,#confirmdiv,#agreediv").removeClass("hidden");
        $("#login").removeClass("accentshould");
        $(".hidden").css("display", "auto");

        const unfocus = setTimeout(function() {
            $("#createaccount").blur();
        }, 300);

        if (!agreed && attempts >= 1) {
            $("#wrongdoing").text("You must agree to create your account.");
            $("#wrongdiv").removeClass("hidden");
        } else if ($("#confirm").val() != $("#password").val() && attempts >= 1) {
            $("#wrongdoing").text("The passwords you entered do not match.");
            $("#wrongdiv").removeClass("hidden");
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
                            alert("Bad request!")
                            break;
                        case 403:
                            alert("This username or email is taken!")
                        default:
                            alert("Something went wrong!")
                            break;
                    }
                })
            })
        }
        attempts++;
    });
    $("label").hover(
        function() {
            $("#checkbox").css("border-color", blue);
        },
        function() {
            $("#checkbox").css("border-color", gunmetal);
        }
    );
    $("input").on("keypress", function(e) {
        if (e.which == 13) {
            $(".accentshould").click();
        }
    });
});