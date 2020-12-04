from . fini import FiniApp

def version():
    from . version import __str_version__
    print(__str_version__)


def __import_modules__(path):
    import os, importlib.util

    modules = [os.path.splitext(f)[0] for f in [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))] ]
    __modules__ = []
    for idx, module in enumerate(modules):
        path_to_module = os.path.join(path, module + ".py")
        spec = importlib.util.spec_from_file_location(module, path_to_module)
        __modules__.append(importlib.util.module_from_spec(spec))
        spec.loader.exec_module(__modules__[idx]) 
    
    return __modules__

def get_providers(path_to_external_providers=None):
    import os, sys, inspect, fini
    
    # First fetch providers in fini package
    providers = inspect.getmembers(sys.modules['fini.providers'], inspect.isclass)

    # Now extend with providers in user supplied path
    if path_to_external_providers:
        modules = __import_modules__(path_to_external_providers)
        for module in modules:
            providers.append(inspect.getmembers(module, inspect.isclass)[0])

    # Go through the list of classes and remove any that are not subclasses of ProviderBase
    __providers__ = {}
    for provider in providers:
        if issubclass(provider[1], fini.managers.provider.ProviderBase):
            # __providers__.append((provider[1].provider_id(), provider[0], provider[1]))
            __providers__[provider[1].provider_id()] = provider

    return __providers__
