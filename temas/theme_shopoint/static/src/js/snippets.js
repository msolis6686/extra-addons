odoo.define('theme_shopoint.snippets', function (require) {
'use strict';

    var rpc = require('web.rpc');
    var sAnimation = require('website.content.snippets.animation');

    sAnimation.registry.render_categ_products = sAnimation.Class.extend({
        selector: ".sp_multi_func",
        start: function() {
            var self = this;
            rpc.query({
                route: '/shopoint/categories/products',
                params: {'public_categ_id': self.$target.find('a').attr('href')},
            }).then(function(result){
                if(result.hasOwnProperty('template')) {
                    self.$target.find('.sp_home_categories').empty().append(result.template);
                }
            });
        }
    });

    sAnimation.registry.render_snippet = sAnimation.Class.extend({
        selector: ".sp_image_gallery_wrapper",
        events: {
            'click img:not(.editor_mode_on)': '_render_modal'
        },
        start: function() {
            let src = []
            this.$target.find('.image_gallery_img img').each(function() {
                src.push($(this).attr('src'));
            });
            this.$target.find('.carousel-inner div').each(function(index) {
                let style = `background-image: url(${src[index]})`;
                $(this).attr('style', style);
            });
        },
        _render_modal: function(evt) {
            const $target = $(evt.target);
            let targetNumber = $target.data('step');
            $target.parent().find('.active').removeClass('active');
            $target.parent().find('.carousel-indicators li').filter(function(index) {
                if(index == targetNumber) {
                    $(this).addClass('active');
                }
            })
            $target.parent().find('.carousel-inner div').filter(function(index) {
                if(index == targetNumber) {
                    $(this).addClass('active');
                }
            });
            $('#imageGallery').modal('show');
        }
    });

    sAnimation.registry.multi_product_carousel = sAnimation.Class.extend({
        selector: ".multi_product_carousel",
        start: function() {
            let $el = this.$el;
            rpc.query({
                route: '/dynamic/data',
                params: {
                    'data_of': 'multi_carousel'
                },
            }).then(function(data) {
                $el.find('.sp_lav_links').html(data.links);
                let $sp_tab_content = $el.find('.sp_tab-content');
                $sp_tab_content.empty();
                $.each(data.tabs, function(i, item) {
                    $sp_tab_content.append(item);
                })
                $el.find('.owl-carousel').owlCarousel ({
                    margin:10,
                    nav:false,
                    dots: true,
                    responsive:{
                        0:{
                            items:1
                        },
                        600:{
                            items:3
                        },
                        1000:{
                            items:data.items_number
                        }
                    }
                })
            });
        },
    });

    sAnimation.registry.single_product_carousel = sAnimation.Class.extend({
        selector: ".single_carousel",
        read_events: {
            'click .left': '_trigger_left_event',
            'click .right': '_trigger_right_event',
        },
        start: function() {
            let $el = this.$el;
            rpc.query({
                route: '/dynamic/data',
                params: {
                    'data_of': 'single_carousel'
                },
            }).then(function(data) {
                let $js_products = $el.find('.js_products');
                let $static_content = $el.find('.static_content');
                $js_products.empty().append(data.single_carousel_products);
                $static_content.empty().append(data.single_carousel_content);
                $js_products.find('.owl-carousel').owlCarousel ({
                    margin:10,
                    nav: true,
                    dots: false,
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
                })
            });
        },
        _trigger_left_event: function(evt) {
            this.$target.find('.owl-prev').trigger('click');
        },
        _trigger_right_event: function(evt) {
            this.$target.find('.owl-next').trigger('click');
        }
    });

    // sAnimation.registry.dynamic_brands = sAnimation.Class.extend({
    //     selector: ".dynamic_brands_container",
    //     start: function() {
    //         let $el = this.$el;
    //         rpc.query({
    //             route: '/dynamic/data',
    //             params: {
    //                 'data_of': 'dynamic_brands'
    //             },
    //         }).then(function(data) {
    //             $el.empty().append(data);
    //             $el.find('.owl-carousel').owlCarousel({
    //                 margin: 10,
    //                 nav: true,
    //                 dots: false,
    //                 autoplay: true,
    //                 responsive:{
    //                     0:{
    //                         items:1
    //                     },
    //                     600:{
    //                         items:3
    //                     },
    //                     1000:{
    //                         items:6
    //                     }
    //                 }
    //             })
    //         });
    //     },
    // });
    sAnimation.registry.blog = sAnimation.Class.extend({
        selector: ".sp_blogs",
        start: function() {
            let $el = this.$el;
            rpc.query({
                route: '/dynamic/data',
                params: {
                    'data_of': 'blog'
                },
            }).then(function(data) {
                $el.empty().append(data);
                $el.find('.owl-carousel').owlCarousel({
                    margin: 10,
                    nav: false,
                    dots: true,
                    autoplay: true,
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
                })
            });
        },
    });

    $(document).ready(function() {
        $('body').on('DOMSubtreeModified', function() {
            if( $(this).hasClass('editor_enable') ) {

                $('.image_gallery_img img').attr('data-toggle', '');

                $('.about_us_2 .overlay').remove();
                $('.about_us_2').removeClass('z_index');

            } 
        });
    });

});