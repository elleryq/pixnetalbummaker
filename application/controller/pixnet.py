from gaeo.controller import BaseController
from pixnetlib import Pixnet

class PixnetController(BaseController):
    """The Pixnet Controller
    """
    def albums(self):
        if self.params.has_key( "username" ):
            self.username=self.params[ "username" ]
            pixnet=Pixnet()
#print( pixnet.get_users_elleryq() )
            result = pixnet.get_album_sets( 
                    {'user': self.username }
                    )
            if result['error']==0:
                self.render(json=self.to_json(result['sets']))
                return
        self.render(json=self.to_json({}))

    def albums_old(self):
        """The default method
        related to templates/pixnet/albums.html
        """
        if self.params.has_key( "username" ):
            self.username=self.params[ "username" ]
            pixnet=Pixnet()
#print( pixnet.get_users_elleryq() )
            result = pixnet.get_album_sets( 
                    {'user': self.username }
                    )
            if result['error']==0:
                self.album_sets = result["sets"]
                self.rawdata = repr( self.album_sets )
            else:
                self.rawdata = "Error happened."
        else:
            self.username="Anonymouse"
            self.username=",".join( self.params.keys() )

    def index(self):
        pass
