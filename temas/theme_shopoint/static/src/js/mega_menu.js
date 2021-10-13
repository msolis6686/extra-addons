odoo.define('theme_shopoint.mega_menu', function (require) {
'use strict';

    var sAnimation = require('website.content.snippets.animation');

    sAnimation.registry.megamenu = sAnimation.Class.extend({
        selector: "header",
        events: {
            'mouseenter .mm4 .mmcateg-content': '_render_subcateg_view',  // For mm4
            'mouseleave .mm4 .sub-categ-active': '_disable_subcateg_view', // For mm4
            'click .js_render_mm': '_render_mega_menu_dropdown',
            'click .js_trigger_submenu': '_render_sub_categ',// For mm4
            'click .navbar-toggler': '_render_mobile_mega_menu'
        },
        init: function() {
            if(window.matchMedia("(max-width: 767px)").matches) {
                this.is_mobile = true;
            } else {
                this.is_mobile = false;
            }
            return this._super.apply(this, arguments);
        },
        start: function() {
            ma5menu({
                menu: '#top .mobile_sub_menu',
                activeClass: 'active',
                position: 'left',
                closeOnBodyClick: true
            });
        },
        _render_mobile_mega_menu: function(evt) {
            evt.preventDefault();
            evt.stopPropagation();
            $('.ma5menu__toggle').trigger('click');
        },
        _render_subcateg_view: function(evt) {
            $(evt.target).parent().find('.sub-categ-active').removeClass('sub-categ-active');
            $(evt.target).find('.mmsubcateg').addClass('sub-categ-active');
        },
        _disable_subcateg_view: function(evt) {
            $(evt.target).find('.sub-categ-active').removeClass('sub-categ-active');
            $(evt.target).removeClass('sub-categ-active');
        },
        _render_mega_menu_dropdown: function(evt) {
            if (!this.is_mobile) {
                let $i = $(evt.currentTarget);
                let $mmcon = $i.siblings('.mmcon');

                if ($mmcon.hasClass('mobile_active')) {
                    $mmcon.removeClass('mobile_active active').css('display','none');
                    $i.removeClass('fa-caret-up').addClass('fa-caret-down');
                } else {
                    //Reset opened mega menu & open new mega menu
                    let $topMenu = $('#sp_top_menu.mobile_view #top_menu');
                    $topMenu.find('.mmcon').removeClass('mobile_active active').css('display','none');
                    $topMenu.find('.js_render_mm').removeClass('fa-caret-up').addClass('fa-caret-down');

                    $mmcon.addClass('mobile_active active'); // active -> Eleminate _render_mega_menu functionality on click
                    $i.removeClass('fa-caret-down').addClass('fa-caret-up');
                }
            }
        },
        _render_sub_categ: function(evt) {
            var $mmsubcateg = $(evt.currentTarget).closest('.mm-img-text').siblings('.mmsubcateg');
            let $i = $(evt.currentTarget);
            if($mmsubcateg.hasClass('active')) {
                $mmsubcateg.removeClass('active');
                $i.removeClass('fa-caret-up').addClass('fa-caret-down');
            } else {
                $mmsubcateg.addClass('active');
                $i.removeClass('fa-caret-down').addClass('fa-caret-up');
            }
        }
    });

    $(document).ready(function() {
        $('.mmcateg-content').mouseenter(function() {
            var self = this;
            if( $('body').hasClass('editor_enable') ) {
                $(self).parent().find('.sub-categ-active').removeClass('sub-categ-active');
                $(self).find('.mmsubcateg').addClass('sub-categ-active');
            }
        });
        $('.mmcateg-content').mouseleave(function() {
            var self = this;
            if( $('body').hasClass('editor_enable') ) {
                $(self).find('.sub-categ-active').removeClass('sub-categ-active');
                $(self).removeClass('sub-categ-active');
            }
        });
    });

});
