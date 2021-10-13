odoo.define('theme_shopoint.cart', function (require) {
'use strict';

    var ajax = require('web.ajax');
    var wSaleUtils = require('website_sale.utils');
    var sAnimation = require('website.content.snippets.animation');
    var publicWidget = require('web.public.widget');

    $(document).ready(function() {

        ajax.jsonRpc('/website/sp/get_info','call',{})
        .then(function(data) {
            localStorage.setItem('is_redirect', data.is_redirect);
        })

        $(document).on("#cart_modal hide.bs.modal", function (e) {
            $('#cart_modal').addClass('d-block');
            $('#cart_modal .modal-dialog').addClass('sp-cart-anim-out');
            setTimeout(function () {
                $('#cart_modal').removeClass('d-block');
            }, 380);
        });
    });

    sAnimation.registry.websiteSaleCartLink = sAnimation.registry.websiteSaleCartLink.extend({
        selector: '#top_menu a[href$="/shop/cart"]',
        read_events: {
            'mouseenter': '_onMouseEnter',
            'mouseleave': '_onMouseLeave',
            'click': '_render_cart',
        },
        _onMouseEnter: function() {
            return false;
        },
        _onMouseLeave: function() {
            return false;
        },
        _render_cart: function(evt) {
            evt.preventDefault();
            $.get("/shop/cart", {
                type: 'popover',
            }).then(function (data) {
                if (parseInt($(evt.currentTarget).find('.my_cart_quantity').text()) != 0 ) {
                    var modal =
                        ' <div class="modal" id="cart_modal" tabindex="-1" role="dialog" aria-labelledby="cartModalLabel" aria-hidden="true"> <div class="modal-dialog" role="document"> <div class="modal-content"> <div class="modal-header"> <h5 class="modal-title" id="cartModalLabel">Shopping Cart</h5><button type="button" class="close" data-dismiss="modal" aria-label="Close"> <span><i class="fa fa-times"></i></span> </button> </div> <div class="modal-body"> ' + data + ' </div> <div class="modal-footer"> <a type="button" class="btn btn-secondary" href="/shop/cart">View Cart</a> <a type="button" class="btn btn-primary cart_checkout" href="/shop/checkout">Process Checkout</a> </div> </div> </div> </div> ';
                } else {
                    var modal =
                    ' <div class="modal" id="cart_modal" tabindex="-1" role="dialog" aria-labelledby="cartModalLabel" aria-hidden="true"> <div class="modal-dialog" role="document"> <div class="modal-content"> <div class="modal-header"> <h5 class="modal-title" id="cartModalLabel">Shopping Cart</h5><button type="button" class="close" data-dismiss="modal" aria-label="Close"> <span><i class="fa fa-times"></i></span> </button> </div> <div class="modal-body"> ' + data + ' </div> </div> </div> </div> ';
                }

                $('body').find('#cart_modal').remove();
                $('body').after(modal);
                $('#cart_modal').modal('show');
            });
        },
    });

    publicWidget.registry.WebsiteSale.include({
        _custom_add_to_cart: function(ev) {
            var self = this;
            var productID = $(ev.currentTarget).closest('form').find('input[name="product_id"]').attr('value');
            ajax.jsonRpc('/shop/cart/update_json','call',{
                'product_id': parseInt(productID), 
                'add_qty': 1,
                'display': false
            })
            .then(function(data) {
                $('header .sp-cart-link .my_cart_quantity').text(data.cart_quantity);
                var $navButton = wSaleUtils.getNavBarButton('.o_wsale_my_cart');
                wSaleUtils.animateClone($navButton, $(ev.currentTarget).closest('form'), 25, 40);
            });          
        },
        _onClickSubmit: function (ev, forceSubmit) {
            if ($(ev.currentTarget).is('#add_to_cart, #products_grid .a-submit') && !forceSubmit) {
                return;
            }
            let is_redirect = JSON.parse(localStorage.getItem('is_redirect'));
            if ( !is_redirect ) {
                ev.preventDefault();
                return this._custom_add_to_cart(ev);
            } else {
                return this._super.apply(this, arguments);
            }
        },
        _onClickAdd: function(ev) {
            let is_buynow = $(ev.currentTarget).attr('id') === 'buy_now';
            let is_redirect = JSON.parse(localStorage.getItem('is_redirect'));
            if ( !is_redirect && !is_buynow ) {
                ev.preventDefault();
                return this._custom_add_to_cart(ev);
            } else {
                return this._super.apply(this, arguments);
            }
        }
    });

    $(document).on('click','.js_item_remove' ,function() {
        var self = $(this);
        let line_id = $(this).attr('line_id');
        let product_id = $(this).attr('product_id');

        ajax.jsonRpc('/shop/cart/update_json','call',{
            'line_id': parseInt(line_id), 
            'product_id': parseInt(product_id), 
            'set_qty': 0
        })
        .then(function(data) {
            $('header .sp-cart-link .my_cart_quantity').text(data.cart_quantity || 0);
            $.get("/shop/cart", {
                type: 'popover',
            }).then(function (data) {
                self.closest('.modal-body').html(data);
                let $cart = $('#cart_products.js_cart_lines tbody tr');
                if( $cart.length > 0 ) {
                    $.each($cart, function() {
                        if($(this).find('.js_quantity').attr('data-line-id') == line_id ) {
                            $(this).find('.js_quantity').val(0).trigger('change');
                            $(this).addClass('d-none');
                            return;
                        }
                    });
                }
            });
        })
    });
});