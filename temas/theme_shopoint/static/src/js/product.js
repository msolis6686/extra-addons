odoo.define('theme_shopoint.product', function (require) {
'use strict';

    var sAnimations = require('website.content.snippets.animation');

    sAnimations.registry.WebsiteSale = sAnimations.registry.WebsiteSale.extend({
        _updateProductImage: function ($productContainer, productId, productTemplateId, new_carousel, isCombinationPossible) {
            this._super.apply(this, arguments);
            $('.carousel-indicators').owlCarousel ({
            margin:0,
            nav:true,
            dots: false,
            responsive:{
                0:{
                    items:5
                },
                600:{
                    items:5
                },
                1000:{
                    items:5
                }
            }
        })
        }
    });

    $(document).ready(function() {
        $('#sp-product-menu div span').filter(function(index) {
            return index == 0;
        }).addClass('sp-menu-active');
        $('.sp-product-description').addClass('sp-menu-item-active');

        $('#sp-product-menu span').on('click', function() {
            $(this).parent().find('.sp-menu-active').removeClass('sp-menu-active');
            $(this).addClass('sp-menu-active');
            $('.sp-menu-item-active').removeClass('sp-menu-item-active');

            let sp_class = $(this).data('sp-action');
            $('.' + sp_class).addClass('sp-menu-item-active');
        });

        $('.sp-accessory-products.owl-carousel').owlCarousel({
            margin:10,
            nav:true,
            dots: true,
            responsive:{
                0:{
                    items:1
                },
                600:{
                    items:3
                },
                1000:{
                    items:4
                }
            }
        });
        $('.sp-alternative-products-wrapper .owl-carousel').owlCarousel({
            margin:20,
            nav:true,
            dots: true,
            responsive:{
                0:{
                    items:1
                },
                600:{
                    items:3
                },
                1000:{
                    items:4
                }
            }
        });
        $('#o-carousel-product .carousel-indicators').owlCarousel({
            margin:20,
            nav:true,
            dots: false,
            responsive:{
                0:{
                    items:5
                },
                600:{
                    items:5
                },
                1000:{
                    items:5
                }
            }
        });
        try {
            $('.sp-carousel-modif').on('DOMSubtreeModified', function() {
                if($(this).find('.carousel-indicators').length > 0) {
                    if($('.test').length > 0 ) {
                        $(".test").not('.slick-initialized').slick({
                            slidesToShow: 5,
                            arrow: true,
                            accessibility: true,
                            verticalSwiping: true,
                            vertical: true,
                            draggable: true
                        });
                    }
                }
            })
        }
        catch(e) {
            console.log(e);
        }
        // Aslo considered quick view radio input values in this
        $(document).on('click','.js_attribute_value .radio_input', function() {
            $(this).closest('.js_attribute_value').parent().find('.radio_input_active').removeClass('radio_input_active');
            $(this).addClass('radio_input_active');
        });

        // $('.sp-order-total').on('DOMSubtreeModified', function() {
        //     $('.sp-cart-total span').text($('#order_total .oe_currency_value').text());
        // });
    });

});
