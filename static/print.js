$(document).ready(function() {
    if (Object.keys(results).length > 0) {
        updateAllLabelValues(results);
        window.print();
    }
});
