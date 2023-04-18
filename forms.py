from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, HiddenField
from wtforms.validators import DataRequired
from wtforms.fields import DateField
import json


def read_data():
    try:
        f = open('worldline_configuration.json', 'r')
        config_data = json.loads(f.read())
        f.close()
    except FileNotFoundError:
        config_data = {}
    except IOError as e:
        print(e)
    return config_data


class AdminForm(FlaskForm):
    config_data = read_data()
    merchantCode = StringField('*Merchant Code', validators=[DataRequired()], default=config_data['merchantCode'])
    merchantSchemeCode = StringField('*Merchant Scheme Code', validators=[DataRequired()], default=config_data['merchantSchemeCode'])
    SALT = StringField('*SALT', validators=[DataRequired()], default=config_data['SALT'])
    currency = SelectField('*Currency', choices=[('INR', 'INR'), ('USD', 'USD')], default=config_data['currency'])
    typeOfPayment = SelectField('*Type of Payment', choices=[('TEST', 'TEST'), ('LIVE', 'LIVE')], default=config_data['typeOfPayment'])
    primaryColor = StringField('Primary Color', default=config_data['primaryColor'])
    secondaryColor = StringField('Secondary Color', default=config_data['secondaryColor'])
    buttonColor1 = StringField('Button Color 1', default=config_data['buttonColor1'])
    buttonColor2 = StringField('Button Color 2', default=config_data['buttonColor2'])
    logoURL = StringField('Logo URL', default=config_data['logoURL'])
    enableExpressPay = SelectField('Enable ExpressPay', choices=[('true', 'Enabled'), ('false', 'Disabled')], default=config_data['enableExpressPay'])
    separateCardMode = SelectField('Separate Card Mode', choices=[('true', 'Enabled'), ('false', 'Disabled')], default=config_data['separateCardMode'])
    enableNewWindowFlow = SelectField('Enable New Window Flow', choices=[('true', 'Enabled'), ('false', 'Disabled')], default=config_data['enableNewWindowFlow'])
    merchantMessage = StringField('Merchant Message', default=config_data['merchantMessage'])
    disclaimerMessage = StringField('Disclaimer Message', default=config_data['disclaimerMessage'])
    paymentMode = SelectField('Payment Mode', choices=[('all', 'all'), ('cards', 'cards'), ('netBanking', 'netBanking'), ('UPI', 'UPI'), ('imps', 'imps'), ('wallets', 'wallets'), ('cashCards', 'cashCards'), ('NEFTRTGS', 'NEFTRTGS'), ('emiBanks', 'emiBanks')])
    paymentModeOrder = TextAreaField('Payment Mode Order', default=config_data['paymentModeOrder'])
    enableInstrumentDeRegistration = SelectField('Enable InstrumentDeRegistration', choices=[('true', 'Enabled'), ('false', 'Disabled')], default=config_data['enableInstrumentDeRegistration'])
    transactionType = SelectField('Transaction Type', choices=[('SALE', 'SALE')], default=config_data['transactionType'])
    hideSavedInstruments = SelectField('Hide SavedInstruments', choices=[('true', 'Enabled'), ('false', 'Disabled')], default=config_data['hideSavedInstruments'])
    saveInstrument = SelectField('Save Instrument', choices=[('true', 'Enabled'), ('false', 'Disabled')], default=config_data['saveInstrument'])
    displayTransactionMessageOnPopup = SelectField('Display Transaction Message On Popup', choices=[('true', 'Enabled'), ('false', 'Disabled')], default=config_data['displayTransactionMessageOnPopup'])
    embedPaymentGatewayOnPage = SelectField('Embed Payment Gateway On Page', choices=[('true', 'Enabled'), ('false', 'Disabled')], default=config_data['embedPaymentGatewayOnPage'])
    enableSI = SelectField('Enable eMandate/SI', choices=[('true', 'Enabled'), ('false', 'Disabled')], default=config_data['enableSI'])
    hideSIDetails = SelectField('Hide SI Details', choices=[('true', 'Enabled'), ('false', 'Disabled')], default=config_data['hideSIDetails'])
    hideSIConfirmation = SelectField('Hide SI Confirmation', choices=[('true', 'Enabled'), ('false', 'Disabled')], default=config_data['hideSIConfirmation'])
    expandSIDetails = SelectField('Expand SI Details', choices=[('true', 'Enabled'), ('false', 'Disabled')], default=config_data['expandSIDetails'])
    enableDebitDay = SelectField('Enable Debit Day', choices=[('true', 'Enabled'), ('false', 'Disabled')], default=config_data['enableDebitDay'])
    showSIResponseMsg = SelectField('Show SI Response Msg', choices=[('true', 'Enabled'), ('false', 'Disabled')], default=config_data['showSIResponseMsg'])
    showSIConfirmation = SelectField('Show SI Confirmation', choices=[('true', 'Enabled'), ('false', 'Disabled')], default=config_data['showSIConfirmation'])
    enableTxnForNonSICards = SelectField('Enable Txn For NonSI Cards', choices=[('true', 'Enabled'), ('false', 'Disabled')], default=config_data['enableTxnForNonSICards'])
    showAllModesWithSI = SelectField('Show All Modes With SI', choices=[('true', 'Enabled'), ('false', 'Disabled')], default=config_data['showAllModesWithSI'])
    submit = SubmitField('Save')


