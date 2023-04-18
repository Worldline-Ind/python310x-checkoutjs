from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from forms import AdminForm, Offline_VerificationForm, RefundForm, ReconciliationForm, Mandate_VerificationForm, Transaction_SchedulingForm, Transaction_VerificationForm, Stop_PaymentForm, Mandate_DeactivationForm, Online_TransactionForm, read_data
from datetime import datetime, timedelta, date
import json
import requests
import hashlib
import random

app = Flask(__name__)

app.config['SECRET_KEY'] = 'c77af429b8cddaf007505e6c8d9557d9'
string_to_bool = {'true': True, True: True, 'false': False, False: False}


def check_data():
    config_data = read_data()
    if (config_data['merchantCode'] and config_data['SALT'] and config_data['merchantSchemeCode'] and config_data['currency']) == "":
        return False
    else:
        return config_data


def call_api(data):
    raw_response = requests.post(url='https://www.paynimo.com/api/paynimoV2.req', data=json.dumps(data))
    return raw_response.json()


@app.route('/payment/admin', methods=['GET', 'POST'])
def admin():
    form = AdminForm()
    config_data = read_data()
    for field in form:
        field.data = config_data[field.name]
    if request.method == 'POST':
        request_data = request.form.to_dict()
        json_object = json.dumps(request_data, indent=4)
        f = open('worldline_configuration.json', 'w')
        f.write(json_object)
        f.close()
        flash('Success: Information has been updated.')
        return redirect(url_for('admin'))
    return render_template('admin.html', form=form, config_data=config_data)


@app.route('/payment', methods=['GET', 'POST'])
def online_transaction():
    form = Online_TransactionForm()
    config_data = check_data()
    if not config_data:
        return render_template('mandatory_fields_page_error.html')
    for field in form:
        field.data = config_data.get(field.name, '')
    form.txn_id.data = str(random.randint(100, 9999999999))
    start_date = date.today().strftime('%Y-%m-%d')
    end_date = (date.today() + timedelta(days=30*365.2425)).strftime('%Y-%m-%d')
    form.returnUrl.data = request.url + '/response' if not string_to_bool[config_data['displayTransactionMessageOnPopup']] else ''
    form.siDetailsAtMerchantEndCond.data = 'true' if string_to_bool[config_data['enableSI']] and string_to_bool[config_data.get('siDetailsAtMerchantEnd', 'false')] else 'false'
    if request.method == 'POST':
        form_data = request.form.to_dict()
        if config_data['typeOfPayment'] == 'TEST':
            form_data['amount'] = '1'
        if not string_to_bool[config_data.get('siDetailsAtMerchantEnd', 'false')] and string_to_bool[config_data['enableSI']]:
            form_data['amountType'] = config_data['amountType']
            form_data['frequency'] = config_data['frequency']
            form_data['debitStartDate'] = date.today().strftime('%Y-%m-%d')
            form_data['debitEndDate'] = (date.today() + timedelta(days=30*365.2425)).strftime('%Y-%m-%d')
            form_data['maxAmount'] = str(int(form_data['amount']) * 2)
        data_string = get_datastring(form_data)
        hashed_data = (hashlib.sha512(data_string.encode())).hexdigest()
        data = get_hash_object(hashed_data, form_data, config_data)
        return jsonify(data)
    return render_template('online_transaction.html', form=form, config_data=config_data, start_date=start_date, end_date=end_date)


@app.route('/payment/response', methods=['POST'])
def response():
    if request.method == 'POST':
        data = request.form['msg'].split('|')
        full_response = request.form['msg']
        if data[0] == '0300':
            config_data = check_data()
            if not config_data:
                return render_template('mandatory_fields_page_error.html')
            request_data = {
                'merchant': {
                    'identifier': config_data['merchantCode']
                },
                'transaction': {
                    'deviceIdentifier': 'S',
                    'currency': config_data['currency'],
                    'dateTime': data[8].split().pop(0),
                    'token': data[5],
                    'requestType': 'S'
                    }
                }
            response = call_api(request_data)
    return render_template('response.html', data=data, response=response if 'response' in locals() else {}, full_response=full_response if 'full_response' in locals() else {})


