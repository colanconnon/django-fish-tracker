from django.core.exceptions import PermissionDenied


def does_user_have_permissions(user, permission):
    if user.has_perm(permission):
        return True
    return False


def parse_user_from_args(*args):
    return args[1].context.user


def requires_permission(permission):
    def _method_wrapper(f):
        def _arguments_wrapper(*args, **kwargs):
            user = parse_user_from_args(*args)
            if user is None:
                raise PermissionDenied("Not authenticated")
            if does_user_have_permissions(user, permission):
                return f(*args, **kwargs)
            raise PermissionDenied("You don't have permission to access this")
        return _arguments_wrapper
    return _method_wrapper