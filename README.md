# 🌳 Directory Tree Generator

A Python script that generates a beautiful tree-like visualization of directory structures, similar to the `tree` command in Unix-like systems.

## ✨ Features

- 📁 Display directory structure in a tree format
- 🔍 Customizable depth levels
- 🎯 Option to show only directories
- 🚫 Hide/show hidden files
- ⛔ Ignore specific patterns
- 🎨 Optional indentation customization

## 📋 Requirements

- Python 3.x
- No additional dependencies required!

## 🚀 Installation

1. Download the `dirtree.py` script
2. Make it executable (optional, for Unix-like systems):
   ```bash
   chmod +x dirtree.py
   ```

## 💻 Usage

Basic usage:
```bash
python dirtree.py [directory]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `directory` | The directory to scan (default: current directory) |

### Options

| Option | Description |
|--------|-------------|
| `-L`, `--level DEPTH` | Descend only DEPTH levels deep |
| `-a`, `--all` | Show all files (including hidden ones) |
| `-d`, `--dir-only` | List directories only |
| `-I`, `--ignore PATTERN` | Ignore files/directories matching PATTERN |
| `--no-indent` | Turn off tree indent characters |

### Examples

1. Display tree for current directory:
   ```bash
   python dirtree.py
   ```

2. Show tree with maximum depth of 2:
   ```bash
   python dirtree.py -L 2
   ```

3. Show only directories:
   ```bash
   python dirtree.py -d
   ```

4. Ignore specific patterns:
   ```bash
   python dirtree.py -I __pycache__ -I .git
   ```

5. Show hidden files:
   ```bash
   python dirtree.py -a
   ```

## 📝 Output Example

```
my_project
├── src
│   ├── main.py
│   └── utils
│       └── helpers.py
├── tests
│   └── test_main.py
└── README.md
```

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📜 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

Inspired by the Unix `tree` command, this Python implementation provides a cross-platform solution for directory visualization. 
