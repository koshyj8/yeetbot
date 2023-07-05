def push(stack,element,limit=None):
    if len(stack)!=limit:
        stack.append(element)
    else:
        return "Overflow"
def pop(stack):
    if len(stack)!=0:
        return stack.pop()
    return "Underflow"
input_string = input("Enter a string: ")
string_list = []
output_string = ""
for i in input_string:
    push(string_list,i)
for i in range(len(input_string)):
    output_string = output_string + pop(string_list)
print(output_string)