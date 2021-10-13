##############################################################################
#
#    Copyright (C) 2015  ADHOC SA  (http://www.adhoc.com.ar)
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'l10n_ar_query_document',
    'version': '13.0.1.2.0',
    'category': 'Account Reporting',
    'author': 'Moldeo Interactive,ADHOC SA',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'l10n_ar',
        'l10n_ar_afipws_fe',
    ],
    'data': [
        'views.xml',
        'wizard/wizard_view.xml'
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
}
