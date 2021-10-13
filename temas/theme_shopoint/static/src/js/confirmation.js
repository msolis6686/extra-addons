odoo.define('theme_shopoint.confirmation', function (require) {
'use strict';

    $(document).ready( () => {

        $('.show-so-details').on('click', function() {
            if($(this).hasClass('active')) {
                $(this).removeClass('active').text('Show Details');
            } else {
                $(this).addClass('active').text('Hide Details');
                $('html, body').animate({scrollTop:520}, 'slow');
            }
            $('.oe_website_sale').slideToggle(400);
        });
    });
});
