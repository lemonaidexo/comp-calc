/*
    inputs.js
    Links input fields to label on inputs.html
*/

/*
    Runs when updates are made to the form to circle or un-circle a value in the label. 
*/
$(document).ready(function() {
    $(".other-textbox").hide();
    $("#input-form").trigger("change");

    /* Prevents enter key from submitting form, https://stackoverflow.com/questions/895171/prevent-users-from-submitting-a-form-by-hitting-enter */
    $(window).keydown(function(event) {
        if (event.keyCode == 13) {
          event.preventDefault();
          return false;
        }
    });
});

$("#input-form").on("change", function() {
    var form_data_raw = $(this).serializeArray();
    var form_data = {}
    for (i in form_data_raw) {
        form_data[form_data_raw[i]["name"]] = form_data_raw[i]["value"]
    }
    updateAllLabelValues(form_data);
});

$(".has-other-option").on("change", function() {
    var other_input_id = "#" + $(this).attr("id") + "-other";
    var other_input_id_container = "#" + $(this).attr("id") + "-other-container";
    if (other_input_id == "#" + $(this).val()) {
        $(other_input_id_container).show();
    } else {
        $(other_input_id_container).hide();
        $(other_input_id).val("");
    }
});

$(".fields-submit").click(function() {
    var button_id = $(this).attr("id");
    if (button_id == "submit-button" || button_id == "submit-both") {
        if (confirm("Are you sure you want to submit? This build will be added to the database and you will be taken to a page where you can print the label.")) {
            $("#submit-type").val("both");
            $("#input-form").submit();
        }
    } else if (button_id == "submit-print") {
        if (confirm("Are you sure you want to submit? You will be taken to a page where you can print the label.")) {
            $("#submit-type").val("print");
            $("#input-form").submit();
        }
    } else {
        if (confirm("Are you sure you want to submit? This build will be added to the database and you will be sent to the home page.")) {
            $("#submit-type").val("db");
            $("#input-form").attr("target", "_self");
            $("#input-form").submit();
        }
    }
    
});

// Replace the existing submit handler with this simpler version
$("#input-form").on("submit", function(event) {
    if (confirm("Are you sure you want to print this build sheet?")) {
        return true;
    }
    event.preventDefault();
    return false;
});

function redirectToHome() {
    window.location.href = 'http://localhost:3421'
  }

document.addEventListener('DOMContentLoaded', function() {
    // Check for calculator data
    const calculatorData = sessionStorage.getItem('calculatorData');
    if (calculatorData) {
        const data = JSON.parse(calculatorData);
        
        // Populate form fields
        document.getElementById('price').value = data.price;
        document.getElementById('manufacturer').value = data.manufacturer;
        document.getElementById('model-number').value = data.model;
        document.getElementById('ram').value = data.ram;
        document.getElementById('OS').value = data.OS; 
        
        // Handle storage devices
        if (data.storage && data.storage.length > 0) {
            document.getElementById('ssd1-storage').value = data.storage[0];
            if (data.storage_type && data.storage_type[0]) {
                document.getElementById('ssd1-type').value = data.storage_type[0];
            }
            
            if (data.storage.length > 1) {
                document.getElementById('ssd2-storage').value = data.storage[1];
                if (data.storage_type && data.storage_type[1]) {
                    document.getElementById('ssd2-type').value = data.storage_type[1];
                }
            }
        }
        
        // Clear the stored data after using it
        sessionStorage.removeItem('calculatorData');
    }
});