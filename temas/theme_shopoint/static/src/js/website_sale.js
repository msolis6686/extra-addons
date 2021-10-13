odoo.define('theme_shopoint.website_sale', function (require) {
'use strict';

    var sAnimations = require('website.content.snippets.animation');
    var ajax = require('web.ajax');

    sAnimations.registry.websiteSaleCart = sAnimations.registry.websiteSaleCart.extend({
        _onClickEditAddress: function(ev) {
            ev.preventDefault();
            $(ev.currentTarget).closest('div.one_kanban').find('form.d-none').submit();
        },
    });
});
