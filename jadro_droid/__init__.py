import collections

Result = collections.namedtuple('Result', 'id,result,error')

class DummyDroid(object):
    def __getattr__(self, name):
        def rpc_call(*args):
            return Result(id=0, result=None, error='no droid')
        return rpc_call
