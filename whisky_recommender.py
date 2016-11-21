import sys
import csv
from collections import defaultdict
from statistics import mean, variance

FLAVOR_COLUMNS = [
    'Body',    'Sweetness', 'Smoky',  'Medicinal',
    'Tobacco', 'Honey',     'Spicy',  'Winey', 
    'Nutty',   'Malty',     'Fruity', 'Floral'
]

USAGE_LINE = "Usage: python3 %s [--file whiskies.txt] [--like whisky1] [--like whisky2] ...\n"

NUM_RECOMMENDATIONS = 8

def sign(v):
    if v < 0:
        return -1
    else:
        return  1

def main(*args):

    # This file can be obtained from https://www.mathstat.strath.ac.uk/outreach/nessie/nessie_whisky.html
    whiskyfile  = "whiskies.txt"
    favorites   = set()
    
    # Parse args
    ai = iter(args)
    while True:
        try:
            a = next(ai)
        except StopIteration:
            break
        if a == "--file":
            whiskyfile = next(ai)
        elif a == "--like":
            favorites.add(next(ai))
        else:
            sys.stderr.write("Invalid argument '%s'." % a)
            return 1
    
    # Read file
    try:
        fh = open(whiskyfile, 'r')
    except:
        sys.stderr.write("Could not open '%s' for reading.\n" % whiskyfile)
        sys.stderr.write(USAGE_LINE)
        return 1
    
    rows = csv.DictReader(fh, delimiter=',')
    whiskies = {
        r['Distillery']: {
            k: int(r[k])
            for k in FLAVOR_COLUMNS
        }
        for r in rows
    }
    
    fh.close()
    
    # Check args
    if len(favorites) < 2:
        sys.stderr.write("You need to specify at least two liked whiskies.\n")
        sys.stderr.write(USAGE_LINE)
        return 1
    if len(favorites - set(whiskies)) > 0:
        sys.stderr.write("You selected the following unknown whiskies: ")
        sys.stderr.write(", ".join(favorites - set(whiskies)))
        sys.stderr.write("\n")
        sys.stderr.write("Remove them and try again.\n")
        return 1
    
    # Compute means in each column
    flavor_means = {
        k: mean(w[k] for w in whiskies.values())
        for k in FLAVOR_COLUMNS
    }
    
    # Compute flavor profiles for each whisky
    profiles = {
        wk: {
            k: sign(v - flavor_means[k])
            for k, v in wv.items()
        }
        for wk, wv in whiskies.items()
    }
    
    # Compute flavor profile for user
    user_votes = {
        k: [profiles[w][k] for w in favorites]
        for k in FLAVOR_COLUMNS
    }
    user_means = {
        k: mean(v) / (variance(v) + 1)
        for k, v in user_votes.items()
    }
    
    # Display flavor profile
    sys.stdout.write("We have detected your flavor preferences as:\n")
    for k, v in sorted(user_means.items(), key=lambda x: -x[1]):
        sys.stdout.write("- %s (weight %.2f)\n" % (k, v))
    sys.stdout.write("\n")
    
    # Compute rating for each whisky
    ratings = {
        w: sum(
            profiles[w][k] * user_means[k] 
            for k in FLAVOR_COLUMNS
        )
        for w in set(whiskies) - favorites
    }
    
    # Display best matches
    sys.stdout.write("Our recommendations: \n")
    for k, v in sorted(ratings.items(), key=lambda x: -x[1])[0:NUM_RECOMMENDATIONS]:
        sys.stdout.write("- %s (weight %.2f)\n" % (k, v))
    
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
