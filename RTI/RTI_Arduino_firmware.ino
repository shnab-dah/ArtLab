/*
RTI v1.0
Code for LED and Camera control for RTI Dome. 
Cycles through a 8x8 LED matrix - no use of a matrix driver.
Includes a UVF-photograph function
Controlled through serial protocol (see below).


wiring rows: 	0 -> p9, 1-> p8, 2 -> p7, 3 -> p6, 4 -> p5, 
				5 -> p4, 6 -> p3, 7 -> p2.
wiring columns: 0 -> p10, 1-> p11, 2 -> p12, 3 -> p13, 4 -> p16, 
				5 -> p17, 6 -> p18, 7 -> p19

camera control pin: 	P14
UV-LEDs in series:		P15

Changelog:
	-
    
Sjors H. Nab, 19/06/2024


Serial protocol:
Baud rate: 9600

Commands:
<0> Turn off all LEDs
<1> Turn on white LEDs (automatically turns of UV LEDs)
<2> Turn on UV LEDs (automatically turns off white LEDs)
<3,$LED_NUMBER> Turns on a specified single LED
<4,$EXPOSURE_TIME> UVF Photograph (exposure time in MS)
<5,$EXPOSURE_TIME> RTI Capture (exposure time in MS)
<6> Trigger shutter manually
*/


// pins
const int cameraCtrl = 14;
const int uvLeds = 13;
const int row[8]{9, 8, 7, 6, 5, 4, 3, 2};
const int col[8]{10,11,12,15,16,17,18,19};

// variables
const int cameraProc = 500; // Time delay for camera processing in ms

//variables for serial protocol
const byte numChars = 32;
char receivedData[numChars];
char tempData[numChars];
int functionCalled = 0;
int int1Data = 0;
int int2Data = 0;
int int3Data = 0;
int int4Data = 0;
boolean newData = false;


// Setup code
void setup()
{
  // defining pin modes
  pinMode(cameraCtrl, OUTPUT);
  pinMode(uvLeds, OUTPUT);
  // set matrix pins
  for(int thisPin = 0; thisPin < 8; thisPin++){
  	pinMode(col[thisPin], OUTPUT);
    pinMode(row[thisPin], OUTPUT);
    digitalWrite(row[thisPin], HIGH);
  }
  Serial.begin(9600); // initiate serial connection
  lightsOn();

  // send instructions
  Serial.println("===================");
  Serial.println("RTI-Dome intialized");
  Serial.println("Software Version: 1.0");
  Serial.println("===================");
  Serial.println("Commands:");
  Serial.println("<0> All lights off");
  Serial.println("<1> White LEDs on");
  Serial.println("<2> UV LEDs on");
  Serial.println("<3,$LED_NUMBER> single LED");
  Serial.println("<4,$EXPOSURE_TIME> UVF photo - exposure time in MS");
  Serial.println("<5,$EXPOSURE_TIME> RTI capture - exposure time in MS");
  Serial.println("<6> Single photo");
  Serial.println("===================");
}


// Main loop
void loop()
{
  recvData();
  if (newData == true){
    strcpy(tempData, receivedData);
    parseData();
    callFunction();
    newData=false;
  }
}


// lights on
void lightsOn(){
  uvOff();
  for (int x=0; x<8; x++){
    digitalWrite(col[x], HIGH);
    digitalWrite(row[x], LOW);
  }
  Serial.println("<All lights turned on.>");
}


// lights off
void lightsOff(){
  uvOff();
  for(int x=0; x < 8; x++){
    digitalWrite(col[x], LOW);
    digitalWrite(row[x], HIGH);
  }
  Serial.println("<All lights turned off.>");
}


// UV on
void uvOn(){
  lightsOff();
  digitalWrite(uvLeds, HIGH);
  Serial.println("<UV Turned on.>");
}


// UV off
void uvOff(){
  digitalWrite(uvLeds, LOW);
  Serial.println("<UV Turned off.>");
}


// single LED
// provide LED number
void singleLED (int LED){
  lightsOff(); // turn of leds
  int y = LED / 8;
  int x = LED % 8;
  digitalWrite(col[x], HIGH);
  digitalWrite(row[y], LOW);
  Serial.print("<Single LED turned on, number: ");
  Serial.print(LED);
  Serial.print(", row: ");
  Serial.print(y);
  Serial.print(", column: ");
  Serial.print(x);
  Serial.println('>');
}