def get_datastring(data):
    return data['merchantCode'] + '|' + data['txn_id'] + '|' + data['amount'] + '|' + data['accNo'] + '|' \
            + data['custID'] + '|' + data['mobNo'] + '|' + data['email'] + '|' + \
            '-'.join(reversed(data['debitStartDate'].split('-'))) + '|' + '-'.join(reversed(data['debitEndDate'].split('-'))) \
            + '|' + data['maxAmount'] + '|' + data['amountType'] + '|' + data['frequency'] + '|' + data['cardNumber'] + '|' \
            + data['expMonth'] + '|' + data['expYear'] + '|' + data['cvvCode'] + '|' + data['SALT']


def get_hash_object(hashed_data, data, config_data):
    prepared_object = {
        'tarCall': False,
        'features': {
            'showPGResponseMsg': True,
            'enableMerTxnDetails': True,
            'enableAbortResponse': False,
            'enableSI': string_to_bool[config_data['enableSI']],
            'siDetailsAtMerchantEnd': string_to_bool[config_data.get('siDetailsAtMerchantEnd', 'false')],
            'enableNewWindowFlow': string_to_bool[config_data['enableNewWindowFlow']],  # for hybrid applications please disable this by passing False
            'enableExpressPay': string_to_bool[config_data['enableExpressPay']],  # if unique customer identifier is passed then save card functionality for end  end customer
            'enableInstrumentDeRegistration': string_to_bool[config_data['enableInstrumentDeRegistration']],  # if unique customer identifier is passed then option to delete saved card by end customer
            'hideSavedInstruments': string_to_bool[config_data['hideSavedInstruments']],
            'separateCardMode': string_to_bool[config_data['separateCardMode']],
            'payWithSavedInstrument': string_to_bool[config_data['saveInstrument']],
            'hideSIDetails': string_to_bool[config_data['hideSIDetails']],
            'hideSIConfirmation': string_to_bool[config_data['hideSIConfirmation']],
            'expandSIDetails': string_to_bool[config_data['expandSIDetails']],
            'enableDebitDay': string_to_bool[config_data['enableDebitDay']],
            'showSIResponseMsg': string_to_bool[config_data['showSIResponseMsg']],
            'showSIConfirmation': string_to_bool[config_data['showSIConfirmation']],
            'enableTxnForNonSICards': string_to_bool[config_data['enableTxnForNonSICards']],
            'showAllModesWithSI': string_to_bool[config_data['showAllModesWithSI']]
        },
        'consumerData': {
            'deviceId': 'WEBSH2',  # //possible values 'WEBSH1', 'WEBSH2' and 'WEBMD5'
            'token': hashed_data,
            'returnUrl': data['returnUrl'],
            'paymentMode': config_data['paymentMode'],
            'paymentModeOrder': config_data['paymentModeOrder'].replace(' ', '').split(','),
            'checkoutElement': '#worldline_embeded_popup' if string_to_bool[config_data['embedPaymentGatewayOnPage']] else '',
            'merchantLogoUrl': config_data['logoURL'],
            'merchantId': data['merchantCode'],  # provided merchant
            'merchantMsg': config_data['merchantMessage'],
            'disclaimerMsg': config_data['disclaimerMessage'],
            'currency': data['currency'],
            'consumerId': data['custID'],  # Your unique consumer identifier to register a eMandate/eNACH
            'consumerMobileNo': data['mobNo'],
            'consumerEmailId': data['email'],
            'txnId': data['txn_id'],  # Unique merchant transaction ID
            'items': [{
                'itemId': data['merchantSchemeCode'],
                'amount': data['amount'],
                'comAmt': '0'
            }],
            'customStyle': {
                'PRIMARY_COLOR_CODE': config_data['primaryColor'],  # merchant primary color code
                'SECONDARY_COLOR_CODE': config_data['secondaryColor'],  # provide merchant's suitable color code
                'BUTTON_COLOR_CODE_1': config_data['buttonColor1'],  # merchant's button background color code
                'BUTTON_COLOR_CODE_2': config_data['buttonColor2']  # provide merchant's suitable color code for button text
            }
        }
    }
    if string_to_bool[data['siDetailsAtMerchantEndCond']]:
        prepared_object['consumerData']['accountNo'] = data['accNo']
        prepared_object['consumerData']['accountHolderName'] = data['accountHolderName']
        prepared_object['consumerData']['ifscCode'] = data['ifscCode']
        prepared_object['consumerData']['accountType'] = data['accountType']
        prepared_object['consumerData']['debitStartDate'] = '-'.join(reversed(data['debitStartDate'].split('-')))
        prepared_object['consumerData']['debitEndDate'] = '-'.join(reversed(data['debitEndDate'].split('-')))
        prepared_object['consumerData']['maxAmount'] = data['maxAmount']
        prepared_object['consumerData']['amountType'] = data['amountType']
        prepared_object['consumerData']['frequency'] = data['frequency']
    elif string_to_bool[config_data['enableSI']] and not string_to_bool[data['siDetailsAtMerchantEndCond']]:
        prepared_object['consumerData']['debitStartDate'] = '-'.join(reversed(data['debitStartDate'].split('-')))
        prepared_object['consumerData']['debitEndDate'] = '-'.join(reversed(data['debitEndDate'].split('-')))
        prepared_object['consumerData']['maxAmount'] = data['maxAmount']
        prepared_object['consumerData']['amountType'] = data['amountType']
        prepared_object['consumerData']['frequency'] = data['frequency']
    return prepared_object


