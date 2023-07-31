odoo.define('product.update_price_button', function (require) {
    "use strict";
    var core = require('web.core');
    var ListController = require('web.ListController');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var _t = core._t;
    ListController.include({
       renderButtons: function($node) {
       this._super.apply(this, arguments);
           if (this.$buttons) {
                $(this.$buttons).find('.oe_new_custom_button').on('click', function() {
                    var self =this
                    var user = session.uid;
                    //alert(user)
                    rpc.query({
                        model: 'bf.mercadopago.subscriptions',
                        method: 'get_subscriptions',
                        args: [[user],{'id':user}],
                        //args: [[self],{'self':self}],
                    }).then(function(res){
                        window.location.reload();
                    })
                });
           }
       },
    });
});