.. image:: https://itpp.dev/images/infinity-readme.png
   :alt: Tested and maintained by IT Projects Labs
   :target: https://itpp.dev

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License: MIT

Sync POS orders
===============

The module provides instant orders synchronization between POSes related to a common *multi session*.

Server side of synchronization is handled by module ``pos_multi_session_sync``. The role of *Sync Server* may have same odoo server as well as separate odoo server (e.g. server in local network).

Instant data exchange are made via built-in longpolling feature extended by ``pos_longpolling`` module.

When POS becomes offline, i.e. don't have connection to *Sync Server*, it is only able to create new orders and not allowed to modify exising orders to avoid synchronization problems.

Some POSes may be configured to work without synchronization. In such case it will work just like without the module.

We recommend using the module together with the `pos_access_right <https://www.odoo.com/apps/modules/13.0/pos_access_right/>`__ module.

.. note::  To synchronize orders correctly, you need a permanent connection to the server.

Modules compatibility
---------------------

Some modules may not be compatible. It happens when a module adds additional data to the ``Order`` or ``Orderline`` JS model. In such cases it is necessary to add ``apply_ms_data`` and extend ``export_as_JSON``, ``init_from_JSON`` methods in corresponding models.

.. code-block:: js

    apply_ms_data: function(data) {
        // This methods is added for compatibility with module https://www.odoo.com/apps/modules/13.0/pos_multi_session/
        /*
        It is necessary to check the presence of the super method
        in order to be able to inherit the apply_ms_data
        without calling require('pos_multi_session') 
        and without adding pos_multi_session in dependencies in the manifest.

        At the time of loading, the super method may not exist. So, if the js file is loaded
        first among all inherited, then there is no super method and it is not called.
        If the file is not the first, then the super method is already created by other modules,
        and we call super method.
        */
        if (_super_order.apply_ms_data) {
            _super_order.apply_ms_data.apply(this, arguments);
        }
        this.first_new_variable = data.first_new_variable;
        this.second_new_variable = data.second_new_variable;
        // etc ...
        
        /* Call renderElement direclty or trigger corresponding event if you need to rerender something after updating */
    },
    export_as_JSON: function() {
        // export new data as JSON
        var data = _super_order.export_as_JSON.apply(this, arguments);
        data.first_new_variable = this.first_new_variable;
        data.second_new_variable = this.second_new_variable;
        return data;
    },
    init_from_JSON: function(json) {
        // import new data from JSON
        this.first_new_variable = json.first_new_variable;
        this.second_new_variable = json.second_new_variable;
        return _super_order.init_from_JSON.call(this, json);
    }

The example above synchronizes ``first_new_variable``, ``second_new_variable`` and other data of accross all POSes.

The code below is a real example from module `pos_order_note <https://www.odoo.com/apps/modules/13.0/pos_order_note/>`__:

.. code-block:: js

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        apply_ms_data: function(data) {
            // This methods is added for compatibility with module https://www.odoo.com/apps/modules/13.0/pos_multi_session/
            if (_super_order.apply_ms_data) {
                _super_order.apply_ms_data.apply(this, arguments);
            }
            this.note = data.note;
            this.old_note = data.old_note;
            this.custom_notes = data.custom_notes;
            this.old_custom_notes = data.old_custom_notes;
            // rerender Order Widget after updating data
            this.pos.gui.screen_instances.products.order_widget.renderElement(true);
        },
        export_as_JSON: function() {
            var data = _super_order.export_as_JSON.apply(this, arguments);
            data.note = this.note;
            data.old_note = this.old_note;
            data.custom_notes = this.custom_notes;
            data.old_custom_notes = this.old_custom_notes;
            return data;
        },
        init_from_JSON: function(json) {
            this.note = json.note;
            this.old_note = json.old_note;
            this.custom_notes = json.custom_notes;
            this.old_custom_notes = json.old_custom_notes;
            return _super_order.init_from_JSON.call(this, json);
        }
    });

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        apply_ms_data: function(data) {
            // This methods is added for compatibility with module https://www.odoo.com/apps/modules/13.0/pos_multi_session/
            if (_super_orderline.apply_ms_data) {
                _super_orderline.apply_ms_data.apply(this, arguments);
            }
            this.custom_notes = data.custom_notes;
            this.old_custom_notes = data.old_custom_notes;
            // rerender Orderline Widget after updating data
            this.trigger('change', this);
        },
        export_as_JSON: function() {
            var data = _super_orderline.export_as_JSON.apply(this, arguments);
            data.custom_notes = this.custom_notes;
            data.old_custom_notes = this.old_custom_notes;
            return data;
        },
        init_from_JSON: function(json) {
            this.custom_notes = json.custom_notes;
            this.old_custom_notes = json.old_custom_notes;
            return _super_orderline.init_from_JSON.call(this, json);
        }
    });

Also it's possible to trigger ``new_updates_to_send`` event on data changes to force pos_multi_session module start syncronization process. Example code from `pos_product_available <https://www.odoo.com/apps/modules/13.0/pos_product_available/>`__:

.. code-block:: js

    update_product_qty_from_order_lines: function(order) {
        var self = this;
        order.orderlines.each(function(line){
            var product = line.get_product();
            product.qty_available -= line.get_quantity();
            self.refresh_qty_available(product);
        });
        // for pos_multi_session: send updates to other POSes
        order.trigger('new_updates_to_send');

    },

Questions?
==========

To get an assistance on this module contact us by email :arrow_right: help@itpp.dev

Contributors
============
* `Ivan Yelizariev <https://it-projects.info/team/yelizariev>`__
* `Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>`__
* `Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>`__


Further information
===================

Odoo Apps Store: https://apps.odoo.com/apps/modules/13.0/pos_multi_session/


Notifications on updates: `via Atom <https://github.com/it-projects-llc/pos-addons/commits/13.0/pos_multi_session.atom>`_, `by Email <https://blogtrottr.com/?subscribe=https://github.com/it-projects-llc/pos-addons/commits/13.0/pos_multi_session.atom>`_

Tested on `Odoo 12.0 <https://github.com/odoo/odoo/commit/b50f51207aa2b4c2d264fc47797a6c123a8ea15e>`_
