odoo.define('theme_shopoint.wishlist', function (require) {
'use strict';

    var sAnimations = require('website.content.snippets.animation');

    sAnimations.registry.ProductWishlist = sAnimations.registry.ProductWishlist.extend({
        _updateWishlistView: function() {
            if (this.wishlistProductIDs.length > -1) {
                $('.o_wsale_my_wish').show();
                $('.my_wish_quantity').text(this.wishlistProductIDs.length);
            } else {
                $('.o_wsale_my_wish').hide();
            }
        }
    });

    $(document).ready(() => {
        $('#b2b_wish').on('click',function() {
            let $parent = $(this);
            if($(this).prop("checked") == true){
                $parent.addClass('check-wish');
            }
            else if($(this).prop("checked") == false){
                $parent.removeClass('check-wish');
            }
        });
        $('.my_wish_quantity').on('DOMSubtreeModified', function() {
            $('.sp-count').text($(this).text());
        });
    });

});
