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

// Keep only this simpler version
$("#input-form").on("submit", function(event) {
    // Get required fields
    const baseSpeedInput = document.getElementById('base-speed');
    const coresInput = document.getElementById('cores');
    const threadsInput = document.getElementById('threads');
    const ramTypeInput = document.getElementById('ram-type');
    const clockRateInput = document.getElementById('clock-rate');
    const ramUpgradableInput = document.getElementById('ram-upgradable');
    const slotsUsedInput = document.getElementById('slots-used');
    const slotsEmptyInput = document.getElementById('slots-empty');

    // Remove previous highlights
    [
        baseSpeedInput, coresInput, threadsInput,
        ramTypeInput, clockRateInput, ramUpgradableInput,
        slotsUsedInput, slotsEmptyInput
    ].forEach(input => {
        input.classList.remove('missing-field');
    });

    let missing = false;

    if (!baseSpeedInput.value) {
        baseSpeedInput.classList.add('missing-field');
        missing = true;
    }
    if (!coresInput.value) {
        coresInput.classList.add('missing-field');
        missing = true;
    }
    if (!threadsInput.value) {
        threadsInput.classList.add('missing-field');
        missing = true;
    }
    if (!ramTypeInput.value) {
        ramTypeInput.classList.add('missing-field');
        missing = true;
    }
    if (!clockRateInput.value) {
        clockRateInput.classList.add('missing-field');
        missing = true;
    }
    // For select, make sure a real value is chosen (not the blank/none option)
    if (!ramUpgradableInput.value || ramUpgradableInput.value === "ram-upgradable-none") {
        ramUpgradableInput.classList.add('missing-field');
        missing = true;
    }
    if (!slotsUsedInput.value) {
        slotsUsedInput.classList.add('missing-field');
        missing = true;
    }
    if (!slotsEmptyInput.value) {
        slotsEmptyInput.classList.add('missing-field');
        missing = true;
    }

    if (missing) {
        alert("Please enter values for all required CPU and RAM fields before printing the build sheet.");
        event.preventDefault();
        return false;
    }

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
    const calculatorData = sessionStorage.getItem('calculatorData');
    if (calculatorData) {
        const data = JSON.parse(calculatorData);
        
        // Populate form fields
        document.getElementById('price').value = data.price;
        document.getElementById('cpu').value = data.cpu;
        document.getElementById('ram').value = data.ram;
        document.getElementById('OS').value = data.OS;
        
        // Add battery capacity and screen size
        if (data.battery_capacity) {
            document.getElementById('battery-capacity').value = data.battery_capacity;
        }
        if (data.diagonal_screen) {
            document.getElementById('diagonal-screen').value = data.diagonal_screen;
        }
        
        // Populate storage devices
        if (data.ssd1_storage) {
            document.getElementById('ssd1-storage').value = data.ssd1_storage;
            document.getElementById('ssd1-storage-unit').value = data.ssd1_storage_unit;
            document.getElementById('ssd1-type').value = data.ssd1_type;
        }
        
        if (data.ssd2_storage) {
            document.getElementById('ssd2-storage').value = data.ssd2_storage;
            document.getElementById('ssd2-storage-unit').value = data.ssd2_storage_unit;
            document.getElementById('ssd2-type').value = data.ssd2_type;
        }
        
        if (data.hdd1_storage) {
            document.getElementById('hdd1-storage').value = data.hdd1_storage;
            document.getElementById('hdd1-storage-unit').value = data.hdd1_storage_unit;
        }
        
        if (data.hdd2_storage) {
            document.getElementById('hdd2-storage').value = data.hdd2_storage;
            document.getElementById('hdd2-storage-unit').value = data.hdd2_storage_unit;
        }
        
        // Handle WiFi kind checkboxes
        if (data.wifi_kind) {
            // Uncheck all WiFi options first
            document.querySelectorAll('[name^="802-bgn"], [name^="dual-band"], [name^="ax"], [name^="ac"], [name^="none-wireless"]')
                .forEach(checkbox => checkbox.checked = false);
            
            // Map the WiFi kinds to their corresponding checkbox IDs
            const wifiMapping = {
                '802.11-bgn': '802-bgn',
                'Dual Band': 'dual-band',
                'ac': 'ac',
                'ax': 'ax',
                'none': 'none-wireless'
            };
            
            // Check the appropriate WiFi option
            const checkboxId = wifiMapping[data.wifi_kind];
            if (checkboxId) {
                document.getElementById(checkboxId).checked = true;
            }
        }

        if (data.desktop_bluetooth !== undefined) {
            document.getElementById('bluetooth').value = data.desktop_bluetooth ? 'bluetooth-true' : 'bluetooth-false';
        }

        if (data.bluetooth !== undefined) {
            document.getElementById('bluetooth').value = data.bluetooth;
        }
        
        // Clear the stored data after using it
        sessionStorage.removeItem('calculatorData');
    }
});