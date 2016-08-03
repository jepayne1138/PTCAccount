Pokemon Trainer Club Account Creator v1.2.1
===========================================

Description
-----------
Automatically creates Pokemon Trainer Club accounts. When fully implemented, will allow for specifying the specific values used or can randomly generate usernames, passwords, and emails. A possible future goal might be to create a temporary email to receive and validate the confirmation email.

Use
---
**Command line interface:**

After installing the package run 'ptc' from the terminal to create a new account.
Optional parameters include *--username*, *--password*, and *--email*.
Use *--help* for command line interface help.

Example 1 (Create entirely random new account)::

    > ptc
    Created new account:
      Username:  dGXJXnAzxqmjbaP
      Password:  yUbiAgcXhBrEwHk
      Email   :  TVKzlu1AcW@6yxi6.com

Example 2 (Create a new account with specified parameters)::

    > ptc --username=mycustomusername --password=hunter2 --email=verifiable@lackmail.ru
    Created new account:
      Username:  mycustomusername
      Password:  hunter2
      Email   :  verifiable@lackmail.ru

Extra Options:

- *--email-tag*: Add the username as a tag to the email (e.g. address+username@gmail.com).

**As package:**

Import the *ptcaccount* package to create new accounts in your own scripts::

    >>> from  ptcaccount import random_account
    >>> random_account()
    {'username': 'dGXJXnAzxqmjbaP', 'password': 'yUbiAgcXhBrEwHk', 'email': 'TVKzlu1AcW@6yxi6.com', 'provider': 'ptc'}


Installation
------------
Supports Python 2 and 3.

Install from Github using pip::

    pip install git+https://github.com/jepayne1138/PTCAccount.git@v1.2.1
