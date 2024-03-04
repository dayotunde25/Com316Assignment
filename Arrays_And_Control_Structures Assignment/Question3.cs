using System;
using System.Linq;

namespace Question3;

public static class Program
{
	public static void Main(){ 
	    
	    Console.WriteLine("Enter a string: "); 
		string texts = Console.ReadLine(); 
		char[] textArray = texts.ToCharArray(); 
		for (int i = 0; i < textArray.Length; i++){ 
		    textArray[i] = Char.ToUpper(textArray[i]);
			Console.Write(textArray[i]);
		}
	    Console.ReadLine(); 
	}
}
