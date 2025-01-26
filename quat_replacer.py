with open('snapshot.txt', 'r') as f:
    snapshot = f.read()
    snapshot = snapshot.replace('&quot', '"')  # Assign the result back to snapshot
    with open('snapshot2.txt', 'w') as f:
        f.write(snapshot)
