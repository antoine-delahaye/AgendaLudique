import os
import sys

import click

from . import test_blueprint

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage

    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()


@test_blueprint.cli.command("run")
@click.option('--coverage/--no-coverage', default=False,
              help='Run tests under code coverage.')
@click.argument('test_names', nargs=-1)
def test(coverage, test_names):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import subprocess
        os.environ['FLASK_COVERAGE'] = '1'
        sys.exit(subprocess.call(sys.argv))

    import unittest
    if test_names:
        to_run = []
        for test in test_names:
            to_run.append("tests." + test)
        tests = unittest.TestLoader().loadTestsFromNames(to_run)
    else:
        tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=0).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()