class Offline_VerificationForm(FlaskForm):
    merchantTxnId = StringField('Merchant Ref No: ', validators=[DataRequired()])
    date = DateField('Date: ', validators=[DataRequired()])
    submit = SubmitField('Submit')


class RefundForm(FlaskForm):
    token = StringField('TPSL Tansaction ID: ', validators=[DataRequired()])
    amount = StringField('Amount: ', validators=[DataRequired()])
    date = DateField('Date: ', validators=[DataRequired()])
    submit = SubmitField('Submit')


class ReconciliationForm(FlaskForm):
    merchantTxnId = TextAreaField('Merchant Ref No: ', validators=[DataRequired()])
    startDate = DateField('From Date: ', validators=[DataRequired()])
    endDate = DateField('To Date: ', validators=[DataRequired()])
    submit = SubmitField('Submit')


class Mandate_VerificationForm(FlaskForm):
    typeOfTransaction = SelectField('Type of Transaction (eMandate/SI on Cards)', choices=[('eMandate', 'eMandate'), ('SIonCards', 'SI on Cards')])
    merchantTxnId = StringField('Merchant Transaction Id', validators=[DataRequired()])
    customerId = StringField('Consumer Id (Customer Id used during transaction)', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    submit = SubmitField('Submit')


class Transaction_SchedulingForm(FlaskForm):
    typeOfTransaction = SelectField('Type of Transaction (eMandate/SI on Cards)', choices=[('eMandate', 'eMandate'), ('SIonCards', 'SI on Cards')])
    mandateRegId = StringField('Mandate Registration Id', validators=[DataRequired()])
    amount = StringField('Amount', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    submit = SubmitField('Submit')


class Transaction_VerificationForm(FlaskForm):
    typeOfTransaction = SelectField('Type of Transaction (eMandate/SI on Cards)', choices=[('eMandate', 'eMandate'), ('SIonCards', 'SI on Cards')])
    merchantTxnId = StringField('Merchant Transaction Id (Transaction Id sent during transaction scheduling)', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    submit = SubmitField('Submit')


class Stop_PaymentForm(FlaskForm):
    tpslTransactionId = StringField('TPSL Transaction Id (TPSL ID given in response of Transaction scheduling): ', validators=[DataRequired()])
    submit = SubmitField('Submit')


class Mandate_DeactivationForm(FlaskForm):
    # TODO remove the default value of typeOfTransaction when mandate deactivation for eMandate is implemented
    typeOfTransaction = SelectField('Type of Transaction (eMandate/SI on Cards)', choices=[('eMandate', 'eMandate'), ('SIonCards', 'SI on Cards')], default='SIonCards')
    mandateRegId = StringField('Mandate Registration Id', validators=[DataRequired()])
    submit = SubmitField('Submit')


class Online_TransactionForm(FlaskForm):
    config_data = read_data()
    merchantCode = StringField('Merchant Code', default=config_data['merchantCode'])
    txn_id = StringField('Transaction ID')
    amount = StringField('Amount')
    merchantSchemeCode = StringField('Scheme', default=config_data['merchantSchemeCode'])
    custID = StringField('Customer Id')
    mobNo = StringField('Mobile Number')
    email = StringField('Email')
    customerName = StringField('Customer Name')
    currency = StringField('Currency', default=config_data['currency'])
    SALT = StringField('SALT', default=config_data['SALT'])
    returnUrl = StringField('Return URL')
    cardNumber = HiddenField('cardNumber')
    expMonth = HiddenField('expMonth')
    expYear = HiddenField('expYear')
    cvvCode = HiddenField('cvvCode')
    siDetailsAtMerchantEndCond = HiddenField('siDetailsAtMerchantEndCond')
    submit = SubmitField('Submit')
