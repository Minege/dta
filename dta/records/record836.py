"""Implementation of TA 836 Record"""
from datetime import datetime, timedelta
from itertools import combinations

from schwifty import BIC, IBAN

from dta.constants import ChargesRule, IdentificationBankAddress, IdentificationPurpose
from dta.fields import AlphaNumeric, Amount, Currency, Date, Iban, Numeric
from dta.records.record import DTARecord
from dta.util import remove_whitespace, is_swiss_iban


class DTARecord836(DTARecord):  # pylint: disable=too-many-instance-attributes
    """TA 836 Record implementation.

    Payments with an IBAN in Switzerland and abroad, in all currencies.

    This type of transaction can only be used if
    the beneficiary's account number corresponds
    to the IBAN standard for the country concerned.

    The constructor of this class should not accept record
    values. All fields should be set after initialization and all
    field attributes must use a subclass of `dta.fields.Field`.

    Attributes:
        reference: 11 characters transaction no. defined by the
            ordering party; must be unique within a data file. The
            first r characters sender id are added automatically.
        client_account: Account to be debited (Only IBAN
            is accepted, despite the fact that the
            standard accepts both with or without IBAN)
        value_date: The date at which the payment should be processed
        currency: The currency for the amount of the payment
        amount: The actual amount of the payment
        conversation_rate: Only indicated if previously agreed
            on the basis of the bank's foreign exchange rate.
            A maximum of 6 decimal places is permitted.
        client_address1: Ordering party's address (first 35 characters)
        client_address2: Ordering party's address (middle 35 characters)
        client_address3: Ordering party's address (last 35 characters)
        bank_address_type: Identification bank address,
            use ``IdentificationBankAddress`` for the values.
        bank_address1: Beneficiary's institution
            When option ``IdentificationBankAddress.BIC_ADDRESS`` or
            ``IdentificationBankAddress.SWIFTH_ADDRESS`` (``'A'``):
            8- or 11-digit BIC address (=SWIFT address)
            When option
            ``IdentificationBankAddress.BENEFICIARY_ADDRESS``:
            Name and address of the beneficiary's institution
            If Field 58 contains a CH or LI IBAN, no details on the
            financial institution are required. In this case, option
            ``IdentificationBankAddress.BENEFICIARY_ADDRESS`` (``'D'``)
            must be chosen in disc format and the address field
            completed with blanks.
        bank_address2: Beneficiary's institution
            When option ``IdentificationBankAddress.BIC_ADDRESS`` or
            ``IdentificationBankAddress.SWIFTH_ADDRESS`` (``'A'``):
            Must be blank and bank_address1 must be a 8- or 11-digit
            BIC address (=SWIFT address). When option
            ``IdentificationBankAddress.BENEFICIARY_ADDRESS``:
            Name and address of the beneficiary's institution
            If Field 58 contains a CH or LI IBAN, no details on the
            financial institution are required. In this case, option
            ``IdentificationBankAddress.BENEFICIARY_ADDRESS`` (``'D'``)
            must be chosen in disc format and the address field
            completed with blanks.
        recipient_iban: The beneficiary's IBAN
        recipient_name: Name of the beneficiary
        recipient_address1: Address of the beneficiary (first 35 characters)
        recipient_address2: Address of the beneficiary (last 35 characters)
        identification_purpose: Identification of purpose,
            use ``IdentificationPurpose`` for the values.
        purpose1: Purpose of the payment
            Structured reference number:
                1 line of 20 positions fixed (without blanks),
                commencing with 2-digit check-digit (PP), rest blank
            Unstructured, free text: first of
                up to 3 lines of 35 characters
        purpose2: Purpose of the payment
            Structured reference number: Must be blank
            Unstructured, free text: second of
                up to 3 lines of 35 characters
        purpose3: Purpose of the payment
            Structured reference number: Must be blank
            Unstructured, free text: third of
                up to 3 lines of 35 characters
        charges_rules: Rules for charges, use ``ChargesRule`` for the values
    """
    reference = AlphaNumeric(length=11)
    client_account = Iban(length=24)
    value_date = Date()
    currency = Currency()
    amount = Amount(length=15)

    conversation_rate = Amount(length=12)
    client_address1 = AlphaNumeric(length=35, truncate=True)
    client_address2 = AlphaNumeric(length=35, truncate=True)
    client_address3 = AlphaNumeric(length=35, truncate=True)

    bank_address_type = AlphaNumeric(length=1, allowed_values=IdentificationBankAddress)
    bank_address1 = AlphaNumeric(length=35)
    bank_address2 = AlphaNumeric(length=35)
    recipient_iban = Iban(length=34)

    recipient_name = AlphaNumeric(length=35, truncate=True)
    recipient_address1 = AlphaNumeric(length=35, truncate=True)
    recipient_address2 = AlphaNumeric(length=35, truncate=True)

    identification_purpose = AlphaNumeric(length=1, allowed_values=IdentificationPurpose)
    purpose1 = AlphaNumeric(length=35)
    purpose2 = AlphaNumeric(length=35)
    purpose3 = AlphaNumeric(length=35)
    charges_rules = Numeric(length=1, allowed_values=ChargesRule)

    _template = (
        '01{header}{reference}{client_account}{value_date}{currency}{amount}{padding:<11}\r\n'
        '02{conversation_rate}{client_address1}{client_address2}{client_address3}{padding:<9}\r\n'
        '03{bank_address_type}{bank_address1}{bank_address2}{recipient_iban}{padding:<21}\r\n'
        '04{recipient_name}{recipient_address1}{recipient_address2}{padding:<21}\r\n'
        '05{identification_purpose}{purpose1}{purpose2}{purpose3}{charges_rules}{padding:<19}'
    )

    def __init__(self) -> None:
        super().__init__()
        self.header.transaction_type = 836

    @property
    def client_address(self):
        """The 3 lines of the client address as a tuple of 3 strings."""
        return self.client_address1, self.client_address2, self.client_address3

    @client_address.setter
    def client_address(self, client_address):
        self.client_address1, self.client_address2, self.client_address3 = client_address

    @property
    def bank_address(self):
        """The 2 lines of the bank address as a tuple of 2 strings."""
        return self.bank_address1, self.bank_address2

    @bank_address.setter
    def bank_address(self, bank_address):
        self.bank_address1, self.bank_address2 = bank_address

    @property
    def recipient_address(self):
        """The 2 lines of the recipient address as a tuple of 2 strings."""
        return self.recipient_address1, self.recipient_address2

    @recipient_address.setter
    def recipient_address(self, recipient_address):
        self.recipient_address1, self.recipient_address2 = recipient_address

    @property
    def purpose(self):
        """The 3 lines of the purpose as a tuple of 3 strings."""
        return self.purpose1, self.purpose2, self.purpose2

    @purpose.setter
    def purpose(self, purpose):
        self.purpose1, self.purpose2, self.purpose2 = purpose

    def generate(self):
        """Generate a TA 836 record as a string.

        The returned value is a simple string. Make sure
        to encode it to the ISO Latincode 8859-1 format
        in accordance with the DTA Standard and Formats.

        Returns: A TA 836 record as a string.
        """
        return self._template.format(
            header=self.header.generate(),
            # First 5 positions must contain a valid DTA identification (sender id).
            # Remaining 11 positions must contain a transaction reference number.
            # The generation of the full (16x) reference from the valid DTA identification is done automatically here
            reference=f'{self.header.sender_id}{self.reference}',
            client_account=self.client_account,
            value_date=self.value_date,
            currency=self.currency,
            amount=self.amount,

            conversation_rate=self.conversation_rate,
            client_address1=self.client_address1,
            client_address2=self.client_address2,
            client_address3=self.client_address3,

            bank_address_type=self.bank_address_type,
            bank_address1=self.bank_address1,
            bank_address2=self.bank_address2,
            recipient_iban=self.recipient_iban,

            recipient_name=self.recipient_name,
            recipient_address1=self.recipient_address1,
            recipient_address2=self.recipient_address2,

            identification_purpose=self.identification_purpose,
            purpose1=self.purpose1,
            purpose2=self.purpose2,
            purpose3=self.purpose3,
            charges_rules=self.charges_rules,

            padding=''
        )

    def validate(self):  # pylint: disable=too-complex, too-many-branches
        """Validate the field's value of the record."""
        super().validate()
        if self.header.processing_date != '000000':
            self.header.add_error('processing_date', "NOT PERMITTED: header processing date must be '000000'.")

        if self.header.recipient_clearing.strip():
            self.header.add_error('recipient_clearing',
                                  "NOT ALLOWED: beneficiary's bank clearing number must be blank.")

        if self.header.transaction_type != '836':
            self.header.add_error('transaction_type', "INVALID: Transaction type must be TA 836.")

        if self.header.payment_type not in ('0', '1'):
            self.header.add_error('payment_type', "INVALID: Payment type must be 0 or 1 TA 836.")

        if not remove_whitespace(self.reference):
            self.add_error('reference', "MISSING TRANSACTION NUMBER: Reference may not be blank.")

        try:
            client_iban = IBAN(self.client_account, allow_invalid=False)
        except ValueError:  # Will throw ValueError if it is not a valid IBAN
            self.add_error(
                'client_account',
                "IBAN INVALID: Client account must be a valid with a 21 digit Swiss IBAN (CH resp. LI) ."
            )
        else:
            if is_swiss_iban(client_iban):
                self.add_error(
                    'client_account',
                    "IBAN INVALID: Client account must be a valid with a 21 digit Swiss IBAN (CH resp. LI) ."
                )

        # Bank clearing is at pos 5-9 in IBAN
        if self.client_account[4:9].lstrip('0') != self.header.client_clearing.strip():
            self.add_error('client_account',
                           "IID IN IBAN NOT IDENTICAL WITH BC-NO: IID in IBAN (pos. 5 to 9) must concur with the "
                           "ordering party's BC no.")

        now = datetime.now()
        ten_days_ago = now - timedelta(days=10)
        sixty_days_ahead = now + timedelta(days=60)
        try:
            value_date = datetime.strptime(self.value_date, Date.DATE_FORMAT)
        except ValueError:
            self.add_error('value_date', "INVALID: Must contain a valid date.")
        else:
            if value_date < ten_days_ago:
                self.add_error('value_date', "EXPIRED: value date may not be elapsed more than 10 calendar days.")
            elif value_date > sixty_days_ahead:
                self.add_error('value_date', "TOO FAR AHEAD: value date may not exceed the reading in date + 60 days.")

        decimal_places = len(self.amount.strip().split(',', maxsplit=1)[1])
        if self.currency == 'CHF' and decimal_places > 2:
            self.add_error('currency',
                           "MORE THAN 2 DECIMAL PLACES: Amount may not contain more than 2 decimal places.")
        elif self.currency != 'CHF' and decimal_places > 3:
            self.add_error(
                'currency',
                " MORE THAN 3 DECIMAL PLACES: Amount may not contain more than 3 decimal places (foreign currencies)."
            )

        if not any(self.client_address):
            self.add_error('client_address', "INCOMPLETE: Ordering party address, at least one line must exist.")
        if self.bank_address_type == IdentificationBankAddress.SWIFT_ADDRESS:
            try:
                BIC(self.bank_address1).validate()
            except ValueError:
                self.add_error(
                    'bank_address_type',
                    f"INCORRECT FIELD IDENTIFICATION: bank address type {IdentificationBankAddress.SWIFT_ADDRESS} "
                    f"may only be used if an 8 or 11 character BIC address (SWIFT) exists."
                )
        # No specification on how to validate a bank's address if the `bank_address_type` is not SWIFT.

        if all(not line1.strip() or not line2.strip() for line1, line2 in combinations(self.client_address, 2)):
            self.add_error('client_address', "INCOMPLETE: At least two address lines must exist.")

        if any('/C/' in address for address in self.client_address):
            self.add_error('client_address', "INVALID: /C/ may not be present for TA 836.")

        # TODO(Jacques Dafflon) Validate IPI reference if identification purpose is structured (I)
