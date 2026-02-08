from functools import wraps


def repr(*keys):
    @wraps
    def decorator(cls):
        def __repr__(self):
            attrs = ", ".join(f"{key}={getattr(self, key)!r}" for key in keys)
            return f"{self.__class__.__name__}({attrs})"

        cls.__repr__ = __repr__
        return cls

    return decorator
