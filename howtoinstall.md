# How to install VibeCodeLang

VibeCodeLang runs with Python 3.10 or newer.

## 1. Install Python

Check if Python is already installed:

```bash
python --version
```

If that command does not work, try:

```bash
python3 --version
```

If Python is not installed, download it from https://www.python.org/downloads/.

## 2. Clone the repository

Install Git if you do not have it, then clone this repository:

```bash
git clone https://github.com/GussApenass/vibecodelang
cd vibecodelang
```

## 3. Install the language locally

Install the project in editable mode:

```bash
python -m pip install -e .
```

If your computer uses `python3`, run:

```bash
python3 -m pip install -e .
```

## 4. Run a VibeCodeLang file

Run one of the examples:

```bash
vibecoded examples/basics.vb
```

You can also run the local launcher directly:

```bash
./vibecoded examples/basics.vb
```

## 5. Create your own file

Create a file ending in `.vb`, for example `hello.vb`:

```vb
var name: string > "world"
out("Hello @{name}")
```

Then run it:

```bash
vibecoded hello.vb
```

## Troubleshooting

If `vibecoded` is not found, install the project again with:

```bash
python -m pip install -e .
```

Or run the local launcher with:

```bash
./vibecoded examples/basics.vb
```

