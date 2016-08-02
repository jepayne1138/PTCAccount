from six.moves import range
import random
import string
# urllib imports supporting Python 2 and 3
try:
    # Python 3
    from urllib.parse import urlencode
except ImportError:
    # Python 2
    from urllib import urlencode

import requests

from ptcaccount.exceptions import *


__all__ = ['create_account', 'random_account']

# The base URL for Pokemon Trainer Club
_BASE_URL = 'https://club.pokemon.com/us/pokemon-trainer-club'

# Account creation validation is done by checking the response URLs
# The following are control flow URL constants
_SUCCESS_DESTS = (
    'https://club.pokemon.com/us/pokemon-trainer-club/parents/email',  # This initially seemed to be the proper success redirect
    'https://club.pokemon.com/us/pokemon-trainer-club/sign-up/',  # but experimentally it now seems to return to the sign-up, but still registers
)
# As both seem to work, we'll check against both success destinations until I have I better idea for how to check success
_DUPE_EMAIL_DEST = 'https://club.pokemon.com/us/pokemon-trainer-club/forgot-password?msg=users.email.exists'
_BAD_DATA_DEST = 'https://club.pokemon.com/us/pokemon-trainer-club/parents/sign-up'


class PTCSession(requests.Session):

    """"A Session subclass handling creating, sending, & validating requests

    A likely unnecessary subclass of requests.Session, but I thought it
    helped to clean up the code.
    """

    def request(self, url, headers=None, data=None, resp_code=None, **kwargs):
        """
        Creates, sends, and validates a request for this session.

        If data parameter is provided, the request will be POST, otherwise
        a GET request is sent

        If a specific response status code is
        expected, set the resp_code parameter and the status code of the
        response will be validated after sending the request. If the status
        codes doesn't match, an exception is raised.

        Args:
          url (str): URL to send.
          headers (dict, optional): Headers to send. Defaults to {}.
          data (dict, optional): Data for a POST request. Defaults to {}.
          resp_code (int, optional): Check if this status code was returned
            upon receiving a response. If no desired code is given, no
            check will be made to validate the response status_code.
            Defaults to None.
          **kwargs: Keyword arguments passed to the Request object.

        Returns:
          requests.Response: The Response object for the sent request.

        Raises:
          PTCInvalidStatusCodeException: If a desired response code was
            provided (resp_code), raise this exception if the actual
            response status codes does not match the desired code.
        """
        # Set headers to an empty dict if no argument provided
        headers = {} if headers is None else headers

        # Encode the data dict if provided
        if isinstance(data, dict):
            data = urlencode(data, doseq=True)
        # If data provided, the request must be a POST method
        method = 'POST' if data else 'GET'

        # Create, prepare, and send the request
        req = requests.Request(method, url, data=data, **kwargs)
        prepped = self.prepare_request(req)
        prepped.headers.update(headers)
        resp = self.send(prepped)

        # Validate the status_code if a desired code was given
        if resp_code is not None and resp.status_code != resp_code:
            raise PTCInvalidStatusCodeException(str(resp.status_code))

        # Return the Response object
        return resp


def _random_string(length=15):
    """Generate a random alpha-numeric string of the given length

    Args:
      length (int, optional): Length of the string to randomly generate.
        Defaults to 15.

    Returns:
      str: String of the desired length consiting of upper, lower, and
        numeric characters.
    """
    return ''.join(
        [random.choice(string.ascii_letters + string.digits) for _ in range(length)]
    )


def _random_email(local_length=10, sub_domain_length=5, top_domain='.com'):
    """Generate a random email-like string

    Generates a random email-like string (i.e. local@subdomain.domain).
    The length of both the local section and sub-domain section can be
    modified, and a different top-level domain can be set.

    Args:
      local_length (int, optional): Length of the local portion of the fake
        email. Defaults to 10.
      sub_domain_length (int, optional): Length of the sub-domain portion of
        the fake email. Defaults to 5.
      top_domain (str, optional): String to append to the end of the fake
        email as the top-level domain. Defaults to '.com'

    Returns:
      str: Random email-like string.
    """
    return '{local}@{sub_domain}{top_domain}'.format(
        local=_random_string(local_length),
        sub_domain=_random_string(sub_domain_length),
        top_domain=top_domain,
    )


