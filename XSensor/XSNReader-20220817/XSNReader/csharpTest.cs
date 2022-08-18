using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using xsensor;

namespace XSNReaderCS
{
    class Program
    {
        static void Main(string[] args)
        {
            XSN xs = new XSN();

            XSN.XSN_InitLibrary();

            if (XSN.XSN_LoadSessionU("d:\\MyTestSession.xsn"))
            {
                byte nbrPads = XSN.XSN_PadCount();
                uint nbrFrames = XSN.XSN_FrameCount();

                // we'll fetch the first frame
                if (nbrFrames > 0)
                {
                    // fetch the pressure map for each pad
                    // - probably want to allocate each pads memory once and store elsewhere

                    // Step to the frame we want to see
                    // frames are 1-indexed
                    if (XSN.XSN_StepToFrame(1))
                    {
                        // Fetch the current pressure units
                        EXSNPressureUnit eCurrentUnits = XSN.XSN_GetPressureUnits();

                        // change units to something we want
                        if (eCurrentUnits != EXSNPressureUnit.eXSNPRESUNIT_NCM2)
                        {
                            XSN.XSN_SetPressureUnits(EXSNPressureUnit.eXSNPRESUNIT_NCM2);
                        }

                        string sModel, sProductID, sSerial;

                        // pads are 0-indexed
                        for (byte pad = 0; pad < nbrPads; pad++)
                        {
                            ushort rows = XSN.XSN_Rows(pad);
                            ushort columns = XSN.XSN_Columns(pad);

                            XSN.XSN_GetPadInfo(pad, out sModel, out sProductID, out sSerial);

                            string sDetails;
                            sDetails = sModel + " " + sProductID + " " + sSerial;

                            Console.WriteLine("\n Pad[{0}] has {1} rows x {2} columns", sDetails, rows.ToString(), columns.ToString());

                            uint dataSize = (uint)(rows * columns);

                            float[] pressureMap = new float[dataSize];

                            if (XSN.XSN_GetPressure(pad, dataSize, pressureMap))
                            {
                                // display the data
                                for (ushort row = 0; row < rows; row++)
                                {
                                    for (ushort column = 0; column < columns; column++)
                                    {
                                        float pressure = pressureMap[(uint)row * (uint)columns + (uint)column];
                                        Console.Write(pressure.ToString() + "\t");
                                    }
                                    Console.WriteLine("");
                                }
                            }
                            else
                            {
                                Console.WriteLine("\n... failed. Error: {0}", XSN.XSN_GetLastErrorCode().ToString());
                            }
                        }
                    }
                    else
                    {
                        Console.WriteLine("\n... failed. Error: {0}", XSN.XSN_GetLastErrorCode().ToString());
                    }
                }

                XSN.XSN_CloseSession();
            }
            else
            {
                Console.WriteLine("\n... failed. Error: {0}", XSN.XSN_GetLastErrorCode().ToString());
            }


            XSN.XSN_ExitLibrary();



            // The code provided will print ‘Hello World’ to the console.
            // Press Ctrl+F5 (or go to Debug > Start Without Debugging) to run your app.
            Console.WriteLine("Press any key to exit...");
            Console.ReadKey();

            // Go to http://aka.ms/dotnet-get-started-console to continue learning how to build a console app! 
        }
    }
}
