from collections import defaultdict

def data_load(filename):
    usernum = 0
    itemnum = 0
    User = defaultdict(list)
    user_train = {}
    user_valid = {}
    user_test = {}
    # assume user/item index starting from 1
    with open(filename, 'r', encoding="utf-8") as file:
        for line in file:
            user_id, movie_id, rating, timestamp = map(int, line.strip().split("::"))
            usernum = max(user_id, usernum)
            itemnum = max(movie_id, itemnum)
            if rating > 2:
                User[user_id].append((timestamp, movie_id))
    
    User = {user: items for user, items in User.items() if len(items) >= 5}
    # sort by timestamp
    for user in User:
        User[user].sort()
        User[user] = [movie_id for _, movie_id in User[user]]

    max_len = 20
    for user in User:
        full_seq = User[user]
        split_1 = int(len(full_seq) * 0.7)
        split_2 = int(len(full_seq) * 0.85)
        train_seq = full_seq[:split_1]
        valid_seq = full_seq[split_1:split_2]
        test_seq = full_seq[split_2:]

        if len(train_seq) < max_len:
            train_seq = [0] * (max_len - len(train_seq)) + train_seq
        else:
            train_seq = train_seq[-max_len:]

        if len(valid_seq) < max_len:
            valid_seq = [0] * (max_len - len(valid_seq)) + valid_seq
        else:
            valid_seq = valid_seq[-max_len:]

        if len(test_seq) < max_len:
            test_seq = [0] * (max_len - len(test_seq)) + test_seq
        else:
            test_seq = test_seq[-max_len:]

        user_train[user] = train_seq
        user_valid[user] = valid_seq
        user_test[user] = test_seq
    return user_train, user_valid, user_test, usernum, itemnum


def main():
    user_train, user_valid, user_test, usernum, itemnum = data_load('ratings.dat')
    # print(user_test)


main()
