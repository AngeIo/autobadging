

<p align="center">
  <img width="250" alt="autobadging logo" src="assets/logo.png">
</p>

# autobadging

User interface to help with badging on *Horoquartz - eTemptation* at C+T

This is a easy-to-use user interface to simply badge on Horoquartz from your Windows desktop, without ever having to open the website! It could be added to your Windows startup process so it opens automatically when you log in on your PC and you don't even have to think about it!

## Features / To-do list
- [x] Easy badging without ever needing to open a browser by yourself
- [x] Creates the shortcuts on your Windows desktop and taskbar
- [x] If allowed, adds itself to Windows startup process to badge as soon as you log in to your computer
- [ ] Improve first time setup with password generation etc.
- [ ] Support for Linux (only tested on Windows)
- [ ] Clean the requirements.txt file to contain only the packages needed by the project

## Screenshot

<img src="assets/screenshot.png">

## Installation

Please make sure you have the following prerequisites:

- [Git](https://git-scm.com/downloads)
- [Python 3](https://www.python.org/downloads/)
- [Microsoft Visual C++](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

### Downloading the source code

Clone the repository:

```shell
git clone https://github.com/AngeIo/autobadging
```

To update the source code to the latest commit, run the following command inside the `autobadging` directory:

```shell
git pull
```

## Usage

Download all the required packages for the script to work:
```shell
pip install -r requirements.txt
```

Rename `variables.py.template` to `variables.py` and modify it to match with your environment (see below for password variable).

Generate your encrypted password using the dedicated script included with this project and copy-paste the result in `variables.py` file:
```shell
python pwgen.py "MyStrongPassword"
```

Then, launch the compiler:
```
python utils/make.py
```

To run the script, click on the `autob` shortcut in your taskbar or on your desktop!

## License
The source code for "autobadging" is using a *???* license (we haven't decided yet).

## Authors
* 0x546F6D (creator of pttb)
* A lot of open source contributors
* GERARD Angelo