//camera shutter
void shutter(){
  digitalWrite(cameraCtrl, HIGH);
  // time to register ctrl -> TEST
  delay(50);
  digitalWrite(cameraCtrl, LOW);
  delay(cameraProc); // pre-delay camera processing
  Serial.println("<Shutter triggered.>");
}


// UVF photograph
void uvPhoto(int exposureTime){
  Serial.println("===================");
  Serial.println("<Initialising UVF photograph>");
  lightsOff(); // turn off LEDs
  uvOn();   // turn on UV LEDs
  shutter(); // trigger camera
  delay(exposureTime); // wait exposure time
  uvOff(); // turn off UV LEDs
  lightsOn(); // turn on LEDs
  Serial.println("<UVF Photograph taken>");
  Serial.println("===================");
}


// RTI capture
// exposure time = time between each capture in MS
void rti(int exposureTime) {
  int expectedDuration = exposureTime/1000*63;
  expectedDuration = expectedDuration +  + cameraProc*63/1000;
  lightsOff();  // Ensure all LEDs are off initially
  Serial.println("===================");
  Serial.println("<RTI Capture Initialised>"); 
  Serial.print("<Time to completion: ");
  Serial.print(expectedDuration/60);
  Serial.print(" minutes and ");
  Serial.print(expectedDuration%60);
  Serial.println(" seconds>");
  for (int y = 0; y < 8; y++) {
    Serial.print("<Completion: ");
    Serial.print(100/8*y);
    Serial.println("%>");
    digitalWrite(row[y], LOW);  // Activate row
    for (int x = 0; x < 8; x++) {
      digitalWrite(col[x], HIGH); // Activate column
      shutter(); // Trigger shutter
      delay(exposureTime); // Wait for shutter time
      digitalWrite(col[x], LOW);  // Deactivate column
    }
    digitalWrite(row[y], HIGH); // Deactivate row
  }
  lightsOn();
  Serial.println("<RTI Capture Completed>");
  Serial.println("===================");
}


//Serial data
//call function based on serial input
void callFunction(){
  // 0 = LEDs off. 
  if(functionCalled == 0){
    lightsOff();}
  // 1 LEDs on
  else if(functionCalled == 1){
    lightsOn();}
  // 2 = UV LED
  else if(functionCalled == 2){
    uvOn();}
  // 3 = single LED ($LED_NUMBER)
  else if(functionCalled == 3){
    singleLED(int1Data);}
  // 4 = UV capture ($EXPOSURE_TIME)
  else if (functionCalled == 4){
    uvPhoto(int1Data);}
  // 5 = RTI capture ($EXPOSURE_TIME)
  else if (functionCalled == 5){
  	rti(int1Data);}
  else if (functionCalled == 6){
  	shutter();}
  // incorrect call
  else{
    Serial.print("<INCORRECT FUNCTION CALL: ");
    Serial.print(functionCalled);
    Serial.println(">");
  }
}


// receive serial data
// recieves and appends data send between startMarker and endMarker
void recvData(){
  static boolean receivingData = false;
  static byte ndx = 0;
  char startMarker = '<';
  char endMarker = '>';
  char rc;
  
  while (Serial.available() > 0 && newData == false){
    rc = Serial.read();
    
    if (receivingData == true){
      // append new character to receivedData
      if (rc != endMarker){
        receivedData[ndx] = rc;
        ndx++;
        // overflow buffer
        if (ndx >= numChars){
          ndx = numChars -1;
        }
      }
      // end receiving
      else {
        receivedData[ndx] = '\0';
        receivingData = false;
        ndx = 0;
        // flag new data
        newData = true;
      }
    }
    // starts recieving at "<"
    else if (rc == startMarker){
      receivingData = true;
    }
  }
}


// parse data input to INTs <FUNCTION, INT1, INT2, INT3, INT4>
void parseData(){
  char * strtokIndx;
  
  strtokIndx = strtok(tempData, ",");
  functionCalled = atoi(strtokIndx);
  
  strtokIndx = strtok(NULL, ",");
  int1Data = atoi(strtokIndx);
  
  strtokIndx = strtok(NULL, ",");
  int2Data = atoi(strtokIndx);
  
  strtokIndx = strtok(NULL, ",");
  int3Data = atoi(strtokIndx);
  
  strtokIndx = strtok(NULL, ",");
  int4Data = atoi(strtokIndx);
}
