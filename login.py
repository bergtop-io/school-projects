import easygui as eg
import os
import hashlib
import sqlite3 as sql

# Functie die een keuzemenu aanroept bestaande uit de ingevoerde parameters, returns invoer.
def choicemenu(choices_list):
    choice_msg = "Wat wil je doen?"
    choice_title = "Keuzemenu"
    choice_fields = choices_list
    choice_value = eg.choicebox(choice_msg, choice_title, choice_fields)
    if choice_value == None:
        return False
    else:
        return choice_value

# Functie die de ingevoerde parameters presenteert als knoppen, returns invoer.
def choicebutton(choices_list, title):
    choice_msg = "Wat wil je doen?"
    choice_title = title
    choice_buttons = choices_list
    choice_value = eg.buttonbox(choice_msg, choice_title, choice_buttons, None, None, choice_buttons[0],)
    if choice_value == None:
        return False
    else:
        return choice_value

# Deze functie codeert of decodeert een wachtwoord op basis van de parameters en returns output.
def gen_pass(password):
    pw_salted = str(password) + "kaasisdebaas" # Yup, kaasisdebaas is de salt
    h = hashlib.md5(pw_salted.encode())
    return str(h.hexdigest())

## De volgende functies hebben betrekking op de database
# Deze functie maakt een connectie aan met een sqldatabase en voegt de invoer toe.
def dbinsert(account):
    conn = sql.connect("sqldb.db")
    cur = conn.cursor()
    # IF NOT EXISTS want ik kon geen andere check inbouwen.
    cur.execute("CREATE TABLE IF NOT EXISTS accounts (username text, passhash text)")
    # cur.execute("DELETE FROM accounts")
    values = (account[0], account[1])
    # if func.lower() == "write": # Oude code, verplaatst naar dbmod()
    cur.execute("INSERT INTO accounts VALUES (?, ?)", values)
    conn.commit()
    conn.close()

# Deze functie checkt de sqldatabase voor ofwel aanwezigheid van accountdata dan wel alleen de accountnaam
def dbcheck(value, func):
    conn = sql.connect("sqldb.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS accounts (username text, passhash text)")
    if func.lower() == "account":
        cur.execute("SELECT * FROM accounts WHERE username=? AND passhash=?", (value[0],value[1],))
        return cur.fetchone()
    elif func.lower() == "name":
        cur.execute("SELECT username FROM accounts WHERE username=?", (value[0],))
        return cur.fetchone()
    conn.close()

# Deze functie modificeert de database, func specificeert een naamverandering danwel password reset.
def dbmod(values, func):
    conn = sql.connect("sqldb.db")
    cur = conn.cursor()
    if func.lower() == "name":
        cur.execute("UPDATE accounts SET username=? WHERE username=? AND passhash=?", (values[1], values[0][0], values[0][1],)) # Okee ik ben onnodig veel met lists bezig maar het werkt priem.
    elif func.lower() == "password":
        cur.execute("UPDATE accounts SET passhash=? WHERE username=? AND passhash=?", (values[1], values[0][0], values[0][1],)) # Gebruikt het oude wachtwoord, moet updaten!!
    conn.commit() # Commits zijn handig als je na een halfuur nog steeds niet weet waarom SQL niks wordt opgeslagen..
    conn.close()
# Deze functie verwijderd een invoer uit de database
def dbremove(values):
    conn = sql.connect("sqldb.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM accounts WHERE username=? AND passhash=?", (values[0], values[1],))
    conn.commit()
    conn.close()

## De volgende functies behandelen loginactiviteiten
# Functie die een loginnaam- en wachtwoordinvoerveld presenteert, returns invoer.
def login():
    while True:
        login_msg = "Voer je gegevens in"
        login_title = "Logingegevens"
        login_fields = ["Login", "Wachtwoord"]
        login_value = eg.multpasswordbox(login_msg, login_title, login_fields,)
        if login_value in [False,None]:
            break
        else:
            login_creds = [login_value[0],gen_pass(login_value[1])]
            dbname = dbcheck(login_creds, "name")
            dbdata = dbcheck(login_creds, "account")
            if dbname == None:
                eg.msgbox("Geen geregistreerd account met de naam {0}.".format(login_creds[0]),login_title)
            elif dbdata == tuple(login_creds):
                eg.msgbox("Je bent ingelogd als {0}.".format(login_value[0]), "Gegevens")
                account_options(login_creds)
                break
            else:
                eg.msgbox("Fout wachtwoord ingevoerd.",login_title)

