"""Calendar plugin for Home Assistant CLI (hass-cli)."""
import logging

import click

import homeassistant_cli.autocompletion as autocompletion
from homeassistant_cli.cli import pass_context
from homeassistant_cli.config import Configuration
from homeassistant_cli.helper import format_output
import homeassistant_cli.remote as api

_LOGGING = logging.getLogger(__name__)


@click.group('calendar')
@pass_context
def cli(ctx):
    """Interact with calendar entities in Home Assistant."""


@cli.command('list')
@pass_context
def list_cmd(ctx: Configuration):
    """List all calendar entities from Home Assistant.

    Outputs each calendar's entity_id and friendly name.

    Example::

        hass-cli calendar list
    """
    ctx.auto_output("table")

    calendars = api.get_calendars(ctx)

    cols = [
        ('ENTITY_ID', 'entity_id'),
        ('NAME', 'name'),
    ]

    ctx.echo(
        format_output(
            ctx, calendars, columns=ctx.columns if ctx.columns else cols
        )
    )


@cli.command('events')
@click.argument(
    'entity',
    required=True,
    shell_complete=autocompletion.entities,  # type: ignore
)
@click.option(
    '--since',
    default="now",
    help="Start of the event window. Accepts a timestamp or a relative "
    "expression such as '1d' or '2h'. Defaults to now.",
)
@click.option(
    '--end',
    default="7d",
    help="End of the event window. Accepts a timestamp or a relative "
    "expression. Defaults to 7 days from now.",
)
@pass_context
def events(ctx: Configuration, entity: str, since: str, end: str):
    """Show upcoming events for a calendar entity.

    ENTITY is the entity_id of the calendar (e.g. ``calendar.my_calendar``).

    Use --since and --end to define the queried time window. Both options
    accept a full ISO 8601 timestamp or a relative expression understood by
    dateparser (e.g. ``1h``, ``3d``, ``next monday``).

    Examples::

        hass-cli calendar events calendar.work
        hass-cli calendar events calendar.holidays --since now --end 30d
        hass-cli calendar events calendar.personal \\
            --since 2024-06-01 --end 2024-06-30
    """
    import dateparser

    ctx.auto_output("table")

    settings = {
        'DATE_ORDER': 'DMY',
        'TIMEZONE': 'UTC',
        'RETURN_AS_TIMEZONE_AWARE': True,
        'PREFER_DAY_OF_MONTH': 'first',
        'PREFER_DATES_FROM': 'future',
    }

    start_time = dateparser.parse(since, settings=settings)
    end_time = dateparser.parse(end, settings=settings)

    if ctx.verbose:
        click.echo(
            'Querying events for {} from {} to {}'.format(
                entity, start_time.isoformat(), end_time.isoformat()
            )
        )

    event_list = api.get_calendar_events(
        ctx, calendar_entity_id=entity, start_time=start_time, end_time=end_time
    )

    cols = [
        ('SUMMARY', 'summary'),
        ('START', 'start'),
        ('END', 'end'),
        ('DESCRIPTION', 'description'),
        ('LOCATION', 'location'),
    ]

    ctx.echo(
        format_output(
            ctx, event_list, columns=ctx.columns if ctx.columns else cols
        )
    )

    if ctx.verbose:
        click.echo(f'{len(event_list)} events found.')
