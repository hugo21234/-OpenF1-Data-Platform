import requests

class RequestFactory:
    def __init__(self, endpoints: dict) -> None:
        self.base_url = 'https://api.openf1.org/v1'

        self.timeout = (3.05, 30)

        self.session = requests.Session()

        self.params = {"session_key": 9161}
        self.ENDPOINTS = endpoints

    def get_data(self, session_key:dict, endpoint:str) -> list[dict]:

        r = self.session.get(self.base_url + endpoint, params=session_key, timeout=self.timeout)

        print(r.status_code)
        print(r.text)

        r.raise_for_status()

        response_data = r.json()
        
        return response_data
    



