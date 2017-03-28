#!/usr/bin/env python
# encoding: utf-8

# Copyright (C) 2017 Chintalagiri Shashank
# Released under the MIT license.

"""
VCS post-commit hook
"""

import sys
import pika
import json
from subprocess import check_output

try:
    from tendril.utils.config import MQ_SERVER
    from tendril.utils.config import MQ_SERVER_PORT
except ImportError:
    MQ_SERVER = 'localhost'
    MQ_SERVER_PORT = 5672

import logging
logging.basicConfig(level=logging.WARNING)


def commit_changes(repo, revision):
    cmd = ('svnlook', 'changed', repo, '-r', revision)
    out = check_output(cmd).splitlines()
    for line in out:
        yield tuple(line.split())


def commit_author(repo, revision):
    cmd = ('svnlook', 'author', repo, '-r', revision)
    return check_output(cmd).rstrip('\n')


def commit_log(repo, revision):
    cmd = ('svnlook', 'log', repo, '-r', revision)
    return check_output(cmd).rstrip('\n')


def get_commit_info(repo, revision):
    author = commit_author(repo, revision)
    changes = [line for line in commit_changes(repo, revision)]
    message = commit_log(repo, revision)
    return author, message, changes


def trigger_update(repo, revision, transaction):
    print revision, repo
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(MQ_SERVER, MQ_SERVER_PORT)
    )
    channel = connection.channel()
    channel.queue_declare(queue='events_vcs_commits', durable=True)
    author, message, changes = get_commit_info(repo, revision)
    message = json.dumps({'repo': repo,
                          'revision': revision,
                          'transaction': transaction,
                          'author': author,
                          'message': message,
                          'changes': changes})
    channel.basic_publish(exchange='',
                          routing_key='events_vcs_commits',
                          body=message,
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # make message persistent
                          ))
    connection.close()


if __name__ == '__main__':
    prepo = sys.argv[1]
    prevision = sys.argv[2]
    ptransaction = sys.argv[3]
    trigger_update(prepo, prevision, ptransaction)
    sys.exit(0)
