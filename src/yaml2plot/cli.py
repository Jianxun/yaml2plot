#! /usr/bin/env python
"""
yaml2plot CLI interface.

Provides command-line interface for plotting SPICE waveforms using the v1.1.0 API.
"""

import click
import sys
from pathlib import Path
from typing import Optional

import plotly.io as pio
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import DoubleQuotedScalarString
from ruamel.yaml.comments import CommentedMap

from .core.plotspec import PlotSpec
from .core.plotting import normalize_plot_data, plot as create_plot
from .loader import load_spice_raw
from .utils.env import configure_plotly_renderer


class CustomFormatter(click.HelpFormatter):
    def write_epilog(self, epilog):
        self.write_paragraph()
        self.write_text(epilog)


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option()
def cli():
    """yaml2plot (y2p) - a CLI tool for creating plots from YAML specifications and SPICE simulation waveforms.

    Examples:\n
        `y2p init sim.raw > spec.yaml` # Generate a boilerplate spec.yaml file from a raw file\n
        `y2p signals sim.raw` # List available signals in a raw file, edit the spec.yaml file to plot the signals you want\n
        `y2p plot spec.yaml` # Plot the signals in the spec.yaml file\n

    Run subcommands with `y2p <subcommand> --help` for more information.
    See the latest Documentation at: [https://Jianxun.github.io/yaml2plot/]
    """
    pass


