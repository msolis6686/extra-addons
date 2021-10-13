odoo.define('theme_shopoint.back_to_top', function (require) {
'use strict';

    $(document).ready( ()=> {

        //Back to top
        let $sp_back_to_top = $('.sp_back_to_top');
        $(window).scroll(function() {
            if (document.body.scrollTop > 100 || document.documentElement.scrollTop > 100 ) {
                $sp_back_to_top.show();
                $sp_back_to_top.removeClass('animOut');
                $sp_back_to_top.addClass('animIn');
            } else {
                if( $sp_back_to_top.hasClass('animIn') ) {
                    setTimeout(function() {
                        $sp_back_to_top.css('display','none');
                    }, 390);
                    $sp_back_to_top.removeClass('animIn');
                    $sp_back_to_top.addClass('animOut');
                }
            }
        });
        $sp_back_to_top.on('click', function() {
            $('html, body').animate({scrollTop:0}, 'slow');
        });

    });
});
