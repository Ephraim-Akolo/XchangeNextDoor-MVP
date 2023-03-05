import numpy as np

def get_payment_account(amount:float, accounts:list[tuple] = [(str(i), i*100.0) for i in range(10)]):
    _ = np.array(accounts)
    addresses, balances = _[:, 0], _[:, 1].astype(np.float64)
    addr_amount, l = [], [i for i in range(np.size(balances))]
    if amount > balances.sum():
        return
    while True:
        arg =np.abs(balances[l]-amount).argmin()
        rem = balances[arg] - amount
        if rem < 0:
            addr_amount.append((str(addresses[arg]), float(balances[arg])))
            amount -= balances[arg]
            l.pop(arg)
        else:
            addr_amount.append((str(addresses[arg]), float(amount)))
            break
    return addr_amount


# def get_payment_account(amount:float, accounts:list[tuple] = [(str(i), i*100.0) for i in range(10)]):
#     total_balance = sum(acct[1] for acct in accounts)
#     if amount > total_balance:
#         return 
#     accounts_sorted = sorted(accounts, key=lambda x:x[1], reverse=True)
#     paid_accounts = []
#     for acct in accounts_sorted:
#         if acct[1] == amount:
#             paid_accounts.append(acct)
#             return paid_accounts
#         elif acct[1] > amount:
#             paid_accounts.append((acct[0], amount))
#             return paid_accounts
#         else:
#             paid_accounts.append(acct)
#             amount -= acct[1]
#     return paid_accounts


print(get_payment_account(1790))