@cli.command()
@click.argument("spec_file", type=click.Path(exists=True, path_type=Path))
@click.argument(
    "raw_file", type=click.Path(exists=True, path_type=Path), required=False
)
@click.option(
    "--raw",
    "raw_override",
    type=click.Path(exists=True, path_type=Path),
    help="Override raw file path (takes precedence over spec file raw: field)",
)
@click.option(
    "--output",
    "-o",
    "output_file",
    type=click.Path(path_type=Path),
    help="Output file path (HTML, PNG, PDF, etc.). If not specified, plot will be displayed.",
)
@click.option("--width", type=int, help="Plot width in pixels (overrides spec file)")
@click.option("--height", type=int, help="Plot height in pixels (overrides spec file)")
@click.option("--title", type=str, help="Plot title (overrides spec file)")
@click.option(
    "--theme",
    type=click.Choice(
        ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white"]
    ),
    help="Plot theme (overrides spec file)",
)
@click.option(
    "--renderer",
    type=click.Choice(["auto", "browser", "notebook", "plotly_mimetype", "json"]),
    default="auto",
    show_default=True,
    help="Plotly renderer to use when displaying plot",
)
def plot(
    spec_file: Path,
    raw_file: Optional[Path] = None,
    raw_override: Optional[Path] = None,
    output_file: Optional[Path] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    title: Optional[str] = None,
    theme: Optional[str] = None,
    renderer: str = "auto",
):
    """
    Plot SPICE waveforms using a specification file.

    The raw file can be specified in three ways (in order of precedence):
    1. --raw option (highest priority)
    2. Second positional argument: y2p plot spec.yaml sim.raw
    3. 'raw:' field in the YAML specification file (lowest priority)

    Examples:
        y2p plot spec.yaml                           # Uses raw: field from YAML
        y2p plot spec.yaml sim.raw                   # Uses positional argument
        y2p plot spec.yaml --raw sim.raw             # Uses --raw option
        y2p plot spec.yaml --output plot.html        # Save to file
        y2p plot spec.yaml --width 1200 --height 800 # Override dimensions
        y2p plot spec.yaml --title "My Analysis"     # Override title
    """
    plot.formatter_class = CustomFormatter
    # Load the specification file
    click.echo(f"Loading plot specification from: {spec_file}")
    try:
        spec = PlotSpec.from_file(spec_file)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    except ValueError as exc:
        raise click.ClickException(f"Invalid plot specification: {exc}") from exc

    # Determine which raw file to use (precedence: --raw > positional > yaml raw: field)
    final_raw_file = None
    warning_msg = None

    if raw_override:
        # --raw option takes highest precedence
        final_raw_file = raw_override
        if raw_file or spec.raw:
            warning_msg = f"CLI --raw option overrides "
            if raw_file:
                warning_msg += f"positional argument '{raw_file}'"
            if raw_file and spec.raw:
                warning_msg += f" and YAML raw: field '{spec.raw}'"
            elif spec.raw:
                warning_msg += f"YAML raw: field '{spec.raw}'"
    elif raw_file:
        # Positional argument takes second precedence
        final_raw_file = raw_file
        if spec.raw:
            warning_msg = f"CLI positional argument '{raw_file}' overrides YAML raw: field '{spec.raw}'"
    elif spec.raw:
        # YAML raw: field takes lowest precedence
        final_raw_file = Path(spec.raw)
    else:
        # No raw file specified anywhere
        raise click.ClickException(
            "No raw file specified. Use one of:\n"
            "  1. --raw option: y2p plot spec.yaml --raw sim.raw\n"
            "  2. Positional argument: y2p plot spec.yaml sim.raw\n"
            "  3. Add 'raw: sim.raw' to your YAML specification file"
        )

    # Emit warning if CLI overrides YAML
    if warning_msg:
        click.echo(f"Warning: {warning_msg}", err=True)

    # Apply CLI overrides via helper
    _apply_overrides(spec, width=width, height=height, title=title, theme=theme)

    # Load plotting data through the shared normalization adapter.
    if final_raw_file.suffix.lower() == ".csv":
        click.echo(f"Loading CSV data from: {final_raw_file}")
    else:
        click.echo(f"Loading SPICE data from: {final_raw_file}")
    try:
        data = normalize_plot_data(final_raw_file)
    except FileNotFoundError as exc:
        raise click.ClickException(f"Input data file not found: {exc}") from exc
    except (ValueError, TypeError) as exc:
        raise click.ClickException(f"Failed to load plotting data: {exc}") from exc

    # Create the plot using v1.0.0 API
    click.echo("Creating plot...")
    try:
        fig = create_plot(data, spec, show=False)
    except KeyError as exc:
        raise click.ClickException(f"Missing signal in plotting data: {exc}") from exc
    except ValueError as exc:
        raise click.ClickException(f"Failed to create plot: {exc}") from exc

    if output_file:
        # Save to file
        click.echo(f"Saving plot to: {output_file}")
        try:
            _save_figure(fig, output_file)
        except OSError as exc:
            raise click.ClickException(
                f"Failed to save plot to '{output_file}': {exc}"
            ) from exc
        click.echo("Plot saved successfully!")
    else:
        # Display the plot
        click.echo("Displaying plot...")
        # Configure renderer based on environment and CLI option
        configure_plotly_renderer()
        if renderer != "auto":
            pio.renderers.default = renderer
        click.echo(f"Using Plotly renderer: {pio.renderers.default}")
        fig.show()


