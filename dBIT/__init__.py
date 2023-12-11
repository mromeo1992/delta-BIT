start = "\033[1m"
end = "\033[0;0m"

line1="By using delta-BIT, you acknowledge that:\n\n"

line2=start+"IT IS NOT INTENDED FOR CLINICAL USE BUT INSTEAD PURELY ACADEMIC (RESEARCH) SOFTWARE"+end
lenght=len(line2)
n_space=12
newline=line1+line2.center(n_space*2+lenght)
print('\n')
print(newline)
print('\n\n')