@app.route('/payment/offline-verification', methods=['GET', 'POST'])
def offline_verification():
    form = Offline_VerificationForm()
    config_data = check_data()
    if not config_data:
        return render_template('mandatory_fields_page_error.html')
    if request.method == 'POST':
        config_data = check_data()
        if not config_data:
            return render_template('mandatory_fields_page_error.html')
        data = {
            'merchant': {
                'identifier': config_data['merchantCode']
            },
            'transaction': {
                'deviceIdentifier': 'S',
                'currency': config_data['currency'],
                'identifier': request.form['merchantTxnId'],
                'dateTime': request.form['date'],
                'requestType': 'O'
            }
        }
        response = call_api(data)
    return render_template('offline_verification.html', form=form, response=response if 'response' in locals() else {})


@app.route('/payment/refund', methods=['GET', 'POST'])
def refund():
    form = RefundForm()
    config_data = check_data()
    if not config_data:
        return render_template('mandatory_fields_page_error.html')
    if request.method == 'POST':
        config_data = check_data()
        if not config_data:
            return render_template('mandatory_fields_page_error.html')
        data = {
            'merchant': {
                'identifier': config_data['merchantCode']
            },
            'cart': {},
            'transaction': {
                'deviceIdentifier': 'S',
                'amount': request.form['amount'],
                'currency': config_data['currency'],
                'token': request.form['token'],
                'dateTime': request.form['date'],
                'requestType': 'R'
            }
        }
        response = call_api(data)
    return render_template('refund.html', form=form, response=response if 'response' in locals() else {})


