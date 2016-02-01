[WIP] Mopidy Jukebox
====================

Mopidy Jukebox is an HTTP client and Frontend for the Mopidy music server.

.. contents::

Introduction
------------

This package can be used at parties, where people can vote for music

API
---

The web api is as following

Voting
~~~~~~

Voting for a track can be done at

.. code-block::

    /jukebox-api/vote

This endpoint supports :code:`POST`, :code:`PUT` and :code:`DELETE`. The track-uri from Mopidy is sent along in the body of the request as form data. The key for the track is :code:`track`.

Searching
~~~~~~~~~

Searching for a track can be done at

.. code-block::

    /jukebox-api/search

This endpoint supports :code:`POST`. The search query is sent along in the body of the request as form data. :code:`field` holds the field to search in and :code:`values` holds the string to search for.

Possible values for :code:`field` are:

* comment
* album
* performer
* artist
* track_name
* uri
* genre
* albumartist
* track_no
* composer
* date
* any

License
-------

This work is licenced under the MIT-License, see LICENSE.txt
