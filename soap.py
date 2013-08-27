import logging
from soaplib.serializers.primitive import String
from soaplib.service import DefinitionBase, rpc
from soaplib.wsgi import Application
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import httplib2
from django.template import Template
from django.template.context import Context
from django.utils.encoding import smart_str, smart_unicode
from xml.etree.ElementTree import XML
# the class with actual web methods

#logger = logging.getLogger(__name__)


class QuoteSOAPService(DefinitionBase):
    @rpc(String, _returns=String)
    def updatequote(self, quote_id):
        logging.info("SAP is sending quote")
        url = "https://login.salesforce.com/services/Soap/u/28.0"

        data = """<?xml version="1.0" encoding="UTF-8"?>
                <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:partner.soap.sforce.com">
                   <soapenv:Header>
                        <urn:CallOptions>
                            <urn:client></urn:client>
                            <urn:defaultNamespace></urn:defaultNamespace>
                        </urn:CallOptions>
                        <urn:LoginScopeHeader>
                            <urn:organizationId></urn:organizationId>
                            <urn:portalId></urn:portalId>
                        </urn:LoginScopeHeader>
                   </soapenv:Header>
                   <soapenv:Body>
                      <urn:login>
                          <urn:username>{{username}}</urn:username>
                          <urn:password>{{password}}</urn:password>
                      </urn:login>
                   </soapenv:Body>
                </soapenv:Envelope>"""
        t = Template(data)
        c = Context({
#            "username": "testmogo@iserviceglobe.net",
#            "password": "venkatesh123ffk0XM9LgYDkBpmRJEJ6PuL7g"
            "username": "admin@sambodhi.com",
            "password": "sfdc*123Lw8jQCSB0ygTot7YagKHoiBJK"
        })
        data = t.render(c)

        logging.info("SENDING:")
        logging.info(data)

        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction' : 'https://login.salesforce.com/services/Soap/u/28.0'
        }
        httplib2.debuglevel = 1 
        
        head = httplib2.Http()
    #    head.follow_all_redirects = True
        response, content = head.request(url, "POST", smart_str(data), headers)
        import ipdb;ipdb.set_trace()
        if response.get('status') == '200':
            xml = XML(content)
            logging.info("response %s"%response)
            logging.info("content %s"%content)
            session_response=xml.find("{http://schemas.xmlsoap.org/soap/envelope/}Body").getchildren()[0]
            session_id = session_response[0][4].text
            quote_id_to_sf(session_id,quote_id)
        else:
            return content

        return "OK"

def quote_id_to_sf(session_id,quote_id):
        url = "https://ap1.salesforce.com/services/Soap/class/QuoteClass1"

        data = """<?xml version="1.0" encoding="UTF-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:quot="http://soap.sforce.com/schemas/class/QuoteClass1">
            <soapenv:Header>
                <quot:SessionHeader>
                     <quot:sessionId>{{session_id}}</quot:sessionId>
                </quot:SessionHeader>
            </soapenv:Header>
           <soapenv:Body>
              <quot:insertQuote>
                 <quot:quoteId>{{quote_id}}</quot:quoteId>
              </quot:insertQuote>
           </soapenv:Body>
        </soapenv:Envelope>"""
        t = Template(data)
        c = Context({
            "session_id": session_id,
            "quote_id": quote_id
        })
        data = t.render(c)

        logging.info("SENDING:")
        logging.info(data)

        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction' : 'https://ap1.salesforce.com/services/Soap/class/QuoteClass1'
        }
        httplib2.debuglevel = 1 
        
        head = httplib2.Http()
    #    head.follow_all_redirects = True
        response, content = head.request(url, "POST", smart_str(data), headers)
        if response.get('status') == 200:
            xml = XML(content)
            quote_response=xml.find("{http://schemas.xmlsoap.org/soap/envelope/}Body").getchildren()[0]
            logging.info("response %s"%response)
            logging.info("content %s"%content)
            return


class QuoteSoapApp(Application):
    def __call__(self, request):
        # wrap the soaplib response into a Django response object
        django_response = HttpResponse()
        def start_response(status, headers):
            status, reason = status.split(' ', 1)
            django_response.status_code = int(status)
            for header, value in headers:
                django_response[header] = value
        response = super(QuoteSoapApp, self).__call__(request.META, start_response)
        django_response.content = '\n'.join(response)
        return django_response

# the view to use in urls.py
my_soap_service = csrf_exempt(QuoteSoapApp([QuoteSOAPService], "http://schema.iserviceglobe.com/sap_sync/"))

