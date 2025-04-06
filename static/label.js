function toggleCheckbox(is_checked, element) {
    /* selected-value vs deselected-value determine whether a checkbox item is circled */
    if (is_checked) {
        element.addClass("selected-value");
        element.removeClass("deselected-value");
    } else {
        element.addClass("deselected-value");
        element.removeClass("selected-value");
    }
}

function updateLabelValue(key, value) {
    var element = $("#lbl-" + key);
    if (element.hasClass("checkbox-from-dropdown")) {
        element = $("#lbl-" + value);
        toggleCheckbox(true, element);
    } else if (element.hasClass("lbl-text")) {
        element.text(value);
    } else if (element.hasClass("lbl-checkbox")) {
        if (value == "on") {
            toggleCheckbox(true, element);
        }
    }
}

function updateAllLabelValues(form_data) {
    $(".lbl-checkbox").each(function() {
        toggleCheckbox(false, $(this));
    });

    for (const [key, value] of Object.entries(form_data)) {
        updateLabelValue(key, value);
    }

    $(".lbl-text").each(function() {
        if ($(this).text() == "") {
            var num_blanks = $(this).attr("blanks"); // sloppy approach but functional
            for (var x = 0; x < num_blanks; x += 1) {
                // $(this).append("\u00A0"); // non-breaking space character
                $(this).append("_");
            }
        }
    });

    $(".empty-alt").each(function() {
        var empty = $(this).text() == "";
        var alt_id = "#" + $(this).attr("id") + "-ifempty";
        var visible_id = "#" + $(this).attr("id") + "-iffilled"
        if (empty) {
            $(this).hide();
            $(visible_id).hide();
            $(alt_id).show();
        } else {
            $(this).show();
            $(visible_id).show();
            $(alt_id).hide();
        }
    });
    $("#label").trigger("change");
}