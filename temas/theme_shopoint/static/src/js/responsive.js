odoo.define('theme_shopoint.responsive', function (require) {
'use strict';

    var sAnimations = require('website.content.snippets.animation');

    sAnimations.registry.responsive = sAnimations.Class.extend({
        selector: '#wrapwrap',
        read_events: {
            'click .o_affix_enabled .navbar-toggler': '_render_menues',
        },
        _render_menues: function(evt) {
            evt.stopPropagation();
            var self = this;
            var $sp_top_menu = self.$target.find('#sp_top_menu');
            if ($sp_top_menu.hasClass('active')) {
                $sp_top_menu.removeClass('active mobile_view');
                $('.js_hide_mm').remove();
            } else {
                $sp_top_menu.addClass('active mobile_view');
                $sp_top_menu.append('<div class="js_hide_mm"/>');
                setTimeout(function() {
                    $('.js_hide_mm').animate({'background-color': 'rgba(0,0,0,.5)'});
                }, 480);
            }
        },
    });
});
