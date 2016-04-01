/* eslint new-cap: [2, {"capIsNewExceptions": ["DataTable"]}] */

$(document).ready(function() {
    $('#main_table').DataTable({
        info: false,
        paging: false,
        searching: false
    });
});
