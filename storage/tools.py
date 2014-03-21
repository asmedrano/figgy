# encoding: utf-8
# Created by David Rideout <drideout@safaribooksonline.com> on 2/7/14 4:58 PM
# Copyright (c) 2013 Safari Books Online, LLC. All rights reserved.

from django.db import IntegrityError
from storage.models import Book, Alias


def process_book_element(book_element):
    """
    Process a book element into the database.

    :param book: book element
    :returns:
    """
    # Try and find that book by the book Id if not fallback to finding it by
    # an Alias
    try:
        book = Book.objects.get(pk=book_element.get('id'))
        update_book(book, book_element)
    except Book.DoesNotExist:
        # try and identify it by one of of its aliases
        aliases_from_book_element = [alias.get("value") for alias in book_element.xpath('aliases/alias')]
        aliases = Alias.objects.filter(value__in=aliases_from_book_element)
        # if no aliases match the identifier, then we are gonna assume this is
        # a new book
        if not aliases:
            create_book(book_element)
            return
        # if only one alias matches, then we've identified the book by an
        # alias, Update it
        update_book(aliases[0].book, book_element)

def create_book(book_element):
    book = Book(pk=book_element.get('id'))
    book.title = book_element.findtext('title')
    book.description = book_element.findtext('description')
    book.version = book_element.findtext('version')

    for alias in book_element.xpath('aliases/alias'):
        scheme = alias.get('scheme')
        value = alias.get('value')
        try:
            book.aliases.get_or_create(scheme=scheme, value=value)
        except IntegrityError:
            pass

    book.save()

def update_book(book, book_element):
    book.title = book_element.findtext('title')
    book.description = book_element.findtext('description')
    book.version = book_element.findtext('version')
    for alias in book_element.xpath('aliases/alias'):
        scheme = alias.get('scheme')
        value = alias.get('value')
        try:
            book.aliases.get_or_create(scheme=scheme, value=value)
        except IntegrityError:
            pass

    book.save()
