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
import fileinput
import re
import sys
import urllib


def escape_comma(buff):
    """Because otherwise Firefox is a sad panda."""
    return buff.replace(',', '%2c')


def get_title(fname):
    title = ""
    foreach = ""
    for line in fileinput.input(fname):
        m = re.match("title = (.+)", line)
        if m:
            title = m.group(1)

        m = re.match("foreach = (.+)", line)
        if m:
            foreach = escape_comma(m.group(1))
    fileinput.close()
    return title, foreach


def get_sections(fname):
    sections = []
    sname = None
    for line in fileinput.input(fname):
        m = re.match('\[section "([^"]+)', line)
        if m:
            sname = m.group(1)
        elif sname:
            m = re.match("query = (.+)", line)
            if m:
                query = escape_comma(m.group(1))

                sections.append({'title': sname, 'query': query})
    fileinput.close()
    return sections


def gen_url(title, foreach, sections):
    base = 'https://review.openstack.org/#/dashboard/?'
    base += urllib.urlencode({'title': title, 'foreach': foreach})
    base += '&'
    encoded = [urllib.urlencode({x['title']: x['query']}) for x in sections]
    base += '&'.join(encoded)
    return base


def get_options():
    parser = argparse.ArgumentParser(
        description='Create a gerrit dashboard URL from a dashboard definition')
    parser.add_argument('dash',
                        metavar='dashboard_file',
                        help="Dashboard file to create url from")
    return parser.parse_args()


def main():
    opts = get_options()
    title, foreach = get_title(opts.dash)
    sections = get_sections(opts.dash)
    url = gen_url(title, foreach, sections)
    print("URL for %s" % title)
    print(url)


if __name__ == '__main__':
    sys.exit(main())
