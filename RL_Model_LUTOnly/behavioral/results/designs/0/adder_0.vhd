-- Scripted code by salim.ullah@tu-dresden.de-- Receives 3 values E O Z for every location 
-- MSB is accurate
library IEEE; 
use IEEE.STD_LOGIC_1164.ALL; 
use IEEE.NUMERIC_STD.ALL; 
use IEEE.STD_LOGIC_SIGNED.ALL; 
library UNISIM; 
use UNISIM.VComponents.all; 

entity adder is 
generic (word_size: integer:=8); 
Port ( 
a : in  STD_LOGIC_VECTOR (word_size-1 downto 0); 
b : in  STD_LOGIC_VECTOR (word_size-1 downto 0); 
sum: out STD_LOGIC_VECTOR (word_size-1 downto 0)); 
end adder; 

architecture Behavioral of adder is 

constant slice_size :integer := ((word_size + 4 - 1)/4)*4; 
signal prop, gen: std_logic_vector(slice_size-1 downto 0); 
signal carries: std_logic_vector(slice_size-1 downto 0); 
signal output: std_logic_vector(slice_size-1 downto 0); 
signal input_carry: std_logic_vector(word_size-1 downto 0); 

begin 
 
 input_carry(0) <= '0'; 
lut_inst_0: lut6_2 

 generic map(INIT => X"x6666666688888888") 
port map( 
I0 => a(0),  
I1 => b(0),  
I2 => '0',  
I3 => '0',  
I4 => '0',  
I5 => '1',  
O5 => gen(0), 
O6 => prop(0) 
); 
lut_inst_1: lut6_2 

 generic map(INIT => X"x6666666688888888") 
port map( 
I0 => a(1),  
I1 => b(1),  
I2 => '0',  
I3 => '0',  
I4 => '0',  
I5 => '1',  
O5 => gen(1), 
O6 => prop(1) 
); 
lut_inst_2: lut6_2 

 generic map(INIT => X"x6666666688888888") 
port map( 
I0 => a(2),  
I1 => b(2),  
I2 => '0',  
I3 => '0',  
I4 => '0',  
I5 => '1',  
O5 => gen(2), 
O6 => prop(2) 
); 
lut_inst_3: lut6_2 

 generic map(INIT => X"x6666666688888888") 
port map( 
I0 => a(3),  
I1 => b(3),  
I2 => '0',  
I3 => '0',  
I4 => '0',  
I5 => '1',  
O5 => gen(3), 
O6 => prop(3) 
); 
lut_inst_4: lut6_2 

 generic map(INIT => X"x6666666688888888") 
port map( 
I0 => a(0),  
I1 => b(0),  
I2 => '0',  
I3 => '0',  
I4 => '0',  
I5 => '1',  
O5 => gen(4), 
O6 => prop(4) 
); 
lut_inst_5: lut6_2 

 generic map(INIT => X"x6666666688888888") 
port map( 
I0 => a(0),  
I1 => b(0),  
I2 => '0',  
I3 => '0',  
I4 => '0',  
I5 => '1',  
O5 => gen(5), 
O6 => prop(5) 
); 
lut_inst_6: lut6_2 

 generic map(INIT => X"x6666666688888888") 
port map( 
I0 => a(0),  
I1 => b(0),  
I2 => '0',  
I3 => '0',  
I4 => '0',  
I5 => '1',  
O5 => gen(6), 
O6 => prop(6) 
); 
lut_inst_7: lut6_2 

 generic map(INIT => X"x6666666688888888") 
port map( 
I0 => a(0),  
I1 => b(0),  
I2 => '0',  
I3 => '0',  
I4 => '0',  
I5 => '1',  
O5 => gen(7), 
O6 => prop(7) 
); 
prop_gen_assign: 
if slice_size > word_size generate 
slice_check: 
for i in (slice_size-1) to word_size generate 
gen(i) <= '0'; 
prop(i) <= '0'; 
 end generate slice_check; 
end generate prop_gen_assign; 

carry_chain: 
for k in 0 to (slice_size/4 - 1) generate 
carry_inst0: CARRY4 
port map ( 
DI => gen(k*4+3 downto k*4), 
S => prop(k*4+3 downto k*4), 
O => output(k*4+3 downto k*4), 
CO => carries(k*4+3 downto k*4), 
CI => input_carry(k), 
CYINIT => '0' 
); 
input_carry(k+1) <= carries(k*4+3); 
end generate carry_chain; 
sum(0) <= '1';
sum(1) <= '1';
sum(2) <= '1';
sum(3) <= '1';
sum(4) <= '1';
sum(5) <= '1';
sum(6) <= '1';
sum(7) <= '1';
end Behavioral; 
