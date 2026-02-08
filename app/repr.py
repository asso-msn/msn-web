import functools


def repr(*keys):
    def decorator(cls):
        @functools.wraps(cls.__repr__)
        def __repr__(self):
            attrs = ", ".join(f"{key}={getattr(self, key)!r}" for key in keys)
            return f"{self.__class__.__name__}({attrs})"

        cls.__repr__ = __repr__
        return cls

    return decorator