def _validate_password(password):
    """Validates that the password can be used to create a PTC account

    As currently the only requirement I am aware of is a length restriction,
    this only checks that the give password string is between 6 and 15
    characters long. If I determine any other restrictions, they can be
    added here later.

    Args:
      password (str, optional): Password to be validated.

    Returns:
      bool: True if the password is valid. (Does not return false, rather
        raise exception with description of invalid nature.)

    Raises:
      PTCInvalidPasswordException: If the given password is not a valid
        password that can be used to make an account. (Currently just
        validates length, so this means the given password was not between
        6 and 15 characters long.)
    """
    # Check that password length is between 6 and 15 characters long
    if len(password) < 6 or len(password) > 15:
        raise PTCInvalidPasswordException('Password must be between 6 and 15 characters.')
    return True


def _tag_email(email_address, tag):
    """Add a plus sign and the tag before the first at sign in the email

    Args:
      email_address (str): Email address tag is to be added to.
      tag (str): Tag to add after the plus sign before first at sign.

    Returns:
      str: Email with the tag added.
    """
    return email_address.replace('@', '+{}@'.format(tag), 1)


def create_account(username, password, email):
    """Creates a new Pokemon Trainer Club account

    Creates a new PTC account with the given username, password and email.
    Currently sets the following account settings:
      - Date of birth: 1970-01-01
      - Country: US
      - Public profile: False
      - Screen name: ''

    Args:
      username (str): Username for the PTC account
      password (str): Password for the PTC account
      email (str): Email for the PtC account

    Returns:
      bool: True if the account was successfully created. (Should not ever
        return false, rather raise exceptions detailing type of failure.)

    Raises:
      PTCInvalidNameException: If the given username is already in use.
      PTCInvalidPasswordException: If the given password is not a valid
        password that can be used to make an account. (Currently just
        validates length, so this means the given password was not between
        6 and 15 characters long.)
      PTCInvalidEmailException: If the given email was either in an invalid
        format (i.e. not local@subdomain.domain) or the email is already
        registered to an existing account.
      PTCInvalidStatusCodeException: If an invalid status code was received
        at any time. (Server or underlying code issue; try again and submit
        bug report on continues failure if creation works in browser.)
    """
    # Validate a user given password
    if password is not None:
        _validate_password(password)

    # Set up the session
    session = PTCSession()

    # (Emulates navigating to the sign-up age verification page)
    session.request(
        url='{base_url}/parents/sign-up'.format(base_url=_BASE_URL),
        headers={  # No headers required
            'Host': 'club.pokemon.com',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch, br',
            'Accept-Language': 'en-US,en;q=0.8',
        },
        resp_code=200
    )

    # Post request submitting date of birth and country
    session.request(
        url='{base_url}/sign-up/'.format(base_url=_BASE_URL),
        headers={  # Content-Type and Referer headers are required
            'Host': 'club.pokemon.com',
            'Cache-Control': 'max-age=0',
            'Origin': 'https://club.pokemon.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer': '{base_url}/sign-up/'.format(base_url=_BASE_URL),
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.8'
        },
        data={
            'csrfmiddlewaretoken': session.cookies.get_dict()['csrftoken'],
            'dob': '1970-01-01',
            'country': 'US',
        },
        resp_code=200
    )

    # Post request submitting account information
    resp = session.request(
        url='{base_url}/parents/sign-up'.format(base_url=_BASE_URL),
        headers={  # Content-Type and Referer headers are required
            'Host': 'club.pokemon.com',
            'Cache-Control': 'max-age=0',
            'Origin': 'https://club.pokemon.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer': 'https://club.pokemon.com/us/pokemon-trainer-club/parents/sign-up',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.8'
        },
        data={
            'csrfmiddlewaretoken': session.cookies.get_dict()['csrftoken'],
            'username': username,
            'password': password,
            'confirm_password': password,
            'email': email,
            'confirm_email': email,
            'public_profile_opt_in': 'False',
            'screen_name': '',
            'terms': 'on',
        },
        resp_code=200
    )

    # Validate response
    return _validate_response(resp)


