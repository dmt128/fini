from .. util import screen
from .earnings_per_share import earnings_per_share
from .price_to_earnings import price_to_earnings

TERMDEF = {
    'eps': earnings_per_share,
    'pe': price_to_earnings
}

def info(term):
    print(screen.Fore.GREEN + TERMDEF.get(term.lower(), "Unknown term: '{}'\n".format(term.lower())) + screen.Style.RESET_ALL)

def available_terms():
    print(screen.Fore.GREEN + "Available terms:")
    for term in TERMDEF.keys():
        print("\t* {}".format(term.upper()))
    print(screen.Style.RESET_ALL)