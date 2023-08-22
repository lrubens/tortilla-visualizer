# tortilla-visualizer

## Installation
- Install [protobuf compiler](https://grpc.io/docs/protoc-installation/)
- `git submodule update --init` 
- `pip install -r requirements.txt`

## Getting Started
- Use a web preview extension in your code editor, I recommend vscode-preview-server in VS Code.
- Run `python app.py` to spin up flask server for processing text proto entered in web editor

## Flask App Structure.
| |────css/
| | |────style.css
| |────examples/
| |────templates/
| | |────index.html
| |────tortilla (submodule)
|────Makefile
|────app.py
