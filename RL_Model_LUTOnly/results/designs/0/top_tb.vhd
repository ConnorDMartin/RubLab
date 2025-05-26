library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
use IEEE.NUMERIC_STD.ALL;

use IEEE.MATH_REAL.ALL;
use STD.TEXTIO.ALL;
use IEEE.STD_LOGIC_TEXTIO.ALL;

entity top_tb is
end top_tb;

architecture Behavioral of top_tb is
constant word_size : integer := 8; --width

signal clock : std_logic := '0';
signal reset: std_logic := '0';

signal a : std_logic_vector(word_size-1 downto 0) := '1' & (word_size-2 downto 0 => '0'); --width
signal b : std_logic_vector(word_size-1 downto 0) := '1' & (word_size-2 downto 0 => '0'); --height

signal p : std_logic_vector(word_size-1 downto 0);

signal acc_p, acc_p_reg : std_logic_vector(word_size-1 downto 0);
signal a1, a2 : std_logic_vector(word_size-1 downto 0) := (others => '0');
signal b1, b2 : std_logic_vector(word_size-1 downto 0) := (others => '0');
signal running : std_logic := '1';


constant clk_period : time := 4.366 ns;

component top is
   --width and heigth of the multiplier
  port(
  topclk : in std_logic;
  topa : in std_logic_vector(word_size-1 downto 0);
  topb : in std_logic_vector(word_size-1 downto 0);

  topp : out std_logic_vector(word_size-1 downto 0)
  );
end component;

  begin

  clock <= clock xor running after clk_period;

  DUT : top

  port map(
  topclk => clock,
  topa => a,
  topb => b,

  topp => p
  );


  Stimuli : process

  file file_results : text;


  variable file_oline : line;


   file file_input1, file_input2 : text;
   variable file_iline1, file_iline2: line;
   variable input_a : integer;
   variable input_b : integer;
  begin

    wait for clk_period * 199;


    file_open(file_results, "add_results_0.csv", write_mode);

    write(file_oline, string'("a,b,acc,approx"));
    writeline(file_results, file_oline);




    file_open(file_input1, "tb_in_a0.txt", read_mode);
    for i in 0 to 255 loop
      readline (file_input1, file_iline1);
      read(file_iline1, input_a);
      a <= std_logic_vector(to_signed(input_a, a'length));

     file_open(file_input2, "tb_in_b0.txt", read_mode);
      for j in 0 to 255 loop
        readline (file_input2, file_iline2);
        read(file_iline2, input_b);
        b <= std_logic_vector(to_signed(input_b, b'length));

       wait until rising_edge(clock);
       wait until rising_edge(clock);

        a1 <= a;
        b1 <= b;



       acc_p <= std_logic_vector(signed(a) + signed(b));

       wait until rising_edge(clock);


       write(file_oline, integer'image(to_integer(signed(a1))));
       write(file_oline, string'(", "));
       write(file_oline, integer'image(to_integer(signed(b1))));
       write(file_oline, string'(", "));
       write(file_oline, integer'image(to_integer(signed(acc_p))));
       write(file_oline, string'(", "));
       write(file_oline, integer'image(to_integer(signed(p))));
       writeline(file_results, file_oline);

      end loop;
        file_close(file_input2);
    end loop;
    file_close(file_input1);

    wait for clk_period * 6;




    file_close(file_results);

     running <= '0';
     wait;
end process;

end Behavioral;
