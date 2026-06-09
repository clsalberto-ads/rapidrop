"""Alembic environment configuration.

Uses process_revision_directives to strip DROP TABLE/DROP INDEX
operations that target PostGIS extension-owned tables (tiger, topology
schemas). This prevents Alembic from trying to drop tables owned by
the postgis_tiger_geocoder extension.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

from src.core.database import Base
from src.core.config import settings
from src.models import *  # noqa: F401, F403

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL_SYNC)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Tables in these schemas are managed by PostGIS extensions, not by us
EXTENSION_SCHEMAS = {"tiger", "tiger_data", "topology", "computations"}


def _is_extension_table(table_name: str) -> bool:
    """Check if this table belongs to a PostGIS extension.

    We check known Tiger/topology lookup tables by name.
    """
    tiger_tables = {
        "addr", "addrfeat", "bg", "county", "county_lookup",
        "countysub_lookup", "cousub", "direction_lookup",
        "edges", "faces", "featnames", "geocode_settings",
        "geocode_settings_default", "layer", "loader_lookuptables",
        "loader_platform", "loader_variables", "pagc_gaz", "pagc_lex",
        "pagc_rules", "place", "place_lookup", "secondary_unit_lookup",
        "state", "state_lookup", "street_type_lookup", "tabblock",
        "tabblock20", "topology", "tract", "zcta5", "zip_lookup",
        "zip_lookup_all", "zip_lookup_base", "zip_state", "zip_state_loc",
        "spatial_ref_sys",
    }
    return table_name in tiger_tables


def process_revision_directives(context, revision, directives):
    """Strip DROP TABLE/DROP INDEX operations for PostGIS extension tables.

    This hook runs after autogenerate and before writing the migration file.
    """
    for directive in directives:
        if hasattr(directive, "upgrade_ops") and directive.upgrade_ops:
            upgrade_ops = directive.upgrade_ops.ops
            # Filter out drop operations for extension tables
            directive.upgrade_ops.ops = [
                op for op in upgrade_ops
                if not _is_drop_extension_op(op)
            ]


def _is_drop_extension_op(op):
    """Check if a migration operation drops an extension-owned table/index."""
    from alembic.operations.ops import DropTableOp, DropIndexOp

    if isinstance(op, DropTableOp):
        return _is_extension_table(op.table_name)
    if isinstance(op, DropIndexOp):
        # DropIndexOp.table_name is often None for PG (global index names).
        # We match on index_name for known Tiger/topology index patterns.
        if op.table_name and _is_extension_table(op.table_name):
            return True
        # Known Tiger / topology index name patterns
        tiger_index_names = {
            "idx_tiger_county", "tige_cousub_the_geom_gist",
            "tiger_place_the_geom_gist", "tiger_faces_the_geom_gist",
            "idx_tiger_state_the_geom_gist", "idx_tiger_edges_countyfp",
            "idx_tiger_edges_the_geom_gist", "idx_tiger_faces_countyfp",
            "idx_tiger_faces_tfid", "idx_tiger_addr_tlid_statefp",
            "idx_tiger_addr_zip", "idx_tiger_featnames_lname",
            "idx_tiger_featnames_snd_name", "idx_tiger_featnames_tlid_statefp",
            "idx_addrfeat_geom_gist", "idx_addrfeat_tlid", "idx_addrfeat_zipl",
            "idx_addrfeat_zipr", "idx_edges_tlid",
            "place_lookup_name_idx", "place_lookup_state_idx",
            "countysub_lookup_name_idx", "countysub_lookup_state_idx",
            "county_lookup_name_idx", "county_lookup_state_idx",
            "direction_lookup_abbrev_idx", "street_type_lookup_abbrev_idx",
            "secondary_unit_lookup_abbrev_idx",
        }
        return op.index_name in tiger_index_names
    return False


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
