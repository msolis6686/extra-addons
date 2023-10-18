# Copyright 2016-2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


{
    "name": "Cloud Platform",
    "summary": "Addons required for the Camptocamp Cloud Platform",
    "version": "13.0.2.0.0",
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Extra Tools",
    "depends": [
        "session_redis",
        "monitoring_status",
        "logging_json",
        "server_environment",  # OCA/server-tools
    ],
    "website": "https://github.com/camptocamp/odoo-cloud-platform",
    "data": [],
    "installable": True,
}
