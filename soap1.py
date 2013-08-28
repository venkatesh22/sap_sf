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


class NewQuoteSOAPService(DefinitionBase):
    @rpc(String,String,String,String,String,String,String,String,String,String,String,String, _returns=String)
    def updatequotewithparameters(self, quote_id,ExternalReference,Grossvalue,netvalue,postingDate,RefDate,SoldToParty,SoldToPartyAdd,Status,TaxAmt,ValidFrm,ValidTo):
        logging.info("SAP is sending quote with more parameters")
        logging.info(locals())
        logging.info("CONNECTING TO SALESFORCE PARTNER WSDL FOR SESSION ID")
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
#        httplib2.debuglevel = 1 
        
        head = httplib2.Http()
    #    head.follow_all_redirects = True
        response, content = head.request(url, "POST", smart_str(data), headers)
        logging.info("########### SESSION ID response ###############%s"%response)
        logging.info("########## SESSION ID content ############## \n %s"%pretty(content))
        if response.get('status') == '200':
            logging.info("GOT THE SESSION ID FROM SALESFORCE")
            xml = XML(content)
            session_response=xml.find("{http://schemas.xmlsoap.org/soap/envelope/}Body").getchildren()[0]
            session_id = session_response[0][4].text
            quote_id_to_sf(session_id,quote_id,ExternalReference,Grossvalue,netvalue,postingDate,RefDate,SoldToParty,SoldToPartyAdd,Status,TaxAmt,ValidFrm,ValidTo)
        else:
            return content

        return "OK"

def quote_id_to_sf(session_id,quote_id,ExternalReference,Grossvalue,netvalue,postingDate,RefDate,SoldToParty,SoldToPartyAdd,Status,TaxAmt,ValidFrm,ValidTo):
        logging.info("############## CONNECTING TO SALESFORCE QUOTE WSDL ##############")
        url = "https://ap1.salesforce.com/services/Soap/class/QuoteClass"

        data = """<?xml version="1.0" encoding="UTF-8"?>
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:quot="http://soap.sforce.com/schemas/class/QuoteClass">
                <soapenv:Header>
                    <quot:SessionHeader>
                        <quot:sessionId>{{session_id}}</quot:sessionId>
                    </quot:SessionHeader>
                </soapenv:Header>
                <soapenv:Body>
                    <quot:insertQuote>
                        <quot:quoteId>{{quote_id}}</quot:quoteId>
                        <quot:ExternalReference>{{external}}</quot:ExternalReference>
                        <quot:Grossvalue>{{gross}}</quot:Grossvalue>
                        <quot:netvalue>{{netvalue}}</quot:netvalue>
                        <quot:SoldToParty>{{SoldToParty}}</quot:SoldToParty>
                        <quot:Status>{{Status}}</quot:Status>
                        <quot:TaxAmt>{{TaxAmt}}</quot:TaxAmt>
                        <quot:ValidFrm>{{ValidFrm}}</quot:ValidFrm>
                        <quot:ValidTo>{{ValidTo}}</quot:ValidTo>
                    </quot:insertQuote>
                </soapenv:Body>
            </soapenv:Envelope>"""
        t = Template(data)
        c = Context({
            "session_id": session_id,
            "quote_id": quote_id,
            "external": ExternalReference,
            "gross": Grossvalue,
            "netvalue": netvalue,
            "postingDate" : postingDate,
            "RefDate" : RefDate,
            "SoldToParty" : SoldToParty,
            "SoldToPartyAdd" : SoldToPartyAdd,
            "Status" : Status,
            "TaxAmt" : TaxAmt,
            "ValidFrm" : ValidFrm,
            "ValidTo" : ValidTo
        })
        data = t.render(c)

        logging.info("SENDING:")
        logging.info(data)

        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction' : 'https://ap1.salesforce.com/services/Soap/class/QuoteClass'
        }
#        httplib2.debuglevel = 1 

        head = httplib2.Http()
    #    head.follow_all_redirects = True
        response, content = head.request(url, "POST", smart_str(data), headers)
        logging.info("######################### QUOTE response ############## %s"%response)
        logging.info("###################### QUOTE content ################# \n%s"%pretty(content))
        if response.get('status') == "200":
            xml = XML(content)
            quote_response=xml.find("{http://schemas.xmlsoap.org/soap/envelope/}Body").getchildren()[0]
            return

def pretty(xml):
    from lxml import etree
    root = etree.fromstring(xml)
    return etree.tostring(root, pretty_print=True)


class NewQuoteSoapApp(Application):
    def __call__(self, request):
        # wrap the soaplib response into a Django response object
        django_response = HttpResponse()
        def start_response(status, headers):
            status, reason = status.split(' ', 1)
            django_response.status_code = int(status)
            for header, value in headers:
                django_response[header] = value
        response = super(NewQuoteSoapApp, self).__call__(request.META, start_response)
        django_response.content = '\n'.join(response)
        return django_response

# the view to use in urls.py
my_soap_service = csrf_exempt(NewQuoteSoapApp([NewQuoteSOAPService], "http://schema.iserviceglobe.com/sap_sync/"))

