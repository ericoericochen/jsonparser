import argparse

from pprint import pprint

from .parser import Scanner, build_ast


argparser = argparse.ArgumentParser()
argparser.add_argument("--json", type=str, required=True)
args = argparser.parse_args()

# parse json string into json
json_path = args.json
with open(json_path, "r") as f:
    json_str = f.read()

scanner = Scanner(json_str)
tokens = scanner.scan_tokens()


print("tokens: ")
pprint(tokens)
print("=" * 100)

ast = build_ast(tokens)

print("ast: ")
pprint(ast)
print("=" * 100)


parsed_json = ast.eval()

print("parsed: ")
print(parsed_json)
