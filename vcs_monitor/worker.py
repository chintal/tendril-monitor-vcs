#!/usr/bin/env python
# encoding: utf-8

# Copyright (C) 2017 Chintalagiri Shashank
# Released under the MIT license.

"""
Sets up a :class:`twisted.web.resource.Resource` hierarchy containing the
available pre-assembled data elements.
"""

import os
import json
import pika
from pika.adapters import twisted_connection
from twisted.internet import defer, reactor, protocol, task
from twisted.python import log

from checkoutmanager.runner import run_one
from tendril.entityhub import projects
from tendril.dox import gedaproject
from tendril.utils.config import MQ_SERVER
from tendril.utils.config import MQ_SERVER_PORT
from tendril.utils.config import SVN_SERVER_ROOT
from tendril.utils.config import SVN_ROOT

import logging
logging.basicConfig(level=logging.INFO)


@defer.inlineCallbacks
def run(connection):
    channel = yield connection.channel()
    yield channel.queue_declare(
        queue='events_vcs_commits',
        durable=True, auto_delete=False, exclusive=False
    )
    queue_object, consumer_tag = yield channel.basic_consume(
        queue='events_vcs_commits', no_ack=False
    )
    l = task.LoopingCall(process, queue_object, connection)
    l.start(0.01)


@defer.inlineCallbacks
def process(queue_object, connection):
    ch, method, properties, body = yield queue_object.get()
    if body:
        log.msg('events_vcs_commits {0}'.format(body))
        commit_info = json.loads(body)
        wcpath = get_wcpath(commit_info['repo'])
        vcs_update(wcpath)
        dox_regen(wcpath)
        disseminate(body, connection)
    yield ch.basic_ack(delivery_tag=method.delivery_tag)


def get_wcpath(repopath):
    relpath = os.path.relpath(repopath, SVN_SERVER_ROOT)
    return os.path.join(SVN_ROOT, relpath)


def vcs_update(wcpath):
    # result = run_one('up', directory=wcpath, std_output=False)
    print "VCS update for ", wcpath


def dox_regen(wcpath):
    # rval = projects.get_projects(wcpath)
    # lprojects = rval[0]
    # for project in lprojects:
    #     print " -- Regenerate dox for ", lprojects[project]
    #     gedaproject.generate_docs(lprojects[project])
    print "Regenerate dox for ", wcpath


@defer.inlineCallbacks
def disseminate(commit_info, connection):
    print "Dissemnating commit info : "
    print commit_info
    channel = yield connection.channel()
    yield channel.exchange_declare(exchange='published_vcs_commits',
                                   type='fanout')
    yield channel.basic_publish(exchange='published_vcs_commits',
                                routing_key='',
                                body=commit_info)


def start():
    parameters = pika.ConnectionParameters()
    cc = protocol.ClientCreator(
        reactor, twisted_connection.TwistedProtocolConnection, parameters
    )
    log.msg('Starting VCS post commit hook monitor')
    d = cc.connectTCP(MQ_SERVER, MQ_SERVER_PORT)
    d.addCallback(lambda x: x.ready)
    d.addCallback(run)
