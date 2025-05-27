# Directory Tree Generator for VS Code

A VS Code extension that generates a directory tree structure for the selected folder.

## Features

- Right-click on any folder in the Explorer and select "Generate Directory Tree"
- Choose to include or exclude hidden files
- Option to show only directories or both files and directories
- Set maximum depth for the tree
- Output is opened in a new text document

## Usage

1. In VS Code's Explorer, right-click on a folder
2. Select "Generate Directory Tree" from the context menu
3. Choose your options:
   - Show/hide hidden files
   - Include files or folders only
   - Set maximum depth (0 for unlimited)
4. The directory tree will be generated and opened in a new editor tab

## Example Output

```
my-project
├── .gitignore
├── README.md
├── package.json
├── src
│   ├── extension.ts
│   └── test
│       └── runTest.ts
└── tsconfig.json

3 directories, 5 files
```

## Requirements

- VS Code 1.80.0 or higher

## Extension Settings

This extension contributes the following settings:

* `dirTreeGen.defaultShowHidden`: Default value for showing hidden files
* `dirTreeGen.defaultDirsOnly`: Default value for showing directories only
* `dirTreeGen.defaultDepthLimit`: Default depth limit (0 for unlimited)

## Known Issues

- Very large directory trees might take a moment to generate

## Release Notes

### 1.0.0

Initial release of Directory Tree Generator

---

**Enjoy!**
