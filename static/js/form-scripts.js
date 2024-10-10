document.addEventListener('DOMContentLoaded', function() {
    var dateElems = document.querySelectorAll('.datepicker');
    M.Datepicker.init(dateElems, { format: 'yyyy-mm-dd' });

    var collapsibleElems = document.querySelectorAll('.collapsible');
    // Initialize collapsibles correctly with accordion behavior
    var instances = M.Collapsible.init(collapsibleElems, { accordion: true });

    var tooltipElems = document.querySelectorAll('.tooltipped');
    M.Tooltip.init(tooltipElems);
});


var elem = document.querySelector('.massr');
var msnry = new Masonry( elem, {
  // options
  itemSelector: '.grid-item',
  columnWidth: 200
});

// element argument can be a selector string
//   for an individual element
var msnry = new Masonry( '.massr', {
  // options
});