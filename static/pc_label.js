/* Special cases */
$("#label").on("change", function() {
    handleRedundantWifiQuestion();
    handleRedundantDiscQuestion();
});

function handleRedundantWifiQuestion() {
    var wifi_checked = $("#lbl-802-bgn").hasClass("selected-value") || $("#lbl-dual-band").hasClass("selected-value") || $("#lbl-ax").hasClass("selected-value") || $("#lbl-ac").hasClass("selected-value");
    var no_wifi_checked = $("#lbl-none-wireless").hasClass("selected-value");
    toggleCheckbox(wifi_checked, $("#lbl-wifi-yes"));
    toggleCheckbox(!wifi_checked && no_wifi_checked, $("#lbl-wifi-no"));
}

function handleRedundantDiscQuestion() {
    var disc_checked = $("#lbl-dvd").hasClass("selected-value") || $("#lbl-blu-ray").hasClass("selected-value") || $("#lbl-other-disc-reader").text() != "";
    var no_disc_checked = $("#lbl-none-optical-drive").hasClass("selected-value");
    toggleCheckbox(disc_checked, $("#lbl-disc-reader-yes"));
    toggleCheckbox(!disc_checked && no_disc_checked, $("#lbl-disc-reader-no"));
}

// Function to populate the wattage adapter field
function populateWattageAdapter() {
    var wattageAdapter = $("#wattage-adapter").val();
    $("#lbl-wattage-adapter").text(wattageAdapter ? wattageAdapter + " W" : "N/A");
}

// Call the function to populate the wattage adapter field when the document is ready
$(document).ready(function() {
    populateWattageAdapter();
});