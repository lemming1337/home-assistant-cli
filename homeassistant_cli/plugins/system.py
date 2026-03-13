"""System plugin for Home Assistant CLI (hass-cli)."""
import logging
from typing import List

import click

import homeassistant_cli.autocompletion as autocompletion
from homeassistant_cli.cli import pass_context
from homeassistant_cli.config import Configuration
import homeassistant_cli.const as const
from homeassistant_cli.helper import format_output
import homeassistant_cli.remote as api

_LOGGING = logging.getLogger(__name__)


@click.group('system')
@pass_context
def cli(ctx):
    """System details and operations for Home Assistant."""


@cli.command()
@pass_context
def log(ctx):
    """Get errors from Home Assistant."""
    click.echo(api.get_raw_error_log(ctx))


@cli.command()
@pass_context
def health(ctx: Configuration):
    """Get system health from Home Assistant."""
    info = api.get_health(ctx)

    ctx.echo(
        format_output(
            ctx,
            [info],
            columns=ctx.columns if ctx.columns else const.COLUMNS_DEFAULT,
        )
    )


@cli.command()
@click.argument(
    'entity',
    required=False,
    shell_complete=autocompletion.entities,  # type: ignore
)
@click.option(
    '--since',
    default="1d",
    help="Start of the period to retrieve logbook entries from. Accepts a "
    "timestamp or a relative expression such as '1d' or '2h'. "
    "Defaults to 1 day.",
)
@click.option(
    '--end',
    default="now",
    help="End of the period to retrieve logbook entries from. Accepts a "
    "timestamp or a relative expression. Defaults to now.",
)
@pass_context
def logbook(ctx: Configuration, entity, since: str, end: str):
    """Get logbook entries from Home Assistant.

    Optionally filter by ENTITY (entity_id). Use --since and --end to
    narrow the time range.

    Both options accept a full timestamp (e.g. ``2024-01-15T10:00:00+00:00``)
    or a relative expression (e.g. ``3h``, ``2d``, ``1 week``).
    See https://dateparser.readthedocs.io/en/latest/ for full syntax.

    Examples::

        hass-cli system logbook
        hass-cli system logbook sensor.temperature --since 6h
        hass-cli system logbook --since 2024-01-01 --end 2024-01-02
    """
    import dateparser

    ctx.auto_output("table")

    settings = {
        'DATE_ORDER': 'DMY',
        'TIMEZONE': 'UTC',
        'RETURN_AS_TIMEZONE_AWARE': True,
    }

    start_time = dateparser.parse(since, settings=settings)
    end_time = dateparser.parse(end, settings=settings)

    if ctx.verbose:
        click.echo(
            'Querying logbook from {} to {}'.format(
                start_time.isoformat(), end_time.isoformat()
            )
        )

    entries = api.get_logbook(
        ctx, start_time=start_time, end_time=end_time, entity_id=entity
    )

    cols = [
        ('WHEN', 'when'),
        ('NAME', 'name'),
        ('MESSAGE', 'message'),
        ('ENTITY', 'entity_id'),
        ('STATE', 'state'),
    ]

    ctx.echo(
        format_output(
            ctx, entries, columns=ctx.columns if ctx.columns else cols
        )
    )

    if ctx.verbose:
        click.echo(f'{len(entries)} logbook entries found.')
