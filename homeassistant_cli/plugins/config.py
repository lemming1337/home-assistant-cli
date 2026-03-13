"""Configuration plugin for Home Assistant CLI (hass-cli)."""
import sys

import click

from homeassistant_cli.cli import pass_context
from homeassistant_cli.config import Configuration
from homeassistant_cli.helper import format_output
import homeassistant_cli.remote as api


@click.group('config')
@pass_context
def cli(ctx):
    """Get configuration from a Home Assistant instance."""
    ctx.auto_output('table')


COLUMNS_DETAILS = [
    ("VERSION", "version"),
    ("CONFIG", "config_dir"),
    ("TZ", "time_zone"),
    ("LOCATION", "location_name"),
    ("LONGITUDE", "longitude"),
    ("LATITUDE", "latitude"),
    ("ELEVATION", "elevation"),
    ("UNITS", "unit_system"),
]


@cli.command()
@pass_context
def full(ctx: Configuration):
    """Get full details on the configuration from Home Assistant."""
    click.echo(
        format_output(
            ctx,
            [api.get_config(ctx)],
            columns=ctx.columns if ctx.columns else COLUMNS_DETAILS,
        )
    )


@cli.command()
@pass_context
def components(ctx: Configuration):
    """Get loaded components from Home Assistant."""
    click.echo(
        format_output(
            ctx,
            api.get_config(ctx)['components'],
            columns=ctx.columns if ctx.columns else [('COMPONENT', '$')],
        )
    )


@cli.command('allowlist_dirs')
@pass_context
def allowlist_dirs(ctx: Configuration):
    """Get the allowlisted external directories from Home Assistant.

    Displays the list of directories that Home Assistant is permitted to
    access on the host filesystem.  The setting was renamed from
    ``whitelist_external_dirs`` to ``allowlist_external_dirs`` in
    Home Assistant 2022.9; both names are checked for backwards compatibility.

    Example::

        hass-cli config allowlist_dirs
    """
    config_data = api.get_config(ctx)
    dirs = config_data.get('allowlist_external_dirs') or config_data.get(
        'whitelist_external_dirs', []
    )
    click.echo(
        format_output(
            ctx,
            dirs,
            columns=ctx.columns if ctx.columns else [('DIRECTORY', '$')],
        )
    )


@cli.command()
@pass_context
def release(ctx: Configuration):
    """Get the release of Home Assistant."""
    click.echo(
        format_output(
            ctx,
            [api.get_config(ctx)['version']],
            columns=ctx.columns if ctx.columns else [('VERSION', '$')],
        )
    )


@cli.command()
@pass_context
def check(ctx: Configuration):
    """Validate the configuration.yaml on the Home Assistant instance.

    Triggers Home Assistant to check its configuration and reports whether
    it is valid or not.  When the configuration contains errors the error
    message is included in the output.

    Exits with a non-zero status code when the configuration is invalid,
    making it safe to use in CI/CD pipelines and shell scripts.

    Example::

        hass-cli config check
        hass-cli config check && echo "Config is valid"
    """
    result = api.check_config(ctx)
    is_valid = result.get('result') == 'valid'

    click.echo(
        format_output(
            ctx,
            [result],
            columns=ctx.columns
            if ctx.columns
            else [('RESULT', 'result'), ('ERRORS', 'errors')],
        )
    )

    if not is_valid:
        sys.exit(1)
