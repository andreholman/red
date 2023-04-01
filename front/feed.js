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
    // SCSS vars
    const border = 16;

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
            console.log("wrapped!")
            let infobox = $(this).find(".info")
            infobox.css({
                "align-items": "end",
                "flex-direction": "column",
            })
            infobox.find(".username").css({ "margin-right": 0 })
            infobox.children(":first").css("margin-bottom", 4)
        }
    });

    // end INIT

    $(".tab").click(function() {
        $("nav").children(".selected").toggleClass("selected")
        $(this).toggleClass("selected")
    })

    $("#switch").click(function() { // theme toggle
        $(".option").toggleClass("selected");
        $("#selector,html,body").toggleClass("light");
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


    $(window).keydown((e) => { // search
        if (e.keyCode == 114 || (e.ctrlKey && e.keyCode == 70)) {
            e.preventDefault();
        }
    })
});