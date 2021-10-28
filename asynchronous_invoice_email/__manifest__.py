# Copyright 2020 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Asynchronous Invoice Email",
    "summary": "Send emails with invoices asynchronously",
    "version": "13.0.1.0.0",
    "category": "Invoice",
    "website": "https://www.sygel.es",
    "author": "Sygel",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account",
        "queue_job",
    ],
}