def _validate_response(resp):
    """Validate final request response to determine if account was created

    Args:
      resp (requests.Response): Response instance from sending a requests

    Returns:
      bool: True if the account was successfully created. (Should not ever
        return false, rather raise exceptions detailing type of failure.)

    Raises:
      PTCInvalidNameException: If the given username is already in use.
      PTCInvalidPasswordException: If the given password is not a valid
        password that can be used to make an account. (Currently just
        validates length, so this means the given password was not between
        6 and 15 characters long.)
      PTCInvalidEmailException: If the given email was either in an invalid
        format (i.e. not local@subdomain.domain) or the email is already
        registered to an existing account.
      PTCInvalidStatusCodeException: If an invalid status code was received
        at any time. (Server or underlying code issue; try again and submit
        bug report on continues failure if creation works in browser.)
    """
    if resp.url in _SUCCESS_DESTS:
        return True
    elif resp.url == _DUPE_EMAIL_DEST:
        raise PTCInvalidEmailException('Email already in use.')
    elif resp.url == _BAD_DATA_DEST:
        if 'Enter a valid email address.' in resp.text:
            raise PTCInvalidEmailException('Invalid email.')
        else:
            raise PTCInvalidNameException('Username already in use.')
    else:
        raise PTCException('Generic failure. User was not created.')
    return False  # Should never hit here


def random_account(username=None, password=None, email=None, email_tag=False):
    """Crate a random Pokemon Trainer Club account

    Creates a new account with random username, password, and email.
    If any of those parameters are given, use them instead of creating
    a random replacement.

    If a password is given, it must be valid, and an exception will be
    raised if the password is not acceptable.

    New random strings will be generated for username and email on a failure
    so that eventually a new account will be successfully created. However,
    if a specific username or email was given and account creation fails,
    a new string will not be generated as it assumes the user wanted to use
    that specific value. Instead, and exception is raised indicating the
    reason for account creation failure.

    Args:
      username (str, optional): Specific username for the new account.
        Defaults to a random alpha-numeric string.
      password (str, optional): Specific password for the new account.
        Defaults to a random alpha-numeric string.
      email (str, optional): Specific email for the new account. Defaults
        to a randomly generated email-like string.

    Returns:
      Tuple[str, str, str]: A tuple containing the final username, password,
       and email of the new account, respectfully.

    Raises:
      PTCInvalidNameException: If the given username is already in use.
      PTCInvalidPasswordException: If the given password is not a valid
        password that can be used to make an account. (Currently just
        validates length, so this means the given password was not between
        6 and 15 characters long.)
      PTCInvalidEmailException: If the given email was either in an invalid
        format (i.e. not local@subdomain.domain) or the email is already
        registered to an existing account.
      PTCInvalidStatusCodeException: If an invalid status code was received
        at any time. (Server or underlying code issue; try again and submit
        bug report on continues failure if creation works in browser.)
    """
    try_username = _random_string() if username is None else str(username)
    password = _random_string() if password is None else str(password)
    try_email = _random_email() if email is None else str(email)

    account_created = False
    while not account_created:
        # Add tag in loop so that it is update if email or username changes
        if email_tag:
            try_email = _tag_email(try_email, try_username)

        # Attempt to create the new account
        try:
            account_created = create_account(
                try_username, password, try_email
            )
        except PTCInvalidNameException:
            # If no username was provided, create new username and try again
            if username is None:
                try_username = _random_string()
            else:
                # If username was provided, re-raise the exception for bad name
                raise
        except PTCInvalidEmailException:
            if email is None:
                try_email = _random_email()
            elif email_tag and username is None:
                # If the bad email has a tag of a random username,
                # re-generate a new username and try again
                try_username = _random_string()
            else:
                # If email was provided, re-raise the exception for bad email
                raise

    # Return the username, password, and email of the new account
    return (try_username, password, try_email)
