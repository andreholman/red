window.odometerOptions = {
    duration: 750 // milliseconds. must change css as well!
};
let postAwardID, awardType, awardsOpen; // awarding


$(document).ready(function() {

    let counts = []; // INIT voting
    $(".post").find(".odometer").each(function() {
        counts.push(parseInt(
            $(this)
            .text()
            .replace(/\n/g, '')
        ));
    });

    // INIT long title info wrapping

    function textWidth(txt, font, padding) {
        $span = $('<span></span>');
        $span.css({
            font: font,
            position: 'absolute',
            top: -1000,
            left: -1000,
            padding: padding
        }).text(txt);
        $span.appendTo('body');
        return $span.width();
    }

    $(".post header").each(function() {
        heading = $(this).find("h3");
        let font = heading.css('font');
        let padding = heading.css('padding');
        let w = textWidth($(heading).html(), font, padding);
        if (w > heading.width()) {
            let infobox = $(this).find(".info")
            infobox.css({
                "align-items": "end",
                "flex-direction": "column",
            })
            infobox.find(".username").css({ "margin-right": 0 })
            infobox.find("div").first().css("margin-bottom", "4px")
        }
    });

    function minifyButtons() { // post option buttons
        if (Math.ceil($("#content-wrapper").width()) < 500) {
            $(".buttons span").css("display", "none")
        } else {
            $(".buttons span").css("display", "")
        }
    }

    function postUrl(parentElement) { // get the url of a post from its DOM element
        return $(parentElement.find("a")[0]).attr("href")
    }

    minifyButtons()
        // end INIT

    $(window).resize(minifyButtons)

    $(".tab").click(function() {
        $("nav").children(".selected").toggleClass("selected")
        $(this).toggleClass("selected")
    })

    $("#switch").click(function() { // theme toggle
        $(".option").toggleClass("selected");
        $("#selector,html,body").toggleClass("light");
        $("div.tab").css("transition-property", "all")
        setTimeout(() => { // prevents instant switching of the top border
            $("div.tab").css("transition-property", "color")
        }, 200)
    })

    $("i").click(function() { // voting
        let parentElement = $(this).closest(".post");
        let postIndex = parentElement.index()

        counter = $(this).closest(".vote").find(".odometer");

        function vote(direction) {
            fetch(postUrl(parentElement) + "vote/", {
                method: "PATCH",
                headers: apiHeaders,
                body: JSON.stringify({
                    v: direction // 1 for up 0 for down
                })
            })
        }

        if ($(this).hasClass("up")) {
            vote(1)

            let downButton = $(this).closest(".vote").find(".down")
            if ($(this).hasClass("voted")) {
                counts[postIndex]--;
            } else {
                counts[postIndex]++;
                $(this).addTemporaryClass("fa-bounce", 800);

                if (downButton.hasClass("voted")) {
                    downButton.removeClass("voted");
                    counts[postIndex]++;
                }
            }
        } else if ($(this).hasClass("down")) {
            vote(0)

            let upButton = $(this).closest(".vote").find(".up")
            if ($(this).hasClass("voted")) {
                counts[postIndex]++;
            } else {
                counts[postIndex]--;
                $(this).addTemporaryClass("shake", 800);

                if (upButton.hasClass("voted")) {
                    upButton.removeClass("voted");
                    counts[postIndex]--;
                }
            }
        }

        counter.html(counts[postIndex])
        $(this).toggleClass("voted");
    });

    $(".post:has(.hider)").click((e) => { // revealing nsfw and spoiler posts
        $thisPost = $(e.currentTarget)
        $thisPost.find(".hider").remove()
        $thisPost.find(".post-content").removeClass("hidden")
    })

    $(".award").click((e) => { // Opening award dialogue
        if (loggedIn) {
            postAwardID = $(e.target).closest(".post").attr("data-id")
            awardsOpen = true;

            console.log("award the " + postAwardID)
            $("#award-modal").addClass("open")
        } else { // redirect
            window.location.href = "/login";
        }
    })

    $(".award-type:not(.disabled):not(.selected)").click((e) => { // selecting award type
        let awardBox = $(e.target).closest(".award-type");

        $(".next-fields").addClass("open")
        $(".award-type.selected").removeClass("selected")
        awardBox.addClass("selected")
        awardType = awardBox.attr("id")
    })

    $("#anon").change(function() { // Checkbox
        if (this.checked) {
            $("#checkbox").addClass("selected");
        } else {
            $("#checkbox").removeClass("selected");
        }
    });

    $(".next-fields button").click((e) => { // submitting award
        let request_body = {
            type: awardType,
            anonymous: $("#anon").is(":checked"),
            message: $("#message").val()
        }
        let parentElement = $(".post[data-id=" + postAwardID + "]")

        fetch(postUrl(parentElement) + 'award/', {
            method: "POST",
            headers: apiHeaders,
            body: JSON.stringify(request_body)
        }).then((output) => {
            if (output.status == 204) {
                window.location.href = postUrl(parentElement)
            } else {
                alert("Something went wrong!")
            }
        })
    })

    $(".share").click((e) => {
        copyToClipboard("https://red.andreholman.com" + postUrl($(e.target).closest(".post")))
        let $span = $(e.currentTarget).find("span")
        if ($span.css("display") == "none") {
            $(e.currentTarget)
                .addTemporaryClass("success", 5000)
                .find("i") // these below applied to the i
                .removeClass("fa-share-nodes")
                .addClass("fa-check")
            setTimeout(() => {
                $(e.currentTarget).find("i").removeClass("fa-check").addClass("fa-share-nodes")
            }, 5000)
        } else {
            $span.text("Copied!")
            setTimeout(() => {
                $span.text("Share")
            }, 5000)
        }
    })

    $("label").hover(
        function() {
            $("#checkbox").addClass("hovered");
        },
        function() {
            $("#checkbox").removeClass("hovered");
        }
    );

    // KEYBIND HANDLING

    $(window).keydown((e) => {
        if (e.keyCode == 114 || (e.ctrlKey && e.keyCode == 70)) {
            e.preventDefault(); // search
        } else if (e.keyCode == 27 && awardsOpen) {
            e.preventDefault();
            $("#award-modal").removeClass("open")
            awardsOpen = false;
        }
    })
});