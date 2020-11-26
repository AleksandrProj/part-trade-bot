from binance.client import Client
import time


class BinanceUser(Client):
    def _request(self, method, uri, signed, force_params=False, **kwargs):
        # set default requests timeout
        kwargs['timeout'] = 10

        # add our global requests params
        if self._requests_params:
            kwargs.update(self._requests_params)

        data = kwargs.get('data', None)
        if data and isinstance(data, dict):
            kwargs['data'] = data

            # find any requests params passed and apply them
            if 'requests_params' in kwargs['data']:
                # merge requests params into kwargs
                kwargs.update(kwargs['data']['requests_params'])
                del (kwargs['data']['requests_params'])

        if signed:
            local_time = int(time.time())
            server_time = int(self.get_server_time()['serverTime']) // 1000
            shift_seconds = server_time - local_time

            # generate signature
            kwargs['data']['timestamp'] = int(local_time + shift_seconds - 1) * 1000
            kwargs['data']['signature'] = self._generate_signature(kwargs['data'])

        # sort get and post params to match signature order
        if data:
            # sort post params
            kwargs['data'] = self._order_params(kwargs['data'])
            # Remove any arguments with values of None.
            null_args = [i for i, (key, value) in enumerate(kwargs['data']) if value is None]
            for i in reversed(null_args):
                del kwargs['data'][i]

        # if get request assign data array to params value for requests lib
        if data and (method == 'get' or force_params):
            kwargs['params'] = '&'.join('%s=%s' % (data[0], data[1]) for data in kwargs['data'])
            del (kwargs['data'])

        self.response = getattr(self.session, method)(uri, **kwargs)
        return self._handle_response()