odoo.define('theme_shopoint.shop', function (require) {
'use strict';

    var ajax = require('web.ajax');
    var sAnimation = require('website.content.snippets.animation');

    sAnimation.registry.disableFixedCategFilterView = sAnimation.Class.extend({
        selector: "#wrapwrap",
        read_events: {
            'click .switch_category_filter_fixed_view': '_render_view',
            'click .disable_panel ': '_disable_view',
            'click #sp_loader': '_load_more',
            'click .optional_product': '_optional_products',
            'click .js_hide_mm': '_hide_megaMenu',
            'click .sp-user-link': '_set_compare_values',
            'mouseenter .sp-user-link': '_set_compare_values',
        },
        _set_compare_values: function(evt) {
            let href = $('.o_comparelist_button a').attr('href');
            if ($('.o_product_panel_content .o_comparelist_products').find('> div').length < 3) {
                href = '#';
            }
            $(evt.currentTarget).find('#wk_compareList').attr('href', href);
        },
        _render_view: function(evt) {
            var self = this.$el;
            this.$el.find('#products_grid_before').after('<div class="disable_panel"></div>')
            this.$el.find('#products_grid_before').removeClass('fixed_category_out').addClass('active fixed_category_in');
        },
        _disable_view: function() {
            this.$el.find('#products_grid_before').removeClass('fixed_category_in').addClass('fixed_category_out');
            setTimeout(function () {
                $('#products_grid_before').removeClass('active');
                $('.disable_panel').remove();
            }, 380);
        },
        _load_more: function(evt) {
            var $el = $(evt.currentTarget);
            let loadingData = JSON.parse($el.attr('data-loading'));
            let page = loadingData.page || 1;
            let page_count = loadingData.page_count;
            if (page < page_count) {
                $el.find('i').addClass('fa-spin fa-spinner');
                loadingData = JSON.stringify({ 'page': page + 1, 'page_count': page_count });
                $el.attr('data-loading', loadingData);
                let url = window.location.href;
                $.get( url ,{
                    'page':page + 1,
                    'lazy_load': true,
                })
                .done(function(data){
                    $('#products_grid .oe_product:last').after(data);
                    $el.find('i').removeClass('fa-spin fa-spinner');
                });
            } else {
                $el.text('No More Products To Load');
            }
        },
        _optional_products: function(evt) {
            let $el = $(evt.currentTarget);
            ajax.jsonRpc('/shop/optional_products/data','call', {
                'product_id': $el.attr('data-p_id'),
                'type': $el.attr('data-type')
            }).then(function(data) {
                $('.oe_website_sale').find('#optionalProducts').remove();// Prevent Multiple modals to get in the DOM
                $('.oe_website_sale').append(data);
                $('#optionalProducts').modal('show');
                $('.optional_products_wrapper.owl-carousel.template').owlCarousel({
                    margin:20,
                    nav:true,
                    dots:true,
                    responsive:{
                        0:{
                            items:1
                        },
                        600:{
                            items:1
                        },
                        1000:{
                            items:1
                        }
                    }
                });
                $('.optional_products_wrapper.owl-carousel.product').owlCarousel({
                    margin:20,
                    nav:true,
                    dots:true,
                    responsive:{
                        0:{
                            items:1
                        },
                        600:{
                            items:2
                        },
                        1000:{
                            items:4
                        }
                    }
                });
            });
        },
        _hide_megaMenu: function(evt) {
            $(evt.target).closest('#sp_top_menu').removeClass('active mobile_view');
            $('.js_hide_mm').remove();
        },

    });

    sAnimation.registry.shop = sAnimation.Class.extend({
        selector: '#products_grid_before',
        read_events: {
            'click .wk-filters-active li': '_append_active',
            'click .css_attribute_color': '_add_class',
            'click .sp-product-filters-item': '_remove_filter',
            'click .price-filter-action': '_price_filter',
            'click form > ul > li': '_render_dropdown',
            'click .js_close_mobile': '_close_category_modal'
        },
        _append_active: function(evt) {
            let $label = $(evt.currentTarget).find('label');
            if($label.hasClass('active')) {
                $label.removeClass('active');
            } else {
                $label.addClass('active');
            }
        },
        _add_class: function(evt) {
            evt.stopPropagation();//Fix
            let $label = $(evt.target).closest('label');
            $label.addClass('active');
        },
        _remove_filter: function(evt) {
            try {
                let cur_url = window.location.href;
                let arr = cur_url.split('?');
                var category = arr[0];
                var attribs = arr[1];
                let new_url = '';
                let target = $(evt.currentTarget).data('filter-type');
                if( target == 'category' ) {
                    let shop_url = category.split('/category')[0];
                    if (attribs != undefined) {
                        new_url = `${shop_url}?${attribs}`;
                    } else {
                        new_url = `${shop_url}`;
                    }
                } else if(target == 'clear_all') {
                    new_url = category.split('/category')[0];
                    $('.sp-product-filters-item').animate({ opacity: '0' }, 400, function() {
                        $(evt.currentTarget).remove();
                    })
                } else if(target == 'search') {
                    let search = $(evt.currentTarget).data('search');
                    new_url = cur_url.replace('&search=' + search, '&search=');
                    new_url = new_url.replace('?search=' + search, '?search=');
                } else if(target == 'price_filter') {
                    let $target = $(evt.currentTarget);
                    let min_price = $target.data('min');
                    let max_price = $target.data('max');
                    new_url = cur_url.replace('&min_price=' + min_price + '&max_price=' + max_price, '');
                    new_url = new_url.replace('?min_price=' + min_price + '&max_price=' + max_price, '');
                } else {
                    new_url = cur_url.replace('&' + $(evt.currentTarget).data('attrib-value'), '');
                    new_url = new_url.replace('?' + $(evt.currentTarget).data('attrib-value'), '?');
                }
                $(evt.currentTarget).animate({ opacity: '0' }, 400, function() {
                    $(evt.currentTarget).remove();
                });
                location.replace(new_url);
            } catch (err) {
                console.log(err);
            }
        },
        _price_filter: function(evt) {
            try {
                evt.preventDefault();
                let href = location.href;
                let arr = href.split('?');
                var category = arr[0];
                var attribs = arr[1];
                const min_price = this.$el.find('.sp-min-price').val();
                const max_price = this.$el.find('.sp-max-price').val();
                if (attribs != undefined && attribs.length > 0) {
                    if (attribs.includes('#')) {
                        var url = attribs.split('#');
                        attribs = url[0];
                    }
                    if(attribs.includes('min_price')) {
                        let min_rgex = /min_price=[0-9]+&/i;
                        attribs = attribs.replace(min_rgex, '');
                        let max_rgex = /max_price=[0-9]+/i;
                        attribs = attribs.replace(max_rgex, '');
                    }
                    if(attribs.split('&').length > 0 && attribs.length != 0) {
                        attribs += `&min_price=${min_price}&max_price=${max_price}`;
                    } else {
                        attribs += `min_price=${min_price}&max_price=${max_price}`;
                    }
                    if (url != undefined) {
                        attribs += `#${url[1]}`;
                    }
                } else {
                    if(category.includes('#')) {
                        let url = href.split('#');
                        category = url[0];
                        attribs = `min_price=${min_price}&max_price=${max_price}#${url[1]}`;
                    } else {
                        attribs = `min_price=${min_price}&max_price=${max_price}`;
                    }
                }
                var new_url = `${category}?${attribs}`;
                location.href = new_url;
            } catch(err) {
                console.log(err);
            }
        },
        _render_dropdown: function(evt) {
            if (!this.$el.hasClass('fixed_category_in')) {
                let $l = $(evt.currentTarget);
                if($l.children('div').hasClass('wk-dropdown')) {
                    $l.children('div').removeClass('wk-dropdown').addClass('wk-dropdown-active');
                    if($l.children('label').length > 0) {
                        $l.children('label').removeClass('d-none').addClass('wk-filters-active-label');
                    } else {
                        $l.children(':not(div)').removeClass('d-none').addClass('wk-filters-active');
                    }
                }
                else {
                    $l.children('div').removeClass('wk-dropdown-active').addClass('wk-dropdown');
                    if($l.children('label').length > 0) {
                        $l.children('label').removeClass('wk-filters-active-label').addClass('d-none');
                    } else {
                        $l.children(':not(div)').removeClass('wk-filters-active').addClass('d-none');
                    }
                }
            }
        },
        _close_category_modal: function(evt) {
            var $target = $(evt.currentTarget).closest('#products_grid_before');
            $target.removeClass('fixed_category_in').addClass('fixed_category_out');
            setTimeout(function() {
                $target.removeClass('active');
            }, 380);
        }
    });


    $(document).ready(function() {
        // Three views in shop page (main list table)
        var product_grid = $('#products_grid');
        if( product_grid.length ) {
            ajax.jsonRpc(
                '/website/get/view', 'call', {
            }).then(function(result) {
                let view_class = result;
                $('.wk-shopoint-setting .wk-shopoint-views span').filter(function() {
                    $(this).removeClass('active');
                    if ($(this).data('sp-format') == view_class) {
                        return $(this);
                    }
                }).addClass('active');
            })
        }

        $('.wk-shopoint-views span').on('click', function() {

            var product_grid = $('#products_grid');
            product_grid.removeClass('shopoint_view_list shopoint_view_table shopoint_view_main');
            $(this).parent().find('.active').removeClass('active');
            $(this).addClass('active');

            let name = 'shopoint_view_main';
            if( $(this).children('i').hasClass('fa-bars') ) {
                product_grid.addClass('shopoint_view_list');
                name = 'shopoint_view_list';
            } else if( $(this).children('i').hasClass('fa-th-list') ) {
                product_grid.addClass('shopoint_view_table');
                name = 'shopoint_view_table';
            } else {
                product_grid.addClass('shopoint_view_main');
                name = 'shopoint_view_main';
            }
            ajax.jsonRpc(
                '/website/set/view', 'call', {
                'name': name
            });

        });

        // products_grid_before -> If filters & categories are inactive then we trigger four products per row
        let products_grid = $('#products_grid');
        if( !$('#products_grid_before').hasClass('col-lg-3') || $('#products_grid_before').hasClass('sp-switch-filter-category-view')) {
            product_grid.removeClass('col-lg-9').addClass('col-lg-12');
            products_grid.find('.oe_product.oe_list').addClass('oe-list-4');
        }
        else {
            product_grid.removeClass('col-lg-12').addClass('col-lg-9');
            products_grid.find('.oe_product.oe_list').removeClass('oe-list-4');
        }

        //Price Slider Range
        const $price_range = $('.sp-price-range-filter .fa');
        $price_range.on('click', function() {
            var $self = $(this);
            let $form = $(this).closest('.sp-price-range-filter').find('.price-range-wrapper');
            // if($form.hasClass('sp-price-active')) {
            //     $form.removeClass('sp-price-active');
            //     $self.removeClass('fa-minus').addClass('fa-plus');
            // } else {
            //     $form.addClass('sp-price-active');
            //     $self.removeClass('fa-plus').addClass('fa-minus');
            // }
            if($form.hasClass('sp-price-active')) {
                $form.removeClass('sp-price-active').addClass('d-none');
                $self.removeClass('fa-minus').addClass('fa-plus');
            } else {
                $form.removeClass('d-none').addClass('sp-price-active');
                $self.removeClass('fa-plus').addClass('fa-minus');
            }
        })
        //Price text fields default values are set & on change price range filter values are set
        let $price_range_conatiner = $('.sp-price-range-filter');
        if($price_range_conatiner.length > 0) {
            let $price_range = $price_range_conatiner.find('.range-slider');
            let $min_price = $price_range_conatiner.find('.sp-min-price');
            let $max_price = $price_range_conatiner.find('.sp-max-price');
            var min_price = $price_range.attr('value').split(',')[0];
            var max_price = $price_range.attr('value').split(',')[1];
            $min_price.val(min_price);
            $max_price.val(max_price);
            $price_range.on('change', function() {
                $min_price.val(parseInt($(this).attr('value').split(',')[0]));
                $max_price.val(parseInt($(this).attr('value').split(',')[1]));
            });
        }
        const $default_range_slider = $('.default-range-slider');
        if($default_range_slider.length) {
            let default_from = parseInt($default_range_slider.attr('value').split(',')[0]);
            let default_to = parseInt($default_range_slider.attr('value').split(',')[1]);
            var width = $('.category_slider').length ? '90%' : '95%';
            $('.range-slider').jRange({
                from: default_from,
                to: default_to,
                showScale : false,
                showLabels: false,
                width: width,
                isRange : false,
            });
        }

        //Quick View
        $(document).on('click', '.shopoint-zoom-img', function() {
            let $self = $(this);
            let product_tmpl_id = $(this).data('product-id');
            ajax.jsonRpc('/shop/product/data','call', {
                'product_id': product_tmpl_id
            }).then(function(data) {
                if($('.homepage').length == 0) {
                    $('.oe_website_sale').find('#sp_eye_view_modal').remove();// Prevent Multiple modals to get in the DOM
                    $('.oe_website_sale').append(data);
                    $('#sp_eye_view_modal').modal('show');
                } else {
                    $('.multi_product_carousel').find('#sp_eye_view_modal').remove();// Prevent Multiple modals to get in the DOM
                    $('.multi_product_carousel').append(data);
                    $('#sp_eye_view_modal').modal('show');
                }
                $('#sp_eye_view_modal .carousel-indicators').owlCarousel ({
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
            });
        });

        $('.oe_product').hover(function() {
            let $product_extra_image = $(this).find('.product-extra-image');
            if($product_extra_image.length > 0 ) {
                $product_extra_image.css('opacity', '1');
                $product_extra_image.siblings('span').css('opacity','0');
            }
        }, function() {
            let $product_extra_image = $(this).find('.product-extra-image');
            if($product_extra_image.length > 0 ) {
                $product_extra_image.css('opacity', '0');
                $product_extra_image.siblings('span').css('opacity', '1');
            }
        });
    });

});
