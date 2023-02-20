# Dev documentation

External doc for typoImprimerieNationale.py

This script has an internal documentation, but it could be a nice idea to read this documentation before for helping to understand the code.

You must be fluent with the Scribus API and Python.

# Internal code

## General principle

The general principle of this script is:

```mermaid
flowchart TD;
	A{One frametext only}-->|User choice|C[For all the frametexts];
	B{All the document}-->|User choice|C[For all the frametexts];
	C-->D[Extract text];
	D-->E[For all the caracters of the text];
	E-->F[Create previous character, current caracter and nextcharacter];
	F-->G{test and apply typo rule};
	G-->E;
	G-->D;
	G-->H[Final stats]
```
