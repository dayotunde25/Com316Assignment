using System;
using System.Linq;

namespace Question1;

public static class Program
{
	public static void Main()
	{
		/*Write a C# program 
		that prompt the user to 
		input three numbers.
		The program should then 
		output the numbers in 
		ascending order. */
		double[] collar = new double[3];
		for (int i = 0; i < collar.Length; i++)
		{
			Console.WriteLine("Enter Number" + (i + 1));
			collar[i] = Convert.ToDouble(Console.ReadLine());
		}
		Array.Sort(collar);
		for (int i = 0; i < collar.Length; i++)
		{
			Console.Write(collar[i] + " ");
		}
		Console.ReadLine();

	}
}
