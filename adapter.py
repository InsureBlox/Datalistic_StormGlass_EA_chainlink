import requests
from bridge import Bridge
from dotenv import dotenv_values


class Adapter:
    base_url_datalistic = 'https://api.datalastic.com/api/v0/vessel'
    from_params = ['uuid']
    to_params = ['lat', 'lon']
    datalistic_api_key = dotenv_values(".env")["DATALISTIC_API_KEY"]
    stormglass_api_key = dotenv_values(".env")["STORMGLASS_API_KEY"]

    def __init__(self, input):
        self.id = input.get('id', '1')
        self.request_data = input.get('data')
        self.request_data["api-key"] = self.datalistic_api_key
        if self.validate_request_data():
            self.bridge = Bridge()
            self.set_params()
            self.create_request()
        else:
            self.result_error('No data provided')

    def validate_request_data(self):
        if self.request_data is None:
            return False
        if self.request_data == {}:
            return False
        return True

    def set_params(self):
        for param in self.from_params:
            self.from_param = self.request_data.get(param)
            if self.from_param is not None:
                break
        for param in self.to_params:
            self.to_param = self.request_data.get(param)
            if self.to_param is not None:
                break

    def create_request(self):
        try:
            params = {
                self.from_param,
            }
            #response = requests.get(self.base_url, params = self.request_data)
            #data = response.json().get("data")
            response = self.bridge.request(self.base_url_datalistic, self.request_data)
            data = response.json().get('data')
            self.result = {k: data[k] for k in data.keys() if k in ['lat', 'lon']}
            data['result'] = self.result
            self.result = self.get_dust(data)
            self.result_success(data)
        except Exception as e:
            self.result_error(e)
        finally:
            self.bridge.close()
    
    def get_dust(self, data):
        params = {'params': 'gust', 'lat': data['result']['lat'],'lng':data['result']['lon'],'start':data['last_position_epoch']}
        res = requests.get('https://api.stormglass.io/v2/weather/point', params= params, headers={'Authorization' : self.stormglass_api_key})
        return(res.json()['hours'][0]['gust']['noaa'])




    def result_success(self, data):
        self.result = {
            'jobRunID': self.id,
            'data': data,
            'result': self.result,
            'statusCode': 200,
        }

    def result_error(self, error):
        self.result = {
            'jobRunID': self.id,
            'status': 'errored',
            'error': f'There was an error: {error}',
            'statusCode': 500,
        }
