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
print('delta-BIT is a progragram for tractography prediction\n')
print('Copyright (C) 2023,  University of Palermo, department of Physics and Chemistry, Palermo, Italy and National Institue of Nuclear Physics (INFN), Italy\n')


print('This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.\n')

print('This program is distributed WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.\n')

print('You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.\n\n')
