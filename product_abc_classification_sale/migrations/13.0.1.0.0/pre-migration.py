# Copyright 2022 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _create_profile_from_config_parameters(env):
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO abc_classification_profile (
            name,
            classification_type,
            data_source,
            value_criteria,
            past_period,
            days_to_ignore,
            company_id
        )
        SELECT CONCAT('Company ', name, ' profile') as name,
            'fixed' as classification_type,
            'sale_report' as data_source,
            'sold_delivered_value' as value_criteria,
            sale_classification_days_to_evaluate,
            sale_classification_days_to_ignore,
            id
        FROM res_company
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
            INSERT INTO abc_classification_profile_level (
                profile_id,
                fixed,
                company_id,
                currency_id,
                symbol
            )
            SELECT acp.id, rc.sale_classification_a, rc.id, rc.currency_id, cur.symbol
            FROM abc_classification_profile acp
                JOIN res_company rc ON rc.id = acp.company_id
                JOIN res_currency as cur ON cur.id = rc.currency_id
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
            INSERT INTO abc_classification_profile_level (
                profile_id,
                fixed,
                company_id,
                currency_id,
                symbol
            )
            SELECT acp.id, rc.sale_classification_b, rc.id, rc.currency_id, cur.symbol
            FROM abc_classification_profile acp
                JOIN res_company rc ON rc.id = acp.company_id
                JOIN res_currency as cur ON cur.id = rc.currency_id
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
            INSERT INTO abc_classification_profile_level (
                profile_id,
                fixed,
                company_id,
                currency_id,
                symbol
            )
            SELECT acp.id, rc.sale_classification_c, rc.id, rc.currency_id, cur.symbol
            FROM abc_classification_profile acp
                JOIN res_company rc ON rc.id = acp.company_id
                JOIN res_currency as cur ON cur.id = rc.currency_id
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
            INSERT INTO abc_classification_profile_level (
                profile_id,
                fixed,
                company_id,
                currency_id,
                symbol
            )
            SELECT acp.id, 0, rc.id, rc.currency_id, cur.symbol
            FROM abc_classification_profile acp
                JOIN res_company rc ON rc.id = acp.company_id
                JOIN res_currency as cur ON cur.id = rc.currency_id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _create_profile_from_config_parameters(env)
