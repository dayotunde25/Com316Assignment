using System;
using System.Linq;

namespace Question4;

public static class Program
{
	public static void Main()
	{
	    int rows, column; 
		Console.WriteLine("Enter the number of rows: ");
		rows = Convert.ToInt32(Console.ReadLine());
		Console.WriteLine("Enter the number of columns: ");
		column = Convert.ToInt32(Console.ReadLine());
	    double [,] matrix1 = new double[rows,column];
		double [,] matrix2 = new double[rows,column];
		// getting values for the first matrix
		    Console.WriteLine("Enter values for Matrix1");
		    for(int j=0; j<rows; j++){ 
			    for(int k=0; k<column; k++){
				    Console.WriteLine("Enter value for element"+"["+j+","+k+"]");
					matrix1[j,k] = Convert.ToDouble(Console.ReadLine());   
				}
			
			}
			// getting values for second matrix
			Console.WriteLine("Enter values for Matrix2");
		    for(int j=0; j<rows; j++){ 
			    for(int k=0; k<column; k++){
				    Console.WriteLine("Enter value for element"+"["+j+","+k+"]");
					matrix2[j,k] = Convert.ToDouble(Console.ReadLine()); 
				
				}
			
			}
			for(int j=0; j<rows; j++){ 
			    for(int k=0; k<column; k++){
				    Console.Write(matrix1[j,k] + " ");
				
				} 
				Console.WriteLine(" ");
			
			}
			
		Console.WriteLine("++"); 
		for(int j=0; j<rows; j++){ 
			    for(int k=0; k<column; k++){
				    Console.Write(matrix2[j,k] + " ");
				
				} 
				Console.WriteLine(" ");
			
			}
			Console.WriteLine("===");
	    // for the result matrix after addition 
		double [,] matrix3 = new double[rows,column];
		for(int j=0; j<rows; j++){ 
			    for(int k=0; k<column; k++){	
					matrix3[j,k] = matrix1[j,k] + matrix2[j,k];   
					Console.Write(matrix3[j,k] + " ");
				
				}
			Console.WriteLine();
		}
	Console.ReadLine();

	}
}
