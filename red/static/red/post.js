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

$.fn.changeElementType = function(type) {
    const attributes = {};

    $.each(this[0].attributes, function(idx, attribute) {
        attributes[attribute.nodeName] = attribute.nodeValue;
    });

    this.replaceWith(function() {
        return $("<" + type + "/>", attributes).append($(this).contents());
    });
}

const apiHeaders = {
    "Content-Type": "application/json",
    "X-CSRFToken": getCookie("csrftoken")
}

$(function() {
    console.info($("#content").val())
    $(".post-vote").click((event) => {
        console.log($(event.target))
        if ($(event.target).hasClass() == "down") {
            direction = 0
        } else {
            direction = 1
        }
        fetch('vote/', {
            method: "POST",
            headers: apiHeaders,
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

    editOpen = false;

    $("#update-post").click(() => {
        if (editOpen) {
            fetch('update/', {
                method: "PUT",
                headers: apiHeaders,
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
        } else { // if form is closed
            editOpen = true;
            const content = $("#content").html().replaceAll("<br>", "\n")
            $("#content").changeElementType("textarea")
            $("#content").val(content)
            $("#update-post").text("Save")
            $("#cancel-post").attr("style", "display:default")
        }
    })

    $("#cancel-post").click(() => {
        editOpen = false;

        $("#content").changeElementType("p")
        $("#update-post").text("Edit")
        $("#cancel-post").attr("style", "display:none")
    })

    $("#delete-post").click(() => {
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

    $("#comment").click(() => {
        fetch('comment/', {
            method: "POST",
            headers: apiHeaders,
            body: JSON.stringify({
                content: $("#comment-content").val(),
                parent: $("#comment-parent").val()
            })
        }).then((output) => {
            switch (output.status) {
                case 204: // success
                    window.location.reload()
                    break;
                case 400:
                    alert("Bad request!")
                    break;
                case 410:
                    alert("Post has been deleted!")
                    window.location.reload()
                    break;
                default:
                    alert("Something went wrong!")
                    break;
            }
        })
    })

    $(".comment")

    // commentOpen = false;

    // $("#reply").click(() => {
    //     if (commentOpen) {
    //         fetch('', {
    //             method: "PUT",
    //             headers: {
    //                 "Content-Type": "application/json",
    //                 "X-CSRFToken": getCookie("csrftoken")
    //             },
    //             body: JSON.stringify({
    //                 content: $("#content").val()
    //             })
    //         }).then((output) => {
    //             switch (output.status) {
    //                 case 204: // success
    //                     window.location.reload()
    //                     break;
    //                 case 410:
    //                     alert("Post/comment has been deleted!")
    //                     window.location.reload()
    //                     break;
    //                 default:
    //                     alert("Something went wrong!")
    //                     break;
    //             }
    //         })
    //     } else { // if form is closed
    //         commentOpen = true;

    //         $("#reply").text("Submit")
    //         $("#cancel-post").attr("style", "display:default")
    //     }
    // })
})