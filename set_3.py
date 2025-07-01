def relationship_status(from_member, to_member, social_graph):
    from_following = social_graph[from_member]["following"]
    to_following = social_graph[to_member]["following"]

    if from_member in to_following and to_member in from_following:
        return "friends"
    elif from_member in to_following:
        return "followed by"
    elif to_member in from_following:
        return "follower"
    else:
        return "no relationship"

def tic_tac_toe(board):
    size= len(board)

    for row in board:
        if row[0] != '' and all(cell == row[0] for cell in row):
            return row[0]
    
    for col in range(size):
        first_col = board[0][col]
        if first_col != '' and all(board[row][col] == first_col for row in range(size)):
            return first_col

    first_diag = board[0][0]
    if first_diag != '' and all(board[i][i] == first_diag for i in range(size)):
        return first_diag

    anti_diag = board[0][size - 1]
    if anti_diag != '' and all(board[i][size-1-i] == anti_diag for i in range(size)):
        return anti_diag

    return "NO WINNER"

def eta(first_stop, second_stop, route_map):
    time = 0
    current_stop = first_stop
  
    while current_stop != second_stop:
        for (start, end), travel_time in route_map.items():
            if start == current_stop:
                time += travel_time['travel_time_mins']
                current_stop = end
                break
    return time

