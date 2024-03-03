using System;
using System.Linq;

namespace Question6;

public static class Program
{
	public static void Main()
	{
		/* Write a C# program that prompts 
		the user to input a number. 
		The program should then output 
		the number and a message saying 
		wether the number is positive, 
		negative ,or zero. */
		try
		{
			double numarv;
			Console.WriteLine("Enter a number to check");
			numarv = Convert.ToDouble(Console.ReadLine());
			if (numarv > 0)
				Console.WriteLine("The number " + numarv + " is Positive");
			else if (numarv < 0)
				Console.WriteLine("The number " + numarv + " is Negative");
			else
				Console.WriteLine("Th number " + numarv + " is Zero");
		}
		catch (Exception e)
		{
			Console.WriteLine("Error, You did not enter a number, try again");
		}
		Console.ReadLine();
	}
}
