odoo.define('theme_shopoint.sp_snippet_editor', function(require) {

    var core = require('web.core');
    var options = require('web_editor.snippets.options');
    var rpc = require('web.rpc');
    var editor = require('web_editor.editor');
    var snippetOptions = require('website.editor.snippets.options');
    var summernoteDefaults = require('summernote/defaults');
    
    editor.Class.include({
        save: function() {
            $('.multi_product_carousel .sp_tab-content').empty();
            $('.multi_product_carousel .sp_lav_links').empty();
            $('.single_carousel .js_products').empty();
            $('.single_carousel .static_content').empty();
            // $('.dynamic_brands_container').empty();
            $('.sp_blogs').empty();
            return this._super.apply(this, arguments);
        }
    });

    options.registry.carousel.include({
        onBuilt: function() {
            var self = this;
            if(self.$target.hasClass('twin')) {
                count = 0;
                $('.twin').each(function() {
                    self.id = 'myCarousel' + new Date().getTime() + '_' + count;
                    self.$target.attr('id', self.id);
                    self.$target.find('[data-target]').attr('data-target', '#' + self.id);
                    self._rebindEvents();
                    count ++;
                });
            } else {
                this._super.apply(this, arguments);
            }
            self._rebindEvents();
        }

    })
    
    options.registry.sp_grid_gallery = options.Class.extend({
        init: function() {
            this.$target = $('.sp_grid_gallery:not(.oe_snippet_body)');
        },
        start: function() {
            this.$target.find('.overlay').removeClass('overlay'); // sp_grid_gallery will remove the before element & will able to change the image
        },
        cleanForSave: function() {
            this.$target.find('.img-content').addClass('overlay');
        }
    });

    options.registry.sp_image_gallery_wrapper = options.Class.extend({
        init: function() {
            this.$target = $('.sp_image_gallery_wrapper:not(.oe_snippet_body)');
            this.dataTarget = $('.sp_image_gallery_wrapper:not(.oe_snippet_body)').find('img').data('target');
            this.$img = this.$target.find('img');
        },
        start: function() {
            this.$img.addClass('editor_mode_on');
            this.$img.attr('data-target','');
        },
        cleanForSave: function() {
            this.$img.removeClass('editor_mode_on');
            this.$img.attr('data-target', this.dataTarget);
        }
    });

    options.registry.sp_blogs = options.Class.extend({
        start: function() {
            if(!$('.sp_blogs .owl-carousel .owl-item').length) {
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
            }
        },
        cleanForSave: function () {
            this.$target.empty();
        }
    });

    // options.registry.dynamic_brands_opt = options.Class.extend({
    //     start: function() {
    //         this.getData(this.$target);
    //     },
    //     getData: function($el) {
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
    //     cleanForSave: function () {
    //         this.$target.empty();
    //     }
    // });

    options.registry.single_product_carousel_opt = options.Class.extend({
        start: function() {
            this.getData(this.$target);
        },
        getData: function($el) {
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
        // cleanForSave: function () {
        //     $el = this.$target;
        //     let $js_products = $el.find('.js_products');
        //     let $static_content = $el.find('.static_content');
        //     $js_products.empty();
        //     $static_content.empty();
        // }
    });

    options.registry.multi_product_carousel_opt = options.Class.extend({
        start: function() {
            this.getData(this.$target);
        },
        getData: function($el) {
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
                });
            });
        },
        // cleanForSave: function () {
        //     $el = this.$target;
        //     $el.find('.sp_lav_links').empty();
        //     $el.find('.sp_tab-content').empty();
        // }
    });

    options.registry.sp_blogs_opt = options.Class.extend({
        start: function() {
            this.getData(this.$target);
        },
        getData: function($el) {
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
                });
            });
        },
        // cleanForSave: function () {
        //     this.$target.empty();
        // }
    });

});
