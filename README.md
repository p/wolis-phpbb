# Wolis - external functional testing for phpBB

## Overview

Wolis is a test suite plus a test runner for phpBB
with a focus on quick test development and low frustration.
You can think of it as phpBB functional tests on steroids.

### Standalone

A key principle of Wolis is it is completely standalone. Unlike phpBB
functional tests which are normally executed within your phpBB repository,
Wolis is designed to be separate from phpBB repository, the tree being tested
and the tree that the web server is using during the actual testing process.
This allows for some interesting operations:

1. Check out a 3.0.11 source tree, copy it to the web root and install a
board. Then copy the tree being tested, which may have uncommitted changes,
over the installed board and run database updater.
2. Install a test board and remove the install directory before running
the remaining tests.
3. Check if the tree being tested cleanly merges into develop or develop-olympus,
even if there are uncommitted changes in the tree. For a branch based on
develop-olympus, check merge first into develop-olympus and then into develop.
4. Merge the tree being tested into develop-olympus, then into develop and
run the test suite.
5. Install an actual extension, which may not be well-behaved, into the
board and run tests.

These operations are not possible in phpBB functional tests because
they cannot modify the tree being tested.

### Rapid development

Despite functional tests existing in phpBB for quite some time, they are
few in quantity and cover rather small amount of functionality. Part of the
reason for this is they take an inordinate amount of time to write.
PHP, having been designed and still very much maintaining a focus on
being an HTML page generator for people with little programming ability,
remains poorly suited for general purpose work like running test suites.
When writing phpBB functional tests, time spent fighting the
environment exceeds time spent actually writing test cases. No more.

Wolis is mostly written in Python, a language much better suited to the task.
Furthermore it uses a test framework ([owebunit](https://github.com/p/owebunit))
specifically designed for
testing full application stacks. All in all developing test cases in
Wolis easily takes an order of magnitude less time and effort than the
corresponding phpBB functional tests would have taken, if they could even
have been written.

### JavaScript testing

Wolis makes use of [CasperJS](http://casperjs.org/)
and [PhantomJS](http://phantomjs.org/) to test the JavaScript code in phpBB.
Currently phpBB's own test suite has no comparable functionality.

### Complete test coverage

With JavaScript testing already implemented, there is nothing impossible for
Wolis as long as it runs on the host machine. In particular tests for all
implemented search backends are planned.

### No fixtures

Wolis does not deal with fixtures. Tests are run in a known sequence
and data needed by a particular test is created by a previously executed test.

phpBB functional tests are rather confused in this regard: they install
the board once per test run, be that the entire suite or a single test.
As a result, depending on whether a phpBB functional test is run individually
or as part of the full suite it would see different data.

Wolis implements crude resume support for test runs aborted part way.
A comprehensive resume implementation is pending.

### Use of third-party tools

Wolis does not shy away from using other tools to achieve its goals. Besides
using CasperJS for JavaScript testing, Wolis already uses
[jshint](http://www.jshint.com/) for JavaScript code checks.

### Black box testing

For the most part Wolis treats phpBB as a black box, that is, it does not
rely on knowledge of phpBB internals (code or database) beyond the HTML
that phpBB generates.

In practical terms, this means unit tests should still go into phpBB's
test suite.

The one exception where Wolis needs to peek into phpBB's database is
solving captchas. This is intended to be accomplished via a separate
library providing database access in a way that is convenient for test code.

### Multiple database support

Wolis already supports testing phpBB with mysql, mysqli and postgres database
drivers. Support for firebird is planned.

### Multiple phpBB version support

Wolis supports testing both phpBB 3.0 Olympus and phpBB 3.1 Ascraeus from
the same Wolis source tree. Wolis detects automatically which phpBB version
is being tested and adjusts tests accordingly.

## Status

The framework part of Wolis is still under active development. With that,
the tests themselves are reasonably stable and I expect Wolis to already offer
better test coverage than phpBB's own functional tests.

Installation is laborious but the code should work in a generic environment.

Dependency installation via composer is not implemented yet.

## Requirements

- Python 2.6 or 2.7
- [utu](https://github.com/p/utu)
- [cidict](https://github.com/p/cidict) (owebunit dependency)
- [ocookie](https://github.com/p/ocookie) (owebunit dependency)
- [owebunit](https://github.com/p/owebunit)
- [lxml](http://lxml.de/)
- [yaml](http://pyyaml.org/)
- [Python Imaging Library](http://www.pythonware.com/products/pil/)
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

## Installation

1. Install git if you do not already have it.
2. Install Python using your operating system's package manager.
3. Install virtualenv and pip. If your operating system does not provide
a package for them, follow instructions
[here](http://www.pip-installer.org/en/latest/installing.html).
4. Activate the new environment.
5. Install Python packages: `pip install -r requirements.txt`.
6. [Install PhantomJS.](http://phantomjs.org/download.html)
7. [Install CasperJS.](http://casperjs.org/installation.html)
8. Install node.js. It might be provided by your operating system's package
manager, or follow instructions [here](http://nodejs.org/download/).
9. Install npm. If it did not come with your node.js package, obtain it
from [here](https://github.com/isaacs/npm).
10. Install npm packages: `npm install -g jshint uglify-js`.
11. Edit `config/default.yaml`.
12. Configure your web server to serve PHP scripts in `test_root_phpbb`.
13. Configure your web server to serve directory listings in `responses_dir`.
14. Setup sudo access from your user account to the one running PHP scripts,
or arrange for umask/group membership to otherwise give you write access to
files that PHP creates.
15. Choose your database engine and create a database for wolis.

## Usage

To run all tests:

	./script/run

To resume a run that failed partway:

	./script/run -r

To run with a different database driver:

	./script/run -d postgres

To use an alternate configuration file:

	./script/run -c config/special.yaml

Note that `-r` requires all other options to still be passed.

## License

MIT.
