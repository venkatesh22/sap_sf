from django.conf.urls.defaults import patterns, include, url
import soap
import soap1
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^quote/soap', soap.my_soap_service),
    (r'^update_quote/soap', soap1.my_soap_service),
    # Examples:
    # url(r'^$', 'sap_sf.views.home', name='home'),
    # url(r'^sap_sf/', include('sap_sf.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
