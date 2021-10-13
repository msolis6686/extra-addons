odoo.define('theme_shopoint.my_home', function (require) {
'use strict';

    var sAnimations = require('website.content.snippets.animation');
    var ajax = require('web.ajax');

    sAnimations.registry.myHome = sAnimations.Class.extend({
        selector: '.sp_address_book',
        read_events: {
            'click .js_delete_address': '_delete_address'
        },
        _delete_address: function(evt) {
            let partner_id = $(evt.currentTarget).closest('.one_kanban').find('input[name="partner_id"]').attr('value');
            console.log(partner_id);
            ajax.jsonRpc('/delete/partner','call', {
                'partner_id': partner_id
            })
            .then(function(result) {
                if(result == true) {
                    $(evt.currentTarget).closest('.one_kanban').hide();
                }
            })
        }
    })


});
