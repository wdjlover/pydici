# coding: utf-8
"""
Test cases
@author: Sébastien Renard (sebastien.renard@digitalfox.org)
@license: GPL v3 or newer
"""

# Python/Django test modules
from django.test import TestCase

# Pydici modules
from pydici.leads.models import Consultant, Client, Lead
import pydici.settings

# Python modules used by tests
from urllib2 import urlparse

TEST_USERNAME = "fox"
TEST_PASSWORD = "rototo"

class SimpleTest(TestCase):
    fixtures = ["auth.json", "core.json", "people.json", "crm.json",
                "leads.json", "staffing.json"]
    def test_basic_page(self):
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)
        for page in ("/leads/",
                     "/leads/3/",
                     "/leads/admin/",
                     "/leads/csv/all",
                     "/leads/csv/active",
                     "/leads/sendmail/2/",
                     "/leads/mail/text",
                     "/leads/mail/html",
                     "/leads/review",
                     "/leads/feeds/latest/",
                     "/leads/feeds/mine/",
                     "/leads/feeds/new/",
                     "/leads/feeds/won/",
                     "/leads/pdcreview/",
                     "/leads/pdcreview/2009/07",
                     "/leads/forbiden",
                     "/leads/mission/",
                     "/leads/mission/all",
                     "/leads/mission/1/",
                     "/leads/consultant/1/",
                     "/leads/graph/pie",
                     "/leads/graph/bar",
                     "/leads/graph/salesmen",
                     ):
            response = self.client.get(page)
            self.failUnlessEqual(response.status_code, 200,
                                 "Failed to test url %s (got %s instead of 200" % (page, response.status_code))

    def test_redirect(self):
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)
        response = self.client.get("/leads/mission/1/deactivate")
        self.failUnlessEqual(response.status_code, 302)
        response = self.client.get("/leads/help")
        self.failUnlessEqual(response.status_code, 301)

    def test_not_found_page(self):
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)
        for page in ("/leads/234/",
                     "/leads/sendmail/434/"):
            response = self.client.get(page)
            self.failUnlessEqual(response.status_code, 404,
                                 "Failed to test url %s (got %s instead of 404" % (page, response.status_code))

    def test_create_lead(self):
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)
        lead = Lead(name="laala",
                  due_date="2008-11-01",
                  update_date="2008-11-01 16:14:16",
                  creation_date="2008-11-01 15:43:43",
                  start_date="2008-11-01",
                  responsible=None,
                  sales=None,
                  external_staffing="JCF",
                  state="QUALIF",
                  client=Client.objects.get(pk=1),
                  salesman=None,
                  description="A wonderfull lead that as a so so long description")

        lead.save()
        self.failUnlessEqual(lead.staffing.count(), 0)
        lead.staffing.add(Consultant.objects.get(pk=1))
        self.failUnlessEqual(lead.staffing.count(), 1)
        # Add staffing here lead.add...
        self.failUnlessEqual(len(lead.update_date_strf()), 14)
        self.failUnlessEqual(lead.staffing_list(), "SRE, (JCF)")
        self.failUnlessEqual(lead.short_description(), "A wonderfull lead th...")
        self.failUnlessEqual(lead.get_absolute_url(),
                             pydici.settings.LEADS_WEB_LINK_ROOT + "/leads/4/")

        url = "".join(urlparse.urlsplit(lead.get_absolute_url())[2:])
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        context = response.context[-1]
        self.failUnlessEqual(unicode(context["lead"]), u"World company : DSI  - laala")
        self.failUnlessEqual(unicode(context["user"]), "fox")

    def test_pdc_review(self):
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)
        url = "/leads/pdcreview/2009/07"
        for arg in ({}, {"projected":None}, {"groupby": "manager"}, {"groupby": "position"}):
            response = self.client.get(url, arg)
            self.failUnlessEqual(response.status_code, 200,
                "Failed to test pdc_review with arg %s (got %s instead of 200" % (arg, response.status_code))
