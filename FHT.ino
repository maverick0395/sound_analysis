// FHT, http://wiki.openmusiclabs.com/wiki/ArduinoFHT
#define LOG_OUT 1 // use the log output function
#define LIN_OUT8 1 // use the linear byte output function
#define FHT_N 256 // set to 256 point fht
#include <FHT.h> // include the library


double vReal[FHT_N];
double vImag[FHT_N];

// pins
#define MicPin A0 // used with analogRead mode only

// consts
#define AmpMax (1024 / 2)
#define MicSamples (1024*2) // Three of these time-weightings have been internationally standardised, 'S' (1 s) originally called Slow, 'F' (125 ms) originally called Fast and 'I' (35 ms) originally called Impulse.

// modes
#define ADCFlow // read data from adc with free-run (not interupt). much better data, dc low. hardcoded for A0.

#define FreqLog // use log scale for FHT frequencies
#ifdef FreqLog
#define FreqOutData fht_log_out
#define FreqGainFactorBits 0
#else
#define FreqOutData fht_lin_out8
#define FreqGainFactorBits 3
#endif
//#define FreqSerialBinary //Use this line for Processing visualising

#define VolumeGainFactorBits 0


//
#define cbi(sfr, bit) (_SFR_BYTE(sfr) &= ~_BV(bit))
#define sbi(sfr, bit) (_SFR_BYTE(sfr) |= _BV(bit))

bool flag = false;
unsigned long ID_counter = 1;

void setup()
{
  //pinMode(MicPin, INPUT); // relevant for digital pins. not relevant for analog. however, don't put into digital OUTPUT mode if going to read analog values.
//TIMSK0 = 0;
#ifdef ADCFlow
  // set the adc to free running mode
  // register explanation: http://maxembedded.com/2011/06/the-adc-of-the-avr/
  // 5 => div 32. sample rate 38.4
  // 7 => switch to divider=128, default 9.6khz sampling
  ADCSRA = 0xe0+7; // "ADC Enable", "ADC Start Conversion", "ADC Auto Trigger Enable" and divider.
  ADMUX = 0x0; // use adc0 (hardcoded, doesn't use MicPin). Use ARef pin for analog reference (same as analogReference(EXTERNAL)).
#ifndef Use3.3
  ADMUX |= 0x40; // Use Vcc for analog reference.
#endif
  DIDR0 = 0x01; // turn off the digital input for adc0
#else
#ifdef Use3.3
  analogReference(EXTERNAL); // 3.3V to AREF
#endif
#endif

#ifdef ADCReClock // change ADC freq divider. default is div 128 9.6khz (bits 111)
  // http://yaab-arduino.blogspot.co.il/2015/02/fast-sampling-from-analog-input.html
  // 1 0 0 = mode 4 = divider 16 = 76.8khz
  //sbi(ADCSRA, ADPS2);
  //cbi(ADCSRA, ADPS1);
  //cbi(ADCSRA, ADPS0);
  // 1 0 1 = mode 5 = divider 32 = 38.4Khz
  //sbi(ADCSRA, ADPS2);
  //cbi(ADCSRA, ADPS1);
  //sbi(ADCSRA, ADPS0);
#endif

  // serial
  Serial.begin(115200);
  
}

void loop()
{
  if (Serial.available() > 0 || flag == true ) {
    while (flag == false) {
      String rasp_command = Serial.readStringUntil('\n');
      if (rasp_command != "start\r" && rasp_command != "stop\r") {
        Serial.println("Confirm " + rasp_command);
      }
      if (rasp_command == "start\r") {
        flag = true;
        ID_counter = 1;
      }
    }

    MeasureFHT();
    
    if (Serial.available() > 0) {
      String rasp_command = Serial.readStringUntil('\n');
      if ( rasp_command == "stop\r" || rasp_command == "Communication check\r") {
        flag = false;
        
      }
    }
    
    
  }
}

// calculate frequencies in the signal and print to serial
void MeasureFHT()
{
  long t0 = micros();
#ifdef ADCFlow
  //cli();  // UDRE interrupt slows this way down on arduino1.0
#endif
  for (int i = 0; i < FHT_N; i++) { // save 256 samples
#ifdef ADCFlow
    while (!(ADCSRA & _BV(ADIF))); // wait for adc to be ready (ADIF)
    sbi(ADCSRA, ADIF); // restart adc
    byte m = ADCL; // fetch adc data
    byte j = ADCH;
    int k = ((int)j << 8) | m; // form into an int
#else
    int k = analogRead(MicPin);
#endif
    k -= 0x0200; // form into a signed int
    k <<= 6; // form into a 16b signed int
    k <<= FreqGainFactorBits;
    
    fht_input[i] = k; // put real data into bins
    //vReal[i] = k;
    //vImag[i] = 0;
  }
#ifdef ADCFlow
  //sei();
#endif
  long dt = micros() - t0;
  
  fht_window(); // window the data for better frequency response
  fht_reorder(); // reorder the data before doing the fht
  fht_run(); // process the data in the fht
#ifdef FreqLog
  fht_mag_log();
#else
  fht_mag_lin8(); // take the output of the fht
#endif

#ifdef FreqSerialBinary
  // print as binary
  Serial.write(255); // send a start byte
  Serial.write(FreqOutData, FHT_N / 2); // send out the data
#else
  // print as text
  
  for (int i = 0; i < FHT_N / 2; i++)
  { 
    Serial.print(ID_counter);
    Serial.print(';');
    Serial.print(i);
    Serial.print(';');
    Serial.println(FreqOutData[i]);
    if (ID_counter == 4294967295) {
      ID_counter = 1;
    } 
    else {
      ID_counter +=1;
    }
    
    //Serial.println(vReal[i]);
    //Serial.print(',');
  }
  long sample_rate = FHT_N * 1000000l / dt;
  //Serial.println(dt);
  //Serial.print(',');
  //Serial.println(sample_rate);
#endif
}
