$(function() {
    $("#logout").click(() => {
        fetch('/logout/', {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            }
        }).then((output) => {
            switch (output.status) {
                case 204: // success
                    alert("You have been logged out.")
                    window.location.reload()
                    break;
                default:
                    alert("Something went wrong!")
                    break;
            }
        })
    })
})