import click
import os

@click.group()
def cli():
    """ Welcome to the cli of hgossip"""
    pass

@click.command()
def updatelang():
    """Update all languages."""
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
        raise RuntimeError('Extract command failed.')
    if os.system('pybabel update -i messages.pot -d translations'):
        raise RuntimeError('Update command failed.')
    os.remove('messages.pot')


@click.command()
def compilelang():
    """Compile all languages."""
    if os.system('pybabel compile -d translations'):
        raise RuntimeError('Compile command failed.')


@click.command()
@click.argument('langcode')
def initlang(langcode):
    """Initialize a new language."""
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
        raise RuntimeError('Extract command failed.')
    if os.system('pybabel init -i messages.pot -d translations -l ' + langcode):
        raise RuntimeError('init command failed.')
    os.remove('messages.pot')

cli.add_command(updatelang)
cli.add_command(compilelang)
cli.add_command(initlang)

if __name__ == '__main__':
    cli()