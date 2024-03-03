using System;
using System.Linq;

namespace Question5;

public static class Program
{
	public static void Main()
	{
		// Declare the array alpha and set its size to 50.
		float[] alpha = new float[50];
		// Loop through the elements of the array and initialize.
		for (int i = 0; i < 50; i++)
		{
			if (i < 25)
				alpha[i] = i * i;
			else
				alpha[i] = i * 3;
		}
		// Output the array in 10 elements per line.
		int k = 1;
		for (int i = 0; i < alpha.Length; i++)
		{
			Console.Write(alpha[i] + "  ");
			if (k == 10)
			{
				Console.WriteLine();
				k = 0;
			}
			k++;
		}
		Console.ReadLine();
	}
}
