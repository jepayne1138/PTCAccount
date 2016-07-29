import argparse
import sys

import ptcaccount.accountcreator as accountcreator
from ptcaccount.exceptions import *


def parse_arguments(args):
    """Parse the command line arguments for the console commands.

    Args:
      args (List[str]): List of string arguments to be parsed.

    Returns:
      Namespace: Namespace with the parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description='Pokemon Trainer Club Account Creator'
    )
    parser.add_argument(
        '-u', '--username', type=str, default=None,
        help='Username for the new account (defaults to random string).'
    )
    parser.add_argument(
        '-p', '--password', type=str, default=None,
        help='Password for the new account (defaults to random string).'
    )
    parser.add_argument(
        '-e', '--email', type=str, default=None,
        help='Email for the new account (defaults to random email-like string).'
    )
    return parser.parse_args(args)


def entry():
    """Main entry point for the package console commands"""
    args = parse_arguments(sys.argv[1:])
    try:
        # Create the random account
        username, password, email = accountcreator.random_account(
            args.username, args.password, args.email
        )

        # Display the account credentials
        print('Created new account:')
        print('  Username:  {}'.format(username))
        print('  Password:  {}'.format(password))
        print('  Email   :  {}'.format(email))

    # Handle account creation failure exceptions
    except PTCInvalidPasswordException as err:
        print('Invalid password: {}'.format(err))
    except (PTCInvalidEmailException, PTCInvalidNameException) as err:
        print('Failed to create account! {}'.format(err))
    except PTCException as err:
        print('Failed to create account! General error:  {}'.format(err))
