from voluptuous import Schema
from voluptuous import Any
from voluptuous import All
from voluptuous import Required
from voluptuous import Length

def_sch = Schema({Required("events"): All(list, Length(min=1))})
#All(list, Length(min=1))
#def_sch({'test':true})
#def_sch({'events':[]})
def_sch({'events':[{'martin':'david'}]})
