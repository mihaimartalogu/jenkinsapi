import urllib2
import logging
import pprint
import config
from utils.retry import retry_function

log = logging.getLogger( __name__ )

class jenkinsobject( object ):
    """
    This appears to be the base object that all other jenkins objects are inherited from
    """
    RETRY_ATTEMPTS = 5

    def __repr__( self ):
        return """<%s.%s %s>""" % ( self.__class__.__module__,
                                    self.__class__.__name__,
                                    str( self ) )

    def print_data(self):
        pprint.pprint( self._data )

    def __str__(self):
        raise NotImplemented

    def __init__( self, baseurl, poll=True ):
        """
        Initialize a jenkins connection
        """
        self.baseurl = baseurl
        if poll:
            try:
                self.poll()
            except urllib2.HTTPError, hte:
                log.exception(hte)
                log.warn( "Failed to conenct to %s" % baseurl )
                raise

    def poll(self):
        self._data = self._poll()

    def _poll(self):
        url = self.python_api_url( self.baseurl )
        return retry_function( self.RETRY_ATTEMPTS , self.get_data, url )

    @classmethod
    def python_api_url( cls, url  ):
        if url.endswith( config.JENKINS_API ):
            return url
        else:
            if url.endswith( r"/" ):
                fmt="%s%s"
            else:
                fmt = "%s/%s"
            return fmt % (url, config.JENKINS_API)

    def get_data( self, url ):
        """
        Find out how to connect, and then grab the data.
        """
        fn_urlopen = self.getHudsonObject().get_opener()
        try:
            stream = fn_urlopen( url )
            result = eval( stream.read() )
        except urllib2.HTTPError, e:
            log.warn( "Error reading %s" % url )
            raise
        return result