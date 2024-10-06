// /static/js/form-scripts.js


document.addEventListener('DOMContentLoaded', function() {
    var dateElems = document.querySelectorAll('.datepicker');
    M.Datepicker.init(dateElems, { format: 'yyyy-mm-dd' });

    var collapsibleElems = document.querySelectorAll('.collapsible');
    M.Collapsible.init(collapsibleElems);

    var tooltipElems = document.querySelectorAll('.tooltipped');
    M.Tooltip.init(tooltipElems);
});

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all collapsibles with the proper options
    var collapsibles = document.querySelectorAll('.collapsible');
    M.Collapsible.init(collapsibles, {
        accordion: false  // Allow multiple sections to be open at once
    });
});