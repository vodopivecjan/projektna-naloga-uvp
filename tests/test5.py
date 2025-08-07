my_list = [{"name": "Alice"}, {"name": "Bob"}]

for i, item in enumerate(my_list):
    update = {"test1": True}    
    # if item["name"] == "Alice":
    item.update(update)

print(my_list)


# l = [1, 2]

# for i, item in enumerate(l):
#     if i > 20:
#         break
#     l.append(item)


# print(l)
