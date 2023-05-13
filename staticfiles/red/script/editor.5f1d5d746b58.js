window.odometerOptions = {
    duration: 750 // milliseconds. must change css as well!
};
let selectedSub;

$(document).ready(function() {
    $("#subs .sub:not(.selected)").click((e) => {
        $("#subs .sub.selected").removeClass("selected");
        $(e.currentTarget).addClass("selected");
        selectedSub = $(e.currentTarget).find("h3").text()
    })

    $("#sub-search").on("input", (e) => {
        query = $(e.target).val().toLowerCase()
        query_terms = query.trim().split(" ")
        console.log("terms: " + query_terms)

        shown_subs = $("#subs .sub:not(.hidden)");
        hidden_subs = $("#subs .sub.hidden");

        let matched = function(name) {
            return query_terms.some(term => {
                return name.toLowerCase().includes(term);
            });
        };

        shown_subs.each(function() {
            $current_sub = $(this)
            if (!matched($current_sub.find("h3").text())) {
                $current_sub.addClass("hidden");
            }
        })
        hidden_subs.each(function() {
            $current_sub = $(this)
            if (matched($current_sub.find("h3").text())) {
                $current_sub.removeClass("hidden");
            }
        })

        // if ($("#subs h3:not(.hidden)").length) {
        //     $("#subs .none").removeClass("shown")
        // } else { // None left shown
        //     $("#subs .none").addClass("shown")
        // }
    })
})