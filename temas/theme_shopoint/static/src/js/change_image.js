odoo.define('theme_shopoint.change_image', function (require) {
'use strict';

    var ajax = require('web.ajax');
    var sAnimation = require('website.content.snippets.animation');

    sAnimation.registry.changeImage = sAnimation.Class.extend({
        selector: "#wk_user_image",
        read_events: {
            'click .wk_delete_icon': '_delete_image',
            'click #apply_image': '_apply_image',
        },
        _delete_image: function() {
            ajax.jsonRpc(
                '/change/image', 'call', {
                'action':'delete'
            }).then(function(){
                location.reload();
            });
        },
        _apply_image: function() {
            var file = document.querySelector('#file').files[0];
            var reader  = new FileReader();
            reader.addEventListener("load", function () {
                var result = reader.result;
                ajax.jsonRpc('/change/image','call',{
                    'action':'edit',
                    'data': result
                }).then(function(){
                    location.reload();
                });
            }, false);
            if (file) {
                reader.readAsDataURL(file);
            }
        }
    });

});
