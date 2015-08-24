$(document).ready(function () {
    // Make table sortable
    $('#main_table').DataTable({
        info: false,
        paging: false,
        searching: false
    });

    // Associate click handlers to anchors
    $('.locale_anchor').click(function (e) {
        e.preventDefault;
        // Remove other selected rows and spacers
        $('tr').removeClass('selected');
        $('.spacer').remove();

        // Add empty row before and after this element
        var row = '#row_' + e.target.id;
        $(row).before('<tr class="spacer_top" colspan="<?php echo $columns_number;?>">&nbsp;</tr>');
        $(row).after('<tr class="spacer_bottom" colspan="<?php echo $columns_number;?>">&nbsp;</tr>');
        // Add selected class to this row
        $(row).addClass('selected');
        // Scroll slight above the anchor
        var y = $(window).scrollTop();
        $("html, body").animate(
            {
                scrollTop: y - 150
            }, 500);
    });

    var anchor = location.hash.substring(1);
    if (anchor !== '') {
        $('#' + anchor).click();
    }
});
