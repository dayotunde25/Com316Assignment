using System;
using System.Collections.Generic;
using System.IO;
namespace Solution{
    class Solution { 
	    static void Main(String[] args) { 
		    int i = 4; 
			double d = 4.0; 
			string s = "Polyilaro ";
			int zee;
			double cor;
			string texting;

			zee = Convert.ToInt32(Console.ReadLine());
		
			cor = Convert.ToDouble(Console.ReadLine());
	
			texting = Console.ReadLine();
			Console.WriteLine(i + zee);
			Console.WriteLine(string.Format("{0:0.00}", (d + cor)));
			Console.WriteLine(s + texting);
		}
	}
}
