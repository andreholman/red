const apiHeaders = {
    "Content-Type": "application/json",
    "X-CSRFToken": getCookie("csrftoken")
}

$(function() {
    $(".post-vote").click((event) => {
        if ($(event.target).hasClass("down")) {
            direction = 0
        } else {
            direction = 1
        }
        fetch('vote/', {
            method: "PATCH",
            headers: apiHeaders,
            body: JSON.stringify({
                v: direction // 1 for up 0 for down
            })
        }).then((output) => {
            switch (output.status) {
                case 204: // success
                    window.location.reload()
                    break;
                case 403:
                    alert("No permission!")
                    break;
                case 410:
                    alert("You have already voted on this post.")
                default:
                    alert("Something went wrong!")
                    break;
            }
        })
    })

    $(".save").click((event) => {
        fetch("save/", {
            method: "PATCH",
            headers: apiHeaders,
        }).then((output) => {
            switch (output.status) {
                case 204: // success
                    window.location.reload()
                    break;
                case 401:
                    alert("You must be logged in to do that!");
                    break;
                case 403:
                    alert("No permission!")
                    break;
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
                    case 403:
                        alert("No permission!")
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
            const content = $("#content").text().replaceAll("<br>", "\n")
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

    // delete post
    $("#delete-post").click(() => {
        fetch('delete/', {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            }
        }).then((output) => {
            switch (output.status) {
                case 204: // success
                    window.location.reload()
                    break;
                case 403:
                    alert("No permission!")
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

    // add comment
    $("#comment").click(() => {
        fetch('comment/', {
            method: "POST",
            headers: apiHeaders,
            body: JSON.stringify({
                content: $("#comment-content").val().trim(),
                parent: $("#comment-parent").val()
            })
        }).then((output) => {
            switch (output.status) {
                case 204: // success
                    $("#comment-parent option:first").attr("selected", true);
                    $("#comment-content").val("")
                    window.location.reload()
                    break;
                case 400:
                    alert("Bad request!")
                    break;
                case 403:
                    alert("No permission!")
                    break;
                case 404:
                    alert("Post has been deleted!")
                    window.location.reload()
                    break;
                default:
                    alert("Something went wrong!")
                    break;
            }
        })
    })

    function parent_comment_id(node) {
        return parseInt($(node).parent().attr("id"))
    }

    let parent_id;
    // vote on comment
    $(".comment-vote").click((event) => {
        if ($(event.target).hasClass("down")) {
            direction = 0
        } else {
            direction = 1
        }
        fetch('commentvote/', {
            method: "PATCH",
            headers: apiHeaders,
            body: JSON.stringify({
                v: direction, // 1 for up 0 for down
                c: parent_comment_id(event.target)
            })
        }).then((output) => {
            switch (output.status) {
                case 204: // success
                    window.location.reload()
                    break;
                case 403:
                    alert("No permission!")
                    break;
                case 400:
                    alert("You have already voted on this comment.")
                default:
                    alert("Something went wrong!")
                    break;
            }
        })
    })

    // edit comment
    commentOpen = false;
    $(".comment-update").click((event) => {
        parent_id = parent_comment_id(event.target)
        if (parent_id == commentOpen) {
            fetch('commentupdate/', {
                method: "PUT",
                headers: apiHeaders,
                body: JSON.stringify({
                    c: parent_id,
                    content: $("#content-" + parent_id).val().trim()
                })
            }).then((output) => {
                switch (output.status) {
                    case 204: // success
                        window.location.reload()
                        break;
                    case 400:
                        alert("Invalid data!")
                    case 403:
                        alert("No permission!")
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
            const content = $("#content-" + parent_id).text().replaceAll("<br>", "\n").trim()

            commentOpen = parent_id

            $("#content-" + parent_id).changeElementType("textarea")
            $("#content-" + parent_id).val(content)
            $("#update-" + parent_id).text("Save")
            $("#cancel-" + parent_id).attr("style", "display:default")
        }
    })

    $(".comment-cancel").click((event) => {
        parent_id = parent_comment_id(event.target)
        const comment_id = "#content-" + parent_id
        const content = $(comment_id).text().replaceAll("<br>", "\n").trim()
        commentOpen = false;

        $("#content-" + parent_id).changeElementType("p")
        $("#update-" + parent_id).text("Edit")
        $("#cancel-" + parent_id).attr("style", "display:none")
    })

    $(".comment-delete").click((event) => {
        fetch('commentdelete/', {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({
                c: parent_comment_id(event.target)
            })
        }).then((output) => {
            switch (output.status) {
                case 204: // success
                    window.location.reload()
                    break;
                case 403:
                    alert("No permission!")
                    break;
                case 410:
                    alert("Comment has already been deleted!")
                    window.location.reload()
                    break;
                default:
                    alert("Something went wrong!")
                    break;
            }
        })
    })

    $('#comment-sort').on('change', () => {
        const optionSelected = $("#comment-sort option:selected");

        url = new URL(window.location.href)

        url.searchParams.set("sort", optionSelected.val())
        window.location.href = url
    });

    $("#gift").click((event) => {
        const award_type = $("#award-type").val()

        if (!award_type) {
            alert("Pick an award type.")
        } else {
            let request_body = {
                type: award_type,
                anonymous: $("#anonymous").is(":checked"),
                message: $("#message").val()
            }

            if ($(event.target).hasClass("comment-gift")) {
                request_body.c = parent_comment_id(event.target)
            }

            fetch('award/', {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify(request_body)
            }).then((output) => {
                switch (output.status) {
                    case 204: // success
                        window.location.reload()
                        break;
                    case 402:
                        alert("Insufficient Funds")
                        break;
                    case 403:
                        alert("No permission!")
                        break;
                    default:
                        alert("Something went wrong!")
                        break;
                }
            })
        }
    })

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