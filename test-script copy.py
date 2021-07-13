d = {1: "a", 2: "b"}

for i in range(4):
    try:
        x = d[i]
        print("iteration: " + str(i))
        continue
        print(x)
    except KeyError:
        print("key wasn't not found in dictionary")