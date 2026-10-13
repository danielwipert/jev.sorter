# Confused category pairs (v2 descriptions)

Built by `python confusions.py`. Ranked by **shared** mistakes on the tuning set:
messages where Jev and DeepSeek both picked the same wrong category.
"All 4" = Sonnet and Haiku made that same pick too.
Examples are from the tuning set only. The test set is held out.

| # | Pair | Status | Jev wrong | DeepSeek wrong | Shared | All 4 agree | Test: shared |
|---|---|---|---|---|---|---|---|
| 1 | `card_arrival <> order_physical_card` | tried in v3 | 3 | 3 | 3 | 0 | 3 |
| 2 | `pending_transfer <> transfer_timing` | tried in v3 | 3 | 5 | 3 | 2 | 4 |
| 3 | `card_about_to_expire <> order_physical_card` | tried in v3 | 3 | 2 | 2 | 0 | 0 |
| 4 | `card_arrival <> card_delivery_estimate` | tried in v3 | 3 | 3 | 2 | 2 | 4 |
| 5 | `declined_card_payment <> reverted_card_payment?` | tried in v3 | 3 | 2 | 2 | 0 | 4 |
| 6 | `card_payment_not_recognised <> direct_debit_payment_not_recognised` | partly described | 2 | 3 | 2 | 2 | 2 |
| 7 | `card_payment_wrong_exchange_rate <> exchange_charge` | tried in v3 | 2 | 2 | 2 | 1 | 0 |
| 8 | `card_payment_wrong_exchange_rate <> exchange_rate` | tried in v3 | 2 | 2 | 2 | 1 | 0 |
| 9 | `declined_card_payment <> declined_transfer` | tried in v3 | 2 | 2 | 2 | 2 | 2 |
| 10 | `declined_transfer <> failed_transfer` | tried in v3 | 2 | 5 | 2 | 0 | 1 |
| 11 | `top_up_by_bank_transfer_charge <> transfer_fee_charged` | not yet tried | 2 | 2 | 2 | 2 | 2 |
| 12 | `verify_my_identity <> why_verify_identity` | partly described | 2 | 3 | 2 | 2 | 1 |
| 13 | `balance_not_updated_after_bank_transfer <> transfer_timing` | not yet tried | 2 | 1 | 1 | 1 | 3 |
| 14 | `card_payment_fee_charged <> extra_charge_on_statement` | not yet tried | 2 | 4 | 1 | 1 | 1 |
| 15 | `card_payment_not_recognised <> extra_charge_on_statement` | partly described | 2 | 3 | 1 | 0 | 0 |

## 1. `card_arrival <> order_physical_card`

- "Where can the cards be delivered?": answer key `order_physical_card`, models said `card_arrival`
- "Where are the cards delivered to": answer key `order_physical_card`, models said `card_arrival`
- "Where are the cards transported to?": answer key `order_physical_card`, models said `card_arrival`

## 2. `pending_transfer <> transfer_timing`

- "Transfers can take up to one day to process before departing for the beneficiary accounts. Please confirm that you've entered your account details correctly. SEPA transfers can take up to two working days, while SWIFT transfers can take up to five working days.": answer key `pending_transfer`, models said `transfer_timing` (all 4 models)
- "It seems like I have been waiting forever for this international transfer. Why is it taking so long? C'mon, it's 2018, things happen at a click of a button. All of the account information is correct, so how long will this take?": answer key `pending_transfer`, models said `transfer_timing` (all 4 models)
- "I need to know why a money transfer is available.": answer key `pending_transfer`, models said `transfer_timing`

## 3. `card_about_to_expire <> order_physical_card`

- "I'm in China and need a new card. Please help.": answer key `card_about_to_expire`, models said `order_physical_card`
- "Where can I order a card when I am in China?": answer key `card_about_to_expire`, models said `order_physical_card`

## 4. `card_arrival <> card_delivery_estimate`

- "What is the expected delivery date for my card?": answer key `card_arrival`, models said `card_delivery_estimate` (all 4 models)
- "How long does it take to recieve my new card?": answer key `card_arrival`, models said `card_delivery_estimate` (all 4 models)

## 5. `declined_card_payment <> reverted_card_payment?`

- "Can you tell me why my card isn't letting me make purchases online? It's been 2 weeks I've been trying.": answer key `reverted_card_payment?`, models said `declined_card_payment`
- "I am not able to purchase anything online! I have been using my card on multiple sites over a period of two weeks and none of the payments have gone through. Why is this happening?": answer key `reverted_card_payment?`, models said `declined_card_payment`

