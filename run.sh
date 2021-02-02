#!/bin/bash

# * The line at the head of the script tells the shell that it is a shell
# * script and it contains commands in it and you need to execute it
# ? #!/bin/sh
# * Executes the script using the Bourne shell or a compatible shell, with path /bin/sh
# ? #!/bin/bash
# * Executes the script using the Bash shell.
# ? #!/bin/csh -f
# * Executes the script using C shell or a compatible shell.
# ? #!/usr/bin/perl -T
# * Executes the script using perl with the option of taint checks
# ? #!/usr/bin/env python
# * Executes the script using python by looking up the path to the python interpreter automatically
# * from the environment variables

# * Shell is an interface using which the programmer can execute command
# * and interact directly to the operating system. Shell scripting is
# * giving commands that a shell can execute.

# ? here the program start its execution
# ? `$1` is the first argument of the function
# ? `runProgram` and its value is the python
# ? interpreter i.e., python[2/3]
function runProgram() { $1 src/main.py; }

# ! function to confirm the user decision of Installing
# ! python if it is not installed
function confirm() {
    read -p "Install Python [y/n]: " ch
    echo $ch
}

# ! function that finds the system platform Information
function getSystemInfo() {
    case "$(/usr/bin/lsb_release -si)" in
    Ubuntu) echo "Ubuntu" ;;
    Mint) echo "Mint" ;;
    arch) echo "Arch" ;;
    *) echo "Can not get the System Information! Download Python manually" ;;
    esac
}

# ! function that install python on Ubuntu platform
function installOnUbuntu() {
    echo "Installing Python on Ubuntu Linux"
    sudo apt-get update
    sudo apt-get install python3.8 python3-pip
}

# ! function that install python on Linux Mint platform
function installOnMint() {
    echo "Installing Python on Linux Mint"
    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt-get update
    sudo apt-get install python3.8 python3-pip
}

# ! function that install python on Arch Linux platform
function installOnArch() {
    echo "Installing Python on Arch Linux"
    packman -S python
}

# ? function that does the actual installation of the python interpreter
# ? based on the current running platform
function install() {
    platform=$(getSystemInfo)

    case "$platform" in
    Ubuntu) installOnUbuntu ;;
    Mint) installOnMint ;;
    Arch) installOnArch ;;
    *) exit ;;
    esac
}

# ? function that install python if it is not already installed
# ? in the user system
function installPython() {
    # ! get confirmation
    ch=$(confirm)

    if [ "$ch" = "y" ]; then
        echo "Installing python for $(uname -s)"
        install
    else
        echo "Piece"
    fi
}

# ! check if python3 is present
if python3 --version | grep "Python*" >/dev/null; then
    echo "Python is installed"
    runProgram python3
# ! check if python2 is present
elif python2 --version | grep "Python*" >/dev/null; then
    echo "Python is installed"
    runProgram python2
# ! check if python is present
elif python --version | grep "Python*" >/dev/null; then
    echo "Python is installed"
    runProgram python
# ! install python if python is not present
else
    echo "Python is not installed"
    installPython
fi