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
        page=1
        if self.params.has_key( "id" ):
            set_id=self.params[ "id" ]
        if self.params.has_key( "username" ):
            username=self.params[ "username" ]
        if self.params.has_key( "page" ):
            page=self.params[ "page" ]
        if set_id and username and page:
            pixnet=Pixnet()
            data = pixnet.get_album_elements(
                    key=None,
                    parameters={
                        'set_id': set_id,
                        'user': username,
                        'page': page
                    }
                    )
        self.render(json=self.to_json(data))

    def index(self):
        pass
