import model 

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, model.Main):
            return obj.clean().serialyze()
        return json.JSONEncoder.default(self, obj)


def _json_load(dct):
    if '__type__' in dct:
        o = getattr(model, dct['__type__'])
        del dct['__type__']
        return o.fromDict(dct)
    return dct

json_decode = lambda o: json.loads(o, object_hook=_json_load)
json_encode = lambda o: json.dumps(o, cls=ComplexEncoder)
