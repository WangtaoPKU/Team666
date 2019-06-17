from crawler import *;
from download import *;

parser = argparse.ArgumentParser(prog="download", conflict_handler = "resolve");
parser.add_argument("--key", "-k", type = str, required = True, help = "key word of the music to search");
args = parser.parse_args();

list_link = search(args.key);
print(list_link);
for link in list_link:
	download(link);
