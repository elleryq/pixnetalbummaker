from gaeo.controller import BaseController
from pixnetlib import Pixnet

class PixnetController(BaseController):
    """The Pixnet Controller
    """
    def albums(self):
        data={}
        username=None
        page=1
        if self.params.has_key( "username" ):
            username=self.params[ "username" ]
        if self.params.has_key( "page" ):
            page=self.params[ "page" ]
        if username and page:
            pixnet=Pixnet()
            data = pixnet.get_album_sets( 
                    key=None,
                    parameters={
                        'user': username,
                        'page': page 
                      }
                    )
        self.render(json=self.to_json(data))

    def photos(self):
        data={}
        set_id=None
        username=None
        if self.params.has_key( "id" ):
            set_id=self.params[ "id" ]
        if self.params.has_key( "username" ):
            username=self.params[ "username" ]
        if set_id and username:
            pixnet=Pixnet()
            result = pixnet.get_album_elements(
                    key=None,
                    parameters={
                        'set_id': set_id,
                        'user': username
                    }
                    )
            if result['error']==0 and result.has_key("elements"):
                data = result['elements']
        self.render(json=self.to_json(data))

    def albums_old(self):
        """The default method
        related to templates/pixnet/albums.html
        """
        if self.params.has_key( "username" ):
            self.username=self.params[ "username" ]
            pixnet=Pixnet()
#print( pixnet.get_users_elleryq() )
            result = pixnet.get_album_sets( 
                    parameters={'user': self.username }
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