@cli.command()
@click.argument("raw_file", type=click.Path(exists=True, path_type=Path))
def init(raw_file: Path):
    """
    Generate a sample plot_spec.yaml file from a raw file. \n
    Use the default independent variable as the X axis.\n
    Use `y2p init sim.raw > spec.yaml` to save the spec.yaml file.
    """
    init.formatter_class = CustomFormatter
    try:
        dataset = load_spice_raw(raw_file)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    except (ValueError, TypeError) as exc:
        raise click.ClickException(f"Failed to load SPICE data: {exc}") from exc

    # Get signals from both coordinates and data variables (coordinates first for x-axis)
    signals = list(dataset.coords.keys()) + list(dataset.data_vars.keys())

    if not signals:
        raise click.ClickException("No signals found in the raw file.")

    spec = CommentedMap()
    spec.yaml_set_comment_before_after_key(
        "title", before="Plot title (customize as needed)"
    )

    spec["raw"] = DoubleQuotedScalarString(raw_file.name)
    spec["title"] = DoubleQuotedScalarString(f"Analysis of {raw_file.name}")

    x_comment = """X-axis configuration
Independent variable of the simulation, default to the first signal in the raw file
"""
    spec.yaml_set_comment_before_after_key("x", before=x_comment)
    x_axis = CommentedMap()
    x_axis["signal"] = DoubleQuotedScalarString(signals[0])
    x_axis["label"] = DoubleQuotedScalarString(f"{signals[0]} (s)")
    spec["x"] = x_axis

    y_comment = """Y-axis configuration (add or remove axes as needed)
The Y-axis is specified as a list of sub-axes with a synchronized X-axis.
Even if you have only one Y-axis, you still need to specify it as a list.
Signal format: <Legend Name>: <Signal Name from Raw File>
"""
    spec.yaml_set_comment_before_after_key("y", before=y_comment)
    y_axes = []
    y_axis = CommentedMap()
    y_axis["label"] = DoubleQuotedScalarString("Voltage (V)")

    y_signals = CommentedMap()
    if len(signals) > 1:
        for sig in signals[1:3]:
            y_signals[sig] = DoubleQuotedScalarString(sig)
    y_axis["signals"] = y_signals
    y_axes.append(y_axis)
    spec["y"] = y_axes

    dimensions_comment = "Plot height and width in pixels. Remove to use the default (full page width)."
    spec.yaml_set_comment_before_after_key("height", before=dimensions_comment)
    spec["height"] = 600
    spec["width"] = 800
    spec["show_rangeslider"] = True

    yaml = YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.dump(spec, sys.stdout)


def _save_figure(fig, output_file: Path):
    """Save figure to various formats based on file extension using a writer map."""
    writers = {
        ".html": fig.write_html,
        ".json": fig.write_json,
        ".png": fig.write_image,
        ".pdf": fig.write_image,
        ".svg": fig.write_image,
        ".jpg": fig.write_image,
        ".jpeg": fig.write_image,
    }

    suffix = output_file.suffix.lower()
    writer = writers.get(suffix)

    if writer is None:
        click.echo(f"Warning: Unknown file extension '{suffix}', defaulting to HTML")
        writer = fig.write_html
        output_file = output_file.with_suffix(".html")

    writer(output_file)


def _apply_overrides(spec: PlotSpec, **overrides):
    """Apply non-None overrides to a PlotSpec instance."""
    for key, value in overrides.items():
        if value is not None and hasattr(spec, key):
            setattr(spec, key, value)
    return spec


@cli.command()
@click.argument("raw_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--limit",
    "-l",
    type=int,
    default=10,
    help="Limit number of signals to display (default: 10)",
)
@click.option(
    "--all", "-a", "show_all", is_flag=True, help="Show all signals, ignoring the limit"
)
@click.option("--grep", help="Filter signals by regular expression")
def signals(raw_file: Path, limit: int, show_all: bool, grep: Optional[str]):
    """
    List available signals in a SPICE raw file.

    """
    click.echo(f"Loading SPICE data from: {raw_file}")
    try:
        dataset = load_spice_raw(raw_file)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    except (ValueError, TypeError, RuntimeError) as exc:
        raise click.ClickException(f"Failed to load SPICE data: {exc}") from exc

    signals = list(dataset.coords.keys()) + list(dataset.data_vars.keys())

    if grep:
        import re

        try:
            original_signals = len(signals)
            signals = [s for s in signals if re.search(grep, s)]
            click.echo(
                f"\nFound {len(signals)} signals (out of {original_signals} total):"
            )
        except re.error as exc:
            raise click.ClickException(f"Invalid regular expression: {exc}") from exc
    else:
        click.echo(f"\nFound {len(signals)} signals:")

    display_limit = len(signals) if show_all else limit

    # Display signals with numbering
    for i, signal in enumerate(signals[:display_limit], 1):
        click.echo(f"  {i:2d}. {signal}")

    if len(signals) > display_limit:
        click.echo(f"  ... and {len(signals) - display_limit} more signals")
        click.echo(f"  (Use --limit {len(signals)} or -a to show all)")


signals.epilog = """
Examples:\n
  y2p signals sim.raw\n
  y2p signals sim.raw --limit 20\n
  y2p signals sim.raw -a\n
  y2p signals sim.raw --grep "v("
"""

if __name__ == "__main__":
    cli()
