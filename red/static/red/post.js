function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// $(function() {
$(".vote").click((event) => {
    if (event.target.id == "down") {
        direction = 0
    } else {
        direction = 1
    }
    fetch('vote/', {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({
            "v": direction // 1 for up 0 for down
        })
    }).then((output) => {
        switch (output.status) {
            case 204: // success
                window.location.reload()
                break;
            case 410:
                alert("You have aleady voted on this post.")
            default:
                alert("Something went wrong!")
                break;
        }
    })
})

$.fn.changeElementType = function(type) {
    const attributes = {};

    $.each(this[0].attributes, function(idx, attribute) {
        attributes[attribute.nodeName] = attribute.nodeValue;
    });

    this.replaceWith(function() {
        return $("<" + type + "/>", attributes).append($(this).contents());
    });
}

formOpen = false;

$("#update").click(() => {
    if (formOpen) {
        fetch('update/', {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({
                content: $("#content").val()
            })
        }).then((output) => {
            switch (output.status) {
                case 204: // success
                    window.location.reload()
                    break;
                case 410:
                    alert("Post has already been deleted!")
                    window.location.reload()
                    break;
                default:
                    alert("Something went wrong!")
                    break;
            }
        })
    } else {
        formOpen = true;
        $("#content").changeElementType("textarea")
        $("#update").text("Save")
        $("#cancel").attr("style", "display:default")
    }
})

$("#cancel").click(() => {
    formOpen = false;
    $("#content").changeElementType("p")
    $("#update").text("Edit")
    $("#cancel").attr("style", "display:none")
})

$("#delete").click(() => {
        fetch('delete/', {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            }
        }).then((output) => {
            switch (output.status) {
                case 204: // success
                    window.location.reload()
                    break;
                case 410:
                    alert("Post has already been deleted!")
                    window.location.reload()
                    break;
                default:
                    alert("Something went wrong!")
                    break;
            }
        })
    })
    // })