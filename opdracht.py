# Leave comments
# Build-in administrator privileges
# Build-in auto-dependency installations
import os
import sys
import subprocess

## Deze functie werkt niet meer, waarschijnlijk vanwege pip deprecation, reproduction op andere pc geeft zelfde errors.
# Volgende functie installeert de benodigde modules, hoofdscript wordt sowieso uitgevoerd.
# dependencies = ["easygui", "hashlib", "sqlite3"]
# def install(name):
#     subprocess.call(["pip", "install", name])

# for x in dependencies:
#     install(x)

import hashlib
import easygui as eg
import login

# Haalt module "login" aan, opties worden hier definieerd.
running = True
while running:
    account_options = ["Aanmelden", "Inloggen", "Annuleer"] # List met keuzes voor het splash venster.
    choice = login.choicebutton(account_options, "Accountopties") # Heb de EG functie wat versimpeld, alleen keuzelist en titel nodig.
    option = login.options(choice, account_options) # Zelfde als bij de buttons, titel overbodig.
    if option == False:
        break
    else:
        pass