# Deze functie definieert de processen mbt het aanmaken en opslaan van een account.
def new_account():
    # Deze loop vraagt om aanmaakgegevens en herhaalt bij een verkeerd ingevoerd wachtwoord, anders returns invoer
    while True:
        cred_msg = "Voer je gegevens in"
        cred_title = "Accountgegevens"
        cred_fields = ["Loginnaam", "Wachtwoord"]
        cred_value = eg.multpasswordbox(cred_msg, cred_title, cred_fields)
        if cred_value in [None, False]:
            break
        else:
            dbentry = dbcheck(cred_value, "name")  # Checkt de database op duplicaat
            if cred_value[0] in str(dbentry):
                eg.msgbox("Deze gebruikersnaam is al in... Gebruik.", cred_title)
            else:
                check_value = eg.passwordbox("Herhaal je wachtwoord", cred_title) # Herhaal wachtwoord, kon niks anders bedenken
                if check_value in [None, False]:
                    pass
                else:
                    if cred_value[1] == check_value:    # Hier gebeurt de magie van het opslaan van alle accountzooi in een lijst
                        pwhash = gen_pass(str(cred_value[1]))
                        dbinsert([cred_value[0], pwhash])
                        eg.msgbox("Succes!\nAccount aangemaakt met de volgende gegevens:\n\nLoginnaam: {0}\nWachtwoord: {1}\nHex: {2}".format(cred_value[0],cred_value[1],pwhash)) # DEL hash
                        break
                    else:
                        eg.msgbox("Je wachtwoorden komen niet overeen!")

## De volgende functies beschrijven accountopties na het inloggen.
# Deze functie verandert de naam, wijzigt daarbij de database.
def change_name(account_creds):
    while True:
        change_msg = "Je huidige naam is {0}. Wat moet je nieuwe naam zijn?".format(account_creds[0])
        change_title = "Accountnaam wijzigen"
        change_fields = []
        change_value = eg.enterbox(change_msg, change_title, change_fields)
        new_creds = [change_value, account_creds[1]]
        dbname = dbcheck(new_creds, "name")
        if change_value in [None,False]:
            return account_creds
        elif len(change_value) < 2 or len(change_value) > 16:
            eg.msgbox("Je naam mag tussen de 2 en 16 karakters zijn!", change_title)
        elif change_value == account_creds[0]:
            eg.msgbox("Je naam blijft onveranderd {0}.".format(change_value), change_title)
            return account_creds
        elif dbname != None:
            eg.msgbox("De naam {0} is al in gebruik.".format(change_value), change_title)
        else:
            dbmod([account_creds, change_value], "name")
            eg.msgbox("Je naam is veranderd van {0} naar {1}.".format(account_creds[0], change_value), change_title)
            account_creds.remove(account_creds[0])
            account_creds.insert(0, change_value) # Deze twee functies updaten de accountinfo.
            return account_creds # Hierdoor valt de nieuwe accountinfo in bovenliggende functies te gebruiken.

# Deze functie vraagt om een nieuw wachtwoord, haalt deze door de hashgenerator en zet hem in de database.
def reset_password(account_creds):
    while True:
        choice_msg = "Weet je zeker dat je je huidige wachtwoord wilt resetten?"
        choice_title = "Wachtwoord resetten"
        choice_buttons = ["Reset", "Annuleer"]
        choice_value = eg.buttonbox(choice_msg, choice_title, choice_buttons)
        if choice_value in [False, None]:
            return account_creds
        elif choice_value.lower() == "reset":
            pw_msg = "Voer een nieuw wachtwoord in"
            pw_title = "Reset wachtwoord"
            pw_fields = []
            pw_value = eg.passwordbox(pw_msg, pw_title, pw_fields)
            change_value = gen_pass(pw_value) # Genereert gelijk de hash, var_name gekozen vanwege overzicht
            dbmod([account_creds, change_value], "password")
            account_creds.remove(account_creds[1])
            account_creds.insert(1, change_value) # Update de accountinfo met nieuw wachtwoord
            return account_creds # Geeft nieuwe creds door naar boven
        else:
            return account_creds

def del_account(value):
    del_msg = "Weet je zeker dat je je account wilt verwijderen?"
    del_title = "Account verwijderen"
    del_buttons = ["Verwijder", "Annuleer"]
    del_value = eg.buttonbox(del_msg, del_title, del_buttons)
    if del_value.lower() == "verwijder":
        del_msg2 = "Weet je het HEEL zeker? De verwijdering is niet ongedaan te maken!"
        del_value2 = eg.buttonbox(del_msg2, del_title, del_buttons)
        if del_value2.lower() == "verwijder":
            dbremove(value)
            del_msg_conf = "Het account {0} is verwijderd.".format(value[0])
            eg.msgbox(del_msg_conf, del_title)
            return True
        else:
            return False
    else:
        return False

# Deze functie geeft de opties om de accounts te manipuleren.
def account_options(account_creds):
    account_creds_current = account_creds
    while True:
        choice = choicemenu(["Accountnaam wijzigen","Wachtwoord resetten","Account verwijderen"])
        if choice in [False,None]:
            break
        else:
            if choice.lower() == "accountnaam wijzigen":
                account_creds_current = change_name(account_creds_current)
            elif choice.lower() == "wachtwoord resetten":
                account_creds_current = reset_password(account_creds_current)
            elif choice.lower() == "account verwijderen":
                remove = del_account(account_creds_current)
                if remove == True:
                    break

# Functie die afhankelijk van parameters nieuwe functies aanroept.
def options(choice, choices_list):
    if choice == choices_list[0]:
        new_account()
    elif choice == choices_list[1]:
        login_value = login()
    elif choice in [choices_list[2], None, False]:
        return False