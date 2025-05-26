library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity top is
generic (word_size : integer := 8);
port(
topclk : in std_logic;
topa : in std_logic_vector(word_size-1 downto 0);
topb : in std_logic_vector(word_size-1 downto 0);
topp : out std_logic_vector(word_size-1 downto 0)
);
end top;

architecture Behavioral of top is

signal reg_in_a : std_logic_vector(word_size-1 downto 0);
signal reg_in_b : std_logic_vector(word_size-1 downto 0);

signal reg_out_p : std_logic_vector(word_size-1 downto 0);

attribute DONT_TOUCH : string;
attribute DONT_TOUCH of  add : label is "TRUE";

begin

add : entity work.adder
generic map(
    word_size => word_size
)
port map(
    a => reg_in_a,
    b => reg_in_b,

    sum => reg_out_p
);

RegProc: process(topclk) --register for the adder IO
begin
    if rising_edge(topclk) then
        reg_in_a <= topa;
        reg_in_b <= topb;

        topp <= reg_out_p;
    end if;
end process RegProc;

end Behavioral;
