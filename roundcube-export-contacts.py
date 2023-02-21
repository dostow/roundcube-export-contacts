#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Export roundcube contacts in vcard format from sqlite database.
"""

import argparse
import codecs
import json
import os
import os.path
import sqlite3
from collections import namedtuple


DEFAULT_CONFIG = "./config.json"
DEFAULT_OUT = "./out"


# structures
User = namedtuple("User", ["id", "email"])
Contact = namedtuple("Contact", ["email", "vcard", "words", "deleted"])


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="json config", default=DEFAULT_CONFIG)
    parser.add_argument("--out", help="output directory path", default=DEFAULT_OUT)
    return parser.parse_args()


def load_config(path):
    with open(path, "r") as fobj:
        config = json.load(fobj)
    return config


def get_users(sqlite_cnx):
    """Get all 'user_id' and 'username' from 'users' table.
    Args:
        sqlite_cnx: connection to sqlite database
    Returns:
        sqlite_users: sql query result
    """

    sqlite_cur = sqlite_cnx.cursor()
    query = "SELECT user_id, username FROM users"

    sqlite_cur.execute(query)
    sqlite_users = sqlite_cur.fetchall()

    return sqlite_users


def get_contacts(sqlite_cnx, user):
    """Get 'email', 'vcard', 'words' and 'del' from contacts table.
    Args:
        sqlite_cnx: connection to sqlite database
        user: User namedtuple
    Returns:
        sqlite_contacts: sql query result
    """

    sqlite_cur = sqlite_cnx.cursor()

    query = "SELECT email, vcard, words, del FROM contacts WHERE user_id = ?"
    data = (user.id, )

    sqlite_cur.execute(query, data)
    sqlite_contacts = sqlite_cur.fetchall()

    return sqlite_contacts


def save_vcard(out, vcard):
    """Save `vcard` data to `out` file.
    Args:
        out: output file
        vcard: vcard data
    """

    if os.path.exists(out):
        print("Append to file %s" % out)
    else:
        print("Create file: %s" % out)

    with codecs.open(out, "a", "utf-8") as fobj:
        fobj.write(vcard)
        fobj.write("\n")


def main():
    args = parse_args()
    config = load_config(args.config)

    if not os.path.exists(args.out):
        os.mkdir(args.out)

    # connect to databases
    sqlite_cnx = sqlite3.connect(**config["sqlite"])

    users = get_users(sqlite_cnx)
    for user in users:
        user = User(user[0], user[1])
        contacts = get_contacts(sqlite_cnx, user)
        for contact in contacts:
            contact = Contact(contact[0], contact[1], contact[2], contact[3])
            filename = "%s_%s%s.vcf" % (user.email, user.id, "_deleted" if contact.deleted else "")
            out = os.path.join(args.out, filename)
            save_vcard(out, contact.vcard)

    sqlite_cnx.close()


if __name__ == "__main__":
    main()
