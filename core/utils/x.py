size = ""

with open("word.txt") as file:
    x = file.readlines()
    for i in x:
        for j in i:
            if j.isalnum():
                size +=j
                
print(f"size {len(size)}")