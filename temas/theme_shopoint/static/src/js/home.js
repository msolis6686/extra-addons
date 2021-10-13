odoo.define('theme_shopoint.home', function (require) {
'use strict';

    $(document).ready( ()=> {

        $('.sp_blogs .owl-carousel').owlCarousel({
            margin:10,
            nav:false,
            dots:true,
            responsive:{
                0:{
                    items:1
                },
                600:{
                    items:2
                },
                1000:{
                    items:3
                }
            }
        });


    });
});
