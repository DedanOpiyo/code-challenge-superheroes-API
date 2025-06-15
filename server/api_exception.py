class APIException(Exception): # Subclass Exception to extend/augment/enrich/customize its behavior
    status_code = 500

    def __init__(self, message, status_code=None, payload=None):
        self.message = message
        self.status_code = status_code or self.status_code
        self.payload = payload or {}

    def to_dict(self):
        response_dict = dict(self.payload) # Copy payload
        response_dict['error'] = self.message # Response_dic to always have this attr       
        return response_dict