# jsonparser

An implementation of `json.loads` to parse a string into json.

## Overview

The `Scanner` takes in the source string and returns a list of tokens. A token is an substring of characters that make up the syntax of an language. For json, we have the following token types.

```txt
LEFT_PARENTHESIS
RIGHT_PARENTHESIS
LEFT_BRACKET
RIGHT_BRACKET
COLON
COMMA
STRING
NUMBER
BOOLEAN
```

Pretty simple. The next step after scanning is to parse the list of tokens into an abstract syntax tree. The AST consists of nodes organized in a tree like structure that represents the json.

The leaf nodes are the `JSONString`, `JSONNumber`, and `JSONBoolean`.

Each node has an `eval` method that converts the node to its equivalent python json object. `JSONString` will eval to a `str` type. `JSONNumber` will evaluate to a `int` or `float` type. `JSONBoolean` will evaluate to a `bool` type.

`JSONDict` and `JSONList` will recursively evaluate its key value pairs and children and return a `dict` and `list` respectively.
