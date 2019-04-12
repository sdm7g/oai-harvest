from oaipmh.client import *
import logging
from lxml import etree
print( __file__ )
etree.use_global_python_log(etree.PyErrorLog())

class RecoveringClient(Client):
# oaipmh Client with option to recover from bad XML in metadata payload
    logger = logging.getLogger( 'oaiharvest.harvest' ).getChild( 'client' )
    def parse(self, xml):
        """Parse the XML to a lxml tree WITH parser option: recover=True.
        """
        # XXX this is only safe for UTF-8 encoded content,
        # and we're basically hacking around non-wellformedness anyway,
        # but oh well

        if self._ignore_bad_character_hack:
            xml = six.text_type(xml, 'UTF-8', 'replace')
            # also get rid of character code 12
            xml = xml.replace(chr(12), '?')
            xml = xml.encode('UTF-8')
        if six.PY3:
            if hasattr(xml, "encode"):
                xml = xml.encode("utf-8")
            # xml = xml.encode("utf-8")
        try:  
            return etree.XML( xml )
        except etree.XMLSyntaxError as perror:
            self.logger.error(perror)
            try:
                tree = etree.XML(xml, etree.XMLParser(recover=True)) # sdm7g: attempt to RECOVER
                id = tree.xpath( '/oai:OAI-PMH/oai:ListRecords/oai:record/oai:header/oai:identifier', namespaces=self.getNamespaces() )
                self.logger.warning( "Recoverable parse error on: {0}".format(id[0].text) )
            except Exception as perror2:
                self.logger.error(perror2)
            return tree


