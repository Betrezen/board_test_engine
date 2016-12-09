import os
import sys
import click

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(ROOT, 'pylib'))

from libs import settings


@click.group()
def cli():
    pass


@cli.command('dbconnect')
@click.option('--dbhost', nargs=1, default='localhost', help='DB host', required=True)
@click.option('--dbport', default=9393, type=int, help='DB port')
def db(dbhost, dbport):
    settings.logger.debug('host={}, port={}'.format(dbhost, dbport))


@cli.command('zeromqconnect')
@click.option('--zeromq_serverhost', default='localhost', help='DB host', required=True)
@click.option('--zeromq_serverport', default=9595, type=int, help='DB port')
def zeromq(zeromq_serverhost, zeromq_serverport):
    settings.logger.debug('host={}, port={}'.format(zeromq_serverhost, zeromq_serverport))

if __name__ == '__main__':
    cli()
