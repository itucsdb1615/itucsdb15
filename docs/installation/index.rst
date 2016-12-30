Installation Guide
==================

1. Install Python (version 3.4 or higher)

Our project is Python based. So you have to have Python.

2. Install Flask

We used Flask microframework for web developement.

.. code-block:: console

   pip3 install -U flask

3. Install Psycopg2

Our project needs Psycopg2 as a PostgreSQL adapter.

.. code-block:: console

   pip3 install -U psycopg2

4. Install flask_login

We used flask-login for login/session management.

.. code-block:: console

   pip3 install flask-login

5. Install passlib

We used passlib for hashing users' passwords.

.. code-block:: console

   pip3 install passlib

Once you have all of the above and also our project codes, you can run "server.py".
As long as "server.py" is running, you can connect to "localhost:5000" to view our site.