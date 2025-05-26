# # Get lookup table value from user
# lut_value = int(input("Enter 64-bit lookup table value in hex: "), 16)
#
# # Split into two 32-bit values
# lut2_val = lut_value >> 32
# lut1_val = lut_value & 0xFFFFFFFF
#
# print('lut1: ', hex(lut1_val))
# print('lut2: ', hex(lut2_val))
#
# # Convert to list of bits
# lut1 = [(lut1_val >> i) & 1 for i in range(32)]
# lut2 = [(lut2_val >> i) & 1 for i in range(32)]
#
#
# print('lut1: ', lut1)
# print('lut2: ', lut2)
#
#
# # Get input bits
# a = int(input("Enter input bit A: "))
# b = int(input("Enter input bit B: "))
# c = int(input("Enter input bit C: "))
# d = int(input("Enter input bit D: "))
# e = int(input("Enter input bit E: "))
# f = int(input("Enter input bit F: "))
#
# # Calculate index
# # index = a*16 + b*8 + c*4 + d*2 + e
# index = e*16 + d*8 + c*4 + b*2 + a
# print('index: ', index)
#
# # Lookup output bits
# o5 = lut1[index]
# if f == 0:
#   o6 = o5
# else:
#   o6 = lut2[index]
#
# # Print output
# print("O5:", o5)
# print("O6:", o6)


class LUT:

  bit_valid = 'E'
  cin = 0
  cout = 0
  sum = 0
  o5 = 0
  o6 = 0


  def __init__(self, lut_value):
    # Initialize lookup tables
    self.lut2_val = lut_value >> 32
    self.lut1_val = lut_value & 0xFFFFFFFF
    self.lut1 = [(self.lut1_val >> i) & 1 for i in range(32)]
    self.lut2 = [(self.lut2_val >> i) & 1 for i in range(32)]


  def lookup(self):

    self.index = self.e*16 + self.d*8 + self.c*4 + self.b*2 + self.a


    self.o5 = self.lut1[self.index]
    if self.f == 0:
      self.o6 = self.o5
    else:
      self.o6 = self.lut2[self.index]


  def get_lut_outputs(self, a, b, c, d, e, f):

    self.a, self.b, self.c, self.d, self.e, self.f = a, b, c, d, e, f
    # print("bit valid: " + str(self.bit_valid))

    if self.bit_valid == 'E':


      self.lookup()

    else:
      self.o5 = 0
      self.o6 = 0

  def get_sum_carry(self, cin):
    self.cin = cin

    # print("Cin: "+str(self.cin))

    if self.bit_valid == 'E':

      if self.o6 == 1:
        self.cout = self.cin
        # print("06 = 1: "+str(self.cout))
      else:
        self.cout = self.o5
        # print("06 = 0: "+str(self.cout))
      self.sum = self.o6 ^ self.cin
      # print("sum: "+str(self.sum))


    elif self.bit_valid == 'Z':
      self.sum = 0
      self.cout = self.cin

    elif self.bit_valid == 'O':
      self.sum = 1
      self.cout = self.cin

  def set_valid(self, valid):
    self.bit_valid = valid



#lut = LUT(0x6666666688888888)

#lut.set_valid('E')

#lut.get_lut_outputs(1, 1, 1, 0, 1, 1, 1)
#print('O5: ', lut.o5)
#print('O6: ', lut.o6)

#lut.get_sum_carry(0)
#print('sum: ', lut.sum)
#print('cout: ', lut.cout)

#print('carry 1')

#lut.get_sum_carry(1)
#print('sum: ', lut.sum)
#print('cout: ', lut.cout)

#print('Z')
#lut.set_valid('Z')
#lut.get_sum_carry(0)
#print('O5: ', lut.o5)
#print('O6: ', lut.o6)
#print('sum: ', lut.sum)
#print('cout: ', lut.cout)

#print('Z')
#lut.set_valid('Z')
#lut.get_sum_carry(1)
#print('O5: ', lut.o5)
#print('O6: ', lut.o6)
#print('sum: ', lut.sum)
#print('cout: ', lut.cout)


#print('O')
#lut.set_valid('O')
#lut.get_sum_carry(0)
#print('O5: ', lut.o5)
#print('O6: ', lut.o6)
#print('sum: ', lut.sum)
#print('cout: ', lut.cout)

#lut.get_sum_carry(1)
#print('O5: ', lut.o5)
#print('O6: ', lut.o6)
#print('sum: ', lut.sum)
#print('cout: ', lut.cout)
