#define LEN 256

volatile int collecting = 0;
volatile int numSamples=0;
unsigned long t;
unsigned long t0;
int as[LEN];
unsigned long ts[LEN];

void setup() {
  Serial.begin(9600);

  ADCSRA = 0;             // clear ADCSRA register
  ADCSRB = 0;             // clear ADCSRB register
  ADMUX |= (0 & 0x07);    // set A0 analog input pin
  ADMUX |= (1 << REFS0);  // set reference voltage
  ADMUX |= (0 << ADLAR);  // left align ADC value to 8 bits from ADCH register

  // sampling rate is [ADC clock] / [prescaler] / [conversion clock cycles]
  // for Arduino Uno ADC clock is 16 MHz and a conversion takes 13 clock cycles
  //ADCSRA |= (1 << ADPS2) | (1 << ADPS0);    // 32 prescaler for 38.5 KHz
  ADCSRA |= (1 << ADPS2);                     // 16 prescaler for 76.9 KHz
  //ADCSRA |= (1 << ADPS1) | (1 << ADPS0);    // 8 prescaler for 153.8 KHz

  ADCSRA |= (1 << ADATE); // enable auto trigger
  ADCSRA |= (1 << ADIE);  // enable interrupts when measurement complete
  ADCSRA |= (1 << ADEN);  // enable ADC
  ADCSRA |= (1 << ADSC);  // start ADC measurements
}

ISR(ADC_vect) {
  if(collecting && numSamples<LEN) {
    as[numSamples] = ADCL | ADCH<<8;
    ts[numSamples] = (micros()-t0);///1000000.0;
    numSamples++;
  }
}

void loop() {
  // unless collecting, or there is a byte of value 254 in the input stream, do nothing
  //if(!(collecting || (Serial.available() > 0 && Serial.read() == 254))) return;
  if(!(collecting || (Serial.available() > 0))) return;
  if(!collecting) {
    Serial.flush();
    while(Serial.available() > 0) Serial.print(Serial.read());
    t0 = micros(); // Inititalize t0 at the beginning of the collection time interval
  }
  collecting = 1;
  
  if (numSamples>LEN-1) {
    noInterrupts();
    t = micros()-t0;  // calculate elapsed time

    Serial.println("%");
    for(int i = 0; i < LEN; i++) {
      if(as[i] < 600 && as[i] > -600) {
        Serial.print("#");
        Serial.print(ts[i]/1000000.0, 6);
        Serial.print(" ");
        Serial.println(as[i]);
      }
    }
    Serial.println("$");
    
    // restart
    numSamples = 0;
    collecting = 0;
    interrupts();
  }
}

