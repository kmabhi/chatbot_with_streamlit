// DCOM Sample: Real-world C# code using DCOM for demo conversion
// This is a simplified, but realistic, DCOM client example in .NET
using System;
using System.Runtime.InteropServices;

namespace DcomDemo
{
    class Program
    {
        [DllImport("ole32.dll")]
        static extern int CoInitializeEx(IntPtr pvReserved, int dwCoInit);
        [DllImport("ole32.dll")]
        static extern void CoUninitialize();

        static void Main(string[] args)
        {
            // Initialize COM library for multi-threaded use
            int hr = CoInitializeEx(IntPtr.Zero, 0x0);
            if (hr < 0)
            {
                Console.WriteLine("Failed to initialize COM library.");
                return;
            }

            try
            {
                // Create a remote COM object (replace CLSID and server name as needed)
                Type remoteType = Type.GetTypeFromProgID("Excel.Application", "RemoteServer");
                dynamic excelApp = Activator.CreateInstance(remoteType);
                excelApp.Visible = true;
                Console.WriteLine("Launched Excel on remote server via DCOM!");

                // Do some automation
                dynamic workbook = excelApp.Workbooks.Add();
                dynamic sheet = workbook.Sheets[1];
                sheet.Cells[1, 1].Value = "Hello from DCOM!";

                // Save and clean up
                workbook.SaveAs("C:\\Temp\\DcomDemo.xlsx");
                workbook.Close(false);
                excelApp.Quit();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
            }
            finally
            {
                CoUninitialize();
            }
        }
    }
}