## 6. `card_payment_not_recognised <> direct_debit_payment_not_recognised`

- "I saw money was taken out of my account by a seller a while back. I do not recognize the seller, but I'm pretty certain I didn't make that payment. Can you track who the seller is?": answer key `direct_debit_payment_not_recognised`, models said `card_payment_not_recognised` (all 4 models)
- "Purchases I did not make are appearing in my bank statement?": answer key `direct_debit_payment_not_recognised`, models said `card_payment_not_recognised` (all 4 models)

## 7. `card_payment_wrong_exchange_rate <> exchange_charge`

- "My client was converting their Russian ruble into UK pound currency when they noticed their bill was much too high for the exchange. What happened?": answer key `card_payment_wrong_exchange_rate`, models said `exchange_charge`
- "I believe you charged me too much to exchange my money": answer key `card_payment_wrong_exchange_rate`, models said `exchange_charge` (all 4 models)

## 8. `card_payment_wrong_exchange_rate <> exchange_rate`

- "What if there is an error on the exchange rate?": answer key `card_payment_wrong_exchange_rate`, models said `exchange_rate`
- "Why is the exchange rate different from what I expected?": answer key `card_payment_wrong_exchange_rate`, models said `exchange_rate` (all 4 models)

## 9. `declined_card_payment <> declined_transfer`

- "I tried to buy something online yesterday but it kept saying declined. Tried another time today but same thing happened. What's Broken?": answer key `declined_transfer`, models said `declined_card_payment` (all 4 models)
- "Why am I getting declines when trying to make a purchase online?": answer key `declined_transfer`, models said `declined_card_payment` (all 4 models)

## 10. `declined_transfer <> failed_transfer`

- "Hi, I am currently in the process of buying a flat and I am waiting for the mortgage to go through but it keeps showing up as an error.  Do you know what could be causing this and can you help me get the money over.": answer key `failed_transfer`, models said `declined_transfer`
- "I need to know what is going on. I'm attempting to purchase a flat and need the money to pay on my initial mortgage payment. I'm only getting an error. Can you find out what's going on and help in making the transfer?": answer key `failed_transfer`, models said `declined_transfer`

## 11. `top_up_by_bank_transfer_charge <> transfer_fee_charged`

- "is there a fee for swift transfer": answer key `top_up_by_bank_transfer_charge`, models said `transfer_fee_charged` (all 4 models)
- "How much would I be charged for a transfer?": answer key `top_up_by_bank_transfer_charge`, models said `transfer_fee_charged` (all 4 models)

## 12. `verify_my_identity <> why_verify_identity`

- "how do I speed up identity verification?": answer key `why_verify_identity`, models said `verify_my_identity` (all 4 models)
- "why do I have to show my ID": answer key `verify_my_identity`, models said `why_verify_identity` (all 4 models)

## 13. `balance_not_updated_after_bank_transfer <> transfer_timing`

- "How long does a transfer from a UK account take? I just made one and it doesn't seem to be working, wondering if everything is okay": answer key `balance_not_updated_after_bank_transfer`, models said `transfer_timing` (all 4 models)

## 14. `card_payment_fee_charged <> extra_charge_on_statement`

- "When do you charge fees on accounts? I just saw a charge on my statement.": answer key `card_payment_fee_charged`, models said `extra_charge_on_statement` (all 4 models)

## 15. `card_payment_not_recognised <> extra_charge_on_statement`

- "I looked at my statement, and there is a charge for 1£ that I don't recognize.  Why is it on there?": answer key `extra_charge_on_statement`, models said `card_payment_not_recognised`

## All 38 tuning messages where all 4 models made the same "wrong" pick

Four different models agreeing against the answer key usually means the key is wrong
or the message really fits both categories. Worth a human read.

