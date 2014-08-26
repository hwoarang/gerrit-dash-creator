#!/usr/bin/env python
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import argparse
import os
import os.path
import sys
import urllib

from six.moves import configparser


def escape_comma(buff):
    """Because otherwise Firefox is a sad panda."""
    return buff.replace(',', '%2c')


def generate_dashboard_url(dashboard):
    """Generate a dashboard URL from a given definition."""
    try:
        title = dashboard.get('dashboard', 'title')
    except configparser.NoOptionError:
        raise ValueError("option 'title' in section 'dashboard' not set")

    try:
        foreach = escape_comma(dashboard.get('dashboard', 'foreach'))
    except configparser.NoOptionError:
        raise ValueError("option 'foreach' in section 'dashboard' not set")

    try:
        baseurl = dashboard.get('dashboard', 'baseurl')
    except configparser.NoOptionError:
        baseurl = 'https://review.openstack.org/#/dashboard/?'

    base = baseurl
    base += urllib.urlencode({'title': title, 'foreach': foreach})
    base += '&'
    for section in dashboard.sections():
        if not section.startswith('section'):
            continue

        try:
            query = dashboard.get(section, 'query')
        except configparser.NoOptionError:
            raise ValueError("option 'query' in '%s' not set" % section)

        title = section[9:-1]
        encoded = urllib.urlencode({title: query})
        base += "&%s" % encoded
    return base


def get_options():
    """Parse command line arguments and options."""
    parser = argparse.ArgumentParser(
        description='Create a Gerrit dashboard URL from specified dashboard '
                    'definition files')
    parser.add_argument('dashboard_files', nargs='+',
                        metavar='dashboard_file',
                        help='Dashboard definition file to create URL from')
    return parser.parse_args()


def read_dashboard_file(fname):
    """Read and parse a dashboard definition from a specified file."""
    dashboard = configparser.ConfigParser()
    dashboard.readfp(open(fname))
    return dashboard


def main():
    """Entrypoint."""
    result = 0
    opts = get_options()

    for dashboard_file in opts.dashboard_files:
        if (not os.path.isfile(dashboard_file) or
                not os.access(dashboard_file, os.R_OK)):
            print("\nerror: dashboard file '%s' is missing or is not "
                  "readable" % dashboard_file)
            result = 1
            continue

        try:
            dashboard = read_dashboard_file(dashboard_file)
        except configparser.Error as e:
            print("\nerror: dashboard file '%s' cannot be parsed\n\n%s" %
                  (dashboard_file, e))
            return 1
            continue

        try:
            url = generate_dashboard_url(dashboard)
        except ValueError as e:
            print("\nerror:\tgenerating dashboard '%s' failed\n\t%s" %
                  (dashboard_file, e))
            result = 1
            continue

        print("\nGenerated URL for the Gerrit dashboard '%s':\n" %
              dashboard_file)
        print(url)

    return result


if __name__ == '__main__':
    sys.exit(main())
