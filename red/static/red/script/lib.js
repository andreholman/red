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

$.fn.changeElementType = function(type) {
    const attributes = {};

    $.each(this[0].attributes, function(idx, attribute) {
        attributes[attribute.nodeName] = attribute.nodeValue;
    });

    this.replaceWith(function() {
        return $("<" + type + "/>", attributes).append($(this).contents());
    });
}