# encoding: utf-8
# Created by David Rideout <drideout@safaribooksonline.com> on 2/7/14 5:01 PM
# Copyright (c) 2013 Safari Books Online, LLC. All rights reserved.

from django.test import TestCase
from lxml import etree
from storage.models import Book, Alias
import storage.tools


class TestTools(TestCase):
    def setUp(self):
        pass

    def test_storage_tools_process_book_element_db(self):
        '''process_book_element should put the book in the database.'''

        xml_str = '''
        <book id="12345">
            <title>A title</title>
            <version>1.0</version>
            <aliases>
                <alias scheme="ISBN-10" value="0158757819"/>
                <alias scheme="ISBN-13" value="0000000000123"/>
            </aliases>
        </book>
        '''

        xml = etree.fromstring(xml_str)
        storage.tools.process_book_element(xml)

        self.assertEqual(Book.objects.count(), 1)
        book = Book.objects.get(pk='12345')

        self.assertEqual(book.title, 'A title')
        self.assertEqual(book.aliases.count(), 2)
        self.assertEqual(Alias.objects.get(scheme='ISBN-10').value, '0158757819')
        self.assertEqual(Alias.objects.get(scheme='ISBN-13').value, '0000000000123')

    def test_storage_tools_process_book_element_updates(self):

        xml_str_1 = '''
        <book id="book-1">
            <title>this is the first book</title>
            <version>1.0</version>
            <aliases>
                <alias scheme="ISBN-10" value="1000000001"/>
                <alias scheme="ISBN-13" value="1000000000001"/>
            </aliases>
        </book>'''
        update_xml_str_1 = '''
        <book id="1000000000001">
            <title>this is the first book, second edition</title>
            <version>2.0</version>
            <description>The second edition of the first book. New and improved!</description>
            <aliases>
                <alias scheme="ISBN-10" value="1000000001"/>
                <alias scheme="ISBN-13" value="1000000000001"/>

                <alias scheme="Proprietary" value="12345ABC"/>
            </aliases>
        </book>
        '''
        xml_str_2 = '''
        <book id="book-2">
            <title>this is the second book, Updated!</title>
            <version>1.0</version>
            <description>A short description about the second book</description>
            <aliases>
                <alias scheme="ISBN-10" value="1000000002"/>
                <alias scheme="ISBN-13" value="1000000000002"/>
            </aliases>
        </book>
        '''
        update_xml_str_2 = """
        <book id="book-2">
            <title>this is the second book</title>
            <version>2.0</version>
            <description>A short description about the second book. There is an extra sentence here.</description>
            <aliases>
                <alias scheme="ISBN-10" value="1000000002"/>
                <alias scheme="ISBN-13" value="1000000000002"/>
                <alias scheme="Proprietary, Unknown type" value="12345ABC"/>
                <alias scheme="ISBN-13" value="1000000000001"/> <!-- this one should be ignored-->
            </aliases>
        </book>"""

        xml = etree.fromstring(xml_str_1)
        storage.tools.process_book_element(xml)
        book = Book.objects.get(pk="book-1")
        self.assertEqual(book.title, "this is the first book")

        xml = etree.fromstring(xml_str_2)
        storage.tools.process_book_element(xml)
        book = Book.objects.get(pk="book-2")
        self.assertEqual(book.aliases.count(), 2)

        # Run the first update
        xml = etree.fromstring(update_xml_str_1)
        storage.tools.process_book_element(xml)

        # we should still have 2 books
        self.assertEqual(Book.objects.count(), 2)

        # book 1 should have been updated.
        # Updated title and 1 more alias
        book = Book.objects.get(pk="book-1")
        self.assertEqual(book.title, "this is the first book, second edition")
        self.assertEqual(book.aliases.count(), 3)

        # Run the second update
        xml = etree.fromstring(update_xml_str_2)
        storage.tools.process_book_element(xml)

        # Sanity check. We shoujld still only have 2 books
        self.assertEqual(Book.objects.count(), 2)

        # book 2 should have a total of 2 aliases
        book = Book.objects.get(pk="book-2")
        self.assertEqual(book.aliases.count(), 2)