- "why top up is not working even if I got my American Express in Apple Bay?": answer key `apple_pay_or_google_pay`, models said `top_up_failed`
- "In what increments can I top-up my card?": answer key `automatic_top_up`, models said `top_up_limits`
- "How long does a transfer from a UK account take? I just made one and it doesn't seem to be working, wondering if everything is okay": answer key `balance_not_updated_after_bank_transfer`, models said `transfer_timing`
- "Why am I unable to transfer money when I was able to before?": answer key `beneficiary_not_allowed`, models said `declined_transfer`
- "If I can't choose my card type will I be able to use it everywhere?": answer key `visa_or_mastercard`, models said `card_acceptance`
- "What is the expected delivery date for my card?": answer key `card_arrival`, models said `card_delivery_estimate`
- "How long does it take to recieve my new card?": answer key `card_arrival`, models said `card_delivery_estimate`
- "My card is not working at stores.": answer key `declined_card_payment`, models said `card_not_working`
- "Is there something wrong with my ATM Card?  Tried using it earlier and it did not work.": answer key `declined_cash_withdrawal`, models said `card_not_working`
- "Why was the price higher when I paid with my card?": answer key `card_payment_fee_charged`, models said `card_payment_wrong_exchange_rate`
- "When do you charge fees on accounts? I just saw a charge on my statement.": answer key `card_payment_fee_charged`, models said `extra_charge_on_statement`
- "Purchases I did not make are appearing in my bank statement?": answer key `direct_debit_payment_not_recognised`, models said `card_payment_not_recognised`
- "I saw money was taken out of my account by a seller a while back. I do not recognize the seller, but I'm pretty certain I didn't make that payment. Can you track who the seller is?": answer key `direct_debit_payment_not_recognised`, models said `card_payment_not_recognised`
- "I believe you charged me too much to exchange my money": answer key `card_payment_wrong_exchange_rate`, models said `exchange_charge`
- "Why is the exchange rate different from what I expected?": answer key `card_payment_wrong_exchange_rate`, models said `exchange_rate`
- "My wallet got stolen a couple hours ago and now I've seen there already is a withdrawal. Help this is absolutely urgent I don't want to loose more money": answer key `cash_withdrawal_not_recognised`, models said `lost_or_stolen_card`
- "Why am I getting declines when trying to make a purchase online?": answer key `declined_transfer`, models said `declined_card_payment`
- "I tried to buy something online yesterday but it kept saying declined. Tried another time today but same thing happened. What's Broken?": answer key `declined_transfer`, models said `declined_card_payment`
- "I tried to use my disposable virtual card to pay a subscription to the gym and it got rejected. Any ideas why?": answer key `virtual_card_not_working`, models said `declined_card_payment`
- "is there a frequent currency discount?": answer key `exchange_charge`, models said `exchange_rate`
- "what is the exchange rate when i get cash": answer key `wrong_exchange_rate_for_cash_withdrawal`, models said `exchange_rate`
- "How can I exchange to EUR?": answer key `fiat_currency_support`, models said `exchange_via_app`
- "My account seems a bit off and getting weird charges.": answer key `transaction_charged_twice`, models said `extra_charge_on_statement`
- "My payment shows that it is pending will I be charged more money?": answer key `pending_transfer`, models said `pending_card_payment`
- "I didn't receive my money earlier and it says the transaction is still in progress. Can you fix it?": answer key `pending_cash_withdrawal`, models said `pending_transfer`
- "What do I do if my top-up has not gone through?": answer key `pending_top_up`, models said `top_up_failed`
- "What is the status of my top up?": answer key `top_up_reverted`, models said `pending_top_up`
- "Transfers can take up to one day to process before departing for the beneficiary accounts. Please confirm that you've entered your account details correctly. SEPA transfers can take up to two working days, while SWIFT transfers can take up to five working days.": answer key `pending_transfer`, models said `transfer_timing`
- "It seems like I have been waiting forever for this international transfer. Why is it taking so long? C'mon, it's 2018, things happen at a click of a button. All of the account information is correct, so how long will this take?": answer key `pending_transfer`, models said `transfer_timing`
- "Am I charged for receiving money?": answer key `top_up_by_bank_transfer_charge`, models said `receiving_money`
- "What cards do you offer?": answer key `visa_or_mastercard`, models said `supported_cards_and_currencies`
- "How much would I be charged for a transfer?": answer key `top_up_by_bank_transfer_charge`, models said `transfer_fee_charged`
- "is there a fee for swift transfer": answer key `top_up_by_bank_transfer_charge`, models said `transfer_fee_charged`
- "Can I transfer using SWIFT?": answer key `top_up_by_bank_transfer_charge`, models said `transfer_into_account`
- "How long does it take for the transfer to go through?": answer key `transfer_not_received_by_recipient`, models said `transfer_timing`
- "What am i missing to verify my id?": answer key `unable_to_verify_identity`, models said `verify_my_identity`
- "how do I speed up identity verification?": answer key `why_verify_identity`, models said `verify_my_identity`
- "why do I have to show my ID": answer key `verify_my_identity`, models said `why_verify_identity`
