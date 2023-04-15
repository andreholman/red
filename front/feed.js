(function($) {
    $.fn.extend({
        addTemporaryClass: function(className, duration) {
            var elements = this;
            setTimeout(function() {
                elements.removeClass(className);
            }, duration);

            return this.each(function() {
                $(this).addClass(className);
            });
        }
    });
})(jQuery);

window.odometerOptions = {
    duration: 750 // milliseconds. must change css as well!
};

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
            infobox.children(":first").css("margin-bottom", 4)
        }
    });

    function minifyButtons() { // post option buttons
        if (Math.ceil($("#content-wrapper").width()) < 500) {
            $(".buttons span").css("display", "none")
        } else {
            $(".buttons span").css("display", "")
        }
    }

    minifyButtons()

    let postAwardIndex, awardType, awardsOpen; // awarding

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
        let postIndex = $(this).closest(".post").index()

        counter = $(this).closest(".vote").find(".odometer");

        if ($(this).hasClass("up")) {
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

    $(".award").click((e) => { // Opening award dialogue
        postAwardIndex = $(e.target).closest(".post").attr("data-id")

        console.log("award the " + postAwardIndex)
        $("#award-modal").addClass("open")
    })

    $(".award-type:not(.disabled):not(.selected)").click((e) => {
        let awardBox = $(e.target).closest(".award-type");
        awardsOpen = true;

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
        }
    })
});