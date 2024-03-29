// place after jquery script tag

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

function copyToClipboard(text) {
    if (!navigator.clipboard) { // if it's necessary to use the deprecated method
        var $temp = $("<input type='hidden'>");
        $("body").append($temp);
        $temp.val(text).select();
        document.execCommand("copy");
        $temp.remove();
    } else {
        navigator.clipboard.writeText(text)
    }
}

const apiHeaders = {
    "Content-Type": "application/json",
    "X-CSRFToken": getCookie("csrftoken")
}

$.fn.extend({
    addTemporaryClass: function(className, duration) {
        var elements = this;
        setTimeout(function() {
            elements.removeClass(className);
        }, duration);

        return this.each(function() {
            $(this).addClass(className);
        });
    },
    changeElementType: function(type) {
        const attributes = {};

        $.each(this[0].attributes, function(idx, attribute) {
            attributes[attribute.nodeName] = attribute.nodeValue;
        });

        this.replaceWith(function() {
            return $("<" + type + "/>", attributes).append($(this).contents());
        });
    }
});