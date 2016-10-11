# RSL

A wrapper in Sublime Text for [rsltc][3], the type checker of RAISE Specification Language - [RSL][0].

# Prerequisites
You should have following software installed and running

- [rsltc][3]

# Install

The package can be installed using one of the following methods:

## Via [Package Control](https://packagecontrol.io) (recommended)

`Package Control: Install Package > RSL`

## Manual

1. `Sublime Menu > Preferences > Browse Packages ...`
2. `git clone https://github.com/li-vu/st-rsl RSL`

# Features

The following commands are available:
- `Type Check`
- `Pretty Print`
- `Translate SML`
- `Run SML`
- `Translate to SAL`
- `Run SAL Wellformed Checker`
- `Run SAL Deadlock Checker`
- `Run SAL Symbolic Model Checker`
- `Translate to SML and Run`: [Chain of Command](https://github.com/jisaacks/ChainOfCommand) is required to run this command.
- `Join Comments`: Experimental feature allows joining consecutive line comments into a block comment.

# License
Copyright (C) 2016 [li-vu](https://github.com/li-vu)

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation. <http://www.gnu.org/licenses/gpl.html>

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

 [0]: http://en.wikipedia.org/wiki/RAISE 
 [1]: https://github.com/li-vu/st-rsl
 [2]: https://packagecontrol.io/
 [3]: https://github.com/dtu-railway-verification/rsltc
