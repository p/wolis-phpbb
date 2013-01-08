# Wolis - external functional testing for phpBB

## Overview

Wolis is a test suite plus a test runner for phpBB
with a focus on quick test development and low frustration.
You can think of it as phpBB functional tests on steroids.

The scope of Wolis is functional tests and up. Wolis can do everything
phpBB fucntional tests can do, such as:

- Installing a board
- Viewing topics and posts
- Creating posts

However, being an external tool it is not restricted to operating within
a single phpBB source tree. Thus it can also perform operations involving
multiple trees, both of different versions and of different products:

- Installing a 3.0.11 board and updating it to 3.1 via database updater
- Installing real extensions into the actual board tree
- Deleting the install directory

Being external to phpBB gives Wolis a choice of programming languages
to perform its tasks. Most of the tests are written in Python using
[owebunit](https://github.com/p/owebunit) test framework,
which is specifically being developed to ease
testing of full application stacks. This makes Wolis tests an order of
magnitude or more faster to write than equivalent phpBB functional tests.
Writing tests in Python rather than PHP accounts for additional significant
increase in productivity.

Wolis also includes frontend tests written
in CoffeeScript which are run via [CasperJS](http://casperjs.org/)
and [PhantomJS](http://phantomjs.org/) in an embedded
WebKit browser. This permits Wolis to check phpBB JavaScript functionality.

Besides tests themselves, Wolis includes a test runner. This is necessary
because the tests need to be executed in a certain order, as there is
no support for fixtures. Any data used by tests must have been created by
previously executed tests.

Having an own test runner however brings with it some additional benefits:

- Test naming can be anything. Wolis chooses to not derive sequencing
information from test names but store it explicitly and separately.
- Test suite can be meaningfully resumed after a failure.
- Dissimilar test styles (Python-owebunit backend/CoffeeScript-CasperJS
frontend) can be seamlessly integrated without needless boilerplate.

Wolis already supports testing phpBB with mysql, mysqli and postgres database
drivers. Support for firebird is planned.

Wolis supports testing both phpBB 3.0 Olympus and phpBB 3.1 Ascraeus from
the same Wolis source tree. Wolis detects automatically which phpBB version
is being tested and adjusts tests accordingly.

## Status

Wolis is already very much functional. It probably covers about half of
what phpBB functional tests cover, with the rest being straightforward
to implement. Wolis already has unique tests, such as database updater test
and JavaScript tests.

There are still a number of environmental dependencies in Wolis such as
hardcoded paths, user accounts for sudo invocations and inability to install
phpBB dependencies via composer as officially supported.

## Requirements

- Python 2.6 or 2.7
- [utu](https://github.com/p/utu)
- [ocookie](https://github.com/p/ocookie) (owebunit dependency)
- [owebunit](https://github.com/p/owebunit)
- [lxml](http://lxml.de/)
- [yaml](http://pyyaml.org/)
- [PhantomJS](http://phantomjs.org/)
- [CasperJS](http://casperjs.org/)
- [Node.js](http://nodejs.org/)
- [uglify-js](https://github.com/mishoo/UglifyJS) npm package
- [jshint](http://www.jshint.com/) npm package
- Git
- A web server configured to serve PHP
- Write access to a directory under web server's document root
- All PHP extensions needed or optionally usable by phpBB present and enabled
- Currently phpBB dependencies must be set up via
[include-path-autoload](https://github.com/p/phpbb3-include-path-autoload)
- Your favorite database engine(s) plus client libraries

Wolis should in principle be deployable to a typical Linux VPS.