@app.route('/payment/reconcile', methods=['GET', 'POST'])
def reconciliation():
    form = ReconciliationForm()
    config_data = check_data()
    if not config_data:
        return render_template('mandatory_fields_page_error.html')
    last_response = []
    if request.method == 'POST':
        config_data = check_data()
        if not config_data:
            return render_template('mandatory_fields_page_error.html')
        transaction_ids = request.form['merchantTxnId'].strip(', ')
        transaction_ids = ''.join(transaction_ids.split())
        start_date = datetime.strptime(request.form['startDate'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form['endDate'], '%Y-%m-%d').date()
        delta = end_date - start_date
        for transaction_id in transaction_ids.split(','):
            count = 0
            for i in range(delta.days + 1):
                day = start_date + timedelta(days=i)
                date = day.strftime('%d-%m-%Y')
                data = {
                    'merchant': {
                        'identifier': config_data['merchantCode']
                    },
                    'transaction': {
                        'deviceIdentifier': 'S',
                        'currency': config_data['currency'],
                        'identifier': transaction_id,
                        'dateTime': date,
                        'requestType': 'O'
                    }
                }
                response = call_api(data)
                if response['paymentMethod']['paymentTransaction']['statusCode'] != 9999 and response['paymentMethod']['paymentTransaction']['errorMessage'] != 'Transactionn Not Found':
                    count = 1
                    last_response.append(response)
                    break
            if count == 0:
                last_response.append(response)
    return render_template('reconciliation.html', form=form, last_response=last_response)


@app.route('/payment/s2s')
def s2s():
    data = request.args.get('msg').split('|')
    config_data = check_data()
    if not config_data:
        return render_template('mandatory_fields_page_error.html')
    clnt_txn_ref = data[3]
    pg_txn_id = data[5]
    status = 0
    data_string = '|'.join(data[:-1]) + '|' + config_data['SALT']
    result = hashlib.sha512(data_string.encode())
    if data[-1] == result.hexdigest():
        status = 1
    else:
        status = 0
    return render_template('s2s.html', clnt_txn_ref=clnt_txn_ref, pg_txn_id=pg_txn_id, status=status)


@app.route('/emandate-si/mandate-verification', methods=['GET', 'POST'])
def mandate_verification():
    form = Mandate_VerificationForm()
    config_data = check_data()
    if not config_data:
        return render_template('mandatory_fields_page_error.html')
    if request.method == 'POST':
        config_data = check_data()
        if not config_data:
            return render_template('mandatory_fields_page_error.html')
        if request.form['typeOfTransaction'] == 'eMandate':
            type_data = '002'
        else:
            type_data = '001'
        data = {
            'merchant': {
                'identifier': config_data['merchantCode']
            },
            'payment': {
                'instruction': {}
            },
            'transaction': {
                'deviceIdentifier': 'S',
                'type': type_data,
                'currency': config_data['currency'],
                'identifier': request.form['merchantTxnId'],
                'dateTime': request.form['date'],
                'subType': '002',
                'requestType': 'TSI'
            },
            'consumer': {
                'identifier': request.form['customerId']
            }
        }
        response = call_api(data)
    return render_template('mandate_verification.html', form=form, response=response if 'response' in locals() else {})


@app.route('/emandate-si/transaction-scheduling', methods=['GET', 'POST'])
def transaction_scheduling():
    form = Transaction_SchedulingForm()
    config_data = check_data()
    if not config_data:
        return render_template('mandatory_fields_page_error.html')
    if request.method == 'POST':
        config_data = check_data()
        if not config_data:
            return render_template('mandatory_fields_page_error.html')
        transaction_id = str(random.randint(100, 9999999999))
        date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        date = date.strftime('%d%m%Y')
        if request.form['typeOfTransaction'] == 'eMandate':
            type_data = '002'
        else:
            type_data = '001'
        data = {
            'merchant': {
                'identifier': config_data['merchantCode']
            },
            'payment': {
                'instrument': {
                    'identifier': config_data['merchantSchemeCode']
                },
                'instruction': {
                    'amount': request.form['amount'],
                    'endDateTime': date,
                    'identifier': request.form['mandateRegId']
                }
            },
            'transaction': {
                'deviceIdentifier': 'S',
                'type': type_data,
                'currency': config_data['currency'],
                'identifier': transaction_id,
                'subType': '003',
                'requestType': 'TSI'
            }
        }
        response = call_api(data)
    return render_template('transaction_scheduling.html', form=form, response=response if 'response' in locals() else {})


@app.route('/emandate-si/transaction-verification', methods=['GET', 'POST'])
def transaction_verification():
    form = Transaction_VerificationForm()
    config_data = check_data()
    if not config_data:
        return render_template('mandatory_fields_page_error.html')
    if request.method == 'POST':
        config_data = check_data()
        if not config_data:
            return render_template('mandatory_fields_page_error.html')
        if request.form['typeOfTransaction'] == 'eMandate':
            type_data = '002'
        else:
            type_data = '001'
        data = {
            'merchant': {
                'identifier': config_data['merchantCode']
            },
            'payment': {
                'instruction': {
                }
            },
            'transaction': {
                'deviceIdentifier': 'S',
                'type': type_data,
                'currency': config_data['currency'],
                'identifier': request.form['merchantTxnId'],
                'dateTime': request.form['date'],
                'subType': '004',
                'requestType': 'TSI'
            }
        }
        response = call_api(data)
        if response['paymentMethod']['paymentTransaction']['statusMessage'] == 'I':
            response['paymentMethod']['paymentTransaction']['statusMessage'] = 'Initiated'
        elif response['paymentMethod']['paymentTransaction']['statusMessage'] == 'D':
            response['paymentMethod']['paymentTransaction']['statusMessage'] = 'Success'
        elif response['paymentMethod']['paymentTransaction']['statusMessage'] == 'F':
            response['paymentMethod']['paymentTransaction']['statusMessage'] = 'Failure'
    return render_template('transaction_verification.html', form=form, response=response if 'response' in locals() else {})


@app.route('/emandate-si/stop-payment', methods=['GET', 'POST'])
def stop_payment():
    form = Stop_PaymentForm()
    config_data = check_data()
    if not config_data:
        return render_template('mandatory_fields_page_error.html')
    if request.method == 'POST':
        config_data = check_data()
        if not config_data:
            return render_template('mandatory_fields_page_error.html')
        transaction_id = str(random.randint(100, 9999999999))
        data = {
            'merchant': {
                'webhookEndpointURL': '',
                'responseType': '',
                'responseEndpointURL': '',
                'description': '',
                'identifier': config_data['merchantCode'],
                'webhookType': ''
            },
            'cart': {
                'item': [
                    {
                        'description': '',
                        'providerIdentifier': '',
                        'surchargeOrDiscountAmount': '',
                        'amount': '',
                        'comAmt': '',
                        'sKU': '',
                        'reference': '',
                        'identifier': ''
                    }
                ],
                'reference': '',
                'identifier': '',
                'description': '',
                'Amount': ''
            },
            'payment': {
                'method': {
                    'token': '',
                    'type': ''
                },
                'instrument': {
                    'expiry': {
                        'year': '',
                        'month': '',
                        'dateTime': ''
                    },
                    'provider': '',
                    'iFSC': '',
                    'holder': {
                        'name': '',
                        'address': {
                            'country': '',
                            'street': '',
                            'state': '',
                            'city': '',
                            'zipCode': '',
                            'county': ''
                        }
                    },
                    'bIC': '',
                    'type': '',
                    'action': '',
                    'mICR': '',
                    'verificationCode': '',
                    'iBAN': '',
                    'processor': '',
                    'issuance': {
                        'year': '',
                        'month': '',
                        'dateTime': ''
                    },
                    'alias': '',
                    'identifier': config_data['merchantSchemeCode'],
                    'token': '',
                    'authentication': {
                        'token': '',
                        'type': '',
                        'subType': ''
                    },
                    'subType': '',
                    'issuer': '',
                    'acquirer': ''
                },
                'instruction': {
                    'occurrence': '',
                    'amount': '11',
                    'frequency': '',
                    'type': '',
                    'description': '',
                    'action': '',
                    'limit': '',
                    'endDateTime': '',
                    'identifier': '',
                    'reference': '',
                    'startDateTime': '',
                    'validity': ''
                }
            },
            'transaction': {
                'deviceIdentifier': 'S',
                'smsSending': '',
                'amount': '',
                'forced3DSCall ': '',
                'type': '001',
                'description': '',
                'currency': config_data['currency'],
                'isRegistration': '',
                'identifier': transaction_id,
                'dateTime': '',
                'token': request.form['tpslTransactionId'],
                'securityToken': '',
                'subType': '006',
                'requestType': 'TSI',
                'reference': '',
                'merchantInitiated': '',
                'merchantRefNo': ''
            },
            'consumer': {
                'mobileNumber': '',
                'emailID': '',
                'identifier': '',
                'accountNo': ''
            }
        }
        response = call_api(data)
    return render_template('stop_payment.html', form=form, response=response if 'response' in locals() else {})


@app.route('/emandate-si/mandate-deactivation', methods=['GET', 'POST'])
def mandate_deactivation():
    form = Mandate_DeactivationForm()
    config_data = check_data()
    if not config_data:
        return render_template('mandatory_fields_page_error.html')
    if request.method == 'POST':
        config_data = check_data()
        if not config_data:
            return render_template('mandatory_fields_page_error.html')
        if request.form['typeOfTransaction'] == 'eMandate':
            type_data = '002'
        else:
            type_data = '001'
        transaction_id = str(random.randint(100, 9999999999))
        data = {
            'merchant': {
                'webhookEndpointURL': '',
                'responseType': '',
                'responseEndpointURL': '',
                'description': '',
                'identifier': config_data['merchantCode'],
                'webhookType': ''
            },
            'cart': {
                'item': [
                    {
                        'description': '',
                        'providerIdentifier': '',
                        'surchargeOrDiscountAmount': '',
                        'amount': '',
                        'comAmt': '',
                        'sKU': '',
                        'reference': '',
                        'identifier': ''
                    }
                ],
                'reference': '',
                'identifier': '',
                'description': '',
                'Amount': ''
            },
            'payment': {
                'method': {
                    'token': '',
                    'type': ''
                },
                'instrument': {
                    'expiry': {
                        'year': '',
                        'month': '',
                        'dateTime': ''
                    },
                    'provider': '',
                    'iFSC': '',
                    'holder': {
                        'name': '',
                        'address': {
                            'country': '',
                            'street': '',
                            'state': '',
                            'city': '',
                            'zipCode': '',
                            'county': ''
                        }
                    },
                    'bIC': '',
                    'type': '',
                    'action': '',
                    'mICR': '',
                    'verificationCode': '',
                    'iBAN': '',
                    'processor': '',
                    'issuance': {
                        'year': '',
                        'month': '',
                        'dateTime': ''
                    },
                    'alias': '',
                    'identifier': '',
                    'token': '',
                    'authentication': {
                        'token': '',
                        'type': '',
                        'subType': ''
                    },
                    'subType': '',
                    'issuer': '',
                    'acquirer': ''
                },
                'instruction': {
                    'occurrence': '',
                    'amount': '',
                    'frequency': '',
                    'type': '',
                    'description': '',
                    'action': '',
                    'limit': '',
                    'endDateTime': '',
                    'identifier': '',
                    'reference': '',
                    'startDateTime': '',
                    'validity': ''
                }
            },
            'transaction': {
                'deviceIdentifier': 'S',
                'smsSending': '',
                'amount': '',
                'forced3DSCall ': '',
                'type': type_data,
                'description': '',
                'currency': config_data['currency'],
                'isRegistration': '',
                'identifier': transaction_id,
                'dateTime': '',
                'token': request.form['mandateRegId'],
                'securityToken': '',
                'subType': '005',
                'requestType': 'TSI',
                'reference': '',
                'merchantInitiated': '',
                'merchantRefNo': ''
            },
            'consumer': {
                'mobileNumber': '',
                'emailID': '',
                'identifier': '',
                'accountNo': ''
            }
        }
        response = call_api(data)
        if response['paymentMethod']['paymentTransaction']['statusCode'] == "" and response['paymentMethod']['error']['desc'] == "":
            response['paymentMethod']['paymentTransaction']['statusCode'] = "Not Found"
            response['paymentMethod']['error']['desc'] = "Not Found"
    return render_template('mandate_deactivation.html', form=form, response=response if 'response' in locals() else {})
