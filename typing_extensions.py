"""
typing_extensions compatibility shim for Python 3.9 / Pydantic v2
"""
import sys
import typing
from typing import *

# Re-export all of typing
__all__ = [s for s in dir(typing) if not s.startswith("_")]

class _SpecialForm:
    def __init__(self, name="SpecialForm"):
        self.name = name
    def __getitem__(self, item):
        return item
    def __repr__(self):
        return f"typing_extensions.{self.name}"
    def __call__(self, *args, **kwargs):
        return object

class Sentinel:
    def __init__(self, name="Sentinel", repr_string=None):
        self.name = name
        self.repr_string = repr_string or f"<{name}>"
    def __repr__(self):
        return self.repr_string

Required = _SpecialForm("Required")
NotRequired = _SpecialForm("NotRequired")
ReadOnly = _SpecialForm("ReadOnly")
TypeAlias = getattr(typing, "TypeAlias", object)
TypeGuard = _SpecialForm("TypeGuard")
TypeIs = _SpecialForm("TypeIs")
Self = getattr(typing, "Self", object)
Never = getattr(typing, "Never", object)
Unpack = _SpecialForm("Unpack")
TypeVarTuple = getattr(typing, "TypeVarTuple", object)
Doc = _SpecialForm("Doc")
Buffer = getattr(typing, "Buffer", object)
LiteralString = str
Any = typing.Any
Concatenate = _SpecialForm("Concatenate")

class ParamSpecArgs:
    def __init__(self, origin):
        self.__origin__ = origin
    def __repr__(self):
        return f"{self.__origin__.__name__}.args"

class ParamSpecKwargs:
    def __init__(self, origin):
        self.__origin__ = origin
    def __repr__(self):
        return f"{self.__origin__.__name__}.kwargs"

class ParamSpec:
    def __init__(self, name, *, bound=None, covariant=False, contravariant=False, default=None):
        self.__name__ = name
        self.__bound__ = bound
        self.__covariant__ = covariant
        self.__contravariant__ = contravariant
        self.args = ParamSpecArgs(self)
        self.kwargs = ParamSpecKwargs(self)
    def __repr__(self):
        return self.__name__

class TypeAliasType:
    def __init__(self, name, value, type_params=()):
        self.__name__ = name
        self.__value__ = value
        self.__type_params__ = type_params
    def __repr__(self):
        return self.__name__

_OrigTypeVar = typing.TypeVar

def TypeVar(name, *constraints, bound=None, covariant=False, contravariant=False, default=None, **kwargs):
    return _OrigTypeVar(name, *constraints, bound=bound, covariant=covariant, contravariant=contravariant)

def assert_never(arg: Any) -> Never:
    raise AssertionError(f"Expected code to be unreachable, but got: {arg}")

def assert_type(val: Any, typ: Any) -> Any:
    return val

def dataclass_transform(*args, **kwargs):
    def decorator(cls):
        return cls
    return decorator

def get_original_bases(cls):
    return getattr(cls, "__orig_bases__", getattr(cls, "__bases__", ()))

def is_protocol(tp):
    return getattr(tp, "_is_protocol", False) or getattr(tp, "__is_protocol__", False)

try:
    from typing import Literal, Annotated, final, Final, Protocol, runtime_checkable
except ImportError:
    pass

class _TypedDictMeta(type):
    def __new__(cls, name, bases, ns, total=True, closed=False, **kwargs):
        return super().__new__(cls, name, (dict,), ns)

    def __call__(cls, *args, **kwargs):
        return dict(*args, **kwargs)

class TypedDict(dict, metaclass=_TypedDictMeta):
    pass

def override(func):
    return func

def deprecated(*args, **kwargs):
    def decorator(func):
        return func
    return decorator

def is_typeddict(tp):
    return isinstance(tp, type) and issubclass(tp, dict) and hasattr(tp, "__annotations__")

def get_args(tp):
    return getattr(tp, "__args__", ())

def get_origin(tp):
    return getattr(tp, "__origin__", None)

def get_type_hints(obj, globalns=None, localns=None, include_extras=False):
    return typing.get_type_hints(obj, globalns=globalns, localns=localns)
