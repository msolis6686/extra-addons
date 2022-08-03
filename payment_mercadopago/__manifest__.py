# pylint: skip-file
{
    "name": "Método de Pagamento Mercado Pago",
    "summary": "Payment Acquirer: Mercado Pago",
    "category": "Accounting",
    "version": "13.0.1.0.0",
    "author": "Code 137",
    "license": "Other OSI approved licence",
    "website": "http://www.code137.com.br",
    "contributors": [
        "Felipe Paloschi <paloschi.eca@gmail.com>",
    ],
    "depends": ["payment", "sale",'account','base'],
    "external_dependencies": {
        "python": ["mercadopago"],
    },
    "data": [
        "views/payment_views.xml",
        "views/invoice_action_data.xml",
        "views/invoice_view.xml",
        "views/mercadopago.xml",
        "data/mercadopago.xml",
    ],
    "application": True,
}
